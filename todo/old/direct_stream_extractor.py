#!/usr/bin/env python3
"""
Direct Stream Extractor
Extrae URLs directas de streams desde páginas de canales específicas
"""

import requests
from bs4 import BeautifulSoup
import cloudscraper
import re
import time
import json
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64

class DirectStreamExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.cloudscraper = cloudscraper.create_scraper()
        self.setup_headers()
        self.driver = None
        
        # Patrones para encontrar streams directos
        self.stream_patterns = [
            # M3U8 patterns
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*m3u8[^"\']*)["\']',
            
            # TS patterns
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            
            # HLS patterns
            r'["\']([^"\']*hls[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*playlist\.m3u8[^"\']*)["\']',
            
            # Common video source patterns
            r'source\s*:\s*["\']([^"\']+)["\']',
            r'src\s*:\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'video\s*:\s*["\']([^"\']+)["\']',
            r'stream\s*:\s*["\']([^"\']+)["\']',
            
            # HLS.js patterns
            r'hls\.loadSource\(["\']([^"\']+)["\']',
            r'video\.src\s*=\s*["\']([^"\']+)["\']',
            
            # Player patterns
            r'player\.src\(["\']([^"\']+)["\']',
            r'jwplayer.*?file\s*:\s*["\']([^"\']+)["\']',
            r'flowplayer.*?clip\s*:\s*["\']([^"\']+)["\']',
            
            # Generic streaming patterns
            r'["\']([^"\']*stream[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*live[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*tv[^"\']*\.m3u8[^"\']*)["\']',
            
            # Base64 encoded patterns (common in some sites)
            r'atob\(["\']([A-Za-z0-9+/=]+)["\']',
            r'base64,["\']([A-Za-z0-9+/=]+)["\']',
        ]
        
        # Patrones para encontrar iframes que contienen streams
        self.iframe_patterns = [
            r'<iframe[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'iframe.*?src\s*=\s*["\']([^"\']+)["\']',
        ]
        
    def setup_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.vertvcable.com/',
        }
        self.session.headers.update(headers)
        self.cloudscraper.headers.update(headers)
    
    def setup_selenium(self):
        """Configura Selenium para casos complejos"""
        if self.driver:
            return self.driver
            
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            print(f"⚠️  Error configurando Selenium: {e}")
            return None
    
    def make_request(self, url, use_selenium=False):
        """Hace petición con diferentes métodos"""
        try:
            if use_selenium:
                driver = self.setup_selenium()
                if driver:
                    driver.get(url)
                    time.sleep(3)
                    return driver.page_source
            
            # Intentar primero con cloudscraper
            try:
                response = self.cloudscraper.get(url, timeout=15)
                if response.status_code == 200:
                    return response.text
            except:
                pass
            
            # Si falla, intentar con requests normal
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
                
        except Exception as e:
            print(f"❌ Error al acceder a {url}: {e}")
            
        return None
    
    def decode_base64_streams(self, content):
        """Decodifica streams en base64"""
        streams = []
        
        # Buscar patrones base64
        base64_patterns = [
            r'atob\(["\']([A-Za-z0-9+/=]+)["\']',
            r'base64,["\']([A-Za-z0-9+/=]+)["\']',
            r'["\']([A-Za-z0-9+/=]{50,})["\']'  # Cadenas largas que podrían ser base64
        ]
        
        for pattern in base64_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    # Verificar si contiene URL de stream
                    if any(ext in decoded.lower() for ext in ['.m3u8', '.ts', 'hls', 'stream', 'live']):
                        if decoded.startswith('http'):
                            streams.append(decoded)
                except:
                    continue
                    
        return streams
    
    def extract_from_javascript(self, content):
        """Extrae streams de código JavaScript"""
        streams = []
        
        # Buscar variables JavaScript que contienen streams
        js_var_patterns = [
            r'var\s+\w+\s*=\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'let\s+\w+\s*=\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'const\s+\w+\s*=\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in js_var_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            streams.extend(matches)
        
        # Buscar streams directamente en el contenido
        for pattern in self.stream_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self.is_valid_stream_url(match):
                    streams.append(match)
        
        return streams
    
    def is_valid_stream_url(self, url):
        """Verifica si una URL es un stream válido"""
        if not url or len(url) < 10:
            return False
            
        # Debe contener extensiones de stream o palabras clave
        stream_indicators = [
            '.m3u8', '.ts', 'hls', 'stream', 'live', 'playlist',
            'manifest', 'chunklist', 'index.m3u8'
        ]
        
        url_lower = url.lower()
        if not any(indicator in url_lower for indicator in stream_indicators):
            return False
        
        # No debe ser imagen, CSS, JS, etc.
        exclude_extensions = [
            '.jpg', '.png', '.gif', '.css', '.js', '.ico', 
            '.svg', '.woff', '.ttf', '.json', '.xml'
        ]
        
        if any(ext in url_lower for ext in exclude_extensions):
            return False
            
        return True
    
    def extract_iframe_streams(self, content, base_url):
        """Extrae streams de iframes"""
        streams = []
        
        soup = BeautifulSoup(content, 'html.parser')
        iframes = soup.find_all('iframe')
        
        for iframe in iframes:
            src = iframe.get('src')
            if not src:
                continue
                
            if not src.startswith('http'):
                src = urljoin(base_url, src)
            
            # Evitar iframes de publicidad y redes sociales
            skip_domains = [
                'google', 'facebook', 'twitter', 'instagram', 'youtube.com/embed',
                'ads', 'doubleclick', 'googlesyndication', 'amazon-adsystem'
            ]
            
            if any(domain in src.lower() for domain in skip_domains):
                continue
            
            print(f"  🔍 Analizando iframe: {src[:60]}...")
            
            # Obtener contenido del iframe
            iframe_content = self.make_request(src)
            if iframe_content:
                iframe_streams = self.extract_streams_from_content(iframe_content, src)
                streams.extend(iframe_streams)
                
                # Si no encontramos streams directos, buscar iframes anidados
                if not iframe_streams:
                    nested_streams = self.extract_iframe_streams(iframe_content, src)
                    streams.extend(nested_streams)
        
        return streams
    
    def extract_streams_from_content(self, content, base_url):
        """Extrae todos los streams posibles del contenido"""
        streams = []
        
        # 1. Buscar streams en JavaScript
        js_streams = self.extract_from_javascript(content)
        streams.extend(js_streams)
        
        # 2. Buscar streams en base64
        b64_streams = self.decode_base64_streams(content)
        streams.extend(b64_streams)
        
        # 3. Buscar en elementos HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Videos directos
        for video in soup.find_all(['video', 'source']):
            src = video.get('src')
            if src and self.is_valid_stream_url(src):
                if not src.startswith('http'):
                    src = urljoin(base_url, src)
                streams.append(src)
        
        # 4. Buscar patrones específicos en el HTML crudo
        for pattern in self.stream_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self.is_valid_stream_url(match):
                    if not match.startswith('http'):
                        match = urljoin(base_url, match)
                    streams.append(match)
        
        return list(set(streams))  # Eliminar duplicados
    
    def extract_direct_stream(self, channel_url, channel_name):
        """Extrae el stream directo de una página de canal específica"""
        print(f"\n🔍 Extrayendo stream directo de: {channel_name}")
        print(f"   URL: {channel_url}")
        
        streams = []
        
        # Método 1: Petición normal
        content = self.make_request(channel_url)
        if content:
            print("  ✅ Contenido obtenido con requests")
            streams.extend(self.extract_streams_from_content(content, channel_url))
            
            # Buscar iframes
            iframe_streams = self.extract_iframe_streams(content, channel_url)
            streams.extend(iframe_streams)
        
        # Método 2: Con Selenium si no encontramos nada
        if not streams:
            print("  🤖 Intentando con Selenium...")
            selenium_content = self.make_request(channel_url, use_selenium=True)
            if selenium_content:
                streams.extend(self.extract_streams_from_content(selenium_content, channel_url))
                iframe_streams = self.extract_iframe_streams(selenium_content, channel_url)
                streams.extend(iframe_streams)
        
        # Filtrar streams válidos
        valid_streams = []
        for stream in streams:
            if self.is_valid_stream_url(stream) and stream.startswith('http'):
                valid_streams.append({
                    'name': channel_name,
                    'url': stream,
                    'source_page': channel_url
                })
        
        if valid_streams:
            print(f"  ✅ Encontrados {len(valid_streams)} streams directos")
            for i, stream in enumerate(valid_streams, 1):
                print(f"    {i}. {stream['url'][:80]}...")
        else:
            print(f"  ❌ No se encontraron streams directos")
        
        return valid_streams
    
    def extract_all_channels(self):
        """Extrae streams de todos los canales encontrados"""
        
        # Canales encontrados en vertvcable.com
        channels = [
            {
                'name': 'EL CANAL DEL FÚTBOL (ECDF)',
                'url': 'https://www.vertvcable.com/el-canal-del-futbol-ecdf-en-vivo/'
            },
            {
                'name': 'Canal 5 Linares',
                'url': 'https://www.vertvcable.com/canal-5-linares-en-vivo/'
            },
            {
                'name': 'Canal 2 Linares',
                'url': 'https://www.vertvcable.com/canal-2-linares-en-vivo/'
            },
            {
                'name': 'Telecanal',
                'url': 'https://www.vertvcable.com/telecanal-en-vivo/'
            },
            {
                'name': 'Canal Pais',
                'url': 'https://www.vertvcable.com/canal-pais-en-vivo/'
            },
            {
                'name': 'Canal De Deportes CRTV Chile',
                'url': 'https://www.vertvcable.com/canal-de-deportes-crtv-chile-en-vivo/'
            },
            {
                'name': 'HBO Family',
                'url': 'https://www.vertvcable.com/hbo-family-en-vivo/'
            },
            {
                'name': 'CHV Deportes',
                'url': 'https://www.vertvcable.com/chv-deportes-en-vivo/'
            }
        ]
        
        print("🎬 EXTRACTOR DE STREAMS DIRECTOS")
        print("="*60)
        print(f"📺 Analizando {len(channels)} canales para extraer URLs directas...")
        
        all_streams = []
        
        for i, channel in enumerate(channels, 1):
            print(f"\n📡 Canal {i}/{len(channels)}")
            try:
                streams = self.extract_direct_stream(channel['url'], channel['name'])
                all_streams.extend(streams)
                time.sleep(2)  # Pausa para no sobrecargar el servidor
            except Exception as e:
                print(f"❌ Error procesando {channel['name']}: {e}")
        
        return all_streams
    
    def verify_stream(self, stream_url):
        """Verifica si un stream funciona"""
        try:
            response = self.session.head(stream_url, timeout=10, allow_redirects=True)
            return response.status_code in [200, 206]
        except:
            return False
    
    def generate_m3u_playlist(self, streams, filename="direct_streams.m3u"):
        """Genera playlist M3U con streams directos"""
        if not streams:
            print("❌ No hay streams para generar playlist")
            return
        
        content = "#EXTM3U\n"
        
        for i, stream in enumerate(streams, 1):
            name = stream.get('name', f'Canal {i}')
            url = stream.get('url', '')
            
            # Limpiar nombre
            name = re.sub(r'[^\w\s-]', '', name).strip()
            if not name:
                name = f'Canal {i}'
            
            content += f'#EXTINF:-1 tvg-name="{name}" group-title="Direct Streams",{name}\n'
            content += f'{url}\n'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Playlist M3U generada: {filename}")
        except Exception as e:
            print(f"❌ Error generando playlist: {e}")
    
    def save_results(self, streams, filename="direct_streams.json"):
        """Guarda resultados en JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(streams, f, ensure_ascii=False, indent=2)
            print(f"💾 Resultados guardados: {filename}")
        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")
    
    def close(self):
        """Cierra recursos"""
        if self.driver:
            self.driver.quit()

def main():
    extractor = DirectStreamExtractor()
    
    try:
        # Extraer streams directos
        streams = extractor.extract_all_channels()
        
        if streams:
            print(f"\n🎉 Extracción completada!")
            print(f"📊 Total de streams directos encontrados: {len(streams)}")
            
            # Mostrar resultados
            print(f"\n📋 Streams directos encontrados:")
            for i, stream in enumerate(streams, 1):
                print(f"  {i}. {stream['name']}")
                print(f"     URL: {stream['url']}")
                print(f"     Fuente: {stream['source_page']}")
                print()
            
            # Guardar resultados
            extractor.save_results(streams)
            extractor.generate_m3u_playlist(streams)
            
            # Verificar streams
            verify = input("🔍 ¿Verificar si los streams funcionan? (s/n): ").lower()
            if verify.startswith('s'):
                print("\n🔍 Verificando streams...")
                working_streams = []
                
                for i, stream in enumerate(streams, 1):
                    print(f"  Verificando {i}/{len(streams)}: {stream['name']}")
                    if extractor.verify_stream(stream['url']):
                        working_streams.append(stream)
                        print(f"    ✅ Funciona")
                    else:
                        print(f"    ❌ No funciona")
                
                print(f"\n📊 Resumen:")
                print(f"✅ Streams funcionando: {len(working_streams)}")
                print(f"❌ Streams no funcionando: {len(streams) - len(working_streams)}")
                
                if working_streams:
                    extractor.generate_m3u_playlist(working_streams, "working_streams.m3u")
                    extractor.save_results(working_streams, "working_streams.json")
        else:
            print("❌ No se encontraron streams directos")
            print("\n💡 Posibles causas:")
            print("- Los streams están protegidos o encriptados")
            print("- Se necesita JavaScript para cargar los streams")
            print("- Los sitios tienen protecciones anti-bot")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
