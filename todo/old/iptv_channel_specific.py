#!/usr/bin/env python3

import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urljoin, urlparse
import time
import random
from datetime import datetime
import re
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ChannelSpecificExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.cloudscraper = cloudscraper.create_scraper()
        self.setup_headers()
        self.driver = None
        
        # Canales específicos encontrados en las interfaces
        self.target_channels = {
            'telegratishd': {
                'History': 'https://www.telegratishd.com/history-en-vivo/',
                'History 2': 'https://www.telegratishd.com/history-2-en-vivo/', 
                'Discovery Channel': 'https://www.telegratishd.com/discovery-channel-en-vivo/',
                'Animal Planet': 'https://www.telegratishd.com/animal-planet-en-vivo/',
                'ESPN': 'https://www.telegratishd.com/espn-en-vivo/',
                'ESPN 2': 'https://www.telegratishd.com/espn-2-en-vivo/',
                'TNT Sports': 'https://www.telegratishd.com/tnt-sports-en-vivo/',
                'Fox Sports': 'https://www.telegratishd.com/fox-sports-en-vivo/',
                'Warner Channel': 'https://www.telegratishd.com/warner-channel-en-vivo/',
                'Universal Channel': 'https://www.telegratishd.com/universal-channel-en-vivo/',
                'Star Channel': 'https://www.telegratishd.com/star-channel-en-vivo/'
            },
            'tvplusgratis2': {
                'Universal Channel': 'https://www.tvplusgratis2.com/universal-channel-en-vivo/',
                'Universal Cinema': 'https://www.tvplusgratis2.com/universal-cinema-en-vivo/',
                'TNT Series': 'https://www.tvplusgratis2.com/tnt-series-en-vivo/',
                'Star Channel': 'https://www.tvplusgratis2.com/star-channel-en-vivo/',
                'Warner Channel': 'https://www.tvplusgratis2.com/warner-channel-en-vivo/',
                'ESPN': 'https://www.tvplusgratis2.com/espn-en-vivo/',
                'Fox Sports': 'https://www.tvplusgratis2.com/fox-sports-en-vivo/'
            },
            'cablevisionhd': {
                'History': 'https://www.cablevisionhd.com/history-en-vivo/',
                'Discovery Channel': 'https://www.cablevisionhd.com/discovery-channel-en-vivo/',
                'Warner Channel': 'https://www.cablevisionhd.com/warner-channel-en-vivo/',
                'ESPN': 'https://www.cablevisionhd.com/espn-en-vivo/',
                'Fox Sports': 'https://www.cablevisionhd.com/fox-sports-en-vivo/'
            }
        }
    
    def setup_headers(self):
        """Configura headers realistas"""
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
    
    def setup_webdriver(self):
        """Configura Selenium WebDriver"""
        if self.driver is not None:
            return self.driver
            
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            print(f"⚠️ No se pudo configurar Selenium: {e}")
            return None
    
    def extract_stream_from_channel_page(self, url, channel_name, source):
        """Extrae el stream de una página específica de canal"""
        print(f"   🔍 Analizando: {channel_name}")
        print(f"   📍 URL: {url}")
        
        streams = []
        
        # Método 1: CloudScraper
        print(f"   ☁️ Intentando con CloudScraper...")
        content = self.make_request(url, use_cloudscraper=True)
        if content:
            extracted = self.extract_streams_from_content(content, url, channel_name, source)
            if extracted:
                streams.extend(extracted)
                print(f"   ✅ CloudScraper: {len(extracted)} streams encontrados")
            else:
                print(f"   ❌ CloudScraper: No se encontraron streams")
        
        # Método 2: Selenium si CloudScraper no funciona
        if not streams:
            print(f"   🤖 Intentando con Selenium...")
            selenium_content = self.make_request(url, use_selenium=True)
            if selenium_content:
                extracted = self.extract_streams_from_content(selenium_content, url, channel_name, source)
                if extracted:
                    streams.extend(extracted)
                    print(f"   ✅ Selenium: {len(extracted)} streams encontrados")
                else:
                    print(f"   ❌ Selenium: No se encontraron streams")
        
        # Si no encontramos nada, agregar stream demo específico para este canal
        if not streams:
            print(f"   ⚠️ No se encontraron streams reales. Agregando demo específico...")
            demo_stream = self.get_demo_stream_for_channel(channel_name, source)
            if demo_stream:
                streams.append(demo_stream)
        
        return streams
    
    def make_request(self, url, use_cloudscraper=False, use_selenium=False):
        """Hace una petición HTTP"""
        try:
            if use_selenium:
                driver = self.setup_webdriver()
                if driver:
                    driver.get(url)
                    time.sleep(5)  # Esperar a que cargue completamente
                    return driver.page_source
                return None
            
            if use_cloudscraper:
                response = self.cloudscraper.get(url, timeout=15)
            else:
                response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error en petición: {e}")
            
        return None
    
    def extract_streams_from_content(self, content, base_url, channel_name, source):
        """Extrae streams del contenido HTML"""
        streams = []
        
        # Patrones específicos para diferentes tipos de reproductores
        stream_patterns = [
            # M3U8 directo
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*m3u8[^"\']*)["\']',
            
            # Reproductores específicos
            r'source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'src\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            
            # HLS específico
            r'hls\.loadSource\(["\']([^"\']+)["\']',
            r'loadSource\(["\']([^"\']*\.m3u8[^"\']*)["\']',
            
            # JWPlayer
            r'jwplayer.*?file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'player\.setup.*?file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            
            # Video.js
            r'video\.src\s*=\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'player\.src\(["\']([^"\']*\.m3u8[^"\']*)["\']',
            
            # Plyr
            r'plyr.*?source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            
            # Clappr
            r'clappr.*?source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            
            # Genérico
            r'["\']([^"\']*live[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*stream[^"\']*\.m3u8[^"\']*)["\']'
        ]
        
        # Buscar patrones en el contenido
        for pattern in stream_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if self.is_valid_stream_url(match):
                    if not match.startswith('http'):
                        match = urljoin(base_url, match)
                    
                    streams.append({
                        'name': channel_name,
                        'url': match,
                        'source': source,
                        'type': 'extracted'
                    })
        
        # Buscar en iframes
        soup = BeautifulSoup(content, 'html.parser')
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            iframe_src = iframe.get('src')
            if iframe_src:
                if not iframe_src.startswith('http'):
                    iframe_src = urljoin(base_url, iframe_src)
                
                # Evitar iframes de publicidad
                if not any(skip in iframe_src.lower() for skip in ['ads', 'google', 'facebook', 'doubleclick']):
                    iframe_streams = self.extract_iframe_streams(iframe_src, channel_name, source)
                    streams.extend(iframe_streams)
        
        # Eliminar duplicados
        seen_urls = set()
        unique_streams = []
        for stream in streams:
            if stream['url'] not in seen_urls:
                seen_urls.add(stream['url'])
                unique_streams.append(stream)
        
        return unique_streams
    
    def extract_iframe_streams(self, iframe_url, channel_name, source):
        """Extrae streams de un iframe"""
        streams = []
        
        try:
            iframe_content = self.make_request(iframe_url, use_cloudscraper=True)
            if iframe_content:
                iframe_streams = self.extract_streams_from_content(iframe_content, iframe_url, channel_name, source)
                for stream in iframe_streams:
                    stream['type'] = 'iframe'
                streams.extend(iframe_streams)
        except:
            pass
        
        return streams
    
    def is_valid_stream_url(self, url):
        """Verifica si una URL es un stream válido"""
        if not url or len(url) < 10:
            return False
        
        # Debe contener .m3u8
        if '.m3u8' not in url.lower():
            return False
        
        # No debe ser archivo estático
        exclude_extensions = ['.jpg', '.png', '.gif', '.css', '.js', '.ico', '.svg', '.woff']
        if any(ext in url.lower() for ext in exclude_extensions):
            return False
        
        # No debe ser de publicidad
        exclude_domains = ['doubleclick', 'googleads', 'facebook', 'twitter', 'instagram']
        if any(domain in url.lower() for domain in exclude_domains):
            return False
        
        return True
    
    def get_demo_stream_for_channel(self, channel_name, source):
        """Obtiene un stream demo específico para el canal"""
        demo_streams = {
            'History': {
                'name': 'History Channel (Demo)',
                'url': 'https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8',
                'source': source,
                'type': 'demo'
            },
            'History 2': {
                'name': 'History 2 (Demo)',
                'url': 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
                'source': source,
                'type': 'demo'
            },
            'Discovery Channel': {
                'name': 'Discovery Channel (Demo)',
                'url': 'https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
                'source': source,
                'type': 'demo'
            },
            'ESPN': {
                'name': 'ESPN (Demo)',
                'url': 'https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8',
                'source': source,
                'type': 'demo'
            },
            'Universal Channel': {
                'name': 'Universal Channel (Demo)',
                'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                'source': source,
                'type': 'demo'
            }
        }
        
        return demo_streams.get(channel_name, {
            'name': f'{channel_name} (Demo)',
            'url': 'https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8',
            'source': source,
            'type': 'demo'
        })
    
    def extract_all_target_channels(self):
        """Extrae todos los canales objetivo"""
        print("\n🎯 EXTRACCIÓN ESPECÍFICA DE CANALES OBJETIVO")
        print("="*60)
        print("📺 Enfocándose en canales específicos encontrados en las interfaces")
        print("🎬 Priorizando: History Channel, Discovery, ESPN, Universal, etc.")
        print("="*60)
        
        all_streams = []
        
        for source, channels in self.target_channels.items():
            print(f"\n📡 Procesando {source.upper()}...")
            print(f"   📋 {len(channels)} canales objetivo encontrados")
            
            for channel_name, channel_url in channels.items():
                try:
                    streams = self.extract_stream_from_channel_page(channel_url, channel_name, source)
                    if streams:
                        all_streams.extend(streams)
                        for stream in streams:
                            print(f"   ✅ {stream['name']}: {stream['type']}")
                    else:
                        print(f"   ❌ {channel_name}: No se encontraron streams")
                    
                    # Pausa entre peticiones
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ Error procesando {channel_name}: {e}")
            
            print(f"   📊 Total de {source}: {len([s for s in all_streams if s['source'] == source])} streams")
        
        return all_streams
    
    def generate_m3u_content(self, streams):
        """Genera contenido M3U organizado por categorías"""
        content = "#EXTM3U\n\n"
        
        # Organizar por categorías
        categories = {
            'Historia y Documentales': ['History', 'History 2', 'Discovery Channel', 'Animal Planet', 'Nat Geo'],
            'Deportes': ['ESPN', 'ESPN 2', 'TNT Sports', 'Fox Sports', 'TYC Sports'],
            'Entretenimiento': ['Universal Channel', 'Warner Channel', 'Star Channel', 'TNT Series'],
            'Otros': []
        }
        
        # Clasificar streams
        categorized_streams = {cat: [] for cat in categories.keys()}
        
        for stream in streams:
            categorized = False
            for category, keywords in categories.items():
                if category != 'Otros' and any(keyword in stream['name'] for keyword in keywords):
                    categorized_streams[category].append(stream)
                    categorized = True
                    break
            
            if not categorized:
                categorized_streams['Otros'].append(stream)
        
        # Generar M3U por categorías
        for category, category_streams in categorized_streams.items():
            if category_streams:
                content += f"# ========== {category.upper()} ==========\n"
                for stream in category_streams:
                    name = stream['name']
                    url = stream['url']
                    source = stream['source']
                    stream_type = stream.get('type', 'unknown')
                    
                    content += f'#EXTINF:-1 tvg-name="{name}" group-title="{category}" tvg-logo="",{name} [{source}] ({stream_type})\n'
                    content += f'{url}\n'
                content += "\n"
        
        return content
    
    def close_driver(self):
        """Cierra el WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def main():
    extractor = None
    
    try:
        print("🎬 EXTRACTOR ESPECÍFICO DE CANALES")
        print("="*50)
        print("🎯 Enfocado en canales específicos como History Channel")
        print("📋 Basado en las interfaces reales de las páginas")
        print("="*50)
        
        extractor = ChannelSpecificExtractor()
        
        # Extraer todos los canales objetivo
        all_streams = extractor.extract_all_target_channels()
        
        if all_streams:
            print(f"\n🎉 EXTRACCIÓN COMPLETADA")
            print(f"✅ Total de streams encontrados: {len(all_streams)}")
            
            # Mostrar resumen por fuente
            sources = {}
            for stream in all_streams:
                source = stream['source']
                if source not in sources:
                    sources[source] = {'extracted': 0, 'demo': 0}
                sources[source][stream.get('type', 'unknown')] += 1
            
            print(f"\n📊 Resumen por fuente:")
            for source, counts in sources.items():
                total = sum(counts.values())
                print(f"   📡 {source}: {total} streams ({counts.get('extracted', 0)} extraídos, {counts.get('demo', 0)} demos)")
            
            # Mostrar canales específicos encontrados
            print(f"\n📺 Canales específicos encontrados:")
            history_channels = [s for s in all_streams if 'History' in s['name']]
            if history_channels:
                print(f"   🎬 History Channels: {len(history_channels)}")
                for hc in history_channels:
                    print(f"      ✅ {hc['name']} ({hc['source']}) - {hc['type']}")
            else:
                print(f"   ❌ History Channel: No encontrado")
            
            discovery_channels = [s for s in all_streams if 'Discovery' in s['name']]
            if discovery_channels:
                print(f"   🔬 Discovery Channels: {len(discovery_channels)}")
            
            espn_channels = [s for s in all_streams if 'ESPN' in s['name']]
            if espn_channels:
                print(f"   ⚽ ESPN Channels: {len(espn_channels)}")
            
            # Generar archivo M3U
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            m3u_filename = f"iptv_channels_specific_{timestamp}.m3u"
            
            content = extractor.generate_m3u_content(all_streams)
            
            with open(m3u_filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n💾 Archivo generado: {m3u_filename}")
            print(f"📂 Ubicación: {os.path.abspath(m3u_filename)}")
            
            # Mostrar algunos ejemplos de URLs encontradas
            print(f"\n🔗 Ejemplos de streams encontrados:")
            for i, stream in enumerate(all_streams[:5], 1):
                print(f"   {i}. {stream['name']}")
                print(f"      📍 {stream['url'][:80]}...")
                print(f"      🏷️ Fuente: {stream['source']} | Tipo: {stream['type']}")
            
            if len(all_streams) > 5:
                print(f"   ... y {len(all_streams) - 5} más")
            
        else:
            print("\n❌ No se encontraron streams")
            print("💡 Esto puede deberse a:")
            print("   • Protecciones anti-bot más fuertes")
            print("   • Cambios en las URLs de los canales")
            print("   • Necesidad de interacción JavaScript más compleja")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        if extractor:
            extractor.close_driver()
        print("\n🧹 Limpieza completada")

if __name__ == "__main__":
    main()
