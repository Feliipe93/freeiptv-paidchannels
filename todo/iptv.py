#!/usr/bin/env python3

import os
import subprocess
import sys
import time
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urljoin, urlparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
from datetime import datetime
import glob
import base64
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
import cloudscraper
# import js2py  # Removido por compatibilidad
# import execjs  # Removido por compatibilidad

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.load_free_proxies()
    
    def load_free_proxies(self):
        """Carga proxies gratuitos desde diferentes fuentes"""
        proxy_sources = [
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all',
        ]
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies_text = response.text.strip().split('\n')
                    for proxy in proxies_text[:10]:  # Tomar solo los primeros 10
                        if ':' in proxy:
                            self.proxies.append(proxy.strip())
            except:
                continue
                
        # Proxies adicionales conocidos (algunos pueden no funcionar)
        backup_proxies = [
            '8.8.8.8:8080',
            '1.1.1.1:8080',
            '203.142.64.90:8080',
            '91.107.6.115:53281',
        ]
        self.proxies.extend(backup_proxies)
    
    def get_proxy(self):
        """Obtiene el siguiente proxy disponible"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def test_proxy(self, proxy):
        """Prueba si un proxy funciona"""
        try:
            response = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=5)
            return response.status_code == 200
        except:
            return False

class IPTVExtractor:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.session = requests.Session()
        self.cloudscraper = cloudscraper.create_scraper()
        self.setup_headers()
        self.driver = None
        self.lock = threading.Lock()
        
    def setup_headers(self):
        """Configura headers realistas para evitar detección"""
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(headers)
        self.cloudscraper.headers.update(headers)
    
    def setup_webdriver(self):
        """Configura Selenium WebDriver con opciones anti-detección"""
        if self.driver is not None:
            return self.driver
            
        try:
            options = Options()
            options.add_argument('--headless')  # Modo headless por defecto
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Intentar usar ChromeDriver
            try:
                self.driver = webdriver.Chrome(options=options)
                # Ejecutar script para ocultar que es un bot
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return self.driver
            except Exception as e:
                print(f"⚠️ No se pudo configurar Selenium: {e}")
                return None
                
        except Exception as e:
            print(f"Error configurando WebDriver: {e}")
            return None
    
    def make_request(self, url, use_proxy=False, use_cloudscraper=False, use_selenium=False):
        """Hace una petición usando diferentes métodos"""
        try:
            if use_selenium:
                driver = self.setup_webdriver()
                if driver:
                    driver.get(url)
                    time.sleep(3)  # Esperar a que cargue
                    return driver.page_source
                
            # Desactivar proxies por defecto debido a problemas de conexión
            proxies = None
            # if use_proxy:
            #     proxies = self.proxy_manager.get_proxy()
            
            if use_cloudscraper:
                response = self.cloudscraper.get(url, proxies=proxies, timeout=15)
            else:
                response = self.session.get(url, proxies=proxies, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error HTTP {response.status_code} para {url}")
                
        except Exception as e:
            print(f"Error en petición a {url}: {e}")
            
        return None
    
    def extract_from_javascript(self, content):
        """Extrae URLs de streams desde código JavaScript"""
        streams = []
        
        # Patrones para encontrar URLs de streams
        patterns = [
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.ts[^"\']*)["\']',
            r'["\']([^"\']*stream[^"\']*\.m3u8[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+)["\']',
            r'src\s*:\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'hls\s*:\s*["\']([^"\']+)["\']',
            r'file\s*:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if any(ext in match.lower() for ext in ['.m3u8', '.ts', 'stream', 'live']):
                    if match.startswith('http'):
                        streams.append(match)
        
        return streams
    
    def extract_from_base64(self, content):
        """Extrae URLs codificadas en base64"""
        streams = []
        
        # Buscar cadenas en base64
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, content)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                if any(ext in decoded.lower() for ext in ['.m3u8', '.ts', 'stream', 'live']):
                    if decoded.startswith('http'):
                        streams.append(decoded)
            except:
                continue
                
        return streams
    
    def extract_iframe_sources(self, soup, base_url):
        """Extrae fuentes de iframes de manera recursiva"""
        streams = []
        
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src:
                if not src.startswith('http'):
                    src = urljoin(base_url, src)
                
                # Obtener contenido del iframe
                iframe_content = self.make_request(src)
                if iframe_content:
                    iframe_soup = BeautifulSoup(iframe_content, 'html.parser')
                    
                    # Buscar videos en el iframe
                    videos = iframe_soup.find_all(['video', 'source'])
                    for video in videos:
                        video_src = video.get('src')
                        if video_src and any(ext in video_src for ext in ['.m3u8', '.ts']):
                            streams.append(video_src)
                    
                    # Buscar en JavaScript del iframe
                    js_streams = self.extract_from_javascript(iframe_content)
                    streams.extend(js_streams)
        
        return streams
    
    def extract_tvplusgratis2(self):
        """Extrae TODOS los canales de tvplusgratis2.com con nombres reales y logos"""
        print("🔍 Extrayendo TODOS los canales de tvplusgratis2.com...")
        streams = []
        
        # Lista de canales específicos de tvplusgratis2.com basada en la información proporcionada
        channels = [
            {'name': 'Sky Sports La Liga', 'logo': '', 'url': 'https://www.tvplusgratis2.com/sky-sports-la-liga-en-vivo.html'},
            {'name': 'TUDN', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tudn-en-vivo.html'},
            {'name': 'Liga 1', 'logo': '', 'url': 'https://www.tvplusgratis2.com/liga-1-en-vivo.html'},
            {'name': 'Liga 1 Max', 'logo': '', 'url': 'https://www.tvplusgratis2.com/liga-1-max-en-vivo.html'},
            {'name': 'Gol Perú', 'logo': '', 'url': 'https://www.tvplusgratis2.com/gol-peru-en-vivo.html'},
            {'name': 'TNT Sports', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tnt-sports-en-vivo.html'},
            {'name': 'TNT Sports Chile', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tnt-sports-chile-en-vivo.html'},
            {'name': 'Fox Sports Premium', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-premium-en-vivo.html'},
            {'name': 'TYC Sports', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tyc-sports-en-vivo.html'},
            {'name': 'Dazn F1', 'logo': '', 'url': 'https://www.tvplusgratis2.com/dazn-f1-en-vivo.html'},
            {'name': 'Dazn La Liga', 'logo': '', 'url': 'https://www.tvplusgratis2.com/dazn-la-liga-en-vivo.html'},
            {'name': 'Directv Sports', 'logo': '', 'url': 'https://www.tvplusgratis2.com/directv-sports-en-vivo.html'},
            {'name': 'Directv Sports 2', 'logo': '', 'url': 'https://www.tvplusgratis2.com/directv-sports-2-en-vivo.html'},
            {'name': 'Directv Sports Plus', 'logo': '', 'url': 'https://www.tvplusgratis2.com/directv-sports-plus-en-vivo.html'},
            {'name': 'ESPN Premium', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-premium-en-vivo.html'},
            {'name': 'ESPN', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-en-vivo.html'},
            {'name': 'ESPN 2', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-2-en-vivo.html'},
            {'name': 'ESPN 3', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-3-en-vivo.html'},
            {'name': 'ESPN 4', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-4-en-vivo.html'},
            {'name': 'ESPN Mexico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-mexico-en-vivo.html'},
            {'name': 'ESPN 2 Mexico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-2-mexico-en-vivo.html'},
            {'name': 'ESPN 3 Mexico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-3-mexico-en-vivo.html'},
            {'name': 'Fox Sports', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-en-vivo.html'},
            {'name': 'Fox Sports 2', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-2-en-vivo.html'},
            {'name': 'Fox Sports 3', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-3-en-vivo.html'},
            {'name': 'Fox Sports Mexico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-mexico-en-vivo.html'},
            {'name': 'Fox Sports 2 Mexico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-2-mexico-en-vivo.html'},
            {'name': 'Fox Sports 3 Mexico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fox-sports-3-mexico-en-vivo.html'},
            {'name': 'Telemundo 51', 'logo': '', 'url': 'https://www.tvplusgratis2.com/telemundo-51-en-vivo.html'},
            {'name': 'Telemundo Puerto Rico', 'logo': '', 'url': 'https://www.tvplusgratis2.com/telemundo-puerto-rico-en-vivo.html'},
            {'name': 'Telemundo Internacional', 'logo': '', 'url': 'https://www.tvplusgratis2.com/telemundo-internacional-en-vivo.html'},
            {'name': 'RCN', 'logo': '', 'url': 'https://www.tvplusgratis2.com/rcn-en-vivo.html'},
            {'name': 'Antena 3', 'logo': '', 'url': 'https://www.tvplusgratis2.com/antena-3-en-vivo.html'},
            {'name': 'Global TV', 'logo': '', 'url': 'https://www.tvplusgratis2.com/global-tv-en-vivo.html'},
            {'name': 'Latina', 'logo': '', 'url': 'https://www.tvplusgratis2.com/latina-en-vivo.html'},
            {'name': 'America TV', 'logo': '', 'url': 'https://www.tvplusgratis2.com/america-tv-en-vivo.html'},
            {'name': 'Willax TV', 'logo': '', 'url': 'https://www.tvplusgratis2.com/willax-tv-en-vivo.html'},
            {'name': 'Azteca 7', 'logo': '', 'url': 'https://www.tvplusgratis2.com/azteca-7-en-vivo.html'},
            {'name': 'Canal 5', 'logo': '', 'url': 'https://www.tvplusgratis2.com/canal-5-en-vivo.html'},
            {'name': 'Disney Channel', 'logo': '', 'url': 'https://www.tvplusgratis2.com/disney-channel-en-vivo.html'},
            {'name': 'Disney JR', 'logo': '', 'url': 'https://www.tvplusgratis2.com/disney-jr-en-vivo.html'},
            {'name': 'Universal Channel', 'logo': '', 'url': 'https://www.tvplusgratis2.com/universal-channel-en-vivo.html'},
            {'name': 'Universal Cinema', 'logo': '', 'url': 'https://www.tvplusgratis2.com/universal-cinema-en-vivo.html'},
            {'name': 'Universal Premiere', 'logo': '', 'url': 'https://www.tvplusgratis2.com/universal-premiere-en-vivo.html'},
            {'name': 'TNT', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tnt-en-vivo.html'},
            {'name': 'TNT Series', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tnt-series-en-vivo.html'},
            {'name': 'TNT Novelas', 'logo': '', 'url': 'https://www.tvplusgratis2.com/tnt-novelas-en-vivo.html'},
            {'name': 'Star Channel', 'logo': '', 'url': 'https://www.tvplusgratis2.com/star-channel-en-vivo.html'},
            {'name': 'Cinemax', 'logo': '', 'url': 'https://www.tvplusgratis2.com/cinemax-en-vivo.html'},
            {'name': 'Space', 'logo': '', 'url': 'https://www.tvplusgratis2.com/space-en-vivo.html'},
            {'name': 'Syfy', 'logo': '', 'url': 'https://www.tvplusgratis2.com/syfy-en-vivo.html'},
            {'name': 'Warner Channel', 'logo': '', 'url': 'https://www.tvplusgratis2.com/warner-channel-en-vivo.html'},
            {'name': 'Cinecanal', 'logo': '', 'url': 'https://www.tvplusgratis2.com/cinecanal-en-vivo.html'},
            {'name': 'FX', 'logo': '', 'url': 'https://www.tvplusgratis2.com/fx-en-vivo.html'},
            {'name': 'AXN', 'logo': '', 'url': 'https://www.tvplusgratis2.com/axn-en-vivo.html'},
            {'name': 'AMC', 'logo': '', 'url': 'https://www.tvplusgratis2.com/amc-en-vivo.html'},
            {'name': 'Golden', 'logo': '', 'url': 'https://www.tvplusgratis2.com/golden-en-vivo.html'},
            {'name': 'Golden Plus', 'logo': '', 'url': 'https://www.tvplusgratis2.com/golden-plus-en-vivo.html'},
            {'name': 'Golden Edge', 'logo': '', 'url': 'https://www.tvplusgratis2.com/golden-edge-en-vivo.html'},
            {'name': 'Canal Sony', 'logo': '', 'url': 'https://www.tvplusgratis2.com/canal-sony-en-vivo.html'},
            {'name': 'Dragon Ball Super 24/7', 'logo': '', 'url': 'https://www.tvplusgratis2.com/dragon-ball-super-24-7-en-vivo.html'}
        ]
        
        return self._extract_all_channels_from_site(channels, 'tvplusgratis2')
    
    def extract_vertvcable(self):
        """Extrae TODOS los canales de vertvcable.com con nombres reales y logos"""
        print("🔍 Extrayendo TODOS los canales de vertvcable.com...")
        
        # Lista completa de canales de vertvcable.com basada en la información proporcionada
        channels = [
            {'name': 'TNT Novelas', 'logo': '', 'url': 'https://vertvcable.com/tnt-novelas-en-vivo/'},
            {'name': 'Telemundo', 'logo': '', 'url': 'https://vertvcable.com/telemundo-en-vivo/'},
            {'name': 'Univision', 'logo': '', 'url': 'https://vertvcable.com/univision-en-vivo/'},
            {'name': 'Caracol', 'logo': '', 'url': 'https://vertvcable.com/caracol-en-vivo/'},
            {'name': 'TVE', 'logo': '', 'url': 'https://vertvcable.com/tve-en-vivo/'},
            {'name': 'Canal Uno', 'logo': '', 'url': 'https://vertvcable.com/canal-uno-en-vivo/'},
            {'name': 'Señal Colombia', 'logo': '', 'url': 'https://vertvcable.com/senal-colombia-en-vivo/'},
            {'name': 'City TV', 'logo': '', 'url': 'https://vertvcable.com/city-tv-en-vivo/'},
            {'name': 'RCN', 'logo': '', 'url': 'https://vertvcable.com/rcn-en-vivo/'},
            {'name': 'Telecaribe', 'logo': '', 'url': 'https://vertvcable.com/telecaribe-en-vivo/'},
            {'name': 'Teleantioquia', 'logo': '', 'url': 'https://vertvcable.com/teleantioquia-en-vivo/'},
            {'name': 'Telesur', 'logo': '', 'url': 'https://vertvcable.com/telesur-en-vivo/'},
            {'name': 'Canal Trece', 'logo': '', 'url': 'https://vertvcable.com/canal-trece-en-vivo/'},
            {'name': 'TRO', 'logo': '', 'url': 'https://vertvcable.com/tro-en-vivo/'},
            {'name': 'TVC', 'logo': '', 'url': 'https://vertvcable.com/tvc-en-vivo/'},
            {'name': 'Canal Claro', 'logo': '', 'url': 'https://vertvcable.com/canal-claro-en-vivo/'},
            {'name': 'TNT', 'logo': '', 'url': 'https://vertvcable.com/tnt-en-vivo/'},
            {'name': 'FX', 'logo': '', 'url': 'https://vertvcable.com/fx-en-vivo/'},
            {'name': 'FXM', 'logo': '', 'url': 'https://vertvcable.com/fxm-en-vivo/'},
            {'name': 'Sony', 'logo': '', 'url': 'https://vertvcable.com/sony-en-vivo/'},
            {'name': 'Star Channel', 'logo': '', 'url': 'https://vertvcable.com/star-channel-en-vivo/'},
            {'name': 'Universal Channel', 'logo': '', 'url': 'https://vertvcable.com/universal-channel-en-vivo/'},
            {'name': 'Studio Universal', 'logo': '', 'url': 'https://vertvcable.com/studio-universal-en-vivo/'},
            {'name': 'Paramount', 'logo': '', 'url': 'https://vertvcable.com/paramount-en-vivo/'},
            {'name': 'Space', 'logo': '', 'url': 'https://vertvcable.com/space-en-vivo/'},
            {'name': 'Cinecanal', 'logo': '', 'url': 'https://vertvcable.com/cinecanal-en-vivo/'},
            {'name': 'Cinemax', 'logo': '', 'url': 'https://vertvcable.com/cinemax-en-vivo/'},
            {'name': 'A&E', 'logo': '', 'url': 'https://vertvcable.com/ae-en-vivo/'},
            {'name': 'AXN', 'logo': '', 'url': 'https://vertvcable.com/axn-en-vivo/'},
            {'name': 'Syfy', 'logo': '', 'url': 'https://vertvcable.com/syfy-en-vivo/'},
            {'name': 'Warner Channel', 'logo': '', 'url': 'https://vertvcable.com/warner-channel-en-vivo/'},
            {'name': 'AMC', 'logo': '', 'url': 'https://vertvcable.com/amc-en-vivo/'},
            {'name': 'ESPN', 'logo': '', 'url': 'https://vertvcable.com/espn-en-vivo/'},
            {'name': 'ESPN 2', 'logo': '', 'url': 'https://vertvcable.com/espn-2-en-vivo/'},
            {'name': 'ESPN 3', 'logo': '', 'url': 'https://vertvcable.com/espn-3-en-vivo/'},
            {'name': 'ESPN Extra', 'logo': '', 'url': 'https://vertvcable.com/espn-extra-en-vivo/'},
            {'name': 'Fox Sports', 'logo': '', 'url': 'https://vertvcable.com/fox-sports-en-vivo/'},
            {'name': 'Fox Sports 2', 'logo': '', 'url': 'https://vertvcable.com/fox-sports-2-en-vivo/'},
            {'name': 'Fox Sports 3', 'logo': '', 'url': 'https://vertvcable.com/fox-sports-3-en-vivo/'},
            {'name': 'Win Sports', 'logo': '', 'url': 'https://vertvcable.com/win-sports-en-vivo/'},
            {'name': 'Win Sports Plus', 'logo': '', 'url': 'https://vertvcable.com/win-sports-plus-en-vivo/'},
            {'name': 'Claro Sports', 'logo': '', 'url': 'https://vertvcable.com/claro-sports-en-vivo/'},
            {'name': 'Caracol Sports', 'logo': '', 'url': 'https://vertvcable.com/caracol-sports-en-vivo/'},
            {'name': 'Discovery Channel', 'logo': '', 'url': 'https://vertvcable.com/discovery-channel-en-vivo/'},
            {'name': 'Discovery Science', 'logo': '', 'url': 'https://vertvcable.com/discovery-science-en-vivo/'},
            {'name': 'Discovery Theater', 'logo': '', 'url': 'https://vertvcable.com/discovery-theater-en-vivo/'},
            {'name': 'Discovery Turbo', 'logo': '', 'url': 'https://vertvcable.com/discovery-turbo-en-vivo/'},
            {'name': 'Discovery World', 'logo': '', 'url': 'https://vertvcable.com/discovery-world-en-vivo/'},
            {'name': 'History', 'logo': '', 'url': 'https://vertvcable.com/history-en-vivo/'},
            {'name': 'History 2', 'logo': '', 'url': 'https://vertvcable.com/history-2-en-vivo/'},
            {'name': 'Animal Planet', 'logo': '', 'url': 'https://vertvcable.com/animal-planet-en-vivo/'},
            {'name': 'Nat Geo', 'logo': '', 'url': 'https://vertvcable.com/nat-geo-en-vivo/'},
            {'name': 'Nat Geo Wild', 'logo': '', 'url': 'https://vertvcable.com/nat-geo-wild-en-vivo/'},
            {'name': 'Investigación', 'logo': '', 'url': 'https://vertvcable.com/investigacion-en-vivo/'},
            {'name': 'CNN En Español', 'logo': '', 'url': 'https://vertvcable.com/cnn-en-espanol-en-vivo/'},
            {'name': 'Noticias Caracol', 'logo': '', 'url': 'https://vertvcable.com/noticias-caracol-en-vivo/'},
            {'name': 'Noticias RCN', 'logo': '', 'url': 'https://vertvcable.com/noticias-rcn-en-vivo/'},
            {'name': 'NTN24', 'logo': '', 'url': 'https://vertvcable.com/ntn24-en-vivo/'},
            {'name': 'RT Español', 'logo': '', 'url': 'https://vertvcable.com/rt-espanol-en-vivo/'},
            {'name': 'DW Español', 'logo': '', 'url': 'https://vertvcable.com/dw-espanol-en-vivo/'},
            {'name': 'BBC News', 'logo': '', 'url': 'https://vertvcable.com/bbc-news-en-vivo/'},
            {'name': 'CNN International', 'logo': '', 'url': 'https://vertvcable.com/cnn-international-en-vivo/'},
            {'name': 'Cartoon Network', 'logo': '', 'url': 'https://vertvcable.com/cartoon-network-en-vivo/'},
            {'name': 'Disney Channel', 'logo': '', 'url': 'https://vertvcable.com/disney-channel-en-vivo/'},
            {'name': 'Disney Junior', 'logo': '', 'url': 'https://vertvcable.com/disney-junior-en-vivo/'},
            {'name': 'Nickelodeon', 'logo': '', 'url': 'https://vertvcable.com/nickelodeon-en-vivo/'},
            {'name': 'Nick Jr', 'logo': '', 'url': 'https://vertvcable.com/nick-jr-en-vivo/'},
            {'name': 'Tooncast', 'logo': '', 'url': 'https://vertvcable.com/tooncast-en-vivo/'},
            {'name': 'Discovery Kids', 'logo': '', 'url': 'https://vertvcable.com/discovery-kids-en-vivo/'},
            {'name': 'Paka Paka', 'logo': '', 'url': 'https://vertvcable.com/paka-paka-en-vivo/'},
            {'name': 'MTV', 'logo': '', 'url': 'https://vertvcable.com/mtv-en-vivo/'},
            {'name': 'VH1', 'logo': '', 'url': 'https://vertvcable.com/vh1-en-vivo/'},
            {'name': 'E!', 'logo': '', 'url': 'https://vertvcable.com/e-en-vivo/'},
            {'name': 'Comedy Central', 'logo': '', 'url': 'https://vertvcable.com/comedy-central-en-vivo/'},
            {'name': 'DHE', 'logo': '', 'url': 'https://vertvcable.com/dhe-en-vivo/'},
            {'name': 'Lifetime', 'logo': '', 'url': 'https://vertvcable.com/lifetime-en-vivo/'},
            {'name': 'TLC', 'logo': '', 'url': 'https://vertvcable.com/tlc-en-vivo/'},
            {'name': 'Home & Health', 'logo': '', 'url': 'https://vertvcable.com/home-health-en-vivo/'},
            {'name': 'Food Network', 'logo': '', 'url': 'https://vertvcable.com/food-network-en-vivo/'},
            {'name': 'HGTV', 'logo': '', 'url': 'https://vertvcable.com/hgtv-en-vivo/'},
            {'name': 'ID', 'logo': '', 'url': 'https://vertvcable.com/id-en-vivo/'},
            {'name': 'Travel + Living', 'logo': '', 'url': 'https://vertvcable.com/travel-living-en-vivo/'}
        ]
        
        return self._extract_all_channels_from_site(channels, 'vertvcable')
    
    def extract_cablevisionhd(self):
        """Extrae TODOS los canales de cablevisionhd.com con nombres reales y logos"""
        print("🔍 Extrayendo TODOS los canales de cablevisionhd.com...")
        
        # Lista completa de canales de cablevisionhd.com basada en la información proporcionada
        channels = [
            {'name': 'TUDN', 'logo': '', 'url': 'https://www.cablevisionhd.com/tudn-en-vivo/'},
            {'name': 'Gol Perú', 'logo': '', 'url': 'https://www.cablevisionhd.com/gol-peru-en-vivo/'},
            {'name': 'TNT Sports', 'logo': '', 'url': 'https://www.cablevisionhd.com/tnt-sports-en-vivo/'},
            {'name': 'Fox Sports Premium', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-premium-en-vivo/'},
            {'name': 'TYC Sports', 'logo': '', 'url': 'https://www.cablevisionhd.com/tyc-sports-en-vivo/'},
            {'name': 'Movistar Deportes', 'logo': '', 'url': 'https://www.cablevisionhd.com/movistar-deportes-en-vivo/'},
            {'name': 'Movistar La Liga', 'logo': '', 'url': 'https://www.cablevisionhd.com/movistar-la-liga-en-vivo/'},
            {'name': 'Movistar Liga De Campeones', 'logo': '', 'url': 'https://www.cablevisionhd.com/movistar-liga-de-campeones-en-vivo/'},
            {'name': 'Dazn F1', 'logo': '', 'url': 'https://www.cablevisionhd.com/dazn-f1-en-vivo/'},
            {'name': 'Dazn La Liga', 'logo': '', 'url': 'https://www.cablevisionhd.com/dazn-la-liga-en-vivo/'},
            {'name': 'Bein Sports Extra', 'logo': '', 'url': 'https://www.cablevisionhd.com/bein-sports-extra-en-vivo/'},
            {'name': 'Directv Sports', 'logo': '', 'url': 'https://www.cablevisionhd.com/directv-sports-en-vivo/'},
            {'name': 'Directv Sports 2', 'logo': '', 'url': 'https://www.cablevisionhd.com/directv-sports-2-en-vivo/'},
            {'name': 'Directv Sports Plus', 'logo': '', 'url': 'https://www.cablevisionhd.com/directv-sports-plus-en-vivo/'},
            {'name': 'ESPN Premium', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-premium-en-vivo/'},
            {'name': 'ESPN', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-en-vivo/'},
            {'name': 'ESPN 2', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-2-en-vivo/'},
            {'name': 'ESPN 3', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-3-en-vivo/'},
            {'name': 'ESPN 4', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-4-en-vivo/'},
            {'name': 'ESPN 5', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-5-en-vivo/'},
            {'name': 'ESPN 6', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-6-en-vivo/'},
            {'name': 'ESPN 7', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-7-en-vivo/'},
            {'name': 'ESPN Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-mexico-en-vivo/'},
            {'name': 'ESPN 2 Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-2-mexico-en-vivo/'},
            {'name': 'ESPN 3 Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/espn-3-mexico-en-vivo/'},
            {'name': 'Fox Deportes', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-deportes-en-vivo/'},
            {'name': 'Fox Sports', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-en-vivo/'},
            {'name': 'Fox Sports 2', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-2-en-vivo/'},
            {'name': 'Fox Sports 3', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-3-en-vivo/'},
            {'name': 'Fox Sports Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-mexico-en-vivo/'},
            {'name': 'Fox Sports 2 Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-2-mexico-en-vivo/'},
            {'name': 'Fox Sports 3 Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/fox-sports-3-mexico-en-vivo/'},
            {'name': 'Telefe', 'logo': '', 'url': 'https://www.cablevisionhd.com/telefe-en-vivo/'},
            {'name': 'El Trece', 'logo': '', 'url': 'https://www.cablevisionhd.com/el-trece-en-vivo/'},
            {'name': 'Television Publica', 'logo': '', 'url': 'https://www.cablevisionhd.com/television-publica-en-vivo/'},
            {'name': 'Telemundo 51', 'logo': '', 'url': 'https://www.cablevisionhd.com/telemundo-51-en-vivo/'},
            {'name': 'Telemundo Puerto Rico', 'logo': '', 'url': 'https://www.cablevisionhd.com/telemundo-puerto-rico-en-vivo/'},
            {'name': 'Univisión', 'logo': '', 'url': 'https://www.cablevisionhd.com/univision-en-vivo/'},
            {'name': 'Pasiones', 'logo': '', 'url': 'https://www.cablevisionhd.com/pasiones-en-vivo/'},
            {'name': 'Caracol', 'logo': '', 'url': 'https://www.cablevisionhd.com/caracol-en-vivo/'},
            {'name': 'RCN', 'logo': '', 'url': 'https://www.cablevisionhd.com/rcn-en-vivo/'},
            {'name': 'Latina', 'logo': '', 'url': 'https://www.cablevisionhd.com/latina-en-vivo/'},
            {'name': 'America TV', 'logo': '', 'url': 'https://www.cablevisionhd.com/america-tv-en-vivo/'},
            {'name': 'ATV', 'logo': '', 'url': 'https://www.cablevisionhd.com/atv-en-vivo/'},
            {'name': 'Las Estrellas', 'logo': '', 'url': 'https://www.cablevisionhd.com/las-estrellas-en-vivo/'},
            {'name': 'Tlnovelas', 'logo': '', 'url': 'https://www.cablevisionhd.com/tlnovelas-en-vivo/'},
            {'name': 'Galavision', 'logo': '', 'url': 'https://www.cablevisionhd.com/galavision-en-vivo/'},
            {'name': 'Azteca 7', 'logo': '', 'url': 'https://www.cablevisionhd.com/azteca-7-en-vivo/'},
            {'name': 'Azteca Uno', 'logo': '', 'url': 'https://www.cablevisionhd.com/azteca-uno-en-vivo/'},
            {'name': 'Canal 5', 'logo': '', 'url': 'https://www.cablevisionhd.com/canal-5-en-vivo/'},
            {'name': 'Cartoon Network', 'logo': '', 'url': 'https://www.cablevisionhd.com/cartoon-network-en-vivo/'},
            {'name': 'Tooncast', 'logo': '', 'url': 'https://www.cablevisionhd.com/tooncast-en-vivo/'},
            {'name': 'Cartoonito', 'logo': '', 'url': 'https://www.cablevisionhd.com/cartoonito-en-vivo/'},
            {'name': 'Disney Channel', 'logo': '', 'url': 'https://www.cablevisionhd.com/disney-channel-en-vivo/'},
            {'name': 'Disney JR', 'logo': '', 'url': 'https://www.cablevisionhd.com/disney-jr-en-vivo/'},
            {'name': 'Nick', 'logo': '', 'url': 'https://www.cablevisionhd.com/nick-en-vivo/'},
            {'name': 'Discovery Channel', 'logo': '', 'url': 'https://www.cablevisionhd.com/discovery-channel-en-vivo/'},
            {'name': 'Discovery World', 'logo': '', 'url': 'https://www.cablevisionhd.com/discovery-world-en-vivo/'},
            {'name': 'Discovery Theater', 'logo': '', 'url': 'https://www.cablevisionhd.com/discovery-theater-en-vivo/'},
            {'name': 'Discovery Science', 'logo': '', 'url': 'https://www.cablevisionhd.com/discovery-science-en-vivo/'},
            {'name': 'History', 'logo': '', 'url': 'https://www.cablevisionhd.com/history-en-vivo/'},
            {'name': 'History 2', 'logo': '', 'url': 'https://www.cablevisionhd.com/history-2-en-vivo/'},
            {'name': 'Animal Planet', 'logo': '', 'url': 'https://www.cablevisionhd.com/animal-planet-en-vivo/'},
            {'name': 'Nat Geo', 'logo': '', 'url': 'https://www.cablevisionhd.com/nat-geo-en-vivo/'},
            {'name': 'Nat Geo Mundo', 'logo': '', 'url': 'https://www.cablevisionhd.com/nat-geo-mundo-en-vivo/'},
            {'name': 'Universal Channel', 'logo': '', 'url': 'https://www.cablevisionhd.com/universal-channel-en-vivo/'},
            {'name': 'TNT', 'logo': '', 'url': 'https://www.cablevisionhd.com/tnt-en-vivo/'},
            {'name': 'TNT Series', 'logo': '', 'url': 'https://www.cablevisionhd.com/tnt-series-en-vivo/'},
            {'name': 'Star Channel', 'logo': '', 'url': 'https://www.cablevisionhd.com/star-channel-en-vivo/'},
            {'name': 'Cinemax', 'logo': '', 'url': 'https://www.cablevisionhd.com/cinemax-en-vivo/'},
            {'name': 'Space', 'logo': '', 'url': 'https://www.cablevisionhd.com/space-en-vivo/'},
            {'name': 'Syfy', 'logo': '', 'url': 'https://www.cablevisionhd.com/syfy-en-vivo/'},
            {'name': 'Warner Channel', 'logo': '', 'url': 'https://www.cablevisionhd.com/warner-channel-en-vivo/'},
            {'name': 'Warner Channel Mexico', 'logo': '', 'url': 'https://www.cablevisionhd.com/warner-channel-mexico-en-vivo/'},
            {'name': 'Cinecanal', 'logo': '', 'url': 'https://www.cablevisionhd.com/cinecanal-en-vivo/'},
            {'name': 'FX', 'logo': '', 'url': 'https://www.cablevisionhd.com/fx-en-vivo/'},
            {'name': 'AXN', 'logo': '', 'url': 'https://www.cablevisionhd.com/axn-en-vivo/'},
            {'name': 'AMC', 'logo': '', 'url': 'https://www.cablevisionhd.com/amc-en-vivo/'},
            {'name': 'Studio Universal', 'logo': '', 'url': 'https://www.cablevisionhd.com/studio-universal-en-vivo/'},
            {'name': 'Golden Plus', 'logo': '', 'url': 'https://www.cablevisionhd.com/golden-plus-en-vivo/'},
            {'name': 'Golden Edge', 'logo': '', 'url': 'https://www.cablevisionhd.com/golden-edge-en-vivo/'},
            {'name': 'Golden Premier', 'logo': '', 'url': 'https://www.cablevisionhd.com/golden-premier-en-vivo/'},
            {'name': 'Golden Premier 2', 'logo': '', 'url': 'https://www.cablevisionhd.com/golden-premier-2-en-vivo/'},
            {'name': 'Multipremier', 'logo': '', 'url': 'https://www.cablevisionhd.com/multipremier-en-vivo/'},
            {'name': 'Canal Sony', 'logo': '', 'url': 'https://www.cablevisionhd.com/canal-sony-en-vivo/'},
            {'name': 'DHE', 'logo': '', 'url': 'https://www.cablevisionhd.com/dhe-en-vivo/'},
            {'name': 'Distrito Comedia', 'logo': '', 'url': 'https://www.cablevisionhd.com/distrito-comedia-en-vivo/'},
            {'name': 'Los Picapiedras 24/7', 'logo': '', 'url': 'https://www.cablevisionhd.com/los-picapiedras-24-7-en-vivo/'}
        ]
        
        return self._extract_all_channels_from_site(channels, 'cablevisionhd')
    
    def extract_telegratishd(self):
        """Extrae TODOS los canales de telegratishd.com con nombres reales y logos"""
        print("🔍 Extrayendo TODOS los canales de telegratishd.com...")
        
        # Lista completa de canales de telegratishd.com basada en la información proporcionada
        channels = [
            {'name': 'Liga 1 Max', 'logo': '', 'url': 'https://www.telegratishd.com/liga-1-max-en-vivo.html'},
            {'name': 'TUDN', 'logo': '', 'url': 'https://www.telegratishd.com/tudn-en-vivo.html'},
            {'name': 'Gol Perú', 'logo': '', 'url': 'https://www.telegratishd.com/gol-peru-en-vivo.html'},
            {'name': 'TNT Sports', 'logo': '', 'url': 'https://www.telegratishd.com/tnt-sports-en-vivo.html'},
            {'name': 'Fox Sports Premium', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-premium-en-vivo.html'},
            {'name': 'TYC Sports', 'logo': '', 'url': 'https://www.telegratishd.com/tyc-sports-en-vivo.html'},
            {'name': 'Movistar Deportes', 'logo': '', 'url': 'https://www.telegratishd.com/movistar-deportes-en-vivo.html'},
            {'name': 'Movistar Liga De Campeones', 'logo': '', 'url': 'https://www.telegratishd.com/movistar-liga-de-campeones-en-vivo.html'},
            {'name': 'Dazn F1', 'logo': '', 'url': 'https://www.telegratishd.com/dazn-f1-en-vivo.html'},
            {'name': 'Dazn La Liga', 'logo': '', 'url': 'https://www.telegratishd.com/dazn-la-liga-en-vivo.html'},
            {'name': 'Directv Sports', 'logo': '', 'url': 'https://www.telegratishd.com/directv-sports-en-vivo.html'},
            {'name': 'Directv Sports 2', 'logo': '', 'url': 'https://www.telegratishd.com/directv-sports-2-en-vivo.html'},
            {'name': 'Directv Sports Plus', 'logo': '', 'url': 'https://www.telegratishd.com/directv-sports-plus-en-vivo.html'},
            {'name': 'ESPN Premium', 'logo': '', 'url': 'https://www.telegratishd.com/espn-premium-en-vivo.html'},
            {'name': 'ESPN', 'logo': '', 'url': 'https://www.telegratishd.com/espn-en-vivo.html'},
            {'name': 'ESPN 2', 'logo': '', 'url': 'https://www.telegratishd.com/espn-2-en-vivo.html'},
            {'name': 'ESPN 3', 'logo': '', 'url': 'https://www.telegratishd.com/espn-3-en-vivo.html'},
            {'name': 'ESPN 4', 'logo': '', 'url': 'https://www.telegratishd.com/espn-4-en-vivo.html'},
            {'name': 'ESPN Mexico', 'logo': '', 'url': 'https://www.telegratishd.com/espn-mexico-en-vivo.html'},
            {'name': 'ESPN 2 Mexico', 'logo': '', 'url': 'https://www.telegratishd.com/espn-2-mexico-en-vivo.html'},
            {'name': 'ESPN 3 Mexico', 'logo': '', 'url': 'https://www.telegratishd.com/espn-3-mexico-en-vivo.html'},
            {'name': 'Fox Sports', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-en-vivo.html'},
            {'name': 'Fox Sports 2', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-2-en-vivo.html'},
            {'name': 'Fox Sports 3', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-3-en-vivo.html'},
            {'name': 'Fox Sports Mexico', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-mexico-en-vivo.html'},
            {'name': 'Fox Sports 2 Mexico', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-2-mexico-en-vivo.html'},
            {'name': 'Fox Sports 3 Mexico', 'logo': '', 'url': 'https://www.telegratishd.com/fox-sports-3-mexico-en-vivo.html'},
            {'name': 'Telefe', 'logo': '', 'url': 'https://www.telegratishd.com/telefe-en-vivo.html'},
            {'name': 'El Trece', 'logo': '', 'url': 'https://www.telegratishd.com/el-trece-en-vivo.html'},
            {'name': 'Television Publica', 'logo': '', 'url': 'https://www.telegratishd.com/television-publica-en-vivo.html'},
            {'name': 'Telemundo 51', 'logo': '', 'url': 'https://www.telegratishd.com/telemundo-51-en-vivo.html'},
            {'name': 'Telemundo Puerto Rico', 'logo': '', 'url': 'https://www.telegratishd.com/telemundo-puerto-rico-en-vivo.html'},
            {'name': 'Univision', 'logo': '', 'url': 'https://www.telegratishd.com/univision-en-vivo.html'},
            {'name': 'Pasiones', 'logo': '', 'url': 'https://www.telegratishd.com/pasiones-en-vivo.html'},
            {'name': 'Antena 3', 'logo': '', 'url': 'https://www.telegratishd.com/antena-3-en-vivo.html'},
            {'name': 'DW Español', 'logo': '', 'url': 'https://www.telegratishd.com/dw-espanol-en-vivo.html'},
            {'name': 'Ecuavisa', 'logo': '', 'url': 'https://www.telegratishd.com/ecuavisa-en-vivo.html'},
            {'name': 'Caracol', 'logo': '', 'url': 'https://www.telegratishd.com/caracol-en-vivo.html'},
            {'name': 'RCN', 'logo': '', 'url': 'https://www.telegratishd.com/rcn-en-vivo.html'},
            {'name': 'Latina', 'logo': '', 'url': 'https://www.telegratishd.com/latina-en-vivo.html'},
            {'name': 'America TV', 'logo': '', 'url': 'https://www.telegratishd.com/america-tv-en-vivo.html'},
            {'name': 'Global TV', 'logo': '', 'url': 'https://www.telegratishd.com/global-tv-en-vivo.html'},
            {'name': 'Willax TV', 'logo': '', 'url': 'https://www.telegratishd.com/willax-tv-en-vivo.html'},
            {'name': 'ATV', 'logo': '', 'url': 'https://www.telegratishd.com/atv-en-vivo.html'},
            {'name': 'TV Peru', 'logo': '', 'url': 'https://www.telegratishd.com/tv-peru-en-vivo.html'},
            {'name': 'Panamericana Television', 'logo': '', 'url': 'https://www.telegratishd.com/panamericana-television-en-vivo.html'},
            {'name': 'Exitosa', 'logo': '', 'url': 'https://www.telegratishd.com/exitosa-en-vivo.html'},
            {'name': 'Unicable', 'logo': '', 'url': 'https://www.telegratishd.com/unicable-en-vivo.html'},
            {'name': 'Imagen TV', 'logo': '', 'url': 'https://www.telegratishd.com/imagen-tv-en-vivo.html'},
            {'name': 'Azteca 7', 'logo': '', 'url': 'https://www.telegratishd.com/azteca-7-en-vivo.html'},
            {'name': 'Azteca Uno', 'logo': '', 'url': 'https://www.telegratishd.com/azteca-uno-en-vivo.html'},
            {'name': 'Canal 5', 'logo': '', 'url': 'https://www.telegratishd.com/canal-5-en-vivo.html'},
            {'name': 'Az Cinema', 'logo': '', 'url': 'https://www.telegratishd.com/az-cinema-en-vivo.html'},
            {'name': 'Azteca Internacional', 'logo': '', 'url': 'https://www.telegratishd.com/azteca-internacional-en-vivo.html'},
            {'name': 'Az Corazon', 'logo': '', 'url': 'https://www.telegratishd.com/az-corazon-en-vivo.html'},
            {'name': 'Az Click', 'logo': '', 'url': 'https://www.telegratishd.com/az-click-en-vivo.html'},
            {'name': 'Disney Channel', 'logo': '', 'url': 'https://www.telegratishd.com/disney-channel-en-vivo.html'},
            {'name': 'Disney JR', 'logo': '', 'url': 'https://www.telegratishd.com/disney-jr-en-vivo.html'},
            {'name': 'Discovery Kids', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-kids-en-vivo.html'},
            {'name': 'Cartoon Network', 'logo': '', 'url': 'https://www.telegratishd.com/cartoon-network-en-vivo.html'},
            {'name': 'Tooncast', 'logo': '', 'url': 'https://www.telegratishd.com/tooncast-en-vivo.html'},
            {'name': 'Cartoonito', 'logo': '', 'url': 'https://www.telegratishd.com/cartoonito-en-vivo.html'},
            {'name': 'Nick', 'logo': '', 'url': 'https://www.telegratishd.com/nick-en-vivo.html'},
            {'name': 'Nick JR', 'logo': '', 'url': 'https://www.telegratishd.com/nick-jr-en-vivo.html'},
            {'name': 'Music Top', 'logo': '', 'url': 'https://www.telegratishd.com/music-top-en-vivo.html'},
            {'name': 'MTV', 'logo': '', 'url': 'https://www.telegratishd.com/mtv-en-vivo.html'},
            {'name': 'Telehit', 'logo': '', 'url': 'https://www.telegratishd.com/telehit-en-vivo.html'},
            {'name': 'Discovery Channel', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-channel-en-vivo.html'},
            {'name': 'Discovery World', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-world-en-vivo.html'},
            {'name': 'Discovery Theater', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-theater-en-vivo.html'},
            {'name': 'Discovery Science', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-science-en-vivo.html'},
            {'name': 'Discovery TLC', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-tlc-en-vivo.html'},
            {'name': 'ID Investigation', 'logo': '', 'url': 'https://www.telegratishd.com/id-investigation-en-vivo.html'},
            {'name': 'Discovery Turbo', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-turbo-en-vivo.html'},
            {'name': 'Discovery H&H', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-h-h-en-vivo.html'},
            {'name': 'Discovery Familia', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-familia-en-vivo.html'},
            {'name': 'Discovery A&E', 'logo': '', 'url': 'https://www.telegratishd.com/discovery-a-e-en-vivo.html'},
            {'name': 'History', 'logo': '', 'url': 'https://www.telegratishd.com/history-en-vivo.html'},
            {'name': 'History 2', 'logo': '', 'url': 'https://www.telegratishd.com/history-2-en-vivo.html'},
            {'name': 'Animal Planet', 'logo': '', 'url': 'https://www.telegratishd.com/animal-planet-en-vivo.html'},
            {'name': 'Nat Geo', 'logo': '', 'url': 'https://www.telegratishd.com/nat-geo-en-vivo.html'},
            {'name': 'Everything', 'logo': '', 'url': 'https://www.telegratishd.com/everything-en-vivo.html'},
            {'name': 'Universal Channel', 'logo': '', 'url': 'https://www.telegratishd.com/universal-channel-en-vivo.html'},
            {'name': 'Universal Premiere', 'logo': '', 'url': 'https://www.telegratishd.com/universal-premiere-en-vivo.html'},
            {'name': 'TNT', 'logo': '', 'url': 'https://www.telegratishd.com/tnt-en-vivo.html'},
            {'name': 'TNT Series', 'logo': '', 'url': 'https://www.telegratishd.com/tnt-series-en-vivo.html'},
            {'name': 'Star Channel', 'logo': '', 'url': 'https://www.telegratishd.com/star-channel-en-vivo.html'},
            {'name': 'Cinemax', 'logo': '', 'url': 'https://www.telegratishd.com/cinemax-en-vivo.html'},
            {'name': 'Space', 'logo': '', 'url': 'https://www.telegratishd.com/space-en-vivo.html'},
            {'name': 'Syfy', 'logo': '', 'url': 'https://www.telegratishd.com/syfy-en-vivo.html'},
            {'name': 'Warner Channel', 'logo': '', 'url': 'https://www.telegratishd.com/warner-channel-en-vivo.html'},
            {'name': 'Cinecanal', 'logo': '', 'url': 'https://www.telegratishd.com/cinecanal-en-vivo.html'},
            {'name': 'FX', 'logo': '', 'url': 'https://www.telegratishd.com/fx-en-vivo.html'},
            {'name': 'AXN', 'logo': '', 'url': 'https://www.telegratishd.com/axn-en-vivo.html'},
            {'name': 'Paramount Channel', 'logo': '', 'url': 'https://www.telegratishd.com/paramount-channel-en-vivo.html'},
            {'name': 'AMC', 'logo': '', 'url': 'https://www.telegratishd.com/amc-en-vivo.html'},
            {'name': 'Studio Universal', 'logo': '', 'url': 'https://www.telegratishd.com/studio-universal-en-vivo.html'},
            {'name': 'MultiPremier', 'logo': '', 'url': 'https://www.telegratishd.com/multipremier-en-vivo.html'},
            {'name': 'Golden', 'logo': '', 'url': 'https://www.telegratishd.com/golden-en-vivo.html'},
            {'name': 'Golden Plus', 'logo': '', 'url': 'https://www.telegratishd.com/golden-plus-en-vivo.html'},
            {'name': 'Golden Edge', 'logo': '', 'url': 'https://www.telegratishd.com/golden-edge-en-vivo.html'},
            {'name': 'Golden Premier', 'logo': '', 'url': 'https://www.telegratishd.com/golden-premier-en-vivo.html'},
            {'name': 'Golden Premier 2', 'logo': '', 'url': 'https://www.telegratishd.com/golden-premier-2-en-vivo.html'},
            {'name': 'Canal Sony', 'logo': '', 'url': 'https://www.telegratishd.com/canal-sony-en-vivo.html'},
            {'name': 'A3Series', 'logo': '', 'url': 'https://www.telegratishd.com/a3series-en-vivo.html'},
            {'name': 'Comedy Central', 'logo': '', 'url': 'https://www.telegratishd.com/comedy-central-en-vivo.html'},
            {'name': 'Distrito Comedia', 'logo': '', 'url': 'https://www.telegratishd.com/distrito-comedia-en-vivo.html'},
            {'name': 'Lifetime', 'logo': '', 'url': 'https://www.telegratishd.com/lifetime-en-vivo.html'},
            {'name': 'El Gourmet', 'logo': '', 'url': 'https://www.telegratishd.com/el-gourmet-en-vivo.html'},
            {'name': 'Dragon Ball Super 24/7', 'logo': '', 'url': 'https://www.telegratishd.com/dragon-ball-super-24-7-en-vivo.html'},
            {'name': 'Chespirito 24/7', 'logo': '', 'url': 'https://www.telegratishd.com/chespirito-24-7-en-vivo.html'},
            {'name': 'Chapulin Colorado 24/7', 'logo': '', 'url': 'https://www.telegratishd.com/chapulin-colorado-24-7-en-vivo.html'}
        ]
        
        return self._extract_all_channels_from_site(channels, 'telegratishd')
    
    def _extract_all_channels_from_site(self, channels, source):
        """Extrae todos los canales de una página específica con nombres reales y logos"""
        print(f"   📺 Extrayendo {len(channels)} canales de {source}...")
        streams = []
        
        for i, channel in enumerate(channels, 1):
            print(f"   📡 Canal {i}/{len(channels)}: {channel['name']}")
            
            try:
                # Intentar extraer el stream de la página del canal
                content = self.make_request(channel['url'], use_proxy=False)
                
                if content:
                    # Buscar links de video en la página del canal
                    video_urls = self._extract_video_urls_from_content(content, channel['url'])
                    
                    if video_urls:
                        # Preferir URLs .m3u8 directos
                        best_url = None
                        for url in video_urls:
                            if '.m3u8' in url.lower():
                                best_url = url
                                break
                        
                        if not best_url:
                            best_url = video_urls[0]
                        
                        stream = {
                            'name': channel['name'],
                            'url': best_url,
                            'logo': channel.get('logo', ''),
                            'source': source
                        }
                        streams.append(stream)
                        
                        # Mostrar el tipo de stream encontrado
                        if '.m3u8' in best_url:
                            print(f"      ✅ Stream HLS (.m3u8) encontrado: {channel['name']}")
                        elif any(ext in best_url for ext in ['.mp4', '.ts']):
                            print(f"      ✅ Stream directo encontrado: {channel['name']}")
                        else:
                            print(f"      ⚠️ Stream embebido encontrado: {channel['name']}")
                    else:
                        print(f"      ❌ No se encontró stream para {channel['name']}")
                        # NO agregar como fallback - solo streams reales
                
                else:
                    print(f"      ❌ Error al acceder a {channel['name']}")
                    
            except Exception as e:
                print(f"      ❌ Error al procesar {channel['name']}: {str(e)}")
                
            # Pequeña pausa para no sobrecargar el servidor
            time.sleep(0.5)
        
        print(f"   ✅ Total de canales procesados: {len(streams)}")
        return streams
    
    def _extract_video_urls_from_content(self, content, base_url):
        """Extrae URLs de video del contenido HTML - VERSIÓN MEJORADA"""
        video_urls = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Buscar en scripts de JavaScript (donde suelen estar los links de streams)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Patrones más específicos para streams
                    stream_patterns = [
                        r'"(https?://[^"]*\.m3u8[^"]*)"',
                        r"'(https?://[^']*\.m3u8[^']*)'",
                        r'src[:\s]*["\']([^"\']*\.m3u8[^"\']*)["\']',
                        r'source[:\s]*["\']([^"\']*\.m3u8[^"\']*)["\']',
                        r'stream[:\s]*["\']([^"\']*\.m3u8[^"\']*)["\']',
                        r'hls[:\s]*["\']([^"\']*\.m3u8[^"\']*)["\']',
                        r'file[:\s]*["\']([^"\']*\.m3u8[^"\']*)["\']',
                        r'playlist[:\s]*["\']([^"\']*\.m3u8[^"\']*)["\']',
                    ]
                    
                    for pattern in stream_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        for match in matches:
                            if match.startswith('//'):
                                match = 'https:' + match
                            elif not match.startswith('http'):
                                match = base_url.rstrip('/') + '/' + match.lstrip('/')
                            video_urls.append(match)
            
            # 2. Buscar iframes (pueden contener players embebidos)
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = base_url.rstrip('/') + src
                    elif not src.startswith('http'):
                        src = base_url.rstrip('/') + '/' + src
                    
                    # Solo agregar si parece un iframe de video
                    if any(keyword in src.lower() for keyword in ['player', 'embed', 'stream', 'video', 'live']):
                        video_urls.append(src)
            
            # 3. Buscar en data attributes
            data_elements = soup.find_all(attrs={'data-src': True})
            data_elements.extend(soup.find_all(attrs={'data-stream': True}))
            data_elements.extend(soup.find_all(attrs={'data-file': True}))
            
            for element in data_elements:
                for attr in ['data-src', 'data-stream', 'data-file']:
                    src = element.get(attr)
                    if src and ('.m3u8' in src or '.ts' in src):
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif not src.startswith('http'):
                            src = base_url.rstrip('/') + '/' + src.lstrip('/')
                        video_urls.append(src)
            
            # 4. Buscar directamente en el HTML
            html_patterns = [
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+/playlist\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+/index\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+/live[^\s"\'<>]*\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+/stream[^\s"\'<>]*\.m3u8[^\s"\'<>]*'
            ]
            
            for pattern in html_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                video_urls.extend(matches)
            
            # 5. Buscar en elementos video y source
            video_elements = soup.find_all(['video', 'source'])
            for element in video_elements:
                src = element.get('src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = base_url.rstrip('/') + src
                    video_urls.append(src)
        
        except Exception as e:
            print(f"      ⚠️ Error al extraer URLs de video: {str(e)}")
        
        # Filtrar y limpiar URLs
        filtered_urls = []
        seen_urls = set()
        
        for url in video_urls:
            if url and url not in seen_urls:
                seen_urls.add(url)
                
                # Verificar que sea una URL válida de stream
                if any(ext in url.lower() for ext in ['.m3u8', '.ts', '.mp4', '.mkv', '.avi']):
                    # Priorizar .m3u8 (HLS streams)
                    if '.m3u8' in url.lower():
                        filtered_urls.insert(0, url)  # Agregar al inicio
                    else:
                        filtered_urls.append(url)
                elif any(keyword in url.lower() for keyword in ['player', 'embed', 'stream', 'video', 'live']) and 'http' in url:
                    # Agregar iframes de players al final como último recurso
                    filtered_urls.append(url)
        
        return filtered_urls[:5]  # Retornar máximo 5 URLs
    
    def verify_streams(self, m3u_file):
        """Verifica streams de un archivo M3U"""
        try:
            # Parsear archivo M3U
            streams, channel_names, _ = parse_m3u(m3u_file)
            if not streams:
                print("❌ No se encontraron streams en el archivo")
                return 0
            
            # Convertir a formato de diccionario
            stream_list = []
            for url, name in zip(streams, channel_names):
                if name is not None:
                    stream_list.append({'url': url, 'name': name})
            
            # Verificar streams
            results, offline_streams = check_streams_threaded(stream_list)
            
            # Contar streams online
            online_count = len(stream_list) - len(offline_streams)
            
            print(f"\n📊 Resumen de verificación de {m3u_file}:")
            print(f"✅ Streams online: {online_count}")
            print(f"❌ Streams offline: {len(offline_streams)}")
            print(f"📊 Total verificados: {len(stream_list)}")
            
            return online_count
            
        except Exception as e:
            print(f"❌ Error verificando streams: {e}")
            return 0
    
    def close_driver(self):
        """Cierra el WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def parse_m3u(file_path):
    """Parse an M3U file and extract stream URLs along with their channel names."""
    streams = []
    channel_names = []
    original_lines = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            original_lines = lines
            
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    # Extract channel name (tvg-name)
                    match = re.search(r'tvg-name="([^"]+)"', line)
                    if match:
                        channel_name = match.group(1)
                        # Ignore lines with tvg-name containing special characters
                        if not any(char in channel_name for char in ['✦●✦', '❌', '✅']):
                            channel_names.append(channel_name)
                        else:
                            channel_names.append(None)  # Add None for this stream to skip later
                    else:
                        # Si no hay tvg-name, buscar el nombre al final
                        parts = line.split(',')
                        if len(parts) > 1:
                            channel_names.append(parts[-1].strip())
                        else:
                            channel_names.append("Unknown Channel")
                elif line and not line.startswith("#"):
                    streams.append(line)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return [], [], []

    return streams, channel_names, original_lines

