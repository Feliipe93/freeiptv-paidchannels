#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor IPTV Completo con Técnicas Anti-Detección para TODOS los Sitios
Aplicando todas las técnicas de los extractores de series a IPTV
"""

import asyncio
import os
import sys
import time
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import random
import cloudscraper

# Intentar importar Playwright para técnicas avanzadas
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright no disponible. Instalando...")
    os.system("pip install playwright beautifulsoup4 requests lxml cloudscraper")
    if PLAYWRIGHT_AVAILABLE:
        os.system("playwright install chromium")

class AdvancedIPTVExtractor:
    """Extractor IPTV con técnicas anti-detección y extracción avanzada"""
    
    def __init__(self):
        # Configurar CloudScraper para bypass de Cloudflare
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Session requests normal como backup
        self.session = requests.Session()
        
        # Headers rotativos para evitar detección
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Patrones avanzados de video mejorados
        self.video_patterns = [
            # Patrones HLS prioritarios
            r'https?://[^"\']*master\.m3u8[^"\']*',
            r'https?://[^"\']*playlist\.m3u8[^"\']*',
            r'https?://[^"\']*index\.m3u8[^"\']*',
            r'https?://cdn\d*\.videok\.pro/[^"\']*\.m3u8[^"\']*',
            r'https?://[^"\']*\.m3u8[^"\']*',
            # Servicios de streaming conocidos
            r'https?://[^"\']*doodstream[^"\']*',
            r'https?://[^"\']*streamtape[^"\']*',
            r'https?://[^"\']*vidmoly[^"\']*',
            r'https?://[^"\']*okru[^"\']*',
            r'https?://[^"\']*hlswish[^"\']*',
            r'https?://[^"\']*streamhide[^"\']*',
            r'https?://[^"\']*embed[^"\']*'
        ]
        
        # Configuración específica por sitio
        self.site_configs = {
            "tvplusgratis2.com": {
                "base_url": "https://tvplusgratis2.com",
                "url_format": "{base_url}/{channel_name}-en-vivo.html",
                "channel_selectors": [
                    'a[href*="-en-vivo.html"]',
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    '.channel-link',
                    '.canal-link'
                ],
                "anti_block": True,
                "requires_js": True
            },
            "telegratishd.com": {
                "base_url": "https://telegratishd.com", 
                "url_format": "{base_url}/{channel_name}-en-vivo.html",
                "channel_selectors": [
                    'a[href*="-en-vivo.html"]',
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    '.channel-item a',
                    '.canal-item a'
                ],
                "anti_block": True,
                "requires_js": True
            },
            "vertvcable.com": {
                "base_url": "https://vertvcable.com",
                "url_format": "{base_url}/{channel_name}",
                "channel_selectors": [
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    'a[href*="/live/"]',
                    '.channel-link',
                    '.tv-channel a'
                ],
                "anti_block": True,
                "requires_js": False
            },
            "cablevisionhd.com": {
                "base_url": "https://cablevisionhd.com",
                "url_format": "{base_url}/{channel_name}",
                "channel_selectors": [
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    'a[href*="/watch/"]',
                    '.channel-list a',
                    '.tv-list a'
                ],
                "anti_block": True,
                "requires_js": False
            }
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Sistema de logging con colores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "DEBUG": "\033[95m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {level}: {message}{colors['RESET']}")
    
    def get_random_headers(self, referer=None):
        """Generar headers aleatorios para evitar detección"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['es-ES,es;q=0.9,en;q=0.8', 'en-US,en;q=0.9', 'es-MX,es;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        if referer:
            headers['Referer'] = referer
        
        return headers
    
    def safe_request(self, url, site_config, timeout=30):
        """Realizar request seguro con técnicas anti-detección"""
        headers = self.get_random_headers()
        
        # Pausa aleatoria para evitar rate limiting
        time.sleep(random.uniform(1, 3))
        
        try:
            # Intentar con CloudScraper primero (mejor para Cloudflare)
            if site_config.get("anti_block", False):
                self.log(f"Usando CloudScraper para {url[:50]}...", "DEBUG")
                response = self.scraper.get(url, headers=headers, timeout=timeout)
            else:
                self.log(f"Usando requests normal para {url[:50]}...", "DEBUG")
                response = self.session.get(url, headers=headers, timeout=timeout)
            
            response.raise_for_status()
            return response
            
        except Exception as e:
            self.log(f"Error en request: {e}", "WARNING")
            # Retry con método alternativo
            try:
                if site_config.get("anti_block", False):
                    response = self.session.get(url, headers=headers, timeout=timeout)
                else:
                    response = self.scraper.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except Exception as e2:
                self.log(f"Error en retry: {e2}", "ERROR")
                return None
    
    def extract_channels_from_main_page(self, site_name, site_config):
        """Extraer lista de canales de la página principal usando múltiples técnicas"""
        self.log(f"🕷️ Extrayendo canales de {site_name}")
        
        base_url = site_config["base_url"]
        response = self.safe_request(base_url, site_config)
        
        if not response:
            self.log(f"❌ No se pudo acceder a {site_name}", "ERROR")
            return []
        
        self.log(f"✅ Página principal cargada ({len(response.content)} bytes)")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        channels = []
        
        # Método 1: Usar selectores específicos del sitio
        for selector in site_config["channel_selectors"]:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text:
                        full_url = urljoin(base_url, href)
                        
                        # Limpiar nombre del canal
                        clean_name = self.clean_channel_name(text)
                        
                        if clean_name and len(clean_name) > 2:
                            channels.append({
                                'name': clean_name,
                                'url': full_url,
                                'selector_used': selector
                            })
                
                self.log(f"Selector {selector}: {len([c for c in channels if c.get('selector_used') == selector])} canales")
                
            except Exception as e:
                self.log(f"Error con selector {selector}: {e}", "WARNING")
                continue
        
        # Método 2: Búsqueda por patrones de texto
        text_patterns = [
            r'ver\s+(\w+(?:\s+\w+)*)\s+en\s+vivo',
            r'canal\s+(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+online',
            r'(\w+(?:\s+\w+)*)\s+gratis',
            r'(\w+(?:\s+\w+)*)\s+hd'
        ]
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            text = link.get_text(strip=True).lower()
            href = link.get('href')
            
            for pattern in text_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and href:
                    channel_name = match.group(1).strip()
                    clean_name = self.clean_channel_name(channel_name)
                    
                    if clean_name and len(clean_name) > 2:
                        full_url = urljoin(base_url, href)
                        
                        # Evitar duplicados
                        if not any(c['name'].lower() == clean_name.lower() for c in channels):
                            channels.append({
                                'name': clean_name,
                                'url': full_url,
                                'selector_used': 'text_pattern'
                            })
        
        # Método 3: Búsqueda por palabras clave de canales de TV
        tv_keywords = [
            'espn', 'fox', 'cnn', 'discovery', 'history', 'nat geo', 'national geographic',
            'disney', 'cartoon', 'nickelodeon', 'mtv', 'vh1', 'comedy', 'fx', 'tnt',
            'hbo', 'showtime', 'starz', 'cinemax', 'univision', 'telemundo', 'caracol',
            'rcn', 'teleantioquia', 'win', 'canal', 'telecafe', 'telepacifico'
        ]
        
        for link in all_links:
            text = link.get_text(strip=True).lower()
            href = link.get('href')
            
            if any(keyword in text for keyword in tv_keywords) and href:
                clean_name = self.clean_channel_name(text)
                
                if clean_name and len(clean_name) > 2:
                    full_url = urljoin(base_url, href)
                    
                    # Evitar duplicados
                    if not any(c['name'].lower() == clean_name.lower() for c in channels):
                        channels.append({
                            'name': clean_name,
                            'url': full_url,
                            'selector_used': 'keyword_search'
                        })
        
        # Remover duplicados y limpiar
        unique_channels = []
        seen_names = set()
        
        for channel in channels:
            name_key = channel['name'].lower().strip()
            if name_key not in seen_names and len(name_key) > 2:
                seen_names.add(name_key)
                unique_channels.append(channel)
        
        self.log(f"🎯 Total canales únicos encontrados en {site_name}: {len(unique_channels)}")
        return unique_channels[:100]  # Limitar a 100 canales por sitio para prueba
    
    def clean_channel_name(self, name):
        """Limpiar nombre de canal"""
        if not name:
            return ""
        
        # Remover prefijos comunes
        name = re.sub(r'^(ver\s+|canal\s+|watch\s+)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(en\s+vivo|online|gratis|hd|live)$', '', name, flags=re.IGNORECASE)
        
        # Limpiar caracteres especiales
        name = re.sub(r'[^\w\s\-]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name.title()
    
    async def extract_video_urls_with_playwright(self, channel_url, site_config):
        """Extraer URLs de video usando Playwright para sitios con JavaScript"""
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        self.log(f"🎭 Usando Playwright para {channel_url[:50]}...")
        
        async with async_playwright() as p:
            # Configurar navegador con anti-detección
            browser = await p.chromium.launch(
                headless=True,  # Cambiar a False para debugging
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--ignore-certificate-errors',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images'  # Acelerar carga
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=random.choice(self.user_agents),
                ignore_https_errors=True
            )
            
            page = await context.new_page()
            
            # Lista para capturar URLs de video
            video_urls = []
            
            # Interceptar respuestas de red
            async def handle_response(response):
                url = response.url
                
                # Ignorar imágenes
                if any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico']):
                    return
                
                # Buscar patrones de video
                for pattern in self.video_patterns:
                    if re.search(pattern, url, re.IGNORECASE):
                        self.log(f"🎥 Video URL detectada: {url[:80]}...", "SUCCESS")
                        video_urls.append(url)
                        return
                
                # Buscar palabras clave
                if any(keyword in url.lower() for keyword in ['m3u8', 'stream', 'video', 'live', 'hls']):
                    self.log(f"🎥 Posible video URL: {url[:80]}...", "DEBUG")
                    video_urls.append(url)
            
            page.on('response', handle_response)
            
            try:
                # Navegar a la página
                await page.goto(channel_url, wait_until='networkidle', timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Buscar y hacer clic en botones de reproducción
                play_selectors = [
                    'button[class*="play"]',
                    '.play-button',
                    '.btn-play', 
                    'button[aria-label*="play"]',
                    '.video-play-button',
                    '[onclick*="play"]',
                    '.player-button',
                    'button',
                    '[id*="play"]',
                    '[class*="button"]'
                ]
                
                for selector in play_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements[:3]:  # Probar solo los primeros 3
                            try:
                                if await element.is_visible():
                                    await element.click(timeout=10000)
                                    await page.wait_for_timeout(8000)
                                    self.log(f"Click en elemento: {selector}", "DEBUG")
                                    
                                    if video_urls:
                                        break
                            except:
                                continue
                        
                        if video_urls:
                            break
                            
                    except:
                        continue
                
                # Buscar iframes (reproductores externos)
                iframes = await page.query_selector_all('iframe')
                for iframe in iframes:
                    try:
                        src = await iframe.get_attribute('src')
                        if src and any(service in src.lower() for service in ['dood', 'videok', 'stream', 'player', 'embed']):
                            video_urls.append(src)
                            self.log(f"🎥 Iframe encontrado: {src[:80]}...", "SUCCESS")
                    except:
                        continue
                
                # Esperar más tiempo para cargas dinámicas
                await page.wait_for_timeout(10000)
                
                await browser.close()
                return video_urls
                
            except Exception as e:
                self.log(f"Error en Playwright: {e}", "ERROR")
                await browser.close()
                return []
    
    def extract_video_urls_basic(self, channel_url, site_config):
        """Extraer URLs de video usando métodos básicos"""
        response = self.safe_request(channel_url, site_config)
        
        if not response:
            return []
        
        content = response.text
        video_urls = []
        
        # Aplicar todos los patrones de video
        for pattern in self.video_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            video_urls.extend(matches)
        
        # Buscar en JavaScript
        js_patterns = [
            r'["\']https?://[^"\']*\.m3u8[^"\']*["\']',
            r'source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'src\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                clean_url = match.strip('\'"')
                if clean_url.startswith('http'):
                    video_urls.append(clean_url)
        
        # Buscar iframes
        soup = BeautifulSoup(content, 'html.parser')
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if src and any(service in src.lower() for service in ['stream', 'player', 'embed', 'dood', 'videok']):
                video_urls.append(src)
        
        return list(set(video_urls))  # Remover duplicados
    
    async def process_channel(self, channel, site_config):
        """Procesar un canal individual para extraer streams"""
        channel_name = channel['name']
        channel_url = channel['url']
        
        self.log(f"🔍 Procesando: {channel_name}")
        
        try:
            # Intentar con Playwright si está disponible y el sitio lo requiere
            if PLAYWRIGHT_AVAILABLE and site_config.get("requires_js", False):
                video_urls = await self.extract_video_urls_with_playwright(channel_url, site_config)
            else:
                video_urls = self.extract_video_urls_basic(channel_url, site_config)
            
            if video_urls:
                # Priorizar URLs master.m3u8
                priority_urls = [url for url in video_urls if 'master.m3u8' in url.lower()]
                regular_urls = [url for url in video_urls if 'master.m3u8' not in url.lower()]
                
                best_url = priority_urls[0] if priority_urls else (regular_urls[0] if regular_urls else None)
                
                if best_url:
                    self.log(f"✅ Stream encontrado para {channel_name}: {best_url[:60]}...", "SUCCESS")
                    return {
                        'name': channel_name,
                        'url': best_url,
                        'source': urlparse(channel_url).netloc,
                        'original_page': channel_url,
                        'all_urls': video_urls[:3]
                    }
            
            self.log(f"❌ No se encontraron streams para {channel_name}", "WARNING")
            return None
            
        except Exception as e:
            self.log(f"❌ Error procesando {channel_name}: {e}", "ERROR")
            return None
    
    async def extract_site_completely(self, site_name):
        """Extraer completamente un sitio usando todas las técnicas"""
        self.log(f"🚀 Extracción completa de {site_name.upper()}")
        
        site_config = self.site_configs.get(site_name)
        if not site_config:
            self.log(f"❌ Configuración no encontrada para {site_name}", "ERROR")
            return []
        
        # Paso 1: Extraer lista de canales
        channels = self.extract_channels_from_main_page(site_name, site_config)
        
        if not channels:
            self.log(f"❌ No se encontraron canales en {site_name}", "ERROR")
            return []
        
        self.log(f"📋 {len(channels)} canales encontrados en {site_name}")
        
        # Paso 2: Procesar canales para extraer streams
        working_channels = []
        
        # Procesar en lotes para evitar sobrecarga
        batch_size = 5
        for i in range(0, len(channels), batch_size):
            batch = channels[i:i+batch_size]
            self.log(f"🔄 Procesando lote {i//batch_size + 1}/{(len(channels) + batch_size - 1)//batch_size}")
            
            # Procesar batch
            for channel in batch:
                result = await self.process_channel(channel, site_config)
                if result:
                    working_channels.append(result)
                
                # Pausa entre canales
                await asyncio.sleep(2)
            
            # Pausa entre lotes
            await asyncio.sleep(5)
        
        self.log(f"🎉 {len(working_channels)} canales con streams extraídos de {site_name}")
        return working_channels
    
    def generate_m3u(self, all_channels, filename="iptv_complete_extraction"):
        """Generar archivo M3U con todos los canales extraídos"""
        if not all_channels:
            self.log("❌ No hay canales para generar M3U", "ERROR")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}.m3u"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                
                for channel in all_channels:
                    # Limpiar nombre para M3U
                    clean_name = re.sub(r'[^\w\s\-]', '', channel['name']).strip()
                    source_name = channel.get('source', 'Unknown')
                    
                    # Formato para Smart TV/SSIPTV
                    title = f"{clean_name} [{source_name}]"
                    group_title = "IPTV Live"
                    
                    f.write(f'#EXTINF:-1 tvg-logo="" group-title="{group_title}",{title}\n')
                    f.write(f'{channel["url"]}\n')
            
            self.log(f"✅ M3U generado: {filename} ({len(all_channels)} canales)", "SUCCESS")
            return filename
            
        except Exception as e:
            self.log(f"❌ Error generando M3U: {e}", "ERROR")
            return None

async def main():
    """Función principal para extracción completa"""
    print("🔥 EXTRACTOR IPTV COMPLETO - TODAS LAS TÉCNICAS ANTI-DETECCIÓN")
    print("=" * 80)
    
    extractor = AdvancedIPTVExtractor()
    
    print("\nOpciones:")
    print("1. Extraer TODOS los sitios (Recomendado)")
    print("2. Extraer un sitio específico")
    print("3. Modo debug - probar técnicas en un canal")
    
    choice = input("\nSeleccione opción (1-3): ").strip()
    
    if choice == "1":
        # Extraer todos los sitios
        extractor.log("🌍 Iniciando extracción completa de TODOS los sitios")
        
        all_channels = []
        sites = list(extractor.site_configs.keys())
        
        for site_name in sites:
            try:
                extractor.log(f"🌐 Procesando {site_name.upper()}")
                site_channels = await extractor.extract_site_completely(site_name)
                all_channels.extend(site_channels)
                
                extractor.log(f"✅ {site_name}: {len(site_channels)} canales extraídos")
                
                # Pausa entre sitios
                await asyncio.sleep(10)
                
            except Exception as e:
                extractor.log(f"❌ Error en {site_name}: {e}", "ERROR")
                continue
        
        if all_channels:
            extractor.log(f"🎊 EXTRACCIÓN COMPLETADA: {len(all_channels)} canales totales")
            
            # Generar M3U
            m3u_file = extractor.generate_m3u(all_channels)
            if m3u_file:
                print(f"\n🎯 RESULTADO FINAL:")
                print(f"   📺 Total canales: {len(all_channels)}")
                print(f"   📄 Archivo M3U: {m3u_file}")
                
                # Mostrar resumen por sitio
                by_site = {}
                for channel in all_channels:
                    site = channel.get('source', 'Unknown')
                    by_site[site] = by_site.get(site, 0) + 1
                
                print(f"\n📊 CANALES POR SITIO:")
                for site, count in by_site.items():
                    print(f"   🌐 {site}: {count} canales")
        else:
            extractor.log("❌ No se pudieron extraer canales", "ERROR")
    
    elif choice == "2":
        # Extraer sitio específico
        sites = list(extractor.site_configs.keys())
        print(f"\nSitios disponibles:")
        for i, site in enumerate(sites, 1):
            print(f"{i}. {site}")
        
        try:
            site_choice = int(input(f"\nSeleccione sitio (1-{len(sites)}): ")) - 1
            if 0 <= site_choice < len(sites):
                site_name = sites[site_choice]
                
                extractor.log(f"🎯 Extrayendo {site_name.upper()}")
                channels = await extractor.extract_site_completely(site_name)
                
                if channels:
                    m3u_file = extractor.generate_m3u(channels, f"iptv_{site_name}")
                    if m3u_file:
                        print(f"\n✅ Extracción completada:")
                        print(f"   📺 Canales: {len(channels)}")
                        print(f"   📄 Archivo: {m3u_file}")
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Entrada inválida")
    
    elif choice == "3":
        # Modo debug
        test_url = input("\nIngrese URL de canal para probar: ").strip()
        if test_url:
            site_name = urlparse(test_url).netloc
            site_config = None
            
            # Buscar configuración del sitio
            for name, config in extractor.site_configs.items():
                if name in site_name:
                    site_config = config
                    break
            
            if not site_config:
                site_config = {"anti_block": True, "requires_js": True}
            
            extractor.log(f"🧪 Probando extracción en: {test_url}")
            
            # Probar ambos métodos
            if PLAYWRIGHT_AVAILABLE:
                urls_pw = await extractor.extract_video_urls_with_playwright(test_url, site_config)
                print(f"\n🎭 Playwright encontró {len(urls_pw)} URLs:")
                for url in urls_pw[:5]:
                    print(f"   🎥 {url}")
            
            urls_basic = extractor.extract_video_urls_basic(test_url, site_config)
            print(f"\n🔧 Método básico encontró {len(urls_basic)} URLs:")
            for url in urls_basic[:5]:
                print(f"   🎥 {url}")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    asyncio.run(main())
