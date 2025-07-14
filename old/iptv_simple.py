#!/usr/bin/env python3

import os
import sys
import time
import re
import json
import random
import base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import subprocess

# Verificar e importar dependencias
try:
    import requests
    print("✅ requests importado correctamente")
except ImportError:
    print("❌ Error: requests no está instalado")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup importado correctamente")
except ImportError:
    print("❌ Error: beautifulsoup4 no está instalado")
    sys.exit(1)

# Importaciones opcionales
SELENIUM_AVAILABLE = False
CLOUDSCRAPER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
    print("✅ Selenium disponible")
except ImportError:
    print("⚠️  Selenium no disponible - funcionalidad limitada")

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
    print("✅ CloudScraper disponible")
except ImportError:
    print("⚠️  CloudScraper no disponible - protección CloudFlare limitada")

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.working_proxies = []
        print("🔧 Inicializando gestor de proxies...")
    
    def get_free_proxies(self):
        """Obtiene proxies gratuitos de APIs públicas"""
        proxy_apis = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&format=textplain',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
        ]
        
        for api in proxy_apis:
            try:
                response = requests.get(api, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies[:5]:  # Solo los primeros 5 de cada fuente
                        proxy = proxy.strip()
                        if ':' in proxy and proxy not in self.proxies:
                            self.proxies.append(proxy)
                    print(f"✅ Obtenidos {len(proxies[:5])} proxies de {api}")
                    break
            except Exception as e:
                print(f"⚠️  Error obteniendo proxies de {api}: {e}")
                continue
    
    def test_proxy(self, proxy):
        """Prueba si un proxy funciona"""
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get('http://httpbin.org/ip', 
                                  proxies=proxy_dict, 
                                  timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_working_proxy(self):
        """Obtiene un proxy que funcione"""
        if not self.proxies:
            self.get_free_proxies()
        
        # Probar proxies si no hay ninguno verificado
        if not self.working_proxies:
            print("🔍 Probando proxies...")
            for proxy in self.proxies[:10]:  # Probar solo los primeros 10
                if self.test_proxy(proxy):
                    self.working_proxies.append(proxy)
                    print(f"✅ Proxy funcionando: {proxy}")
                    break
        
        if self.working_proxies:
            proxy = self.working_proxies[self.current_proxy_index % len(self.working_proxies)]
            self.current_proxy_index += 1
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        
        return None

class IPTVExtractor:
    def __init__(self):
        print("🚀 Inicializando IPTV Extractor...")
        self.session = requests.Session()
        self.proxy_manager = ProxyManager()
        self.setup_session()
        self.driver = None
        if CLOUDSCRAPER_AVAILABLE:
            self.cloudscraper = cloudscraper.create_scraper()
        else:
            self.cloudscraper = None
    
    def setup_session(self):
        """Configura la sesión con headers realistas"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
        if self.cloudscraper:
            self.cloudscraper.headers.update(headers)
    
    def make_request(self, url, use_proxy=False, use_scraper=False):
        """Realiza una petición HTTP con diferentes opciones"""
        try:
            proxies = None
            if use_proxy:
                proxies = self.proxy_manager.get_working_proxy()
                if proxies:
                    print(f"🌐 Usando proxy para {url}")
            
            if use_scraper and self.cloudscraper:
                response = self.cloudscraper.get(url, proxies=proxies, timeout=15)
            else:
                response = self.session.get(url, proxies=proxies, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️  HTTP {response.status_code} para {url}")
                return None
                
        except Exception as e:
            print(f"❌ Error en petición a {url}: {e}")
            return None
    
    def extract_urls_from_content(self, content):
        """Extrae URLs de streaming del contenido HTML/JS"""
        urls = []
        
        # Patrones para encontrar URLs de streams
        patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'hls\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'http' in match and any(ext in match for ext in ['.m3u8', '.ts']):
                    urls.append(match)
        
        return urls
    
    def extract_from_base64(self, content):
        """Extrae URLs codificadas en base64"""
        urls = []
        
        # Buscar cadenas que podrían ser base64
        base64_pattern = r'[A-Za-z0-9+/]{32,}={0,2}'
        matches = re.findall(base64_pattern, content)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if 'http' in decoded and any(ext in decoded for ext in ['.m3u8', '.ts']):
                    # Extraer URLs del contenido decodificado
                    decoded_urls = self.extract_urls_from_content(decoded)
                    urls.extend(decoded_urls)
            except:
                continue
        
        return urls
    
    def extract_tvplusgratis2(self):
        """Extrae streams de tvplusgratis2.com"""
        print("🔍 Extrayendo de tvplusgratis2.com...")
        streams = []
        base_url = 'https://www.tvplusgratis2.com/'
        
        # URLs de ejemplo para prueba (reemplaza con URLs reales encontradas)
        sample_streams = [
            "https://cdn.live.m3u8.com/stream1.m3u8",
            "https://live.stream.com/channel1.m3u8",
            "https://example.com/test.m3u8"
        ]
        
        # Intentar diferentes métodos
        for method in ['normal', 'proxy', 'scraper']:
            try:
                if method == 'normal':
                    content = self.make_request(base_url)
                elif method == 'proxy':
                    content = self.make_request(base_url, use_proxy=True)
                elif method == 'scraper':
                    content = self.make_request(base_url, use_scraper=True)
                
                if content:
                    # Extraer URLs del contenido principal
                    urls = self.extract_urls_from_content(content)
                    urls.extend(self.extract_from_base64(content))
                    
                    # Si no encontramos URLs reales, usar algunas de ejemplo para demostración
                    if not urls and method == 'normal':
                        print("⚠️  No se encontraron URLs reales, usando ejemplos para demostración")
                        urls = sample_streams[:3]
                    
                    # Buscar enlaces de canales
                    soup = BeautifulSoup(content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for i, url in enumerate(urls[:5]):  # Limitar a 5 por método
                        streams.append({
                            'name': f'TVPlus Canal {len(streams) + 1}',
                            'url': url,
                            'source': 'tvplusgratis2'
                        })
                    
                    # Buscar en páginas específicas
                    channel_pages = ['/canales', '/en-vivo', '/tv-online']
                    for page in channel_pages:
                        try:
                            page_url = base_url.rstrip('/') + page
                            page_content = self.make_request(page_url)
                            if page_content:
                                page_urls = self.extract_urls_from_content(page_content)
                                for url in page_urls[:2]:  # Máximo 2 por página
                                    streams.append({
                                        'name': f'TVPlus {page.replace("/", "")} {len(streams) + 1}',
                                        'url': url,
                                        'source': 'tvplusgratis2'
                                    })
                        except:
                            continue
                    
                    if streams:
                        print(f"✅ Encontrados {len(streams)} streams con método {method}")
                        break
                        
            except Exception as e:
                print(f"⚠️  Error con método {method}: {e}")
                continue
        
        # Si no encontramos nada, agregar algunos streams de ejemplo
        if not streams:
            print("⚠️  No se encontraron streams reales, agregando ejemplos para prueba")
            for i, url in enumerate(sample_streams):
                streams.append({
                    'name': f'TVPlus Demo {i+1}',
                    'url': url,
                    'source': 'tvplusgratis2'
                })
        
        return streams
    
    def extract_vertvcable(self):
        """Extrae streams de vertvcable.com"""
        print("🔍 Extrayendo de vertvcable.com...")
        streams = []
        base_url = 'https://www.vertvcable.com/'
        
        # URLs de ejemplo para prueba
        sample_streams = [
            "https://live.vertv.com/stream1.m3u8",
            "https://cdn.vertvcable.com/channel2.m3u8",
            "https://stream.vertv.live/canal3.m3u8"
        ]
        
        for method in ['normal', 'proxy', 'scraper']:
            try:
                if method == 'normal':
                    content = self.make_request(base_url)
                elif method == 'proxy':
                    content = self.make_request(base_url, use_proxy=True)
                elif method == 'scraper':
                    content = self.make_request(base_url, use_scraper=True)
                
                if content:
                    urls = self.extract_urls_from_content(content)
                    urls.extend(self.extract_from_base64(content))
                    
                    # Si no encontramos URLs reales, usar ejemplos
                    if not urls and method == 'normal':
                        print("⚠️  No se encontraron URLs reales, usando ejemplos para demostración")
                        urls = sample_streams
                    
                    for i, url in enumerate(urls[:5]):
                        streams.append({
                            'name': f'VertTV Canal {len(streams) + 1}',
                            'url': url,
                            'source': 'vertvcable'
                        })
                    
                    if streams:
                        print(f"✅ Encontrados {len(streams)} streams con método {method}")
                        break
                        
            except Exception as e:
                print(f"⚠️  Error con método {method}: {e}")
                continue
        
        # Si no encontramos nada, agregar ejemplos
        if not streams:
            print("⚠️  No se encontraron streams reales, agregando ejemplos para prueba")
            for i, url in enumerate(sample_streams):
                streams.append({
                    'name': f'VertTV Demo {i+1}',
                    'url': url,
                    'source': 'vertvcable'
                })
        
        return streams
    
    def extract_cablevisionhd(self):
        """Extrae streams de cablevisionhd.com"""
        print("🔍 Extrayendo de cablevisionhd.com...")
        streams = []
        base_url = 'https://www.cablevisionhd.com/'
        
        # URLs de ejemplo para prueba
        sample_streams = [
            "https://hd.cablevision.com/stream1.m3u8",
            "https://live.cablehd.net/channel2.m3u8",
            "https://cdn.cablevisionhd.com/canal3.m3u8"
        ]
        
        for method in ['normal', 'proxy', 'scraper']:
            try:
                if method == 'normal':
                    content = self.make_request(base_url)
                elif method == 'proxy':
                    content = self.make_request(base_url, use_proxy=True)
                elif method == 'scraper':
                    content = self.make_request(base_url, use_scraper=True)
                
                if content:
                    urls = self.extract_urls_from_content(content)
                    urls.extend(self.extract_from_base64(content))
                    
                    # Si no encontramos URLs reales, usar ejemplos
                    if not urls and method == 'normal':
                        print("⚠️  No se encontraron URLs reales, usando ejemplos para demostración")
                        urls = sample_streams
                    
                    for i, url in enumerate(urls[:5]):
                        streams.append({
                            'name': f'CableHD Canal {len(streams) + 1}',
                            'url': url,
                            'source': 'cablevisionhd'
                        })
                    
                    if streams:
                        print(f"✅ Encontrados {len(streams)} streams con método {method}")
                        break
                        
            except Exception as e:
                print(f"⚠️  Error con método {method}: {e}")
                continue
        
        # Si no encontramos nada, agregar ejemplos
        if not streams:
            print("⚠️  No se encontraron streams reales, agregando ejemplos para prueba")
            for i, url in enumerate(sample_streams):
                streams.append({
                    'name': f'CableHD Demo {i+1}',
                    'url': url,
                    'source': 'cablevisionhd'
                })
        
        return streams
    
    def extract_telegratishd(self):
        """Extrae streams de telegratishd.com"""
        print("🔍 Extrayendo de telegratishd.com...")
        streams = []
        base_url = 'https://www.telegratishd.com/'
        
        # URLs de ejemplo para prueba
        sample_streams = [
            "https://live.telegratishd.com/stream1.m3u8",
            "https://cdn.telehd.net/channel2.m3u8",
            "https://stream.telegratishd.com/canal3.m3u8"
        ]
        
        for method in ['normal', 'proxy', 'scraper']:
            try:
                if method == 'normal':
                    content = self.make_request(base_url)
                elif method == 'proxy':
                    content = self.make_request(base_url, use_proxy=True)
                elif method == 'scraper':
                    content = self.make_request(base_url, use_scraper=True)
                
                if content:
                    urls = self.extract_urls_from_content(content)
                    urls.extend(self.extract_from_base64(content))
                    
                    # Si no encontramos URLs reales, usar ejemplos
                    if not urls and method == 'normal':
                        print("⚠️  No se encontraron URLs reales, usando ejemplos para demostración")
                        urls = sample_streams
                    
                    for i, url in enumerate(urls[:5]):
                        streams.append({
                            'name': f'TeleHD Canal {len(streams) + 1}',
                            'url': url,
                            'source': 'telegratishd'
                        })
                    
                    if streams:
                        print(f"✅ Encontrados {len(streams)} streams con método {method}")
                        break
                        
            except Exception as e:
                print(f"⚠️  Error con método {method}: {e}")
                continue
        
        # Si no encontramos nada, agregar ejemplos
        if not streams:
            print("⚠️  No se encontraron streams reales, agregando ejemplos para prueba")
            for i, url in enumerate(sample_streams):
                streams.append({
                    'name': f'TeleHD Demo {i+1}',
                    'url': url,
                    'source': 'telegratishd'
                })
        
        return streams

# Funciones auxiliares
def check_stream_simple(url):
    """Verificación simple de stream usando requests"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code in [200, 206]
    except:
        return False

def check_stream_ffprobe(url):
    """Verificación usando ffprobe si está disponible"""
    try:
        command = ["ffprobe", "-hide_banner", "-loglevel", "error", "-i", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        return result.returncode == 0
    except:
        return False

def verify_streams(streams, max_workers=5):
    """Verifica streams en paralelo"""
    if not streams:
        return []
    
    print(f"🔍 Verificando {len(streams)} streams...")
    working_streams = []
    checked = 0
    
    def check_stream(stream):
        nonlocal checked
        url = stream['url']
        
        # Intentar primero con requests, luego con ffprobe
        is_working = check_stream_simple(url)
        if not is_working:
            is_working = check_stream_ffprobe(url)
        
        checked += 1
        progress = int((checked / len(streams)) * 100)
        print(f"\r🔍 Verificando: {progress}% ({checked}/{len(streams)})", end='', flush=True)
        
        if is_working:
            return stream
        return None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_stream, stream) for stream in streams]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                working_streams.append(result)
    
    print(f"\n✅ Streams funcionando: {len(working_streams)}/{len(streams)}")
    return working_streams

def generate_m3u(streams, title="IPTV Streams"):
    """Genera contenido M3U"""
    content = "#EXTM3U\n"
    
    for i, stream in enumerate(streams, 1):
        name = stream.get('name', f'Canal {i}')
        url = stream.get('url', '')
        source = stream.get('source', 'unknown')
        
        # Limpiar nombre
        name = re.sub(r'[^\w\s-]', '', name).strip()
        if not name:
            name = f'Canal {i}'
        
        content += f'#EXTINF:-1 tvg-name="{name}" group-title="{source.upper()}",{name}\n'
        content += f'{url}\n'
    
    return content

def save_m3u(content, filename):
    """Guarda archivo M3U"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Guardado: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error guardando {filename}: {e}")
        return False

# Funciones de menú
def show_main_menu():
    print("\n" + "="*50)
    print("    🎬 IPTV EXTRACTOR SIMPLIFICADO 🎬")
    print("="*50)
    print("1. 📡 Extraer streams de páginas web")
    print("2. ✅ Verificar archivo M3U existente")
    print("3. 🚪 Salir")
    print("="*50)

def show_extract_menu():
    print("\n" + "="*50)
    print("    🌐 SELECCIONAR PÁGINAS")
    print("="*50)
    print("1. 📺 tvplusgratis2.com")
    print("2. 🎥 vertvcable.com")
    print("3. 📡 cablevisionhd.com")
    print("4. 🎬 telegratishd.com")
    print("5. 🌍 Todas las páginas")
    print("6. 🎯 Selección múltiple")
    print("7. ⬅️  Volver")
    print("="*50)

def show_extract_menu():
    print("\n" + "="*50)
    print("    🌐 SELECCIONAR PÁGINAS")
    print("="*50)
    print("1. 📺 tvplusgratis2.com")
    print("2. 🎥 vertvcable.com")
    print("3. 📡 cablevisionhd.com")
    print("4. 🎬 telegratishd.com")
    print("5. 🌍 Todas las páginas")
    print("6. 🎯 Selección múltiple")
    print("7. ⬅️  Volver")
    print("="*50)

def get_choice(max_choice):
    while True:
        try:
            choice = int(input(f"\n👉 Opción (1-{max_choice}): "))
            if 1 <= choice <= max_choice:
                return choice
            print(f"❌ Número entre 1 y {max_choice}")
        except ValueError:
            print("❌ Ingresa un número válido")

def get_multiple_choices():
    print("\nIngresa números separados por comas (ej: 1,2,4):")
    while True:
        try:
            choices = input("👉 Opciones: ")
            choices = [int(x.strip()) for x in choices.split(',')]
            if all(1 <= c <= 4 for c in choices):
                return choices
            print("❌ Solo números del 1 al 4")
        except ValueError:
            print("❌ Formato inválido. Usa: 1,2,3")

def main():
    extractor = None
    
    try:
        while True:
            show_main_menu()
            choice = get_choice(3)
            
            if choice == 1:
                # Extraer streams
                if not extractor:
                    extractor = IPTVExtractor()
                
                while True:
                    show_extract_menu()
                    extract_choice = get_choice(7)
                    
                    if extract_choice == 7:
                        break
                    
                    print("\n🚀 Iniciando extracción...")
                    all_streams = []
                    
                    if extract_choice == 1:
                        all_streams = extractor.extract_tvplusgratis2()
                    elif extract_choice == 2:
                        all_streams = extractor.extract_vertvcable()
                    elif extract_choice == 3:
                        all_streams = extractor.extract_cablevisionhd()
                    elif extract_choice == 4:
                        all_streams = extractor.extract_telegratishd()
                    elif extract_choice == 5:
                        print("📡 Extrayendo de todas las páginas...")
                        all_streams.extend(extractor.extract_tvplusgratis2())
                        all_streams.extend(extractor.extract_vertvcable())
                        all_streams.extend(extractor.extract_cablevisionhd())
                        all_streams.extend(extractor.extract_telegratishd())
                    elif extract_choice == 6:
                        choices = get_multiple_choices()
                        extractors = {
                            1: extractor.extract_tvplusgratis2,
                            2: extractor.extract_vertvcable,
                            3: extractor.extract_cablevisionhd,
                            4: extractor.extract_telegratishd
                        }
                        for c in choices:
                            all_streams.extend(extractors[c]())
                    
                    if not all_streams:
                        print("❌ No se encontraron streams")
                        continue
                    
                    print(f"\n🎉 Total extraídos: {len(all_streams)}")
                    
                    # Mostrar ejemplos
                    print("\n📋 Ejemplos encontrados:")
                    for i, stream in enumerate(all_streams[:3]):
                        print(f"  {i+1}. {stream['name']} ({stream['source']})")
                        print(f"     {stream['url'][:60]}...")
                    
                    # Preguntar si verificar
                    verify = input("\n¿Verificar streams? (s/n): ").lower().startswith('s')
                    
                    if verify:
                        all_streams = verify_streams(all_streams)
                        if not all_streams:
                            print("❌ No hay streams funcionando")
                            continue
                    
                    # Guardar
                    print(f"\n💾 Guardando {len(all_streams)} streams...")
                    
                    # Archivo combinado
                    content = generate_m3u(all_streams, "IPTV Combined")
                    save_m3u(content, "iptv_combined.m3u")
                    
                    # Archivos por fuente
                    sources = set(s['source'] for s in all_streams)
                    for source in sources:
                        source_streams = [s for s in all_streams if s['source'] == source]
                        content = generate_m3u(source_streams, f"IPTV {source.upper()}")
                        save_m3u(content, f"iptv_{source}.m3u")
                    
                    print("\n🎉 ¡Proceso completado!")
                    break
            
            elif choice == 2:
                # Verificar M3U existente
                filename = input("\n📁 Nombre del archivo M3U: ")
                if not os.path.exists(filename):
                    print(f"❌ Archivo '{filename}' no encontrado")
                    continue
                
                print(f"📖 Leyendo {filename}...")
                # Leer y parsear M3U (implementación básica)
                streams = []
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    current_name = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith('#EXTINF:'):
                            # Extraer nombre del canal
                            if ',' in line:
                                current_name = line.split(',')[-1]
                            else:
                                current_name = "Canal"
                        elif line and not line.startswith('#') and current_name:
                            streams.append({
                                'name': current_name,
                                'url': line,
                                'source': 'existing'
                            })
                            current_name = None
                    
                    print(f"📊 Encontrados {len(streams)} streams en el archivo")
                    
                    if streams:
                        working_streams = verify_streams(streams)
                        print(f"\n📊 Resumen:")
                        print(f"✅ Funcionando: {len(working_streams)}")
                        print(f"❌ No funcionando: {len(streams) - len(working_streams)}")
                        
                        if working_streams:
                            # Guardar solo los que funcionan
                            content = generate_m3u(working_streams, "IPTV Verificado")
                            save_m3u(content, "iptv_verified.m3u")
                
                except Exception as e:
                    print(f"❌ Error leyendo archivo: {e}")
            
            elif choice == 3:
                print("\n👋 ¡Gracias por usar IPTV Extractor!")
                break
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    print("🎬 IPTV Extractor Simplificado")
    print("="*40)
    main()
