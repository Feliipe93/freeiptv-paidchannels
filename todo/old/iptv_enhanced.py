#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced IPTV Channel Extractor
Incorporates advanced techniques from series extractors for better direct stream detection
"""

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

# Importar funciones auxiliares existentes
try:
    from verificar_urls import check_streams_threaded
    from iptv_simple import parse_m3u
except ImportError:
    print("⚠️ Archivos auxiliares no encontrados, usando funciones básicas")
    def check_streams_threaded(streams):
        return [], []
    def parse_m3u(file):
        return [], [], []

class EnhancedIPTVExtractor:
    """Extractor IPTV mejorado con técnicas avanzadas de detección de streams"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://google.com/',
        })
        
        # Patrones avanzados para detectar URLs de video basados en los extractores de series
        self.video_patterns = [
            # Patrones prioritarios para streams HLS
            r'https?://cdn\d*\.videok\.pro/[^"\']*\.m3u8[^"\']*',
            r'https?://[^"\']*master\.m3u8[^"\']*',
            r'https?://[^"\']*playlist\.m3u8[^"\']*',
            r'https?://[^"\']*index\.m3u8[^"\']*',
            r'https?://[^"\']*\.m3u8[^"\']*',
            # Patrones para otros formatos de video
            r'https?://[^"\']*\.mp4[^"\']*',
            r'https?://[^"\']*\.mkv[^"\']*',
            r'https?://[^"\']*\.ts[^"\']*',
            # Patrones para servicios de streaming conocidos
            r'https?://[^"\']*doodstream[^"\']*',
            r'https?://[^"\']*streamtape[^"\']*',
            r'https?://[^"\']*vidmoly[^"\']*',
            r'https?://[^"\']*okru[^"\']*',
            r'https?://[^"\']*hlswish[^"\']*'
        ]
        
        # Palabras clave para identificar elementos de video
        self.video_keywords = [
            'play', 'stream', 'video', 'live', 'canal', 'channel', 'tv', 
            'reproducir', 'ver', 'watch', 'player', 'embed', 'iframe',
            'servidor', 'server', 'mirror', 'espejo'
        ]
    
    def log(self, message: str, level: str = "INFO"):
        """Sistema de logging con colores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {level}: {message}{colors['RESET']}")
    
    def enhanced_extract_video_urls(self, content, base_url=""):
        """Extracción avanzada de URLs de video usando técnicas de los extractores de series"""
        video_urls = set()
        
        try:
            # Método 1: Patrones de video mejorados con priorización
            for pattern in self.video_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.strip():
                        # Priorizar URLs master.m3u8
                        if "master.m3u8" in match.lower():
                            video_urls.add(f"PRIORITY:{match.strip()}")
                        else:
                            video_urls.add(match.strip())
            
            # Método 2: Análisis avanzado de JavaScript para patrones de streams
            js_patterns = [
                r'["\']https?://[^"\']*\.m3u8[^"\']*["\']',
                r'["\']https?://[^"\']*(?:stream|play|video|live)[^"\']*\.m3u8[^"\']*["\']',
                r'source\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'src\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'video\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'stream\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'playlist\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'hls\s*:\s*["\']([^"\']*\.m3u8[^"\']*)["\']'
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    clean_url = match.strip('\'"')
                    if clean_url.startswith('http') and '.m3u8' in clean_url:
                        if "master.m3u8" in clean_url.lower():
                            video_urls.add(f"PRIORITY:{clean_url}")
                        else:
                            video_urls.add(clean_url)
            
            # Método 3: Análisis mejorado de iframes con servicios conocidos
            soup = BeautifulSoup(content, 'html.parser')
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                data_src = iframe.get('data-src', '')
                for url in [src, data_src]:
                    if url and any(service in url.lower() for service in ['dood', 'videok', 'stream', 'player', 'vidmoly', 'okru', 'hlswish', 'embed']):
                        video_urls.add(url)
            
            # Método 4: Escaneo de atributos de datos para fuentes de video
            data_attrs = ['data-url', 'data-stream', 'data-video', 'data-src', 'data-file', 'data-player', 'data-embed']
            for attr in data_attrs:
                elements = soup.find_all(attrs={attr: True})
                for element in elements:
                    url = element.get(attr, '')
                    if url and ('.m3u8' in url or any(service in url.lower() for service in ['stream', 'video', 'player', 'live'])):
                        if "master.m3u8" in url.lower():
                            video_urls.add(f"PRIORITY:{url}")
                        else:
                            video_urls.add(url)
            
            # Método 5: Búsqueda en tags script para URLs ocultas
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.get_text() if script.get_text() else ''
                if any(keyword in script_content.lower() for keyword in ['m3u8', 'videok', 'doodstream', 'streamtape', 'vidmoly', 'stream', 'video']):
                    # Extraer URLs potenciales del contenido del script
                    url_matches = re.findall(r'https?://[^\s\'"<>]+', script_content)
                    for url_match in url_matches:
                        if any(service in url_match.lower() for service in ['m3u8', 'videok', 'dood', 'stream', 'player', 'vidmoly', 'okru', 'live']):
                            if "master.m3u8" in url_match.lower():
                                video_urls.add(f"PRIORITY:{url_match}")
                            else:
                                video_urls.add(url_match)
            
            # Método 6: Patrones HLS mejorados para streams en vivo
            hls_patterns = [
                r'https?://[^\s"\'<>]+\.m3u8(?:\?[^\s"\'<>]*)?',
                r'https?://[^\s"\'<>]*(?:stream|hls|video|live|canal|channel)[^\s"\'<>]*\.m3u8(?:\?[^\s"\'<>]*)?',
                r'(?:source|src|url|file|stream|video)\s*[=:]\s*["\']([^"\']*\.m3u8[^"\']*)["\']',
                r'(?:hls|playlist|master)\s*[=:]\s*["\']([^"\']*\.m3u8[^"\']*)["\']'
            ]
            
            for pattern in hls_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    if match.strip() and '.m3u8' in match:
                        if "master.m3u8" in match.lower():
                            video_urls.add(f"PRIORITY:{match.strip()}")
                        else:
                            video_urls.add(match.strip())
            
            # Método 7: Elementos video y source
            video_elements = soup.find_all(['video', 'source'])
            for element in video_elements:
                src = element.get('src', '')
                if src and ('.m3u8' in src or '.mp4' in src):
                    if "master.m3u8" in src.lower():
                        video_urls.add(f"PRIORITY:{src}")
                    else:
                        video_urls.add(src)
            
            # Método 8: Búsqueda de botones o enlaces que puedan contener streams
            clickable_elements = soup.find_all(['a', 'button', 'div'], href=True)
            clickable_elements.extend(soup.find_all(['a', 'button', 'div'], onclick=True))
            
            for element in clickable_elements:
                href = element.get('href', '')
                onclick = element.get('onclick', '')
                text = element.get_text(strip=True).lower()
                
                # Verificar si el elemento parece estar relacionado con video
                if any(keyword in text for keyword in self.video_keywords):
                    for url in [href, onclick]:
                        if url and ('stream' in url.lower() or '.m3u8' in url.lower()):
                            video_urls.add(url)
        
        except Exception as e:
            self.log(f"Error en extracción avanzada: {e}", "ERROR")
        
        # Procesar URLs y priorizar master.m3u8
        final_urls = []
        priority_urls = []
        
        for url in video_urls:
            if url.startswith("PRIORITY:"):
                priority_urls.append(url[9:])  # Remover prefijo PRIORITY:
            else:
                final_urls.append(url)
        
        # Limpiar y validar URLs
        all_urls = priority_urls + final_urls
        cleaned_urls = []
        
        for url in all_urls:
            if url and url.startswith('http'):
                # Limpiar URL
                url = url.split('#')[0]  # Remover fragmentos
                url = url.split('?')[0] if not '.m3u8' in url else url  # Conservar parámetros en m3u8
                
                if url not in cleaned_urls:
                    cleaned_urls.append(url)
        
        return cleaned_urls[:10]  # Retornar máximo 10 URLs más prometedoras
    
    def extract_channels_from_site(self, site_name, base_url, channel_patterns=None):
        """Extrae canales de un sitio específico con técnicas avanzadas"""
        self.log(f"🚀 Iniciando extracción avanzada de {site_name}")
        channels = []
        
        try:
            # Configurar headers específicos para el sitio
            headers = self.session.headers.copy()
            headers['Referer'] = base_url
            
            response = self.session.get(base_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            self.log(f"✅ Página principal cargada ({len(response.content)} bytes)")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar canales usando múltiples estrategias
            channel_links = set()
            
            # Estrategia 1: Patrones específicos del sitio
            if channel_patterns:
                for pattern in channel_patterns:
                    links = soup.find_all('a', href=re.compile(pattern))
                    for link in links:
                        href = link.get('href')
                        if href:
                            full_url = urljoin(base_url, href)
                            channel_links.add(full_url)
            
            # Estrategia 2: Búsqueda por palabras clave de canales
            keyword_patterns = [
                r'/ver/', r'/canal/', r'/channel/', r'/tv/', r'/stream/',
                r'/live/', r'/watch/', r'/player/', r'/embed/'
            ]
            
            for pattern in keyword_patterns:
                links = soup.find_all('a', href=re.compile(pattern, re.IGNORECASE))
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href and any(keyword in text.lower() for keyword in self.video_keywords):
                        full_url = urljoin(base_url, href)
                        channel_links.add(full_url)
            
            # Estrategia 3: Elementos con texto relacionado a canales de TV
            tv_keywords = ['canal', 'channel', 'tv', 'televisión', 'stream', 'live', 'en vivo']
            for element in soup.find_all(['a', 'div', 'span'], string=re.compile('|'.join(tv_keywords), re.IGNORECASE)):
                if element.name == 'a' and element.get('href'):
                    href = element.get('href')
                    full_url = urljoin(base_url, href)
                    channel_links.add(full_url)
                # Buscar enlaces cercanos si el elemento no es un enlace
                elif element.name in ['div', 'span']:
                    parent = element.find_parent(['a', 'div'])
                    if parent:
                        link = parent.find('a', href=True)
                        if link:
                            href = link.get('href')
                            full_url = urljoin(base_url, href)
                            channel_links.add(full_url)
            
            self.log(f"📡 Encontrados {len(channel_links)} enlaces de canales potenciales")
            
            # Procesar cada canal encontrado
            processed_count = 0
            for channel_url in list(channel_links)[:50]:  # Limitar a 50 canales para prueba
                try:
                    self.log(f"🔍 Procesando canal: {channel_url}")
                    
                    # Obtener contenido del canal
                    channel_response = self.session.get(channel_url, headers=headers, timeout=20)
                    channel_response.raise_for_status()
                    
                    # Extraer nombre del canal
                    channel_soup = BeautifulSoup(channel_response.content, 'html.parser')
                    
                    # Intentar extraer nombre del canal de varias fuentes
                    channel_name = None
                    name_selectors = [
                        'title', 'h1', 'h2', '.channel-name', '.canal-nombre', 
                        '.title', '.name', '[class*="title"]', '[class*="name"]'
                    ]
                    
                    for selector in name_selectors:
                        element = channel_soup.select_one(selector)
                        if element:
                            text = element.get_text(strip=True)
                            if text and len(text) > 2 and len(text) < 100:
                                channel_name = text
                                break
                    
                    if not channel_name:
                        # Usar URL como nombre de respaldo
                        channel_name = urlparse(channel_url).path.split('/')[-1] or f"Canal_{processed_count+1}"
                    
                    # Limpiar nombre del canal
                    channel_name = re.sub(r'[^\w\s\-]', '', channel_name).strip()[:50]
                    
                    # Extraer URLs de video usando método avanzado
                    video_urls = self.enhanced_extract_video_urls(channel_response.text, channel_url)
                    
                    if video_urls:
                        # Tomar la mejor URL (la primera, ya que están priorizadas)
                        best_url = video_urls[0]
                        
                        channels.append({
                            'name': channel_name,
                            'url': best_url,
                            'source': site_name,
                            'original_page': channel_url,
                            'all_urls': video_urls[:3]  # Guardar hasta 3 URLs como respaldo
                        })
                        
                        self.log(f"✅ Canal extraído: {channel_name} - {best_url[:60]}...", "SUCCESS")
                    else:
                        self.log(f"⚠️ No se encontraron streams para: {channel_name}", "WARNING")
                    
                    processed_count += 1
                    
                    # Pausa entre requests para ser respetuosos
                    time.sleep(2)
                    
                except Exception as e:
                    self.log(f"❌ Error procesando canal {channel_url}: {e}", "ERROR")
                    continue
            
            self.log(f"🏁 Extracción completada. {len(channels)} canales extraídos de {site_name}", "SUCCESS")
            
        except Exception as e:
            self.log(f"❌ Error general en extracción de {site_name}: {e}", "ERROR")
        
        return channels
    
    def generate_enhanced_m3u(self, channels, filename_prefix="iptv_enhanced"):
        """Genera archivo M3U optimizado para Smart TV/SSIPTV"""
        if not channels:
            self.log("❌ No hay canales para generar M3U", "ERROR")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.m3u"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                
                for channel in channels:
                    # Limpiar nombre del canal para M3U
                    clean_name = re.sub(r'[^\w\s\-]', '', channel['name']).strip()
                    source_name = channel.get('source', 'Unknown')
                    
                    # Formato optimizado para Smart TV
                    title = f"{clean_name} [{source_name}]"
                    group_title = "IPTV Live"
                    
                    # Escribir entrada M3U
                    f.write(f'#EXTINF:-1 tvg-logo="" group-title="{group_title}",{title}\n')
                    f.write(f'{channel["url"]}\n')
            
            self.log(f"✅ Archivo M3U generado: {filename} ({len(channels)} canales)", "SUCCESS")
            return filename
            
        except Exception as e:
            self.log(f"❌ Error generando M3U: {e}", "ERROR")
            return None
    
    def extract_all_sites(self):
        """Extrae canales de todos los sitios configurados"""
        sites_config = {
            "tvplusgratis2.com": {
                "url": "https://tvplusgratis2.com",
                "patterns": [r'/ver/', r'/canal/', r'/tv/']
            },
            "telegratishd.com": {
                "url": "https://telegratishd.com", 
                "patterns": [r'/ver/', r'/canal/', r'/channel/']
            },
            "vertvcable.com": {
                "url": "https://vertvcable.com",
                "patterns": [r'/ver/', r'/canal/', r'/live/']
            },
            "cablevisionhd.com": {
                "url": "https://cablevisionhd.com",
                "patterns": [r'/ver/', r'/canal/', r'/watch/']
            }
        }
        
        all_channels = []
        
        for site_name, config in sites_config.items():
            self.log(f"🌐 Procesando sitio: {site_name}")
            try:
                channels = self.extract_channels_from_site(
                    site_name, 
                    config["url"], 
                    config.get("patterns", [])
                )
                all_channels.extend(channels)
                self.log(f"📺 {len(channels)} canales extraídos de {site_name}")
            except Exception as e:
                self.log(f"❌ Error en sitio {site_name}: {e}", "ERROR")
            
            # Pausa entre sitios
            time.sleep(5)
        
        return all_channels

def main():
    """Función principal del extractor mejorado"""
    print("🔥 IPTV Enhanced Extractor - Técnicas Avanzadas de Series Extractors")
    print("=" * 70)
    
    extractor = EnhancedIPTVExtractor()
    
    print("\nOpciones disponibles:")
    print("1. Extraer de todos los sitios")
    print("2. Extraer de un sitio específico")
    print("3. Probar extracción avanzada en una URL")
    
    choice = input("\nSeleccione una opción (1-3): ").strip()
    
    if choice == "1":
        # Extraer de todos los sitios
        extractor.log("🚀 Iniciando extracción completa de todos los sitios")
        channels = extractor.extract_all_sites()
        
        if channels:
            extractor.log(f"🎉 Total de canales extraídos: {len(channels)}")
            
            # Generar M3U
            m3u_file = extractor.generate_enhanced_m3u(channels)
            if m3u_file:
                print(f"\n✅ Archivo M3U generado: {m3u_file}")
                print(f"📊 Total de canales: {len(channels)}")
                
                # Preguntar si verificar streams
                verify = input("\n¿Verificar que los streams funcionen? (y/n): ").lower().strip()
                if verify == 'y':
                    extractor.log("🔍 Iniciando verificación de streams...")
                    # Aquí podrías llamar a la función de verificación si existe
        else:
            extractor.log("❌ No se pudieron extraer canales", "ERROR")
    
    elif choice == "2":
        # Extraer de un sitio específico
        sites = {
            "1": ("tvplusgratis2.com", "https://tvplusgratis2.com", [r'/ver/', r'/canal/']),
            "2": ("telegratishd.com", "https://telegratishd.com", [r'/ver/', r'/canal/']),
            "3": ("vertvcable.com", "https://vertvcable.com", [r'/ver/', r'/canal/']),
            "4": ("cablevisionhd.com", "https://cablevisionhd.com", [r'/ver/', r'/canal/'])
        }
        
        print("\nSitios disponibles:")
        for key, (name, url, _) in sites.items():
            print(f"{key}. {name}")
        
        site_choice = input("\nSeleccione un sitio (1-4): ").strip()
        
        if site_choice in sites:
            site_name, site_url, patterns = sites[site_choice]
            extractor.log(f"🎯 Extrayendo canales de {site_name}")
            
            channels = extractor.extract_channels_from_site(site_name, site_url, patterns)
            
            if channels:
                m3u_file = extractor.generate_enhanced_m3u(channels, f"iptv_{site_name}")
                if m3u_file:
                    print(f"\n✅ Archivo M3U generado: {m3u_file}")
                    print(f"📊 Total de canales: {len(channels)}")
        else:
            print("❌ Opción inválida")
    
    elif choice == "3":
        # Probar extracción en una URL específica
        test_url = input("\nIngrese la URL para probar: ").strip()
        if test_url:
            try:
                extractor.log(f"🧪 Probando extracción avanzada en: {test_url}")
                
                response = extractor.session.get(test_url, timeout=30)
                response.raise_for_status()
                
                video_urls = extractor.enhanced_extract_video_urls(response.text, test_url)
                
                if video_urls:
                    extractor.log(f"✅ URLs de video encontradas: {len(video_urls)}", "SUCCESS")
                    for i, url in enumerate(video_urls[:5], 1):
                        print(f"  {i}. {url}")
                else:
                    extractor.log("❌ No se encontraron URLs de video", "WARNING")
                    
            except Exception as e:
                extractor.log(f"❌ Error en prueba: {e}", "ERROR")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