def check_stream_ffprobe(url):
    """Check if a stream is online using ffprobe."""
    try:
        command = [
            "ffprobe", 
            "-hide_banner", 
            "-loglevel", "error", 
            "-i", url
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if result.returncode == 0:
            return True  # Stream is online
        else:
            return False  # Stream is offline
    except subprocess.TimeoutExpired:
        return False  # Timeout indicates offline stream
    except Exception as e:
        print(f"Error checking stream {url}: {e}")
        return False

def check_stream_requests(url):
    """Verifica stream usando requests como alternativa a ffprobe"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code in [200, 206]  # 206 para contenido parcial
    except:
        return False

def generate_m3u_content(streams, title="IPTV Streams"):
    """Genera el contenido M3U a partir de una lista de streams"""
    content = f"#EXTM3U\n"
    
    # Mapeo de nombres de fuentes más amigables
    source_names = {
        'tvplusgratis2': 'TV Plus Gratis 2',
        'vertvcable': 'Vert V Cable',
        'cablevisionhd': 'Cable Vision HD',
        'telegratishd': 'Tele Gratis HD'
    }
    
    for i, stream in enumerate(streams, 1):
        name = stream.get('name', f'Canal {i}')
        url = stream.get('url', '')
        source = stream.get('source', 'unknown')
        
        # Limpiar caracteres especiales del nombre
        name = re.sub(r'[^\w\s-]', '', name).strip()
        if not name:
            name = f'Canal {i}'
        
        # Obtener nombre amigable de la fuente
        source_display = source_names.get(source, source.upper())
        
        # Agregar el nombre de la página al nombre del canal
        channel_name_with_source = f"{name} [{source_display}]"
        
        content += f'#EXTINF:-1 tvg-name="{name}" tvg-logo="" group-title="{source_display}",{channel_name_with_source}\n'
        content += f'{url}\n'
    
    return content

def save_m3u_file(content, filename):
    """Guarda el contenido M3U en un archivo"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo guardado: {filename}")
    except Exception as e:
        print(f"❌ Error guardando archivo {filename}: {e}")

