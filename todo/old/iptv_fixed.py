#!/usr/bin/env python3
"""
IPTV Extractor Mejorado - Versión sin proxies problemáticos
"""

import os
import sys
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import subprocess

class IPTVExtractorFixed:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        
    def setup_headers(self):
        """Configura headers realistas"""
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
    
    def make_request(self, url, timeout=10):
        """Hace petición sin proxies"""
        try:
            print(f"      📡 Conectando a {url[:50]}...")
            response = self.session.get(url, timeout=timeout)
            if response.status_code == 200:
                print(f"      ✅ Conexión exitosa")
                return response.text
            else:
                print(f"      ⚠️ Código: {response.status_code}")
                return None
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}...")
            return None
    
    def extract_streams_from_content(self, content, base_url, source):
        """Extrae streams del contenido HTML"""
        streams = []
        
        if not content:
            return streams
        
        # Patrones para encontrar streams
        patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'src\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'source\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'file\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'url\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self.is_valid_stream(match):
                    if not match.startswith('http'):
                        match = urljoin(base_url, match)
                    streams.append({
                        'name': f'Canal {source} {len(streams) + 1}',
                        'url': match,
                        'source': source
                    })
        
        # Buscar en iframes
        soup = BeautifulSoup(content, 'html.parser')
        iframes = soup.find_all('iframe')
        
        for iframe in iframes:
            src = iframe.get('src')
            if src and not any(skip in src.lower() for skip in ['ads', 'google', 'facebook']):
                if not src.startswith('http'):
                    src = urljoin(base_url, src)
                
                iframe_content = self.make_request(src)
                if iframe_content:
                    iframe_streams = self.extract_streams_from_content(iframe_content, src, source)
                    streams.extend(iframe_streams)
        
        return streams
    
    def is_valid_stream(self, url):
        """Verifica si es una URL de stream válida"""
        if not url or len(url) < 10:
            return False
        if '.m3u8' not in url.lower():
            return False
        exclude = ['.jpg', '.png', '.gif', '.css', '.js', '.ico', '.svg']
        if any(ext in url.lower() for ext in exclude):
            return False
        return True
    
    def extract_from_page(self, page_name, page_url):
        """Extrae streams de una página específica"""
        print(f"\n🔍 Extrayendo de {page_name}...")
        
        # Intentar extraer streams reales
        content = self.make_request(page_url)
        streams = self.extract_streams_from_content(content, page_url, page_name)
        
        # Si no se encuentran streams, agregar demos
        if not streams:
            print(f"   ⚠️ No se encontraron streams reales. Agregando demos...")
            streams = self.get_demo_streams(page_name)
        
        print(f"   ✅ Total: {len(streams)} streams")
        return streams
    
    def get_demo_streams(self, source):
        """Streams de demostración funcionales"""
        demo_streams = {
            'tvplusgratis2': [
                {
                    'name': 'Big Buck Bunny (Demo)',
                    'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                    'source': source
                },
                {
                    'name': 'Sintel HLS (Demo)',
                    'url': 'https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
                    'source': source
                }
            ],
            'vertvcable': [
                {
                    'name': 'Tears of Steel (Demo)',
                    'url': 'https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8',
                    'source': source
                },
                {
                    'name': 'Arte Canal (Demo)',
                    'url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                    'source': source
                }
            ],
            'cablevisionhd': [
                {
                    'name': 'Test Stream (Demo)',
                    'url': 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
                    'source': source
                }
            ],
            'telegratishd': [
                {
                    'name': 'Sample Stream (Demo)',
                    'url': 'https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8',
                    'source': source
                }
            ]
        }
        
        return demo_streams.get(source, [])
    
    def remove_duplicates(self, streams):
        """Elimina duplicados"""
        seen_urls = set()
        unique_streams = []
        
        for stream in streams:
            url = stream.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_streams.append(stream)
        
        return unique_streams

def check_stream_simple(url):
    """Verifica stream de forma simple"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code in [200, 206]
    except:
        return False

def verify_streams(streams):
    """Verifica streams en paralelo"""
    print(f"\n🔍 Verificando {len(streams)} streams...")
    
    online_streams = []
    offline_count = 0
    
    def check_single_stream(stream):
        url = stream['url']
        is_online = check_stream_simple(url)
        return stream if is_online else None
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_stream = {executor.submit(check_single_stream, stream): stream for stream in streams}
        
        for i, future in enumerate(as_completed(future_to_stream), 1):
            try:
                result = future.result()
                if result:
                    online_streams.append(result)
                else:
                    offline_count += 1
                
                # Mostrar progreso
                print(f"\r   📊 Progreso: {i}/{len(streams)} ({len(online_streams)} online, {offline_count} offline)", end="")
                
            except Exception as e:
                offline_count += 1
    
    print(f"\n   ✅ Verificación completada: {len(online_streams)} online, {offline_count} offline")
    return online_streams

def generate_m3u_content(streams, title="IPTV Streams"):
    """Genera contenido M3U"""
    content = "#EXTM3U\n\n"
    
    for i, stream in enumerate(streams, 1):
        name = stream.get('name', f'Canal {i}')
        url = stream.get('url', '')
        source = stream.get('source', 'unknown')
        
        # Limpiar nombre
        name = re.sub(r'[^\w\s-]', '', name).strip()
        if not name:
            name = f'Canal {i}'
        
        content += f'#EXTINF:-1 tvg-name="{name}" group-title="{source.upper()}",{name}\n'
        content += f'{url}\n\n'
    
    return content

def save_m3u_file(content, filename):
    """Guarda archivo M3U"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo guardado: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error guardando {filename}: {e}")
        return False

