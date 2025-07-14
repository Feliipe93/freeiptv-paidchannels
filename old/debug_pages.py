#!/usr/bin/env python3

import os
import sys
import time
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import base64

# Importaciones opcionales
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class PageDebugger:
    def __init__(self):
        self.session = requests.Session()
        if CLOUDSCRAPER_AVAILABLE:
            self.scraper = cloudscraper.create_scraper()
        else:
            self.scraper = None
        self.setup_session()
        self.driver = None
    
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
        if self.scraper:
            self.scraper.headers.update(headers)
    
    def setup_selenium(self):
        """Configura Selenium para análisis avanzado"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium no disponible")
            return None
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            print(f"❌ Error configurando Selenium: {e}")
            return None
    
    def analyze_page_structure(self, url, site_name):
        """Analiza la estructura completa de una página"""
        print(f"\n🔍 ANALIZANDO {site_name.upper()}: {url}")
        print("="*80)
        
        # Análisis con requests normal
        print("\n📡 ANÁLISIS CON REQUESTS:")
        self.analyze_with_requests(url)
        
        # Análisis con CloudScraper
        if CLOUDSCRAPER_AVAILABLE:
            print("\n☁️  ANÁLISIS CON CLOUDSCRAPER:")
            self.analyze_with_cloudscraper(url)
        
        # Análisis con Selenium
        if SELENIUM_AVAILABLE:
            print("\n🤖 ANÁLISIS CON SELENIUM:")
            self.analyze_with_selenium(url)
        
        # Guardar estructura en archivo
        self.save_page_analysis(url, site_name)
        
        print("\n" + "="*80)
    
    def analyze_with_requests(self, url):
        """Análisis básico con requests"""
        try:
            response = self.session.get(url, timeout=15)
            print(f"✅ Status Code: {response.status_code}")
            print(f"📏 Content Length: {len(response.content)} bytes")
            print(f"🔧 Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.analyze_html_structure(soup, "REQUESTS")
                self.find_potential_streams(response.text, "REQUESTS")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con requests: {e}")
    
    def analyze_with_cloudscraper(self, url):
        """Análisis con CloudScraper"""
        if not self.scraper:
            print("❌ CloudScraper no disponible")
            return
        
        try:
            response = self.scraper.get(url, timeout=15)
            print(f"✅ Status Code: {response.status_code}")
            print(f"📏 Content Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.analyze_html_structure(soup, "CLOUDSCRAPER")
                self.find_potential_streams(response.text, "CLOUDSCRAPER")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error con CloudScraper: {e}")
    
    def analyze_with_selenium(self, url):
        """Análisis avanzado con Selenium"""
        driver = self.setup_selenium()
        if not driver:
            return
        
        try:
            driver.get(url)
            time.sleep(5)  # Esperar a que se cargue completamente
            
            print(f"✅ Página cargada exitosamente")
            print(f"🔗 URL final: {driver.current_url}")
            print(f"📰 Título: {driver.title}")
            
            # Analizar estructura HTML después de JavaScript
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            self.analyze_html_structure(soup, "SELENIUM")
            self.find_potential_streams(html, "SELENIUM")
            
            # Analizar requests de red (si es posible)
            self.analyze_network_requests(driver)
            
        except Exception as e:
            print(f"❌ Error con Selenium: {e}")
        finally:
            if driver:
                driver.quit()
    
    def analyze_html_structure(self, soup, method):
        """Analiza la estructura HTML"""
        print(f"\n🏗️  ESTRUCTURA HTML ({method}):")
        
        # Scripts
        scripts = soup.find_all('script')
        print(f"📜 Scripts encontrados: {len(scripts)}")
        
        # Enlaces
        links = soup.find_all('a', href=True)
        print(f"🔗 Enlaces encontrados: {len(links)}")
        
        # Videos e iframes
        videos = soup.find_all('video')
        iframes = soup.find_all('iframe')
        print(f"🎥 Videos: {len(videos)}, iFrames: {len(iframes)}")
        
        # Formularios
        forms = soup.find_all('form')
        print(f"📝 Formularios: {len(forms)}")
        
        # Metadatos importantes
        meta_tags = soup.find_all('meta')
        print(f"🏷️  Meta tags: {len(meta_tags)}")
        
        # Buscar divs con clases relacionadas a video/stream
        stream_divs = soup.find_all('div', class_=re.compile(r'video|stream|player|canal|tv', re.I))
        print(f"📺 Divs relacionados a streams: {len(stream_divs)}")
        
        # Mostrar algunos ejemplos de scripts importantes
        self.analyze_scripts(scripts, method)
        
        # Mostrar iframes interesantes
        self.analyze_iframes(iframes, method)
    
    def analyze_scripts(self, scripts, method):
        """Analiza scripts JavaScript en busca de streams"""
        print(f"\n🔍 ANÁLISIS DE SCRIPTS ({method}):")
        
        interesting_scripts = []
        
        for i, script in enumerate(scripts):
            if script.string and len(script.string) > 100:
                content = script.string.lower()
                score = 0
                
                # Asignar puntuación basada en palabras clave
                keywords = ['m3u8', 'stream', 'video', 'source', 'url', 'src', 'live', 'hls', 'player']
                for keyword in keywords:
                    score += content.count(keyword)
                
                if score > 0:
                    interesting_scripts.append({
                        'index': i,
                        'score': score,
                        'length': len(script.string),
                        'content': script.string[:500] + "..." if len(script.string) > 500 else script.string
                    })
        
        # Ordenar por puntuación
        interesting_scripts.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"📊 Scripts interesantes encontrados: {len(interesting_scripts)}")
        
        for i, script_info in enumerate(interesting_scripts[:3]):  # Mostrar solo los 3 mejores
            print(f"\n📜 Script #{script_info['index']} (Score: {script_info['score']}):")
            print(f"📏 Longitud: {script_info['length']} caracteres")
            print("📝 Contenido (primeros 500 chars):")
            print("-" * 60)
            print(script_info['content'])
            print("-" * 60)
    
    def analyze_iframes(self, iframes, method):
        """Analiza iframes en busca de streams"""
        print(f"\n🖼️  ANÁLISIS DE IFRAMES ({method}):")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get('src', '')
            print(f"\n🎬 iFrame #{i+1}:")
            print(f"   📍 src: {src}")
            print(f"   📐 width: {iframe.get('width', 'auto')}")
            print(f"   📐 height: {iframe.get('height', 'auto')}")
            
            if src:
                # Intentar analizar el contenido del iframe
                try:
                    if not src.startswith('http'):
                        print(f"   ⚠️  URL relativa, salteando análisis profundo")
                        continue
                    
                    print(f"   🔍 Analizando contenido del iframe...")
                    iframe_response = self.session.get(src, timeout=10)
                    if iframe_response.status_code == 200:
                        iframe_streams = self.find_potential_streams(iframe_response.text, f"IFRAME-{i+1}")
                        print(f"   📊 Streams potenciales en iframe: {len(iframe_streams)}")
                    else:
                        print(f"   ❌ Error accediendo iframe: {iframe_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error analizando iframe: {e}")
    
    def find_potential_streams(self, content, method):
        """Busca URLs potenciales de streams"""
        print(f"\n🎯 BÚSQUEDA DE STREAMS ({method}):")
        
        # Patrones para URLs de streams
        patterns = {
            'm3u8_direct': r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            'ts_direct': r'["\']([^"\']*\.ts[^"\']*)["\']',
            'stream_keyword': r'["\']([^"\']*stream[^"\']*\.(m3u8|ts)[^"\']*)["\']',
            'source_property': r'source\s*:\s*["\']([^"\']+)["\']',
            'src_property': r'src\s*:\s*["\']([^"\']+)["\']',
            'url_property': r'url\s*:\s*["\']([^"\']+)["\']',
            'file_property': r'file\s*:\s*["\']([^"\']+)["\']',
            'hls_property': r'hls\s*:\s*["\']([^"\']+)["\']',
            'playlist_property': r'playlist\s*:\s*["\']([^"\']+)["\']'
        }
        
        found_streams = []
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"   🎯 {pattern_name}: {len(matches)} coincidencias")
                for match in matches[:5]:  # Mostrar solo las primeras 5
                    url = match if isinstance(match, str) else match[0]
                    if any(ext in url.lower() for ext in ['.m3u8', '.ts', 'stream', 'live']):
                        found_streams.append(url)
                        print(f"      🔗 {url}")
        
        # Buscar URLs en base64
        base64_streams = self.find_base64_streams(content)
        if base64_streams:
            print(f"   🔐 Base64 decodificados: {len(base64_streams)}")
            for stream in base64_streams[:3]:
                found_streams.append(stream)
                print(f"      🔗 {stream}")
        
        # Buscar patrones de configuración de reproductores
        player_configs = self.find_player_configs(content)
        if player_configs:
            print(f"   🎮 Configuraciones de reproductores: {len(player_configs)}")
            for config in player_configs[:3]:
                print(f"      ⚙️  {config}")
        
        return found_streams
    
    def find_base64_streams(self, content):
        """Busca streams codificados en base64"""
        streams = []
        
        # Buscar cadenas que podrían ser base64
        base64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
        matches = re.findall(base64_pattern, content)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if any(ext in decoded.lower() for ext in ['.m3u8', '.ts', 'stream', 'live', 'http']):
                    # Buscar URLs dentro del contenido decodificado
                    url_pattern = r'https?://[^\s<>"\']{10,}'
                    urls = re.findall(url_pattern, decoded)
                    for url in urls:
                        if any(ext in url for ext in ['.m3u8', '.ts']):
                            streams.append(url)
            except:
                continue
        
        return streams
    
    def find_player_configs(self, content):
        """Busca configuraciones de reproductores de video"""
        configs = []
        
        # Patrones para configuraciones de reproductores conocidos
        patterns = [
            r'jwplayer\s*\([^)]+\)\.setup\s*\(\s*({[^}]+})\s*\)',
            r'videojs\s*\([^)]+\)\.src\s*\(\s*({[^}]+})\s*\)',
            r'new\s+Playerjs\s*\(\s*({[^}]+})\s*\)',
            r'Clappr\.Player\s*\(\s*({[^}]+})\s*\)',
            r'flowplayer\s*\([^)]*,\s*({[^}]+})\s*\)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    # Intentar parsear como JSON (aproximado)
                    configs.append(match[:200] + "..." if len(match) > 200 else match)
                except:
                    continue
        
        return configs
    
    def analyze_network_requests(self, driver):
        """Analiza requests de red con Selenium"""
        print(f"\n🌐 ANÁLISIS DE RED:")
        
        try:
            # Intentar obtener logs de red (funciona en algunos casos)
            logs = driver.get_log('performance')
            
            network_requests = []
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    if any(ext in url for ext in ['.m3u8', '.ts', 'stream', 'live']):
                        network_requests.append(url)
            
            if network_requests:
                print(f"   📡 Requests de red relevantes: {len(network_requests)}")
                for req in network_requests[:5]:
                    print(f"      🔗 {req}")
            else:
                print("   ❌ No se encontraron requests de red relevantes")
                
        except Exception as e:
            print(f"   ⚠️  No se pudieron obtener logs de red: {e}")
    
    def save_page_analysis(self, url, site_name):
        """Guarda el análisis en un archivo"""
        try:
            # Crear directorio de análisis si no existe
            analysis_dir = "page_analysis"
            if not os.path.exists(analysis_dir):
                os.makedirs(analysis_dir)
            
            # Guardar HTML de la página
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    filename = f"{analysis_dir}/{site_name}_source.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"💾 HTML guardado en: {filename}")
            except:
                pass
            
            # Guardar análisis estructurado
            analysis_data = {
                'url': url,
                'site_name': site_name,
                'timestamp': time.time(),
                'analysis_complete': True
            }
            
            filename = f"{analysis_dir}/{site_name}_analysis.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2)
            print(f"💾 Análisis guardado en: {filename}")
            
        except Exception as e:
            print(f"❌ Error guardando análisis: {e}")
    
    def interactive_debug(self, url, site_name):
        """Modo interactivo para debugging detallado"""
        print(f"\n🛠️  MODO DEBUG INTERACTIVO PARA {site_name.upper()}")
        print("="*60)
        
        while True:
            print("\nOpciones disponibles:")
            print("1. Analizar estructura HTML")
            print("2. Buscar streams con patrones específicos")
            print("3. Analizar JavaScript específico")
            print("4. Probar URL personalizada")
            print("5. Extraer todos los enlaces")
            print("6. Buscar formularios y campos")
            print("7. Volver al menú principal")
            
            choice = input("\n👉 Selecciona una opción (1-7): ")
            
            if choice == '1':
                self.debug_html_structure(url)
            elif choice == '2':
                self.debug_custom_patterns(url)
            elif choice == '3':
                self.debug_javascript(url)
            elif choice == '4':
                custom_url = input("Ingresa URL personalizada: ")
                self.analyze_page_structure(custom_url, "CUSTOM")
            elif choice == '5':
                self.extract_all_links(url)
            elif choice == '6':
                self.analyze_forms(url)
            elif choice == '7':
                break
            else:
                print("❌ Opción inválida")
    
    def debug_html_structure(self, url):
        """Debug detallado de estructura HTML"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"\n🔍 ELEMENTOS POR TIPO:")
            elements = {
                'div': soup.find_all('div'),
                'span': soup.find_all('span'),
                'script': soup.find_all('script'),
                'iframe': soup.find_all('iframe'),
                'video': soup.find_all('video'),
                'source': soup.find_all('source'),
                'a': soup.find_all('a'),
                'form': soup.find_all('form'),
                'input': soup.find_all('input')
            }
            
            for tag, elements_list in elements.items():
                print(f"{tag.upper()}: {len(elements_list)}")
            
            # Mostrar clases CSS más comunes
            all_classes = []
            for element in soup.find_all(class_=True):
                all_classes.extend(element.get('class'))
            
            from collections import Counter
            common_classes = Counter(all_classes).most_common(10)
            
            print(f"\n🎨 CLASES CSS MÁS COMUNES:")
            for class_name, count in common_classes:
                print(f"   .{class_name}: {count}")
                
        except Exception as e:
            print(f"❌ Error en debug HTML: {e}")
    
    def debug_custom_patterns(self, url):
        """Permite probar patrones personalizados"""
        try:
            response = self.session.get(url, timeout=15)
            content = response.text
            
            pattern = input("Ingresa patrón regex personalizado: ")
            
            matches = re.findall(pattern, content, re.IGNORECASE)
            print(f"\n🎯 Encontradas {len(matches)} coincidencias:")
            
            for i, match in enumerate(matches[:10]):
                print(f"   {i+1}. {match}")
                
        except Exception as e:
            print(f"❌ Error en debug de patrones: {e}")
    
    def debug_javascript(self, url):
        """Analiza JavaScript específico"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            
            print(f"\n📜 SCRIPTS DISPONIBLES: {len(scripts)}")
            for i, script in enumerate(scripts):
                if script.string and len(script.string) > 50:
                    print(f"   {i+1}. Longitud: {len(script.string)} chars")
            
            choice = input("Selecciona número de script para analizar: ")
            try:
                script_idx = int(choice) - 1
                if 0 <= script_idx < len(scripts):
                    script_content = scripts[script_idx].string
                    if script_content:
                        print(f"\n📝 CONTENIDO DEL SCRIPT #{choice}:")
                        print("-" * 80)
                        print(script_content[:2000] + "..." if len(script_content) > 2000 else script_content)
                        print("-" * 80)
                    else:
                        print("❌ Script vacío o sin contenido")
                else:
                    print("❌ Número de script inválido")
            except ValueError:
                print("❌ Número inválido")
                
        except Exception as e:
            print(f"❌ Error en debug de JavaScript: {e}")
    
    def extract_all_links(self, url):
        """Extrae todos los enlaces de la página"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = soup.find_all('a', href=True)
            print(f"\n🔗 TODOS LOS ENLACES ({len(links)}):")
            
            for i, link in enumerate(links[:20]):  # Mostrar solo los primeros 20
                href = link.get('href')
                text = link.get_text(strip=True)[:50]
                print(f"   {i+1}. {href} ({text})")
            
            if len(links) > 20:
                print(f"   ... y {len(links) - 20} más")
                
        except Exception as e:
            print(f"❌ Error extrayendo enlaces: {e}")
    
    def analyze_forms(self, url):
        """Analiza formularios en la página"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            forms = soup.find_all('form')
            print(f"\n📝 FORMULARIOS ENCONTRADOS: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"\n📝 Formulario #{i+1}:")
                print(f"   📍 Action: {form.get('action', 'N/A')}")
                print(f"   📋 Method: {form.get('method', 'GET')}")
                
                inputs = form.find_all(['input', 'select', 'textarea'])
                print(f"   🔧 Campos: {len(inputs)}")
                
                for input_elem in inputs[:5]:
                    input_type = input_elem.get('type', input_elem.name)
                    input_name = input_elem.get('name', 'N/A')
                    print(f"      - {input_type}: {input_name}")
                
        except Exception as e:
            print(f"❌ Error analizando formularios: {e}")

def main():
    debugger = PageDebugger()
    
    # URLs de las páginas a analizar
    pages = [
        ('https://www.tvplusgratis2.com/', 'tvplusgratis2'),
        ('https://www.vertvcable.com/', 'vertvcable'),
        ('https://www.cablevisionhd.com/', 'cablevisionhd'),
        ('https://www.telegratishd.com/', 'telegratishd')
    ]
    
    print("🔍 ANALIZADOR DE PÁGINAS IPTV")
    print("="*50)
    print("\nEste script analizará la estructura de las páginas web")
    print("para entender cómo extraer los streams correctamente.\n")
    
    while True:
        print("\nOpciones disponibles:")
        print("1. Análisis completo de todas las páginas")
        print("2. Análisis individual por página")
        print("3. Modo debug interactivo")
        print("4. Analizar URL personalizada")
        print("5. Salir")
        
        choice = input("\n👉 Selecciona una opción (1-5): ")
        
        if choice == '1':
            print("\n🚀 Iniciando análisis completo...")
            for url, name in pages:
                try:
                    debugger.analyze_page_structure(url, name)
                    time.sleep(2)  # Pausa entre análisis
                except Exception as e:
                    print(f"❌ Error analizando {name}: {e}")
            print("\n✅ Análisis completo terminado")
            
        elif choice == '2':
            print("\nSelecciona la página a analizar:")
            for i, (url, name) in enumerate(pages, 1):
                print(f"{i}. {name} - {url}")
            
            try:
                page_choice = int(input("Número de página: ")) - 1
                if 0 <= page_choice < len(pages):
                    url, name = pages[page_choice]
                    debugger.analyze_page_structure(url, name)
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Número inválido")
                
        elif choice == '3':
            print("\nSelecciona la página para debug interactivo:")
            for i, (url, name) in enumerate(pages, 1):
                print(f"{i}. {name} - {url}")
            
            try:
                page_choice = int(input("Número de página: ")) - 1
                if 0 <= page_choice < len(pages):
                    url, name = pages[page_choice]
                    debugger.interactive_debug(url, name)
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Número inválido")
                
        elif choice == '4':
            custom_url = input("Ingresa la URL a analizar: ")
            custom_name = input("Ingresa un nombre para la página: ")
            debugger.analyze_page_structure(custom_url, custom_name)
            
        elif choice == '5':
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    print("✅ Dependencias cargadas correctamente")
    if CLOUDSCRAPER_AVAILABLE:
        print("✅ CloudScraper disponible")
    else:
        print("⚠️  CloudScraper no disponible")
    
    if SELENIUM_AVAILABLE:
        print("✅ Selenium disponible")
    else:
        print("⚠️  Selenium no disponible")
    
    main()