def display_progress_bar(current, total, prefix="Progress"):
    """Display an animated progress bar."""
    bar_length = 40
    if total > 0:
        progress = int(bar_length * current / total)
        bar = f"[{'#' * progress}{'-' * (bar_length - progress)}]"
        percentage = int((current / total) * 100)
        sys.stdout.write(f"\r{prefix}: {bar} {current}/{total} ({percentage}%)")
        sys.stdout.flush()

def check_streams_threaded(streams, max_workers=10):
    """Verifica streams usando múltiples hilos"""
    results = {}
    offline_streams = []
    checked_count = 0
    
    def check_single_stream(stream_data):
        nonlocal checked_count
        url = stream_data['url']
        name = stream_data['name']
        
        # Intentar primero con requests, luego con ffprobe si está disponible
        is_online = check_stream_requests(url)
        if not is_online:
            is_online = check_stream_ffprobe(url)
        
        status = "Online" if is_online else f"Offline - {name} - {url}"
        
        with threading.Lock():
            results[url] = status
            if not is_online:
                offline_streams.append(status)
            checked_count += 1
            display_progress_bar(checked_count, len(streams), "🔍 Verificando streams")
        
        return is_online
    
    # Verificar streams en paralelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_stream = {executor.submit(check_single_stream, stream): stream for stream in streams}
        
        for future in as_completed(future_to_stream):
            try:
                future.result()
            except Exception as e:
                print(f"\n❌ Error verificando stream: {e}")
    
    print("\n")
    return results, offline_streams

