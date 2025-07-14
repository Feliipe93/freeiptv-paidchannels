#!/usr/bin/env python3
"""
IPTV Smart Extractor
Extractor inteligente basado en análisis de páginas web
"""

import os
import requests
from bs4 import BeautifulSoup
import cloudscraper
import re
import time
import json
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class SmartIPTVExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.cloudscraper = cloudscraper.create_scraper()
        self.setup_headers()
        
        # Patrones encontrados en el análisis
        self.channel_patterns = [
            r'href="([^"]*(?:en-vivo|live|canal|channel)[^"]*)"',
            r'href="([^"]*(?:ver-|watch-)[^"]*)"',
            r'href="([^"]*(?:stream|streaming)[^"]*)"'
        ]
        
        # Patrones para encontrar streams directos
        self.stream_patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+)["\']',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'src\s*:\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']'
        ]
        
    def setup_headers(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(headers)
        self.cloudscraper.headers.update(headers)
    
    def make_request(self, url, use_cloudscraper=True):
        """Hace una petición web con manejo de errores"""
        try:
            if use_cloudscraper:
                response = self.cloudscraper.get(url, timeout=15)
            else:
                response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ Error HTTP {response.status_code} para {url}")
                
        except Exception as e:
            print(f"❌ Error en petición a {url}: {e}")
            
        return None
    
    def extract_channel_links(self, content, base_url):
        """Extrae enlaces de canales de una página"""
        channel_links = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Buscar enlaces con patrones específicos
        for pattern in self.channel_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if not match.startswith('http'):
                    match = urljoin(base_url, match)
                channel_links.append(match)
        
        # Buscar enlaces en elementos HTML
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if href and any(keyword in href.lower() for keyword in ['en-vivo', 'live', 'canal', 'ver-', 'stream']):
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                channel_links.append(href)
                
        return list(set(channel_links))  # Eliminar duplicados
    
    def extract_streams_from_page(self, url, channel_name=None):
        """Extrae streams directos de una página de canal específica"""
        print(f"  🔍 Analizando: {url}")
        streams = []
        
        content = self.make_request(url)
        if not content:
            return streams
            
        # Buscar patrones de streams
        for pattern in self.stream_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if any(ext in match.lower() for ext in ['.m3u8', '.ts', 'stream', 'live']):
                    if match.startswith('http'):
                        streams.append({
                            'name': channel_name or self.extract_title_from_url(url),
                            'url': match,
                            'source_page': url
                        })
        
        # Buscar en elementos video/iframe
        soup = BeautifulSoup(content, 'html.parser')
        
        # Videos directos
        videos = soup.find_all(['video', 'source'])
        for video in videos:
            src = video.get('src')
            if src and any(ext in src for ext in ['.m3u8', '.ts']):
                if not src.startswith('http'):
                    src = urljoin(url, src)
                streams.append({
                    'name': channel_name or self.extract_title_from_url(url),
                    'url': src,
                    'source_page': url
                })
        
        # Iframes
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src and not any(skip in src.lower() for skip in ['google', 'facebook', 'twitter', 'ads']):
                if not src.startswith('http'):
                    src = urljoin(url, src)
                iframe_streams = self.extract_streams_from_iframe(src, channel_name)
                streams.extend(iframe_streams)
        
        return streams
    
    def extract_streams_from_iframe(self, iframe_url, channel_name=None):
        """Extrae streams de un iframe"""
        streams = []
        
        try:
            content = self.make_request(iframe_url)
            if content:
                for pattern in self.stream_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if any(ext in match.lower() for ext in ['.m3u8', '.ts']) and match.startswith('http'):
                            streams.append({
                                'name': channel_name or 'Canal Iframe',
                                'url': match,
                                'source_page': iframe_url
                            })
        except:
            pass
            
        return streams
    
    def extract_title_from_url(self, url):
        """Extrae un nombre de canal de la URL"""
        path = urlparse(url).path
        name = path.split('/')[-2] if path.endswith('/') else path.split('/')[-1]
        name = name.replace('-en-vivo', '').replace('-live', '').replace('-', ' ')
        return name.title()
    
    def extract_vertvcable(self):
        """Extrae streams de vertvcable.com"""
        print("🔍 Extrayendo streams de vertvcable.com...")
        all_streams = []
        
        base_url = 'https://www.vertvcable.com/'
        
        # Obtener página principal
        content = self.make_request(base_url)
        if not content:
            print("❌ No se pudo acceder a la página principal")
            return []
        
        # Extraer enlaces de canales
        channel_links = self.extract_channel_links(content, base_url)
        print(f"✅ Encontrados {len(channel_links)} enlaces de canales")
        
        # Procesar cada canal
        for i, channel_url in enumerate(channel_links[:20], 1):  # Limitar a 20 para evitar sobrecarga
            print(f"📺 Canal {i}/{min(20, len(channel_links))}: {self.extract_title_from_url(channel_url)}")
            
            channel_streams = self.extract_streams_from_page(channel_url)
            if channel_streams:
                all_streams.extend(channel_streams)
                print(f"  ✅ Encontrados {len(channel_streams)} streams")
            else:
                print(f"  ❌ No se encontraron streams")
            
            time.sleep(1)  # Pausa para evitar sobrecarga del servidor
        
        return all_streams
    
    def extract_tvplusgratis2(self):
        """Extrae streams de tvplusgratis2.com (con manejo especial por el 403)"""
        print("🔍 Extrayendo streams de tvplusgratis2.com...")
        all_streams = []
        
        base_url = 'https://www.tvplusgratis2.com/'
        
        # Intentar diferentes páginas conocidas
        known_paths = [
            '',
            'canales/',
            'tv-en-vivo/',
            'streaming/',
            'ver-tv/',
            'television-gratis/'
        ]
        
        for path in known_paths:
            url = base_url + path
            print(f"  🔍 Intentando: {url}")
            
            content = self.make_request(url)
            if content and '403 Forbidden' not in content:
                channel_links = self.extract_channel_links(content, url)
                if channel_links:
                    print(f"  ✅ Encontrados {len(channel_links)} enlaces")
                    
                    for channel_url in channel_links[:10]:  # Limitar para prueba
                        channel_streams = self.extract_streams_from_page(channel_url)
                        all_streams.extend(channel_streams)
                        time.sleep(1)
                break
            else:
                print(f"  ❌ Acceso denegado o error")
        
        return all_streams
    
    def extract_all_sites(self):
        """Extrae streams de todos los sitios"""
        print("🚀 Iniciando extracción inteligente de IPTV")
        print("="*60)
        
        all_streams = []
        
        # Extraer de cada sitio
        sites = [
            ('vertvcable', self.extract_vertvcable),
            ('tvplusgratis2', self.extract_tvplusgratis2)
        ]
        
        for site_name, extract_func in sites:
            print(f"\n📡 Procesando {site_name}...")
            try:
                streams = extract_func()
                if streams:
                    all_streams.extend(streams)
                    print(f"✅ {site_name}: {len(streams)} streams encontrados")
                else:
                    print(f"❌ {site_name}: No se encontraron streams")
            except Exception as e:
                print(f"❌ Error en {site_name}: {e}")
        
        return all_streams
    
    def verify_stream(self, stream_url):
        """Verifica si un stream está activo"""
        try:
            response = self.session.head(stream_url, timeout=10, allow_redirects=True)
            return response.status_code in [200, 206]
        except:
            return False
    
    def save_results(self, streams, filename="smart_iptv_streams.json"):
        """Guarda los resultados en un archivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(streams, f, ensure_ascii=False, indent=2)
            print(f"💾 Resultados guardados en: {filename}")
        except Exception as e:
            print(f"❌ Error guardando archivo: {e}")
    
    def generate_m3u(self, streams, filename="smart_streams.m3u"):
        """Genera un archivo M3U con los streams encontrados"""
        try:
            content = "#EXTM3U\n"
            
            for i, stream in enumerate(streams, 1):
                name = stream.get('name', f'Canal {i}')
                url = stream.get('url', '')
                
                # Limpiar caracteres especiales del nombre
                name = re.sub(r'[^\w\s-]', '', name).strip()
                if not name:
                    name = f'Canal {i}'
                
                content += f'#EXTINF:-1 tvg-name="{name}" group-title="Smart Extractor",{name}\n'
                content += f'{url}\n'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📺 Archivo M3U generado: {filename}")
            
        except Exception as e:
            print(f"❌ Error generando M3U: {e}")

def main():
    extractor = SmartIPTVExtractor()
    
    print("🎬 SMART IPTV EXTRACTOR")
    print("Basado en análisis de estructura de páginas web")
    print("="*60)
    
    # Extraer streams
    streams = extractor.extract_all_sites()
    
    if streams:
        print(f"\n🎉 Extracción completada!")
        print(f"📊 Total de streams encontrados: {len(streams)}")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 Ejemplos de streams encontrados:")
        for i, stream in enumerate(streams[:5], 1):
            print(f"  {i}. {stream['name']}")
            print(f"     URL: {stream['url'][:60]}...")
            print(f"     Fuente: {stream['source_page']}")
        
        if len(streams) > 5:
            print(f"  ... y {len(streams) - 5} más")
        
        # Guardar resultados
        extractor.save_results(streams)
        extractor.generate_m3u(streams)
        
        # Opción de verificar streams
        verify = input(f"\n🔍 ¿Verificar si los streams están activos? (s/n): ").lower()
        if verify.startswith('s'):
            print("\n🔍 Verificando streams (esto puede tomar tiempo)...")
            active_streams = []
            
            for i, stream in enumerate(streams, 1):
                print(f"  Verificando {i}/{len(streams)}: {stream['name']}")
                if extractor.verify_stream(stream['url']):
                    active_streams.append(stream)
                    print(f"    ✅ Activo")
                else:
                    print(f"    ❌ Inactivo")
            
            print(f"\n📊 Resumen de verificación:")
            print(f"✅ Streams activos: {len(active_streams)}")
            print(f"❌ Streams inactivos: {len(streams) - len(active_streams)}")
            
            if active_streams:
                extractor.save_results(active_streams, "active_streams.json")
                extractor.generate_m3u(active_streams, "active_streams.m3u")
    else:
        print("❌ No se encontraron streams válidos")
        print("\n💡 Sugerencias:")
        print("- Verifica la conexión a internet")
        print("- Los sitios pueden tener protecciones anti-bot")
        print("- Prueba con diferentes sitios")

if __name__ == "__main__":
    main()
