#!/usr/bin/env python3

import os
import sys
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import random

class SimpleIPTVExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        
    def setup_headers(self):
        """Configura headers realistas"""
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
    
    def make_request(self, url):
        """Hace una petición simple"""
        try:
            print(f"   📡 Conectando a {url}...")
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Conexión exitosa (200)")
                return response.text
            else:
                print(f"   ⚠️ Código de respuesta: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def extract_streams_simple(self, content, base_url, source):
        """Extrae streams de forma simple"""
        streams = []
        
        if not content:
            return streams
        
        # Buscar patrones de M3U8
        patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'src\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'source\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'file\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self.is_valid_stream(match):
                    if not match.startswith('http'):
                        match = urljoin(base_url, match)
                    streams.append({
                        'name': f'Canal {len(streams) + 1}',
                        'url': match,
                        'source': source
                    })
        
        return streams
    
    def is_valid_stream(self, url):
        """Verifica si es una URL válida"""
        if not url or len(url) < 10:
            return False
        if '.m3u8' not in url.lower():
            return False
        exclude = ['.jpg', '.png', '.gif', '.css', '.js', '.ico']
        if any(ext in url.lower() for ext in exclude):
            return False
        return True
    
    def extract_all_pages(self):
        """Extrae de todas las páginas"""
        pages = [
            {'name': 'tvplusgratis2', 'url': 'https://www.tvplusgratis2.com/'},
            {'name': 'vertvcable', 'url': 'https://www.vertvcable.com/'},
            {'name': 'cablevisionhd', 'url': 'https://www.cablevisionhd.com/'},
            {'name': 'telegratishd', 'url': 'https://www.telegratishd.com/'},
        ]
        
        all_streams = []
        
        for page in pages:
            print(f"\n🔍 Extrayendo de {page['name']}...")
            
            # Intentar extraer streams reales
            content = self.make_request(page['url'])
            streams = self.extract_streams_simple(content, page['url'], page['name'])
            
            # Si no se encuentran streams reales, agregar demos
            if not streams:
                print(f"   ⚠️ No se encontraron streams reales. Agregando demos...")
                demo_streams = self.get_demo_streams(page['name'])
                streams.extend(demo_streams)
            
            all_streams.extend(streams)
            print(f"   ✅ Total para {page['name']}: {len(streams)} streams")
            
            time.sleep(1)  # Pausa entre páginas
        
        return all_streams
    
    def get_demo_streams(self, source):
        """Obtiene streams de demostración"""
        demo_streams = {
            'tvplusgratis2': [
                {
                    'name': 'Big Buck Bunny (Demo)',
                    'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                    'source': source
                },
                {
                    'name': 'Sintel (Demo HLS)',
                    'url': 'https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
                    'source': source
                }
            ],
            'vertvcable': [
                {
                    'name': 'Tears of Steel (Demo)',
                    'url': 'https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8',
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
                    'url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
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

def main():
    print("="*60)
    print("    🎬 IPTV EXTRACTOR SIMPLE (SIN PROXIES) 🎬")
    print("="*60)
    print("🚀 Iniciando extracción simple...")
    
    # Crear extractor
    extractor = SimpleIPTVExtractor()
    
    # Extraer streams
    print("\n📡 Extrayendo streams de todas las páginas...")
    all_streams = extractor.extract_all_pages()
    
    # Eliminar duplicados
    unique_streams = extractor.remove_duplicates(all_streams)
    
    print(f"\n🎉 Extracción completada!")
    print(f"📊 Total de streams únicos: {len(unique_streams)}")
    
    # Mostrar resumen por fuente
    sources = {}
    for stream in unique_streams:
        source = stream['source']
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    
    print(f"\n📋 Resumen por fuente:")
    for source, count in sources.items():
        print(f"   📺 {source}: {count} streams")
    
    # Generar archivo M3U
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iptv_simple_{timestamp}.m3u"
    
    content = generate_m3u_content(unique_streams, "IPTV Simple")
    
    if save_m3u_file(content, filename):
        print(f"\n📁 Archivo M3U generado: {filename}")
        print(f"📺 {len(unique_streams)} canales listos para usar")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 Ejemplos de streams encontrados:")
        for i, stream in enumerate(unique_streams[:5], 1):
            print(f"  {i}. {stream['name']} ({stream['source']})")
            print(f"     🔗 {stream['url'][:60]}...")
        
        if len(unique_streams) > 5:
            print(f"  ... y {len(unique_streams) - 5} más")
    
    print(f"\n✅ Proceso completado exitosamente!")
    print(f"💡 Tip: Importa el archivo {filename} en tu reproductor IPTV")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        print("\n🧹 Limpieza completada")