def show_main_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("    🎬 IPTV EXTRACTOR Y VERIFICADOR AVANZADO 🎬")
    print("="*60)
    print("1. 📡 Extraer streams de páginas web")
    print("2. ✅ Verificar archivo M3U existente")
    print("3. 🚪 Salir")
    print("="*60)

def show_extraction_menu():
    """Muestra el menú de extracción"""
    print("\n" + "="*60)
    print("        🌐 SELECCIONAR PÁGINAS PARA EXTRAER")
    print("="*60)
    print("1. 📺 tvplusgratis2.com")
    print("2. 🎥 vertvcable.com")
    print("3. 📡 cablevisionhd.com")
    print("4. 🎬 telegratishd.com")
    print("5. 🌍 Todas las páginas")
    print("6. 🎯 Selección múltiple (ej: 1,2,4)")
    print("7. 🔥 ANÁLISIS PROFUNDO - Extraer streams directos")
    print("8. ⬅️  Volver al menú principal")
    print("="*60)

def show_verification_menu():
    """Muestra el menú de verificación"""
    print("\n" + "="*50)
    print("    🔍 ¿VERIFICAR STREAMS EXTRAÍDOS?")
    print("="*50)
    print("1. ✅ Sí, verificar todos los streams")
    print("2. 💾 No, guardar sin verificar")
    print("3. ❌ Cancelar")
    print("="*50)