def show_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("    🎬 IPTV EXTRACTOR MEJORADO (SIN PROXIES) 🎬")
    print("="*60)
    print("1. 📺 Extraer de tvplusgratis2.com")
    print("2. 🎥 Extraer de vertvcable.com")
    print("3. 📡 Extraer de cablevisionhd.com")
    print("4. 🎬 Extraer de telegratishd.com")
    print("5. 🌍 Extraer de todas las páginas")
    print("6. 🔥 Análisis profundo (canales específicos)")
    print("7. 🚪 Salir")
    print("="*60)

def extract_direct_streams():
    """Extrae streams directos de canales específicos"""
    channels = [
        ('EL CANAL DEL FÚTBOL (ECDF)', 'https://www.vertvcable.com/el-canal-del-futbol-ecdf-en-vivo/'),
        ('Canal 5 Linares', 'https://www.vertvcable.com/canal-5-linares-en-vivo/'),
        ('Canal 2 Linares', 'https://www.vertvcable.com/canal-2-linares-en-vivo/'),
        ('Telecanal', 'https://www.vertvcable.com/telecanal-en-vivo/'),
        ('Canal Pais', 'https://www.vertvcable.com/canal-pais-en-vivo/'),
    ]
    
    print("\n🔥 ANÁLISIS PROFUNDO - CANALES ESPECÍFICOS")
    print("="*60)
    
    extractor = IPTVExtractorFixed()
    all_streams = []
    
    for name, url in channels:
        print(f"\n🔍 Analizando: {name}")
        streams = extractor.extract_streams_from_content(
            extractor.make_request(url), url, 'vertvcable_direct'
        )
        
        if streams:
            all_streams.extend(streams)
            print(f"   ✅ {len(streams)} streams encontrados")
        else:
            print(f"   ❌ No se encontraron streams")
        
        time.sleep(1)
    
    if not all_streams:
        print("\n⚠️ No se encontraron streams directos. Agregando demos...")
        all_streams = [
            {
                'name': 'Demo Stream 1',
                'url': 'https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
                'source': 'direct_demo'
            }
        ]
    
    return all_streams

def get_user_choice(max_option):
    """Obtiene elección del usuario"""
    while True:
        try:
            choice = input(f"\n👉 Selecciona una opción (1-{max_option}): ")
            choice = int(choice)
            if 1 <= choice <= max_option:
                return choice
            else:
                print(f"❌ Por favor, ingresa un número entre 1 y {max_option}")
        except ValueError:
            print("❌ Por favor, ingresa un número válido")

def main():
    pages = {
        1: ('tvplusgratis2', 'https://www.tvplusgratis2.com/'),
        2: ('vertvcable', 'https://www.vertvcable.com/'),
        3: ('cablevisionhd', 'https://www.cablevisionhd.com/'),
        4: ('telegratishd', 'https://www.telegratishd.com/'),
    }
    
    extractor = IPTVExtractorFixed()
    
    while True:
        show_menu()
        choice = get_user_choice(7)
        
        if choice == 7:
            print("\n👋 ¡Gracias por usar IPTV Extractor!")
            break
        
        all_streams = []
        
        if choice == 5:  # Todas las páginas
            print("\n🚀 Extrayendo de todas las páginas...")
            for page_id, (name, url) in pages.items():
                streams = extractor.extract_from_page(name, url)
                all_streams.extend(streams)
                time.sleep(1)
        
        elif choice == 6:  # Análisis profundo
            all_streams = extract_direct_streams()
        
        elif choice in pages:  # Página específica
            name, url = pages[choice]
            print(f"\n🚀 Extrayendo de {name}...")
            all_streams = extractor.extract_from_page(name, url)
        
        if not all_streams:
            print("\n❌ No se encontraron streams")
            continue
        
        # Eliminar duplicados
        unique_streams = extractor.remove_duplicates(all_streams)
        
        print(f"\n🎉 Extracción completada!")
        print(f"📊 Total de streams únicos: {len(unique_streams)}")
        
        # Preguntar si verificar
        verify = input("\n🔍 ¿Verificar streams? (s/n): ").lower().strip()
        
        if verify in ['s', 'si', 'sí', 'y', 'yes']:
            verified_streams = verify_streams(unique_streams)
            unique_streams = verified_streams
        
        # Generar archivo M3U
        if unique_streams:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"iptv_extracted_{timestamp}.m3u"
            
            content = generate_m3u_content(unique_streams, "IPTV Extracted")
            
            if save_m3u_file(content, filename):
                print(f"\n📁 Archivo M3U generado: {filename}")
                print(f"📺 {len(unique_streams)} canales listos para usar")
                
                # Mostrar ejemplos
                print(f"\n📋 Ejemplos de streams:")
                for i, stream in enumerate(unique_streams[:3], 1):
                    print(f"  {i}. {stream['name']} ({stream['source']})")
                    print(f"     🔗 {stream['url'][:60]}...")
                
                if len(unique_streams) > 3:
                    print(f"  ... y {len(unique_streams) - 3} más")
        
        print(f"\n✅ Proceso completado!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        print("\n🧹 Limpieza completada")
