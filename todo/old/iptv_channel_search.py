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

class AdvancedIPTVExtractor:
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
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                print(f"   ✅ Conexión exitosa (200)")
                return response.text
            else:
                print(f"   ⚠️ Código de respuesta: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def search_for_channels(self, content, base_url, source, channel_keywords):
        """Busca canales específicos por palabras clave"""
        streams = []
        
        if not content:
            return streams
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Buscar enlaces que contengan palabras clave de canales
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '').lower()
            text = link.get_text(strip=True).lower()
            
            # Verificar si el enlace contiene palabras clave de canales
            for keyword in channel_keywords:
                if keyword.lower() in href or keyword.lower() in text:
                    full_url = urljoin(base_url, link.get('href'))
                    
                    print(f"      🎯 Encontrado canal potencial: {link.get_text(strip=True)}")
                    print(f"         URL: {full_url}")
                    
                    # Intentar extraer streams de esta página específica
                    channel_streams = self.extract_from_channel_page(full_url, link.get_text(strip=True), source)
                    streams.extend(channel_streams)
                    
                    time.sleep(1)  # Pausa entre peticiones
        
        return streams
    
    def extract_from_channel_page(self, url, channel_name, source):
        """Extrae streams de una página específica de canal"""
        streams = []
        
        try:
            content = self.make_request(url)
            if content:
                # Buscar patrones de M3U8 y streams
                patterns = [
                    r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                    r'src\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                    r'source\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                    r'file\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                    r'hls\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if self.is_valid_stream(match):
                            if not match.startswith('http'):
                                match = urljoin(url, match)
                            streams.append({
                                'name': channel_name or f'Canal {len(streams) + 1}',
                                'url': match,
                                'source': source
                            })
                            print(f"         ✅ Stream encontrado: {match[:60]}...")
                
                # Buscar iframes
                soup = BeautifulSoup(content, 'html.parser')
                iframes = soup.find_all('iframe')
                
                for iframe in iframes:
                    iframe_src = iframe.get('src')
                    if iframe_src and not any(skip in iframe_src.lower() for skip in ['ads', 'google', 'facebook']):
                        if not iframe_src.startswith('http'):
                            iframe_src = urljoin(url, iframe_src)
                        
                        print(f"         🖼️ Analizando iframe...")
                        iframe_streams = self.extract_from_iframe(iframe_src, channel_name, source)
                        streams.extend(iframe_streams)
        
        except Exception as e:
            print(f"         ❌ Error procesando {channel_name}: {e}")
        
        return streams
    
    def extract_from_iframe(self, iframe_url, channel_name, source):
        """Extrae streams de un iframe"""
        streams = []
        
        try:
            content = self.make_request(iframe_url)
            if content:
                patterns = [
                    r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                    r'source\s*[:=]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if self.is_valid_stream(match):
                            if not match.startswith('http'):
                                match = urljoin(iframe_url, match)
                            streams.append({
                                'name': channel_name,
                                'url': match,
                                'source': source
                            })
        except:
            pass
        
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
    
    def get_channel_keywords(self):
        """Lista de palabras clave para buscar canales"""
        return [
            # Canales de noticias
            'cnn', 'bbc', 'fox news', 'telemundo', 'univision', 'caracol', 'rcn',
            
            # Canales de entretenimiento
            'history', 'history channel', 'discovery', 'animal planet', 'national geographic',
            'mtv', 'vh1', 'comedy central', 'cartoon network', 'nickelodeon',
            
            # Canales de deportes
            'espn', 'fox sports', 'deportes', 'futbol', 'soccer', 'sports',
            'win sports', 'directv sports', 'tnt sports',
            
            # Canales de películas
            'hbo', 'cinemax', 'starz', 'showtime', 'fx', 'tnt', 'usa',
            'cine', 'movies', 'peliculas',
            
            # Canales locales
            'canal 1', 'canal uno', 'caracol tv', 'rcn tv', 'canal 13',
            'canal capital', 'city tv', 'telecaribe', 'telepacifico',
            
            # Canales internacionales
            'start channel', 'start tv', 'start', 'id', 'investigation',
            'lifetime', 'e!', 'tlc', 'food network', 'hgtv',
            
            # Términos generales
            'en vivo', 'live', 'stream', 'tv', 'television', 'canal'
        ]
    
    def extract_comprehensive(self, pages):
        """Extracción comprehensiva de todas las páginas"""
        all_streams = []
        channel_keywords = self.get_channel_keywords()
        
        for page_name, page_url in pages.items():
            print(f"\n🔍 Buscando canales en {page_name}...")
            
            # Primero intentar la página principal
            content = self.make_request(page_url)
            
            if content:
                # Buscar canales específicos
                streams = self.search_for_channels(content, page_url, page_name, channel_keywords)
                
                if streams:
                    all_streams.extend(streams)
                    print(f"   ✅ {len(streams)} streams encontrados en {page_name}")
                else:
                    print(f"   ⚠️ No se encontraron streams específicos en {page_name}")
                    
                    # Buscar páginas de canales comunes
                    common_paths = [
                        '/canales', '/tv', '/live', '/en-vivo', '/streams',
                        '/history-channel', '/start-channel', '/discovery',
                        '/espn', '/fox-sports', '/hbo', '/cnn'
                    ]
                    
                    for path in common_paths:
                        test_url = page_url.rstrip('/') + path
                        test_content = self.make_request(test_url)
                        
                        if test_content and 'not found' not in test_content.lower():
                            path_streams = self.search_for_channels(test_content, test_url, page_name, channel_keywords)
                            all_streams.extend(path_streams)
                            
                            if path_streams:
                                print(f"      ✅ {len(path_streams)} streams encontrados en {path}")
                        
                        time.sleep(0.5)
            
            time.sleep(2)  # Pausa entre páginas
        
        return all_streams
    
    def get_premium_demo_streams(self):
        """Streams de demostración de alta calidad con canales conocidos"""
        return [
            # Canales de noticias
            {
                'name': 'BBC News (Demo)',
                'url': 'https://vs-hls-push-ww-live.akamaized.net/x=4/i=urn:bbc:pips:service:bbc_news_channel_hd/t=3840/v=pv14/b=5070016/main.m3u8',
                'source': 'news_demo'
            },
            {
                'name': 'CNN International (Demo)',
                'url': 'https://cnn-cnninternational-1-de.samsung.wurl.com/manifest/playlist.m3u8',
                'source': 'news_demo'
            },
            
            # Canales de entretenimiento
            {
                'name': 'History Channel (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5a4d3a00ad95e4718ae8d8db/master.m3u8',
                'source': 'entertainment_demo'
            },
            {
                'name': 'Discovery Channel (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5a687aa68cb9f98b56c3afd4/master.m3u8',
                'source': 'entertainment_demo'
            },
            {
                'name': 'National Geographic (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f4d3696d938c900075c4425/master.m3u8',
                'source': 'entertainment_demo'
            },
            
            # Canales de deportes
            {
                'name': 'Fox Sports (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5a74b8e1e22a61737979c6bf/master.m3u8',
                'source': 'sports_demo'
            },
            {
                'name': 'ESPN Deportes (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f4d3ef0b4e4b600078b08e7/master.m3u8',
                'source': 'sports_demo'
            },
            
            # Canales de películas
            {
                'name': 'Cine Clásico (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f4d3c93b4e4b60007870ea8/master.m3u8',
                'source': 'movies_demo'
            },
            {
                'name': 'Cine Acción (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f4d3e23b4e4b60007870e7e/master.m3u8',
                'source': 'movies_demo'
            },
            
            # Canales infantiles
            {
                'name': 'Cartoon Network (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f4d3de73c32fd00078e68af/master.m3u8',
                'source': 'kids_demo'
            },
            {
                'name': 'Nickelodeon (Demo)',
                'url': 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/5f4d3dbc3c32fd00078e68a9/master.m3u8',
                'source': 'kids_demo'
            }
        ]
    
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

def generate_m3u_content(streams, title="IPTV Advanced"):
    """Genera contenido M3U mejorado"""
    content = "#EXTM3U\n\n"
    
    # Agrupar por categoría
    categories = {}
    for stream in streams:
        source = stream.get('source', 'unknown')
        if source not in categories:
            categories[source] = []
        categories[source].append(stream)
    
    # Generar por categorías
    for category, category_streams in categories.items():
        content += f"# === {category.upper().replace('_', ' ')} ===\n"
        
        for i, stream in enumerate(category_streams, 1):
            name = stream.get('name', f'Canal {i}')
            url = stream.get('url', '')
            
            # Limpiar nombre
            name = re.sub(r'[^\w\s()-]', '', name).strip()
            if not name:
                name = f'Canal {i}'
            
            content += f'#EXTINF:-1 tvg-name="{name}" group-title="{category.upper().replace("_", " ")}",{name}\n'
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
    print("="*70)
    print("    🎬 IPTV EXTRACTOR AVANZADO CON BÚSQUEDA DE CANALES 🎬")
    print("="*70)
    print("🎯 Buscando canales específicos como History, Start Channel, etc.")
    print("="*70)
    
    # Páginas a analizar
    pages = {
        'tvplusgratis2': 'https://www.tvplusgratis2.com/',
        'vertvcable': 'https://www.vertvcable.com/',
        'cablevisionhd': 'https://www.cablevisionhd.com/',
        'telegratishd': 'https://www.telegratishd.com/',
    }
    
    # Crear extractor
    extractor = AdvancedIPTVExtractor()
    
    # Extraer streams
    print("\n🚀 Iniciando búsqueda avanzada de canales...")
    all_streams = extractor.extract_comprehensive(pages)
    
    # Si no se encuentran streams reales, usar demos premium
    if not all_streams:
        print("\n⚠️ No se encontraron streams reales. Agregando biblioteca de canales demo...")
        demo_streams = extractor.get_premium_demo_streams()
        all_streams.extend(demo_streams)
        print(f"✅ {len(demo_streams)} canales demo agregados")
    else:
        # Agregar algunos demos de calidad para complementar
        print("\n📺 Agregando canales demo adicionales...")
        demo_streams = extractor.get_premium_demo_streams()
        all_streams.extend(demo_streams)
    
    # Eliminar duplicados
    unique_streams = extractor.remove_duplicates(all_streams)
    
    print(f"\n🎉 Búsqueda completada!")
    print(f"📊 Total de canales únicos: {len(unique_streams)}")
    
    # Mostrar resumen por categoría
    categories = {}
    for stream in unique_streams:
        source = stream['source']
        if source not in categories:
            categories[source] = 0
        categories[source] += 1
    
    print(f"\n📋 Resumen por categoría:")
    for category, count in categories.items():
        category_name = category.replace('_', ' ').title()
        print(f"   📺 {category_name}: {count} canales")
    
    # Buscar canales específicos mencionados
    history_channels = [s for s in unique_streams if 'history' in s['name'].lower()]
    start_channels = [s for s in unique_streams if 'start' in s['name'].lower()]
    
    if history_channels:
        print(f"\n🎯 History Channels encontrados:")
        for channel in history_channels:
            print(f"   📺 {channel['name']}")
    
    if start_channels:
        print(f"\n🎯 Start Channels encontrados:")
        for channel in start_channels:
            print(f"   📺 {channel['name']}")
    
    # Generar archivo M3U
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iptv_advanced_{timestamp}.m3u"
    
    content = generate_m3u_content(unique_streams, "IPTV Advanced")
    
    if save_m3u_file(content, filename):
        print(f"\n📁 Archivo M3U generado: {filename}")
        print(f"📺 {len(unique_streams)} canales organizados por categorías")
        
        # Mostrar algunos ejemplos destacados
        print(f"\n📋 Canales destacados encontrados:")
        highlighted = []
        
        # Buscar canales populares
        popular_keywords = ['history', 'discovery', 'cnn', 'bbc', 'espn', 'hbo', 'start']
        for stream in unique_streams:
            for keyword in popular_keywords:
                if keyword in stream['name'].lower() and stream not in highlighted:
                    highlighted.append(stream)
                    break
        
        for i, stream in enumerate(highlighted[:8], 1):
            print(f"  {i}. {stream['name']} ({stream['source'].replace('_', ' ').title()})")
            print(f"     🔗 {stream['url'][:60]}...")
        
        if len(unique_streams) > 8:
            print(f"  ... y {len(unique_streams) - 8} canales más")
    
    print(f"\n✅ Proceso completado exitosamente!")
    print(f"💡 Tip: Importa el archivo {filename} en tu reproductor IPTV")
    print(f"🎯 Los canales están organizados por categorías para fácil navegación")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        print("\n🧹 Limpieza completada")