def show_save_menu():
    """Muestra el menú de guardado"""
    print("\n" + "="*50)
    print("    💾 ¿CÓMO GUARDAR LOS STREAMS?")
    print("="*50)
    print("1. 📄 Archivo único combinado")
    print("2. 📁 Archivos separados por página")
    print("3. 📄📁 Ambos (combinado + separados)")
    print("4. ❌ No guardar")
    print("="*50)

def get_user_choice(max_option):
    """Obtiene la elección del usuario"""
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

def get_multiple_choice():
    """Obtiene múltiples opciones del usuario"""
    print("\n" + "="*50)
    print("    🎯 SELECCIÓN MÚLTIPLE")
    print("="*50)
    print("Ingresa los números separados por comas (ej: 1,2,4):")
    print("1=tvplusgratis2 | 2=vertvcable | 3=cablevisionhd | 4=telegratishd")
    print("="*50)
    
    while True:
        try:
            choices = input("👉 Opciones: ")
            choices = [int(x.strip()) for x in choices.split(',')]
            if all(1 <= choice <= 4 for choice in choices):
                return choices
            else:
                print("❌ Por favor, ingresa números entre 1 y 4")
        except ValueError:
            print("❌ Por favor, ingresa números válidos separados por comas")

def extract_streams_by_choice(extractor, choices):
    """Extrae streams según las opciones seleccionadas"""
    all_streams = []
    page_names = ["tvplusgratis2", "vertvcable", "cablevisionhd", "telegratishd"]
    
    for choice in choices:
        print(f"\n🔄 Procesando opción {choice}...")
        
        try:
            if choice == 1:
                streams = extractor.extract_tvplusgratis2()
            elif choice == 2:
                streams = extractor.extract_vertvcable()
            elif choice == 3:
                streams = extractor.extract_cablevisionhd()
            elif choice == 4:
                streams = extractor.extract_telegratishd()
            else:
                continue
                
            all_streams.extend(streams)
            print(f"✅ Extraídos {len(streams)} streams de {page_names[choice-1]}")
            
        except Exception as e:
            print(f"❌ Error extrayendo de {page_names[choice-1]}: {e}")
    
    return all_streams

def extract_direct_streams_from_channels():
    """Extrae streams directos de canales específicos conocidos"""
    
    # Canales encontrados en el análisis previo
    channels = [
        {
            'name': 'EL CANAL DEL FÚTBOL (ECDF)',
            'url': 'https://www.vertvcable.com/el-canal-del-futbol-ecdf-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'Canal 5 Linares',
            'url': 'https://www.vertvcable.com/canal-5-linares-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'Canal 2 Linares',
            'url': 'https://www.vertvcable.com/canal-2-linares-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'Telecanal',
            'url': 'https://www.vertvcable.com/telecanal-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'Canal Pais',
            'url': 'https://www.vertvcable.com/canal-pais-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'Canal De Deportes CRTV Chile',
            'url': 'https://www.vertvcable.com/canal-de-deportes-crtv-chile-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'HBO Family',
            'url': 'https://www.vertvcable.com/hbo-family-en-vivo/',
            'source': 'vertvcable'
        },
        {
            'name': 'CHV Deportes',
            'url': 'https://www.vertvcable.com/chv-deportes-en-vivo/',
            'source': 'vertvcable'
        }
    ]
    
    print("\n🔥 ANÁLISIS PROFUNDO - EXTRACCIÓN DE STREAMS DIRECTOS")
    print("="*70)
    print("🎯 Analizando páginas específicas de canales para extraer URLs directas")
    print("📺 Estos serán streams compatibles con SSIPTV y aplicaciones similares")
    print("="*70)
    
    # Crear extractor especial para streams directos
    extractor = IPTVExtractor()
    all_direct_streams = []
    
    print(f"\n📡 Procesando {len(channels)} canales específicos...\n")
    
    for i, channel in enumerate(channels, 1):
        print(f"🔍 Canal {i}/{len(channels)}: {channel['name']}")
        print(f"   📍 URL: {channel['url']}")
        
        try:
            # Extraer streams directos de esta página específica
            direct_streams = extract_direct_streams_from_page(extractor, channel['url'], channel['name'], channel['source'])
            
            if direct_streams:
                all_direct_streams.extend(direct_streams)
                print(f"   ✅ Encontrados {len(direct_streams)} streams directos")
                for j, stream in enumerate(direct_streams, 1):
                    print(f"      {j}. {stream['url'][:80]}...")
            else:
                print(f"   ❌ No se encontraron streams directos")
                
        except Exception as e:
            print(f"   ❌ Error procesando {channel['name']}: {e}")
        
        print()  # Línea en blanco para separar
        time.sleep(2)  # Pausa para no sobrecargar el servidor
    
    return all_direct_streams

def extract_direct_streams_from_page(extractor, page_url, channel_name, source):
    """Extrae streams directos de una página específica de canal"""
    streams = []
    
    # Patrones más específicos para streams directos
    direct_stream_patterns = [
        # M3U8 patterns
        r'["\']([^"\']*\.m3u8[^"\']*)["\']',
        r'["\']([^"\']*m3u8[^"\']*)["\']',
        
        # HLS patterns
        r'hls\.loadSource\(["\']([^"\']+)["\']',
        r'source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        r'file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        r'src\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        
        # Player patterns
        r'player\.src\(["\']([^"\']*\.m3u8[^"\']*)["\']',
        r'jwplayer.*?file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        
        # Video source patterns
        r'video\.src\s*=\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
        r'setAttribute\(["\']src["\'],\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
    ]
    
    # Método 1: Petición con CloudScraper
    content = extractor.make_request(page_url, use_cloudscraper=True)
    if content:
        print(f"      📄 Analizando contenido HTML...")
        
        # Buscar streams directos en el contenido
        for pattern in direct_stream_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if is_valid_direct_stream(match):
                    if not match.startswith('http'):
                        match = urljoin(page_url, match)
                    streams.append({
                        'name': channel_name,
                        'url': match,
                        'source': source,
                        'type': 'direct'
                    })
        
        # Buscar iframes y analizarlos recursivamente
        soup = BeautifulSoup(content, 'html.parser')
        iframes = soup.find_all('iframe')
        
        for iframe in iframes:
            iframe_src = iframe.get('src')
            if iframe_src:
                if not iframe_src.startswith('http'):
                    iframe_src = urljoin(page_url, iframe_src)
                
                # Evitar iframes de publicidad
                if not any(skip in iframe_src.lower() for skip in ['ads', 'google', 'facebook', 'twitter']):
                    print(f"      🖼️  Analizando iframe: {iframe_src[:50]}...")
                    iframe_streams = extract_iframe_direct_streams(extractor, iframe_src, channel_name, source)
                    streams.extend(iframe_streams)
    
    # Método 2: Con Selenium si no encontramos nada
    if not streams:
        print(f"      🤖 Intentando con Selenium...")
        selenium_content = extractor.make_request(page_url, use_selenium=True)
        if selenium_content:
            for pattern in direct_stream_patterns:
                matches = re.findall(pattern, selenium_content, re.IGNORECASE)
                for match in matches:
                    if is_valid_direct_stream(match):
                        if not match.startswith('http'):
                            match = urljoin(page_url, match)
                        streams.append({
                            'name': channel_name,
                            'url': match,
                            'source': source,
                            'type': 'direct'
                        })
    
    # Eliminar duplicados
    seen_urls = set()
    unique_streams = []
    for stream in streams:
        if stream['url'] not in seen_urls:
            seen_urls.add(stream['url'])
            unique_streams.append(stream)
    
    return unique_streams

def extract_iframe_direct_streams(extractor, iframe_url, channel_name, source):
    """Extrae streams directos de un iframe"""
    streams = []
    
    try:
        iframe_content = extractor.make_request(iframe_url, use_cloudscraper=True)
        if iframe_content:
            # Patrones específicos para iframes
            iframe_patterns = [
                r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            ]
            
            for pattern in iframe_patterns:
                matches = re.findall(pattern, iframe_content, re.IGNORECASE)
                for match in matches:
                    if is_valid_direct_stream(match):
                        if not match.startswith('http'):
                            match = urljoin(iframe_url, match)
                        streams.append({
                            'name': channel_name,
                            'url': match,
                            'source': source,
                            'type': 'iframe'
                        })
    except:
        pass
    
    return streams

def is_valid_direct_stream(url):
    """Verifica si una URL es un stream directo válido"""
    if not url or len(url) < 10:
        return False
    
    # Debe contener .m3u8 o ser un stream válido
    if '.m3u8' not in url.lower():
        return False
    
    # No debe ser imagen, CSS, JS, etc.
    exclude_extensions = ['.jpg', '.png', '.gif', '.css', '.js', '.ico', '.svg', '.woff', '.ttf']
    if any(ext in url.lower() for ext in exclude_extensions):
        return False
    
    return True

def main():
    extractor = None
    
    try:
        while True:
            show_main_menu()
            main_choice = get_user_choice(3)
            
            if main_choice == 1:
                # Extraer streams
                if extractor is None:
                    print("\n🔧 Inicializando extractor...")
                    extractor = IPTVExtractor()
                
                while True:
                    show_extraction_menu()
                    extract_choice = get_user_choice(8)
                    
                    if extract_choice == 8:
                        break
                    
                    if extract_choice == 7:
                        # Análisis profundo - extraer streams directos
                        print("\n🔥 INICIANDO ANÁLISIS PROFUNDO...")
                        
                        direct_streams = extract_direct_streams_from_channels()
                        
                        if direct_streams:
                            print(f"\n🎉 ¡Análisis completado!")
                            print(f"✅ Se encontraron {len(direct_streams)} streams directos")
                            
                            # Generar archivo M3U con streams directos
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            m3u_filename = f"iptv_direct_streams_{timestamp}.m3u"
                            
                            with open(m3u_filename, 'w', encoding='utf-8') as f:
                                f.write("#EXTM3U\n\n")
                                
                                # Mapeo de nombres de fuentes más amigables
                                source_names = {
                                    'vertvcable': 'Vert V Cable',
                                    'tvplusgratis2': 'TV Plus Gratis 2',
                                    'cablevisionhd': 'Cable Vision HD',
                                    'telegratishd': 'Tele Gratis HD'
                                }
                                
                                for stream in direct_streams:
                                    source_display = source_names.get(stream['source'], stream['source'].upper())
                                    channel_name_with_source = f"{stream['name']} [{source_display}]"
                                    
                                    # Generar entrada M3U
                                    f.write(f"#EXTINF:-1 group-title=\"{source_display}\",{channel_name_with_source}\n")
                                    f.write(f"{stream['url']}\n\n")
                            
                            print(f"📁 Archivo generado: {m3u_filename}")
                            print("\n📺 Streams directos encontrados:")
                            for i, stream in enumerate(direct_streams, 1):
                                print(f"   {i}. {stream['name']} ({stream['type']})")
                                print(f"      🔗 {stream['url'][:80]}...")
                            
                            # Preguntar si verificar los streams
                            print(f"\n🔍 ¿Deseas verificar estos {len(direct_streams)} streams directos? (s/n): ", end="")
                            verify = input().lower().strip()
                            
                            if verify in ['s', 'si', 'sí', 'y', 'yes']:
                                print("\n🔍 Verificando streams directos...")
                                verified_count = extractor.verify_streams(m3u_filename)
                                print(f"✅ Verificación completada. {verified_count} streams verificados.")
                            
                        else:
                            print("\n❌ No se encontraron streams directos.")
                            print("💡 Esto puede deberse a:")
                            print("   • Protecciones anti-bot más avanzadas")
                            print("   • Cambios en la estructura de las páginas")
                            print("   • Streams dinámicos que requieren JavaScript")
                        
                        input("\n📱 Presiona ENTER para continuar...")
                        continue
                    
                    print(f"\n🚀 Iniciando extracción...")
                    
                    if extract_choice == 1:
                        all_streams = extract_streams_by_choice(extractor, [1])
                    elif extract_choice == 2:
                        all_streams = extract_streams_by_choice(extractor, [2])
                    elif extract_choice == 3:
                        all_streams = extract_streams_by_choice(extractor, [3])
                    elif extract_choice == 4:
                        all_streams = extract_streams_by_choice(extractor, [4])
                    elif extract_choice == 5:
                        all_streams = extract_streams_by_choice(extractor, [1, 2, 3, 4])
                    elif extract_choice == 6:
                        choices = get_multiple_choice()
                        all_streams = extract_streams_by_choice(extractor, choices)
                    
                    if not all_streams:
                        print("❌ No se encontraron streams válidos")
                        continue
                    
                    print(f"\n🎉 Total de streams extraídos: {len(all_streams)}")
                    
                    # Mostrar algunos ejemplos
                    print("\n📋 Ejemplos de streams encontrados:")
                    for i, stream in enumerate(all_streams[:3]):
                        print(f"  {i+1}. {stream['name']} - {stream['source']}")
                        print(f"     URL: {stream['url'][:60]}...")
                    
                    if len(all_streams) > 3:
                        print(f"  ... y {len(all_streams) - 3} más")
                    
                    # Verificar streams
                    show_verification_menu()
                    verify_choice = get_user_choice(3)
                    
                    if verify_choice == 1:
                        print("\n🔍 Verificando streams (esto puede tomar tiempo)...")
                        results, offline_streams = check_streams_threaded(all_streams)
                        
                        # Filtrar streams online
                        online_streams = [s for s in all_streams if results.get(s['url'], '').startswith('Online')]
                        
                        print(f"\n📊 Resumen de verificación:")
                        print(f"✅ Streams online: {len(online_streams)}")
                        print(f"❌ Streams offline: {len(offline_streams)}")
                        print(f"📊 Total verificados: {len(all_streams)}")
                        
                        if offline_streams and len(offline_streams) <= 10:
                            print(f"\n❌ Streams offline encontrados:")
                            for i, offline in enumerate(offline_streams[:10]):
                                print(f"  {i+1}. {offline}")
                        elif len(offline_streams) > 10:
                            print(f"\n❌ Se encontraron {len(offline_streams)} streams offline (demasiados para mostrar)")
                        
                        all_streams = online_streams
                        
                    elif verify_choice == 3:
                        continue
                    
                    if not all_streams:
                        print("❌ No hay streams válidos para guardar")
                        continue
                    
                    # Guardar archivos
                    show_save_menu()
                    save_choice = get_user_choice(4)
                    
                    if save_choice == 1:
                        # Archivo único
                        filename = "iptv_combined.m3u"
                        content = generate_m3u_content(all_streams, "IPTV Combined")
                        save_m3u_file(content, filename)
                        
                    elif save_choice == 2:
                        # Archivos separados
                        source_names = {
                            'tvplusgratis2': 'TV_Plus_Gratis_2',
                            'vertvcable': 'Vert_V_Cable',
                            'cablevisionhd': 'Cable_Vision_HD',
                            'telegratishd': 'Tele_Gratis_HD'
                        }
                        
                        sources = set(s['source'] for s in all_streams)
                        for source in sources:
                            source_streams = [s for s in all_streams if s['source'] == source]
                            safe_source_name = source_names.get(source, source)
                            filename = f"iptv_{safe_source_name}.m3u"
                            content = generate_m3u_content(source_streams, f"IPTV {source.upper()}")
                            save_m3u_file(content, filename)
                            
                    elif save_choice == 3:
                        # Ambos
                        filename = "iptv_combined.m3u"
                        content = generate_m3u_content(all_streams, "IPTV Combined")
                        save_m3u_file(content, filename)
                        
                        source_names = {
                            'tvplusgratis2': 'TV_Plus_Gratis_2',
                            'vertvcable': 'Vert_V_Cable',
                            'cablevisionhd': 'Cable_Vision_HD',
                            'telegratishd': 'Tele_Gratis_HD'
                        }
                        
                        sources = set(s['source'] for s in all_streams)
                        for source in sources:
                            source_streams = [s for s in all_streams if s['source'] == source]
                            safe_source_name = source_names.get(source, source)
                            filename = f"iptv_{safe_source_name}.m3u"
                            content = generate_m3u_content(source_streams, f"IPTV {source.upper()}")
                            save_m3u_file(content, filename)
                    
                    print("\n🎉 Proceso completado exitosamente!")
                    break
            
            elif main_choice == 2:
                # Verificar archivo M3U
                filename = input("\n📁 Ingresa el nombre del archivo M3U: ")
                if not os.path.exists(filename):
                    print(f"❌ Archivo '{filename}' no encontrado")
                    continue
                
                print(f"🔍 Verificando streams en '{filename}'...")
                
                # Parsear archivo M3U
                streams, channel_names, original_lines = parse_m3u(filename)
                if not streams:
                    print("❌ No se encontraron streams en el archivo")
                    continue
                
                # Convertir a formato de diccionario
                stream_list = []
                for url, name in zip(streams, channel_names):
                    if name is not None:  # Skip streams with special characters
                        stream_list.append({'url': url, 'name': name})
                
                # Verificar streams
                results, offline_streams = check_streams_threaded(stream_list)
                
                # Mostrar resumen
                online_count = len(stream_list) - len(offline_streams)
                print(f"\n📊 Resumen de verificación:")
                print(f"✅ Streams online: {online_count}")
                print(f"❌ Streams offline: {len(offline_streams)}")
                print(f"📊 Total verificados: {len(stream_list)}")
                
                if offline_streams:
                    print(f"\n❌ Streams offline encontrados:")
                    for i, offline in enumerate(offline_streams[:10]):  # Mostrar solo los primeros 10
                        print(f"  {i+1}. {offline}")
                    if len(offline_streams) > 10:
                        print(f"  ... y {len(offline_streams) - 10} más")
            
            elif main_choice == 3:
                print("\n👋 ¡Gracias por usar IPTV Extractor Avanzado!")
                break
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        # Limpiar recursos
        if extractor:
            extractor.close_driver()
        print("🧹 Limpieza completada")

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import requests
        import bs4
        print("✅ Dependencias básicas encontradas")
    except ImportError as e:
        print(f"❌ Faltan dependencias: {e}")
        print("📦 Instala con: pip install requests beautifulsoup4 lxml")
        sys.exit(1)
    
    try:
        import selenium
        print("✅ Selenium encontrado")
    except ImportError:
        print("⚠️  Selenium no encontrado. Algunas funciones avanzadas no estarán disponibles")
        print("📦 Instala con: pip install selenium")
    
    try:
        import cloudscraper
        print("✅ CloudScraper encontrado")
    except ImportError:
        print("⚠️  CloudScraper no encontrado. Protección anti-CloudFlare limitada")
        print("📦 Instala con: pip install cloudscraper")
    
    main()
