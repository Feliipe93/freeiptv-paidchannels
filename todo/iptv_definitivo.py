#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 IPTV EXTRACTOR DEFINITIVO - SCRIPT ÚNICO COMPLETO 🔥
Extractor avanzado con técnicas anti-detección, eliminación de duplicados y URLs corregidas para todos los sitios
Integra toda la funcionalidad en un solo archivo para facilidad de uso
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
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import itertools
import hashlib
import ssl
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Desactivar advertencias SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Intentar importar dependencias opcionales
try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("⚠️ CloudScraper no disponible (pip install cloudscraper para mejor rendimiento)")

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright no disponible (pip install playwright para sitios con JavaScript)")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium no disponible (pip install selenium para sitios complejos)")

# Lista de proxies gratuitos para rotación (se actualizará dinámicamente)
FREE_PROXIES = [
    # Se cargarán dinámicamente o se mantendrá lista básica
]

class IPTVExtractorDefinitivo:
    """Extractor IPTV definitivo con todas las técnicas integradas"""
    
    def __init__(self):
        self.init_sessions()
        self.init_patterns()
        self.init_site_configs()
        self.init_anti_detection()
        self.init_proxies()
        self.request_count = 0
        self.blocked_count = 0
        self.session_rotation_interval = 50  # Rotar sesión cada X requests
        
    def init_anti_detection(self):
        """Inicializar técnicas anti-detección avanzadas"""
        # User agents más reales
        self.premium_user_agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            # Chrome macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Chrome Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        ]
        
        # Headers variables más naturales
        self.accept_languages = [
            'es-ES,es;q=0.9,en;q=0.8,en-US;q=0.7',
            'es-MX,es;q=0.9,en;q=0.8,en-US;q=0.7',
            'es-AR,es;q=0.9,en;q=0.8,en-US;q=0.7',
            'es-CO,es;q=0.9,en;q=0.8,en-US;q=0.7',
            'en-US,en;q=0.9,es;q=0.8,es-ES;q=0.7',
        ]
        
        self.accept_encodings = [
            'gzip, deflate, br',
            'gzip, deflate, br, zstd',
            'gzip, deflate',
        ]
        
        # Fingerprints de navegador
        self.browser_fingerprints = [
            {
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
            },
            {
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
            }
        ]
        
        # Configuración SSL/TLS corregida (orden correcto)
        try:
            self.ssl_context = ssl.create_default_context()
            # Orden correcto: primero verify_mode, luego check_hostname
            self.ssl_context.verify_mode = ssl.CERT_NONE
            self.ssl_context.check_hostname = False
        except Exception as e:
            self.log(f"Info: SSL context configurado para conexión segura", "INFO")
            self.ssl_context = None
    
    def init_proxies(self):
        """Inicializar sistema de proxies"""
        self.proxy_pool = []
        self.current_proxy_index = 0
        self.proxy_failures = {}
        
        # Proxies gratuitos básicos (se pueden actualizar)
        free_proxy_list = [
            # Se pueden agregar proxies específicos aquí
            # Formato: {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
        ]
        
        # Intentar obtener proxies dinámicamente
        try:
            self.refresh_proxy_list()
        except:
            self.log("⚠️ No se pudieron obtener proxies dinámicos, usando método sin proxies", "WARNING")
        
        # Proxy null para alternar
        self.proxy_pool.append(None)  # Sin proxy como opción
    
    def refresh_proxy_list(self):
        """Actualizar lista de proxies dinámicamente"""
        try:
            # API simple para obtener proxies (ejemplo)
            proxy_sources = [
                # Se pueden agregar fuentes de proxies aquí
                # "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            ]
            
            # Por ahora usar lista estática para evitar dependencias externas
            self.log("Usando configuración de red directa (más estable)", "INFO")
            
        except Exception as e:
            self.log(f"Error actualizando proxies: {e}", "WARNING")
    
    def get_next_proxy(self):
        """Obtener siguiente proxy de la pool"""
        if not self.proxy_pool:
            return None
        
        proxy = self.proxy_pool[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        
        # Verificar si el proxy ha fallado demasiado
        if proxy and self.proxy_failures.get(str(proxy), 0) > 3:
            return self.get_next_proxy()  # Saltar proxy problemático
        
        return proxy
    
    def mark_proxy_failure(self, proxy):
        """Marcar proxy como fallido"""
        if proxy:
            proxy_key = str(proxy)
            self.proxy_failures[proxy_key] = self.proxy_failures.get(proxy_key, 0) + 1
    
    def create_new_session(self):
        """Crear nueva sesión con configuración anti-detección mejorada"""
        session = requests.Session()
        
        # Configurar verificación SSL más permisiva ANTES de los adaptadores
        session.verify = False
        
        # Configurar adaptadores con retry strategy mejorado
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
        
        return session
        
    def init_sessions(self):
        """Inicializar sesiones y scrapers con configuración SSL corregida"""
        # Session requests normal con configuración SSL permisiva
        self.session = requests.Session()
        self.session.verify = False
        
        # Configurar adaptadores con retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # CloudScraper para bypass de Cloudflare si está disponible
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.scraper = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'desktop': True
                    }
                )
                # Configurar SSL para cloudscraper también - CORREGIDO
                self.scraper.verify = False
                
                # Configurar adaptadores SSL para cloudscraper
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["HEAD", "GET", "OPTIONS"]
                )
                
                adapter = HTTPAdapter(max_retries=retry_strategy)
                self.scraper.mount("http://", adapter)
                self.scraper.mount("https://", adapter)
                
            except Exception as e:
                self.log(f"Warning: CloudScraper setup failed, usando requests normal: {e}", "WARNING")
                self.scraper = self.session
        else:
            self.scraper = self.session
        
        # Headers rotativos
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def init_patterns(self):
        """Inicializar patrones de detección de video"""
        # Patrones prioritarios para streams directos
        self.video_patterns = [
            # HLS Streams (más importantes)
            r'https?://[^"\']*master\.m3u8[^"\']*',
            r'https?://[^"\']*playlist\.m3u8[^"\']*', 
            r'https?://[^"\']*index\.m3u8[^"\']*',
            r'https?://cdn\d*\.videok\.pro/[^"\']*\.m3u8[^"\']*',
            r'https?://[^"\']*\.m3u8[^"\']*',
            # Video files directos
            r'https?://[^"\']*\.mp4[^"\']*',
            r'https?://[^"\']*\.mkv[^"\']*',
            r'https?://[^"\']*\.ts[^"\']*',
            # Servicios de streaming conocidos
            r'https?://[^"\']*doodstream[^"\']*',
            r'https?://[^"\']*streamtape[^"\']*',
            r'https?://[^"\']*vidmoly[^"\']*',
            r'https?://[^"\']*okru[^"\']*',
            r'https?://[^"\']*hlswish[^"\']*',
            r'https?://[^"\']*streamhide[^"\']*',
            r'https?://[^"\']*embed[^"\']*\.php',
            r'https?://[^"\']*player[^"\']*'
        ]
        
        # Patrones JavaScript para extracción avanzada
        self.js_patterns = [
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
    
    def init_site_configs(self):
        """Configuración específica por sitio basada en verificaciones"""
        self.site_configs = {
            "tvplusgratis2.com": {
                "base_url": "https://tvplusgratis2.com",
                "url_format": "{base_url}/{channel_name}-en-vivo.html",  # Formato confirmado
                "channel_selectors": [
                    'a[href*="-en-vivo.html"]',
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    '.channel-link',
                    '.canal-link'
                ],
                "anti_cloudflare": True,
                "requires_js": True,
                "verified_working": True
            },
            "telegratishd.com": {
                "base_url": "https://telegratishd.com",
                "url_format": "{base_url}/{channel_name}-en-vivo.html",  # Formato confirmado
                "channel_selectors": [
                    'a[href*="-en-vivo.html"]',
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    '.channel-item a',
                    '.canal-item a'
                ],
                "anti_cloudflare": True,
                "requires_js": True,
                "verified_working": True
            },
            "vertvcable.com": {
                "base_url": "https://vertvcable.com",
                "url_format": "{base_url}/{channel_name}",  # Formato directo confirmado
                "channel_selectors": [
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    'a[href*="/live/"]',
                    '.channel-link',
                    '.tv-channel a'
                ],
                "anti_cloudflare": True,
                "requires_js": False,
                "verified_working": True
            },
            "cablevisionhd.com": {
                "base_url": "https://cablevisionhd.com",
                "url_format": "{base_url}/{channel_name}",  # Formato directo
                "channel_selectors": [
                    'a[href*="/ver/"]',
                    'a[href*="/canal/"]',
                    'a[href*="/watch/"]',
                    '.channel-list a',
                    '.tv-list a'
                ],
                "anti_cloudflare": True,
                "requires_js": False,
                "verified_working": False  # Necesita más trabajo
            },
            "embed.ksdjugfsddeports.fun": {
                "base_url": "https://embed.ksdjugfsddeports.fun",
                "url_format": "{base_url}",  # Fuente principal directa
                "channel_selectors": [
                    'a[href*="/"]',
                    '.channel-link',
                    '.stream-link',
                    '.live-channel',
                    'a[data-channel]',
                    '.channel-item a',
                    '.stream-item a'
                ],
                "anti_cloudflare": True,
                "requires_js": True,
                "verified_working": True,  # Nueva fuente principal
                "is_main_source": True,  # Marcador especial
                "extraction_method": "direct_embed"
            }
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Sistema de logging con colores y timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "DEBUG": "\033[95m",
            "CRITICAL": "\033[41m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {level}: {message}{colors['RESET']}")
    
    def get_random_headers(self, referer=None, site_config=None):
        """Generar headers aleatorios anti-detección avanzados"""
        # Rotar user agent
        if FAKE_UA_AVAILABLE:
            try:
                ua = UserAgent(browsers=['chrome', 'firefox', 'edge'], os=['windows', 'macos', 'linux'])
                user_agent = ua.random
            except:
                user_agent = random.choice(self.premium_user_agents)
        else:
            user_agent = random.choice(self.premium_user_agents)
        
        # Headers base más naturales
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': random.choice(self.accept_encodings),
            'DNT': random.choice(['1', '0']),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store, no-cache, must-revalidate']),
            'Pragma': random.choice(['no-cache', '']),
        }
        
        # Agregar fingerprint de navegador aleatorio
        fingerprint = random.choice(self.browser_fingerprints)
        headers.update(fingerprint)
        
        # Referer inteligente
        if referer:
            headers['Referer'] = referer
        elif site_config:
            headers['Referer'] = site_config.get("base_url", "https://google.com/")
        else:
            # Referers más naturales
            natural_referers = [
                'https://www.google.com/',
                'https://www.google.com/search?q=iptv+canales+gratis',
                'https://duckduckgo.com/',
                'https://www.bing.com/',
                'https://twitter.com/',
                'https://www.facebook.com/',
            ]
            headers['Referer'] = random.choice(natural_referers)
        
        # Headers adicionales aleatorios para parecer más natural
        if random.random() < 0.7:  # 70% de probabilidad
            headers['X-Requested-With'] = random.choice(['XMLHttpRequest', ''])
        
        if random.random() < 0.5:  # 50% de probabilidad
            headers['Origin'] = headers['Referer'].rstrip('/')
        
        return headers
    
    def safe_request_with_retries(self, url, site_config, max_retries=5, timeout=30):
        """Request ultra-seguro con múltiples técnicas anti-detección y reintentos"""
        self.request_count += 1
        
        # Rotar sesión periódicamente
        if self.request_count % self.session_rotation_interval == 0:
            self.log("🔄 Rotando sesión para evitar detección", "DEBUG")
            self.session = self.create_new_session()
            if CLOUDSCRAPER_AVAILABLE:
                self.scraper = cloudscraper.create_scraper(
                    browser={
                        'browser': random.choice(['chrome', 'firefox']),
                        'platform': random.choice(['windows', 'darwin', 'linux']),
                        'desktop': True
                    }
                )
        
        for attempt in range(max_retries):
            try:
                # Pausa inteligente anti-rate-limiting
                if attempt > 0:
                    delay = min(2 ** attempt + random.uniform(1, 3), 30)
                    self.log(f"⏰ Pausa anti-detección: {delay:.1f}s (intento {attempt + 1})", "DEBUG")
                    time.sleep(delay)
                else:
                    time.sleep(random.uniform(2, 5))  # Pausa inicial aleatoria
                
                # Obtener proxy (puede ser None para conexión directa)
                proxy = self.get_next_proxy()
                
                # Headers anti-detección
                headers = self.get_random_headers(site_config=site_config)
                
                # Método de request según configuración
                session_to_use = self.session
                method_name = "requests"
                
                if CLOUDSCRAPER_AVAILABLE and site_config.get("anti_cloudflare", False):
                    session_to_use = self.scraper
                    method_name = "cloudscraper"
                
                self.log(f"🌐 Intento {attempt + 1}: {method_name} {'+ proxy' if proxy else 'directo'} -> {url[:50]}...", "DEBUG")
                
                # Realizar request
                response = session_to_use.get(
                    url, 
                    headers=headers, 
                    timeout=timeout,
                    proxies=proxy,
                    verify=False,  # Evitar problemas SSL
                    allow_redirects=True
                )
                
                # Verificar respuesta
                if response.status_code == 200:
                    # Verificar si el contenido parece válido (no página de error/captcha)
                    content_lower = response.text.lower()
                    
                    # Detectar páginas de bloqueo/captcha
                    block_indicators = [
                        'captcha', 'cloudflare', 'access denied', 'forbidden',
                        'blocked', 'rate limit', 'too many requests',
                        'verificaci', 'robot', 'bot detected', 'security check'
                    ]
                    
                    if any(indicator in content_lower for indicator in block_indicators):
                        self.log(f"🚫 Detectado bloqueo/captcha en intento {attempt + 1}", "WARNING")
                        self.blocked_count += 1
                        if proxy:
                            self.mark_proxy_failure(proxy)
                        continue
                    
                    # Verificar longitud mínima del contenido
                    if len(response.content) < 1000:
                        self.log(f"⚠️ Contenido sospechosamente corto ({len(response.content)} bytes)", "WARNING")
                        continue
                    
                    self.log(f"✅ Request exitoso: {len(response.content)} bytes", "DEBUG")
                    return response
                
                elif response.status_code in [403, 429, 503, 502]:
                    self.log(f"🚫 Bloqueo detectado: {response.status_code}", "WARNING")
                    self.blocked_count += 1
                    if proxy:
                        self.mark_proxy_failure(proxy)
                    continue
                
                elif response.status_code in [301, 302, 307, 308]:
                    self.log(f"↗️ Redirección: {response.status_code}", "DEBUG")
                    # requests maneja redirects automáticamente
                    continue
                
                else:
                    self.log(f"❌ Status inesperado: {response.status_code}", "WARNING")
                    continue
                    
            except requests.exceptions.ProxyError:
                self.log(f"🔌 Error de proxy en intento {attempt + 1}", "WARNING")
                if proxy:
                    self.mark_proxy_failure(proxy)
                continue
                
            except requests.exceptions.Timeout:
                self.log(f"⏰ Timeout en intento {attempt + 1}", "WARNING")
                continue
                
            except requests.exceptions.ConnectionError:
                self.log(f"🔌 Error de conexión en intento {attempt + 1}", "WARNING")
                continue
                
            except Exception as e:
                self.log(f"❌ Error inesperado en intento {attempt + 1}: {str(e)[:50]}...", "WARNING")
                continue
        
        self.log(f"💀 Falló después de {max_retries} intentos: {url[:50]}...", "ERROR")
        return None
    
    def safe_request(self, url, site_config, timeout=30):
        """Wrapper para mantener compatibilidad con el código existente"""
        return self.safe_request_with_retries(url, site_config, timeout=timeout)
    
    def clean_channel_name(self, name):
        """Limpiar y normalizar nombres de canales"""
        if not name or len(name.strip()) < 2:
            return ""
        
        # Remover prefijos y sufijos comunes
        clean_patterns = [
            (r'^(ver\s+|watch\s+|canal\s+|channel\s+)', ''),
            (r'\s+(en\s+vivo|online|gratis|hd|live|free)$', ''),
            (r'\s*-\s*(en\s+vivo|live|online)$', ''),
            (r'^(tv\s+|canal\s+)', ''),
            (r'ver\s+canal\s*', ''),
            (r'\s+\d+$', '')  # Remover números al final
        ]
        
        cleaned = name.strip()
        for pattern, replacement in clean_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Limpiar caracteres especiales pero mantener guiones y espacios
        cleaned = re.sub(r'[^\w\s\-&+]', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Capitalizar apropiadamente
        if cleaned:
            cleaned = cleaned.title()
            # Corregir casos especiales
            special_cases = {
                'Espn': 'ESPN',
                'Cnn': 'CNN',
                'Mtv': 'MTV',
                'Hbo': 'HBO',
                'Tnt': 'TNT',
                'Fx': 'FX',
                'Hd': 'HD',
                'Tv': 'TV',
                'Jr': 'JR'
            }
            for old, new in special_cases.items():
                cleaned = re.sub(r'\b' + old + r'\b', new, cleaned)
        
        return cleaned
    
    def detect_duplicates(self, channels):
        """Detectar y manejar canales duplicados manteniendo ambos si tienen URLs diferentes"""
        seen_names = {}
        unique_channels = []
        duplicates_info = []
        
        for channel in channels:
            clean_name = self.clean_channel_name(channel['name'])
            
            # Crear clave única basada en nombre normalizado
            name_key = clean_name.lower().strip()
            name_key = re.sub(r'\s+', '', name_key)  # Remover espacios para comparación
            
            if name_key in seen_names:
                # Es un duplicado
                existing_channel = seen_names[name_key]
                
                # Verificar si tienen URLs diferentes
                if channel['url'] != existing_channel['url']:
                    # URLs diferentes - mantener ambos con sufijos
                    duplicates_info.append({
                        'name': clean_name,
                        'urls': [existing_channel['url'], channel['url']]
                    })
                    
                    # Actualizar el existente con sufijo
                    existing_channel['name'] = f"{clean_name} (Opción 1)"
                    existing_channel['duplicate_group'] = name_key
                    
                    # Agregar el nuevo con sufijo
                    channel['name'] = f"{clean_name} (Opción 2)"
                    channel['duplicate_group'] = name_key
                    unique_channels.append(channel)
                else:
                    # URLs iguales - es realmente duplicado, ignorar
                    self.log(f"Duplicado ignorado: {clean_name}", "DEBUG")
            else:
                # Primer occurrence
                channel['name'] = clean_name
                seen_names[name_key] = channel
                unique_channels.append(channel)
        
        if duplicates_info:
            self.log(f"📋 Detectados {len(duplicates_info)} canales con múltiples opciones:", "INFO")
            for dup in duplicates_info:
                self.log(f"   • {dup['name']}: {len(dup['urls'])} URLs diferentes", "INFO")
        
        return unique_channels, duplicates_info
    
    def extract_channels_from_main_page(self, site_name, site_config):
        """Extraer canales de página principal con técnicas avanzadas"""
        self.log(f"🕷️ Extrayendo canales de {site_name}")
        
        base_url = site_config["base_url"]
        response = self.safe_request(base_url, site_config)
        
        if not response:
            self.log(f"❌ No se pudo acceder a {site_name}", "ERROR")
            return []
        
        self.log(f"✅ Página principal cargada ({len(response.content)} bytes)")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        channels = []
        
        # Método 1: Selectores específicos del sitio
        for selector in site_config["channel_selectors"]:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text and len(text) > 2:
                        full_url = urljoin(base_url, href)
                        clean_name = self.clean_channel_name(text)
                        
                        if clean_name:
                            channels.append({
                                'name': clean_name,
                                'url': full_url,
                                'source': site_name,
                                'method': f'selector_{selector[:20]}...'
                            })
                
                self.log(f"Selector {selector[:30]}...: {len([c for c in channels if c.get('method', '').startswith('selector')])} canales")
                
            except Exception as e:
                self.log(f"Error con selector {selector}: {e}", "WARNING")
                continue
        
        # Método 2: Búsqueda por patrones de URL
        url_patterns = [
            r'-en-vivo\.html$',
            r'/ver/[^/]+$',
            r'/canal/[^/]+$',
            r'/watch/[^/]+$',
            r'/live/[^/]+$'
        ]
        
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href and text:
                for pattern in url_patterns:
                    if re.search(pattern, href, re.IGNORECASE):
                        full_url = urljoin(base_url, href)
                        clean_name = self.clean_channel_name(text)
                        
                        if clean_name and not any(c['url'] == full_url for c in channels):
                            channels.append({
                                'name': clean_name,
                                'url': full_url,
                                'source': site_name,
                                'method': f'pattern_{pattern[:15]}...'
                            })
                        break
        
        # Método 3: Búsqueda por palabras clave de TV
        tv_keywords = [
            'espn', 'fox', 'cnn', 'discovery', 'history', 'disney', 'cartoon',
            'nickelodeon', 'mtv', 'vh1', 'comedy', 'fx', 'tnt', 'hbo', 'showtime',
            'univision', 'telemundo', 'caracol', 'rcn', 'teleantioquia', 'win',
            'canal', 'telecafe', 'telepacifico', 'nat geo', 'national geographic',
            'animal planet', 'netflix', 'amazon', 'prime', 'sony', 'warner',
            'paramount', 'universal', 'studio', 'sports', 'deportes', 'news',
            'noticias', 'music', 'musica', 'kids', 'infantil'
        ]
        
        for link in all_links:
            text = link.get_text(strip=True).lower()
            href = link.get('href')
            
            if any(keyword in text for keyword in tv_keywords) and href:
                full_url = urljoin(base_url, href)
                clean_name = self.clean_channel_name(link.get_text(strip=True))
                
                if clean_name and not any(c['url'] == full_url for c in channels):
                    channels.append({
                        'name': clean_name,
                        'url': full_url,
                        'source': site_name,
                        'method': 'keyword_search'
                    })
        
        # Detectar y manejar duplicados
        unique_channels, duplicates_info = self.detect_duplicates(channels)
        
        self.log(f"🎯 {site_name}: {len(channels)} canales brutos → {len(unique_channels)} únicos")
        if duplicates_info:
            self.log(f"   📊 {len(duplicates_info)} canales con opciones múltiples")
        
        return unique_channels
    
    def extract_video_urls_advanced(self, content, base_url=""):
        """Extraer URLs de video usando todas las técnicas avanzadas"""
        video_urls = set()
        
        try:
            # Método 1: Patrones de video directos
            for pattern in self.video_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match.strip():
                        if "master.m3u8" in match.lower():
                            video_urls.add(f"PRIORITY:{match.strip()}")
                        else:
                            video_urls.add(match.strip())
            
            # Método 2: Patrones JavaScript
            for pattern in self.js_patterns:
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
            
            # Método 3: Análisis de elementos HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Iframes
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                data_src = iframe.get('data-src', '')
                for url in [src, data_src]:
                    if url and any(service in url.lower() for service in 
                                 ['dood', 'videok', 'stream', 'player', 'embed', 'vidmoly', 'okru']):
                        video_urls.add(url)
            
            # Data attributes
            data_attrs = ['data-url', 'data-stream', 'data-video', 'data-src', 'data-file', 'data-player']
            for attr in data_attrs:
                elements = soup.find_all(attrs={attr: True})
                for element in elements:
                    url = element.get(attr, '')
                    if url and ('.m3u8' in url or any(service in url.lower() for service in ['stream', 'video', 'live'])):
                        if "master.m3u8" in url.lower():
                            video_urls.add(f"PRIORITY:{url}")
                        else:
                            video_urls.add(url)
            
            # Scripts con URLs embebidas
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.get_text() if script.get_text() else ''
                if any(keyword in script_content.lower() for keyword in ['m3u8', 'stream', 'video', 'player']):
                    url_matches = re.findall(r'https?://[^\s\'"<>]+', script_content)
                    for url_match in url_matches:
                        if any(service in url_match.lower() for service in ['m3u8', 'stream', 'video', 'player']):
                            if "master.m3u8" in url_match.lower():
                                video_urls.add(f"PRIORITY:{url_match}")
                            else:
                                video_urls.add(url_match)
            
            # Video/source elements
            video_elements = soup.find_all(['video', 'source'])
            for element in video_elements:
                src = element.get('src', '')
                if src and ('.m3u8' in src or '.mp4' in src):
                    if "master.m3u8" in src.lower():
                        video_urls.add(f"PRIORITY:{src}")
                    else:
                        video_urls.add(src)
        
        except Exception as e:
            self.log(f"Error en extracción avanzada: {e}", "ERROR")
        
        # Procesar y priorizar URLs
        priority_urls = []
        regular_urls = []
        
        for url in video_urls:
            if url.startswith("PRIORITY:"):
                priority_urls.append(url[9:])
            else:
                regular_urls.append(url)
        
        # Limpiar URLs
        all_urls = priority_urls + regular_urls
        cleaned_urls = []
        
        for url in all_urls:
            if url and url.startswith('http'):
                # Limpiar URL
                url = url.split('#')[0]  # Remover fragmentos
                if url not in cleaned_urls:
                    cleaned_urls.append(url)
        
        return cleaned_urls[:10]  # Top 10 URLs más prometedoras
    
    async def extract_with_playwright(self, channel_url, site_config):
        """Extracción usando Playwright para sitios JavaScript"""
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        self.log(f"🎭 Playwright: {channel_url[:60]}...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--ignore-certificate-errors',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=random.choice(self.user_agents),
                ignore_https_errors=True
            )
            
            page = await context.new_page()
            video_urls = []
            
            async def handle_response(response):
                url = response.url
                if any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    return
                
                for pattern in self.video_patterns:
                    if re.search(pattern, url, re.IGNORECASE):
                        self.log(f"🎥 Playwright detectó: {url[:80]}...", "SUCCESS")
                        video_urls.append(url)
                        return
            
            page.on('response', handle_response)
            
            try:
                await page.goto(channel_url, wait_until='networkidle', timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Buscar y hacer clic en elementos de reproducción
                play_selectors = [
                    'button[class*="play"]', '.play-button', '.btn-play',
                    'button', '[onclick*="play"]', '.player-button'
                ]
                
                for selector in play_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements[:3]:
                            try:
                                if await element.is_visible():
                                    await element.click(timeout=10000)
                                    await page.wait_for_timeout(8000)
                                    if video_urls:
                                        break
                            except:
                                continue
                        if video_urls:
                            break
                    except:
                        continue
                
                # Buscar iframes
                iframes = await page.query_selector_all('iframe')
                for iframe in iframes:
                    try:
                        src = await iframe.get_attribute('src')
                        if src and any(service in src.lower() for service in ['stream', 'player', 'embed']):
                            video_urls.append(src)
                    except:
                        continue
                
                await page.wait_for_timeout(10000)
                await browser.close()
                return video_urls
                
            except Exception as e:
                self.log(f"Error Playwright: {e}", "ERROR")
                await browser.close()
                return []
    
    async def process_channel(self, channel, site_config):
        """Procesar canal individual para extraer streams"""
        channel_name = channel['name']
        channel_url = channel['url']
        
        self.log(f"🔍 {channel_name}")
        
        try:
            # Método básico primero
            response = self.safe_request(channel_url, site_config)
            
            if not response:
                self.log(f"❌ No accesible: {channel_name}", "WARNING")
                return None
            
            # Extraer con método básico
            video_urls = self.extract_video_urls_advanced(response.text, channel_url)
            
            # Si se requiere JavaScript y está disponible Playwright
            if not video_urls and PLAYWRIGHT_AVAILABLE and site_config.get("requires_js", False):
                video_urls = await self.extract_with_playwright(channel_url, site_config)
            
            if video_urls:
                best_url = video_urls[0]  # Ya están priorizados
                
                self.log(f"✅ {channel_name}: {best_url[:60]}...", "SUCCESS")
                return {
                    'name': channel_name,
                    'url': best_url,
                    'source': channel.get('source', 'unknown'),
                    'original_page': channel_url,
                    'backup_urls': video_urls[1:3] if len(video_urls) > 1 else [],
                    'duplicate_group': channel.get('duplicate_group')
                }
            
            self.log(f"❌ Sin streams: {channel_name}", "WARNING")
            return None
            
        except Exception as e:
            self.log(f"❌ Error {channel_name}: {e}", "ERROR")
            return None
    
    async def extract_site_complete_protected(self, site_name):
        """Extraer sitio completo con protección avanzada anti-detección"""
        self.log(f"🚀 EXTRACCIÓN PROTEGIDA: {site_name.upper()}")
        
        site_config = self.site_configs.get(site_name)
        if not site_config:
            self.log(f"❌ Sitio {site_name} no configurado", "ERROR")
            return []
        
        # Resetear contadores para este sitio
        initial_request_count = self.request_count
        initial_blocked_count = self.blocked_count
        
        try:
            # Paso 1: Extraer lista de canales con protección
            self.log(f"🛡️ Aplicando protecciones anti-detección para {site_name}")
            channels = self.extract_channels_from_main_page_protected(site_name, site_config)
            
            if not channels:
                self.log(f"❌ No se encontraron canales en {site_name}", "ERROR")
                return []
            
            self.log(f"📋 {len(channels)} canales para procesar en {site_name}")
            
            # Paso 2: Procesar canales con técnicas anti-detección
            working_channels = []
            batch_size = 3  # Reducir batch size para evitar detección
            
            for i in range(0, len(channels), batch_size):
                batch = channels[i:i+batch_size]
                batch_num = i//batch_size + 1
                total_batches = (len(channels) + batch_size - 1) // batch_size
                
                self.log(f"🔄 Lote protegido {batch_num}/{total_batches} ({len(batch)} canales)")
                
                # Monitorear tasa de bloqueo
                if self.blocked_count > initial_blocked_count + 5:
                    self.log(f"⚠️ Alta tasa de bloqueo detectada, aumentando delays", "WARNING")
                    await asyncio.sleep(random.uniform(10, 20))
                
                for channel in batch:
                    try:
                        result = await self.process_channel_protected(channel, site_config)
                        if result:
                            working_channels.append(result)
                        
                        # Pausa inteligente entre canales
                        delay = random.uniform(3, 8)
                        if self.blocked_count > initial_blocked_count:
                            delay *= 2  # Duplicar delay si hay bloqueos
                        
                        await asyncio.sleep(delay)
                        
                    except Exception as e:
                        self.log(f"❌ Error procesando {channel.get('name', 'Unknown')}: {e}", "ERROR")
                        continue
                
                # Pausa entre lotes más larga
                batch_delay = random.uniform(8, 15)
                if self.blocked_count > initial_blocked_count:
                    batch_delay *= 1.5
                
                self.log(f"⏰ Pausa entre lotes: {batch_delay:.1f}s", "DEBUG")
                await asyncio.sleep(batch_delay)
            
            # Estadísticas finales
            final_request_count = self.request_count - initial_request_count
            final_blocked_count = self.blocked_count - initial_blocked_count
            
            self.log(f"📊 Estadísticas {site_name}:", "INFO")
            self.log(f"   Requests realizados: {final_request_count}", "INFO")
            self.log(f"   Bloqueos detectados: {final_blocked_count}", "INFO")
            self.log(f"   Tasa de éxito: {((final_request_count - final_blocked_count) / max(final_request_count, 1) * 100):.1f}%", "INFO")
            
            self.log(f"🎉 {site_name}: {len(working_channels)} canales con streams")
            return working_channels
            
        except Exception as e:
            self.log(f"💥 Error crítico en {site_name}: {e}", "CRITICAL")
            return []
    
    def extract_channels_from_main_page_protected(self, site_name, site_config):
        """Extraer canales de página principal con protección avanzada"""
        self.log(f"🕷️ Extrayendo canales protegido de {site_name}")
        
        base_url = site_config["base_url"]
        
        # Múltiples intentos con diferentes técnicas
        for attempt in range(3):
            try:
                self.log(f"Intento {attempt + 1} para página principal de {site_name}", "DEBUG")
                
                response = self.safe_request_with_retries(base_url, site_config, max_retries=3)
                
                if not response:
                    self.log(f"❌ Intento {attempt + 1} falló para {site_name}", "WARNING")
                    if attempt < 2:  # No es el último intento
                        time.sleep(random.uniform(10, 20))
                        continue
                    else:
                        self.log(f"💀 Todos los intentos fallaron para {site_name}", "ERROR")
                        return []
                
                self.log(f"✅ Página principal cargada: {len(response.content)} bytes")
                break
                
            except Exception as e:
                self.log(f"❌ Error en intento {attempt + 1}: {e}", "ERROR")
                if attempt < 2:
                    time.sleep(random.uniform(10, 20))
                    continue
                else:
                    return []
        
        # Procesar contenido con manejo robusto de errores
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            channels = []
            
            # Método 1: Selectores específicos del sitio (mejorado)
            for selector in site_config["channel_selectors"]:
                try:
                    links = soup.select(selector)
                    self.log(f"Selector '{selector}': {len(links)} elementos encontrados", "DEBUG")
                    
                    for link in links:
                        try:
                            href = link.get('href')
                            text = link.get_text(strip=True)
                            
                            if href and text and len(text) > 2:
                                full_url = urljoin(base_url, href)
                                clean_name = self.clean_channel_name(text)
                                
                                if clean_name and len(clean_name) > 2:
                                    channels.append({
                                        'name': clean_name,
                                        'url': full_url,
                                        'source': site_name,
                                        'method': f'selector_{selector[:20]}...',
                                        'original_text': text
                                    })
                        except Exception as e:
                            self.log(f"Error procesando link individual: {e}", "DEBUG")
                            continue
                    
                    self.log(f"Selector {selector[:30]}...: {len([c for c in channels if c.get('method', '').startswith('selector')])} canales válidos")
                    
                except Exception as e:
                    self.log(f"Error con selector {selector}: {e}", "WARNING")
                    continue
            
            # Método 2: Búsqueda por patrones de URL (mejorado)
            try:
                url_patterns = [
                    r'-en-vivo\.html$',
                    r'/ver/[^/]+$',
                    r'/canal/[^/]+$',
                    r'/watch/[^/]+$',
                    r'/live/[^/]+$',
                    r'/tv/[^/]+$',
                    r'/stream/[^/]+$'
                ]
                
                all_links = soup.find_all('a', href=True)
                self.log(f"Total links en página: {len(all_links)}", "DEBUG")
                
                for link in all_links:
                    try:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if href and text and len(text) > 2:
                            for pattern in url_patterns:
                                if re.search(pattern, href, re.IGNORECASE):
                                    full_url = urljoin(base_url, href)
                                    clean_name = self.clean_channel_name(text)
                                    
                                    if clean_name and not any(c['url'] == full_url for c in channels):
                                        channels.append({
                                            'name': clean_name,
                                            'url': full_url,
                                            'source': site_name,
                                            'method': f'pattern_{pattern[:15]}...',
                                            'original_text': text
                                        })
                                    break
                    except Exception as e:
                        self.log(f"Error procesando pattern link: {e}", "DEBUG")
                        continue
            
            except Exception as e:
                self.log(f"Error en búsqueda por patrones: {e}", "WARNING")
            
            # Método 3: Búsqueda por palabras clave de TV (mejorado)
            try:
                tv_keywords = [
                    'espn', 'fox', 'cnn', 'discovery', 'history', 'disney', 'cartoon',
                    'nickelodeon', 'nick', 'mtv', 'vh1', 'comedy', 'fx', 'tnt', 'hbo', 'showtime',
                    'univision', 'telemundo', 'caracol', 'rcn', 'teleantioquia', 'win',
                    'canal', 'telecafe', 'telepacifico', 'nat geo', 'national geographic',
                    'animal planet', 'netflix', 'amazon', 'prime', 'sony', 'warner',
                    'paramount', 'universal', 'studio', 'sports', 'deportes', 'news',
                    'noticias', 'music', 'musica', 'kids', 'infantil', 'cine', 'movies',
                    'films', 'series', 'novelas', 'drama', 'reality', 'documentales'
                ]
                
                for link in all_links:
                    try:
                        text = link.get_text(strip=True).lower()
                        href = link.get('href')
                        
                        if any(keyword in text for keyword in tv_keywords) and href:
                            full_url = urljoin(base_url, href)
                            clean_name = self.clean_channel_name(link.get_text(strip=True))
                            
                            if clean_name and not any(c['url'] == full_url for c in channels):
                                channels.append({
                                    'name': clean_name,
                                    'url': full_url,
                                    'source': site_name,
                                    'method': 'keyword_search',
                                    'original_text': link.get_text(strip=True)
                                })
                    except Exception as e:
                        self.log(f"Error en keyword search: {e}", "DEBUG")
                        continue
            
            except Exception as e:
                self.log(f"Error en búsqueda por keywords: {e}", "WARNING")
            
            # Detectar y manejar duplicados
            unique_channels, duplicates_info = self.detect_duplicates(channels)
            
            self.log(f"🎯 {site_name}: {len(channels)} canales brutos → {len(unique_channels)} únicos")
            if duplicates_info:
                self.log(f"   📊 {len(duplicates_info)} canales con opciones múltiples")
            
            return unique_channels
            
        except Exception as e:
            self.log(f"💥 Error crítico procesando contenido: {e}", "CRITICAL")
            return []
    
    async def process_channel_protected(self, channel, site_config):
        """Procesar canal individual con protección avanzada"""
        channel_name = channel['name']
        channel_url = channel['url']
        
        self.log(f"🔍 Procesando protegido: {channel_name}")
        
        try:
            # Método básico con protección
            response = self.safe_request_with_retries(channel_url, site_config, max_retries=3)
            
            if not response:
                self.log(f"❌ No accesible (protegido): {channel_name}", "WARNING")
                return None
            
            # Extraer con método básico
            video_urls = self.extract_video_urls_advanced(response.text, channel_url)
            
            # Si se requiere JavaScript y está disponible Playwright, intentar
            if not video_urls and PLAYWRIGHT_AVAILABLE and site_config.get("requires_js", False):
                try:
                    self.log(f"🎭 Intentando Playwright para {channel_name}", "DEBUG")
                    video_urls = await self.extract_with_playwright_protected(channel_url, site_config)
                except Exception as e:
                    self.log(f"Error Playwright para {channel_name}: {e}", "WARNING")
            
            if video_urls:
                best_url = video_urls[0]  # Ya están priorizados
                
                self.log(f"✅ {channel_name}: {best_url[:60]}...", "SUCCESS")
                return {
                    'name': channel_name,
                    'url': best_url,
                    'source': channel.get('source', 'unknown'),
                    'original_page': channel_url,
                    'backup_urls': video_urls[1:3] if len(video_urls) > 1 else [],
                    'duplicate_group': channel.get('duplicate_group'),
                    'extraction_method': 'protected'
                }
            
            self.log(f"❌ Sin streams (protegido): {channel_name}", "WARNING")
            return None
            
        except Exception as e:
            self.log(f"❌ Error protegido {channel_name}: {e}", "ERROR")
            return None
    
    async def extract_with_playwright_protected(self, channel_url, site_config):
        """Extracción Playwright con protección anti-detección"""
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        self.log(f"🎭 Playwright protegido: {channel_url[:60]}...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-web-security',
                        '--ignore-certificate-errors',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-images',
                        '--disable-javascript-harmony-shipping',
                        '--disable-ipc-flooding-protection',
                        '--no-first-run',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                )
                
                # User agent aleatorio
                user_agent = random.choice(self.premium_user_agents)
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=user_agent,
                    ignore_https_errors=True,
                    java_script_enabled=True
                )
                
                # Stealth mode básico
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en-US', 'en']});
                """)
                
                page = await context.new_page()
                video_urls = []
                
                async def handle_response(response):
                    url = response.url
                    if any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico']):
                        return
                    
                    for pattern in self.video_patterns:
                        if re.search(pattern, url, re.IGNORECASE):
                            self.log(f"🎥 Playwright detectó: {url[:80]}...", "SUCCESS")
                            video_urls.append(url)
                            return
                
                page.on('response', handle_response)
                
                # Navegar con timeout extendido
                await page.goto(channel_url, wait_until='networkidle', timeout=90000)
                await page.wait_for_timeout(8000)
                
                # Buscar y hacer clic en elementos de reproducción con más paciencia
                play_selectors = [
                    'button[class*="play"]', '.play-button', '.btn-play', '.play-btn',
                    'button', '[onclick*="play"]', '.player-button', '.video-play',
                    '.play-icon', '[data-play]', '.start-button', '.player-start'
                ]
                
                for selector in play_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements[:5]:  # Probar más elementos
                            try:
                                if await element.is_visible():
                                    await element.click(timeout=15000)
                                    await page.wait_for_timeout(12000)  # Esperar más tiempo
                                    if video_urls:
                                        break
                            except:
                                continue
                        if video_urls:
                            break
                    except:
                        continue
                
                # Buscar iframes con más detalle
                iframes = await page.query_selector_all('iframe')
                for iframe in iframes:
                    try:
                        src = await iframe.get_attribute('src')
                        data_src = await iframe.get_attribute('data-src')
                        for url in [src, data_src]:
                            if url and any(service in url.lower() for service in ['stream', 'player', 'embed', 'video']):
                                video_urls.append(url)
                    except:
                        continue
                
                await page.wait_for_timeout(15000)  # Espera final más larga
                await browser.close()
                return video_urls
                
        except Exception as e:
            self.log(f"Error Playwright protegido: {e}", "ERROR")
            return []
    
    def generate_m3u_enhanced(self, all_channels, filename="iptv_definitivo"):
        """Generar M3U optimizado con manejo de duplicados"""
        if not all_channels:
            self.log("❌ No hay canales para M3U", "ERROR")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}.m3u"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                f.write(f"# Generado por IPTV Extractor Definitivo - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total de canales: {len(all_channels)}\n")
                f.write("\n")
                
                # Agrupar por fuente para organización
                by_source = {}
                for channel in all_channels:
                    source = channel.get('source', 'Unknown')
                    if source not in by_source:
                        by_source[source] = []
                    by_source[source].append(channel)
                
                # Escribir canales agrupados por fuente
                for source, channels in by_source.items():
                    f.write(f"# === {source.upper()} ({len(channels)} canales) ===\n")
                    
                    for channel in channels:
                        # Nombre limpio para M3U
                        clean_name = re.sub(r'[^\w\s\-()&+]', '', channel['name']).strip()
                        source_name = source.replace('.com', '').replace('www.', '')
                        
                        # Determinar grupo
                        group_title = "IPTV Live"
                        if any(keyword in clean_name.lower() for keyword in ['sport', 'deporte', 'espn', 'fox']):
                            group_title = "Deportes"
                        elif any(keyword in clean_name.lower() for keyword in ['news', 'noticia', 'cnn']):
                            group_title = "Noticias"
                        elif any(keyword in clean_name.lower() for keyword in ['disney', 'cartoon', 'nick']):
                            group_title = "Infantil"
                        elif any(keyword in clean_name.lower() for keyword in ['movie', 'cinema', 'film']):
                            group_title = "Películas"
                        
                        # Título para M3U
                        title = f"{clean_name} [{source_name}]"
                        
                        # Agregar información de opciones múltiples si existe
                        if channel.get('duplicate_group'):
                            title = f"{clean_name} [{source_name}]"
                        
                        f.write(f'#EXTINF:-1 tvg-logo="" group-title="{group_title}",{title}\n')
                        f.write(f'{channel["url"]}\n')
                    
                    f.write("\n")
            
            self.log(f"✅ M3U generado: {filename}", "SUCCESS")
            return filename
            
        except Exception as e:
            self.log(f"❌ Error generando M3U: {e}", "ERROR")
            return None
    
    def generate_m3u_fixed_name(self, all_channels, filename):
        """Generar M3U con nombre fijo (sin timestamp)"""
        if not all_channels:
            self.log("❌ No hay canales para M3U", "ERROR")
            return None
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
            # Extraer URLs
            urls = re.findall(r'https?://[^\s]+', content)
            
            if not urls:
                self.log("❌ No se encontraron URLs en el M3U", "ERROR")
                return
            
            # Tomar muestra aleatoria
            sample_urls = random.sample(urls, min(sample_size, len(urls)))
            
            working = 0
            total = len(sample_urls)
            
            for i, url in enumerate(sample_urls, 1):
                try:
                    self.log(f"🧪 Verificando {i}/{total}: {url[:50]}...")
                    
                    response = self.session.head(url, timeout=10)
                    if response.status_code < 400:
                        working += 1
                        self.log(f"   ✅ Funciona", "SUCCESS")
                    else:
                        self.log(f"   ❌ Error {response.status_code}", "WARNING")
                        
                except Exception as e:
                    self.log(f"   ❌ Error: {str(e)[:30]}...", "WARNING")
                
                time.sleep(1)
            
            success_rate = (working / total) * 100
            self.log(f"📊 Resultado: {working}/{total} streams funcionan ({success_rate:.1f}%)", 
                    "SUCCESS" if success_rate > 70 else "WARNING")
            
        except Exception as e:
            self.log(f"❌ Error en verificación: {e}", "ERROR")
    
    async def extract_main_source_fast(self, site_name="embed.ksdjugfsddeports.fun"):
        """Método ultra-rápido para extraer de la fuente principal embed.ksdjugfsddeports.fun"""
        self.log(f"🚀 EXTRACCIÓN ULTRA-RÁPIDA: {site_name.upper()}")
        
        site_config = self.site_configs.get(site_name)
        if not site_config:
            self.log(f"❌ Configuración no encontrada para {site_name}", "ERROR")
            return []
        
        base_url = site_config["base_url"]
        channels = []
        
        try:
            # Paso 1: Usar solo requests session sin CloudScraper para evitar problemas SSL
            self.log(f"⚡ Acceso ultra-rápido a {base_url}")
            
            # Crear sesión simple sin problemas SSL
            simple_session = requests.Session()
            simple_session.verify = False
            
            # Headers básicos
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = simple_session.get(base_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                self.log(f"❌ Error HTTP {response.status_code} accediendo a {site_name}", "ERROR")
                return []
            
            self.log(f"✅ Contenido cargado: {len(response.content)} bytes")
            
            # Paso 2: Extracción directa de embed URLs y streams
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Buscar enlaces embebidos directamente
            embed_patterns = [
                r'https?://[^"\']*embed[^"\']*',
                r'https?://[^"\']*player[^"\']*',
                r'https?://[^"\']*stream[^"\']*',
                r'https?://[^"\']*live[^"\']*',
                r'https?://[^"\']*tv[^"\']*\.m3u8[^"\']*',
                r'https?://[^"\']*\.m3u8[^"\']*'
            ]
            
            found_embeds = set()
            for pattern in embed_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                found_embeds.update(matches)
            
            # También buscar en elementos HTML
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if any(keyword in href.lower() for keyword in ['embed', 'player', 'stream', 'live', '.m3u8']):
                    if href.startswith('http'):
                        found_embeds.add(href)
                    else:
                        found_embeds.add(urljoin(base_url, href))
            
            self.log(f"🔍 Encontrados {len(found_embeds)} enlaces potenciales")
            
            # Paso 3: Procesamiento ultra-rápido de embeds
            processed_channels = []
            
            for i, embed_url in enumerate(list(found_embeds)[:30]):  # Limitar a 30 para velocidad
                try:
                    # Generar nombre de canal basado en URL
                    parsed_url = urlparse(embed_url)
                    path_parts = parsed_url.path.strip('/').split('/')
                    
                    if path_parts and path_parts[-1]:
                        channel_name = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
                    else:
                        channel_name = f"Canal {i+1}"
                    
                    # Limpiar y mejorar nombre
                    channel_name = re.sub(r'\.php.*$', '', channel_name)
                    channel_name = re.sub(r'\.html.*$', '', channel_name)
                    channel_name = re.sub(r'\d+$', '', channel_name).strip()
                    
                    if not channel_name or len(channel_name) < 3:
                        channel_name = f"Stream {i+1}"
                    
                    # Si ya es un .m3u8 directo, usarlo
                    if '.m3u8' in embed_url.lower():
                        processed_channels.append({
                            'name': channel_name,
                            'url': embed_url,
                            'source': site_name,
                            'original_page': base_url,
                            'extraction_method': 'direct_m3u8',
                            'embed_type': 'main_source'
                        })
                        self.log(f"   ✅ {channel_name}: M3U8 directo encontrado", "SUCCESS")
                    else:
                        # NUEVA EXTRACCIÓN EN PROFUNDIDAD - Como descubriste
                        self.log(f"⚡ Procesando {i+1}/{len(found_embeds)}: {channel_name}")
                        
                        try:
                            # Paso 1: Obtener la página .php (como tudn.php)
                            stream_response = simple_session.get(embed_url, headers=headers, timeout=10)
                            if stream_response.status_code == 200:
                                
                                # Paso 2: Extraer los iframes embebidos (como embed/tudn.html y embed2/tudn.html)
                                php_content = stream_response.text
                                iframe_patterns = [
                                    r'src="([^"]*embed2/[^"]*\.html[^"]*)"',
                                    r'src="([^"]*embed/[^"]*\.html[^"]*)"',
                                    r'https://embed\.ksdjugfsddeports\.fun/embed2/[^"\']*\.html',
                                    r'https://embed\.ksdjugfsddeports\.fun/embed/[^"\']*\.html'
                                ]
                                
                                iframe_urls = set()
                                for pattern in iframe_patterns:
                                    matches = re.findall(pattern, php_content, re.IGNORECASE)
                                    for match in matches:
                                        if match.startswith('http'):
                                            iframe_urls.add(match)
                                        else:
                                            iframe_urls.add(urljoin(embed_url, match))
                                
                                self.log(f"   🔍 Encontrados {len(iframe_urls)} iframes para {channel_name}", "DEBUG")
                                
                                # Paso 3: Buscar streams en cada iframe
                                video_urls_found = []
                                for iframe_url in list(iframe_urls)[:2]:  # Máximo 2 iframes por canal
                                    try:
                                        iframe_response = simple_session.get(iframe_url, headers=headers, timeout=8)
                                        if iframe_response.status_code == 200:
                                            iframe_video_urls = self.extract_video_urls_advanced(iframe_response.text, iframe_url)
                                            video_urls_found.extend(iframe_video_urls)
                                            
                                            if iframe_video_urls:
                                                self.log(f"   🎯 Iframe {iframe_url[-20:]}... encontró {len(iframe_video_urls)} streams", "DEBUG")
                                    except Exception as e:
                                        self.log(f"   ⚠️ Error en iframe {iframe_url[-20:]}...: {e}", "DEBUG")
                                        continue
                                
                                # Paso 4: Si encontramos streams, usar el mejor
                                if video_urls_found:
                                    best_stream = video_urls_found[0]  # Ya están priorizados
                                    processed_channels.append({
                                        'name': channel_name,
                                        'url': best_stream,
                                        'source': site_name,
                                        'original_page': embed_url,
                                        'backup_urls': video_urls_found[1:3] if len(video_urls_found) > 1 else [],
                                        'extraction_method': 'deep_iframe',
                                        'embed_type': 'main_source',
                                        'iframe_count': len(iframe_urls)
                                    })
                                    
                                    self.log(f"   ✅ {channel_name}: Stream encontrado en iframe ({best_stream[:60]}...)", "SUCCESS")
                                else:
                                    self.log(f"   ⚠️ {channel_name}: Sin streams en iframes", "WARNING")
                            else:
                                self.log(f"   ❌ Error HTTP {stream_response.status_code} para {channel_name}", "WARNING")
                                
                        except Exception as e:
                            self.log(f"   ❌ Error procesando {channel_name}: {e}", "WARNING")
                    
                    # Pausa mínima para no sobrecargar
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    self.log(f"   ❌ Error procesando embed {i+1}: {e}", "WARNING")
                    continue
            
            simple_session.close()
            self.log(f"🎉 EXTRACCIÓN ULTRA-RÁPIDA COMPLETADA: {len(processed_channels)} canales")
            return processed_channels
            
        except Exception as e:
            self.log(f"💥 Error crítico en extracción ultra-rápida: {e}", "CRITICAL")
            return []

async def main():
    """Función principal del extractor definitivo"""
    print("🔥" * 80)
    print("  IPTV EXTRACTOR DEFINITIVO - SCRIPT ÚNICO COMPLETO")
    print("🔥" * 80)
    print()
    print("✨ Características:")
    print("   • Técnicas anti-detección avanzadas")
    print("   • Detección automática de duplicados")
    print("   • URLs corregidas para todos los sitios")
    print("   • Extracción directa de streams .m3u8")
    print("   • Compatible con Smart TV/SSIPTV")
    print("   • Verificación de streams")
    print()
    
    extractor = IPTVExtractorDefinitivo()
    
    print("📋 OPCIONES DISPONIBLES:")
    print("1. 🌍 Extraer TODOS los sitios (Recomendado)")
    print("2. 🎯 Extraer sitio específico")
    print("3. 🔥 PRUEBA ESPECIAL: Solo tvplusgratis2.com (Para verificación)")
    print("4. 🧪 Modo debug - probar canal específico")
    print("5. 📊 Verificar archivo M3U existente")
    print("6. ❓ Mostrar información de sitios")
    print("7. ⚡ ULTRA-RÁPIDO: Fuente principal embed.ksdjugfsddeports.fun (IDEAL)")
    print("   💡 ¿Por qué es IDEAL? Va directo a la fuente original donde las otras")
    print("      páginas obtienen sus streams. URLs .m3u8 más directas y estables")
    print("      para Smart TV/SSIPTV, sin intermediarios que puedan fallar.")
    
    choice = input("\n👉 Seleccione opción (1-7): ").strip()
    
    if choice == "1":
        # Extraer todos los sitios
        extractor.log("🌍 INICIANDO EXTRACCIÓN COMPLETA DE TODOS LOS SITIOS")
        
        all_channels = []
        sites = [name for name, config in extractor.site_configs.items() if config.get("verified_working", False)]
        
        for site_name in sites:
            try:
                extractor.log(f"🌐 PROCESANDO {site_name.upper()} CON PROTECCIÓN AVANZADA")
                site_channels = await extractor.extract_site_complete_protected(site_name)
                all_channels.extend(site_channels)
                
                extractor.log(f"✅ {site_name}: {len(site_channels)} canales extraídos")
                
                # Pausa más larga entre sitios para evitar detección
                await asyncio.sleep(random.uniform(15, 25))
                
            except Exception as e:
                extractor.log(f"❌ Error en {site_name}: {e}", "ERROR")
                continue
        
        if all_channels:
            extractor.log(f"🎊 EXTRACCIÓN COMPLETADA: {len(all_channels)} canales totales", "CRITICAL")
            
            # Generar M3U
            m3u_file = extractor.generate_m3u_enhanced(all_channels)
            
            if m3u_file:
                print(f"\n🎯 RESULTADO FINAL:")
                print(f"   📺 Total canales extraídos: {len(all_channels)}")
                print(f"   📄 Archivo M3U: {m3u_file}")
                
                # Resumen por sitio
                by_site = {}
                for channel in all_channels:
                    site = channel.get('source', 'Unknown')
                    by_site[site] = by_site.get(site, 0) + 1
                
                print(f"\n📊 RESUMEN POR SITIO:")
                for site, count in by_site.items():
                    print(f"   🌐 {site}: {count} canales")
                
                # Preguntar por verificación
                verify = input(f"\n¿Verificar una muestra de streams? (y/n): ").lower().strip()
                if verify == 'y':
                    sample_size = int(input("Número de streams a verificar (default: 10): ") or "10")
                    extractor.verify_streams_sample(m3u_file, sample_size)
        else:
            extractor.log("❌ No se pudieron extraer canales de ningún sitio", "ERROR")
    
    elif choice == "2":
        # Extraer sitio específico
        sites = list(extractor.site_configs.keys())
        print(f"\n📋 SITIOS DISPONIBLES:")
        for i, site in enumerate(sites, 1):
            status = "✅" if extractor.site_configs[site].get("verified_working") else "⚠️"
            print(f"{i}. {status} {site}")
        
        try:
            site_choice = int(input(f"\n👉 Seleccione sitio (1-{len(sites)}): ")) - 1
            if 0 <= site_choice < len(sites):
                site_name = sites[site_choice]
                
                extractor.log(f"🎯 Extrayendo {site_name.upper()} con protección avanzada")
                channels = await extractor.extract_site_complete_protected(site_name)
                
                if channels:
                    m3u_file = extractor.generate_m3u_enhanced(channels, f"iptv_{site_name}")
                    if m3u_file:
                        print(f"\n✅ Extracción completada:")
                        print(f"   📺 Canales: {len(channels)}")
                        print(f"   📄 Archivo: {m3u_file}")
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Entrada inválida")
    
    elif choice == "3":
        # Prueba especial de tvplusgratis2
        extractor.log("🔥 PRUEBA ESPECIAL: TVPLUSGRATIS2.COM CON MÁXIMA PROTECCIÓN")
        
        try:
            channels = await extractor.extract_site_complete_protected("tvplusgratis2.com")
            
            if channels:
                extractor.log(f"🎊 EXTRACCIÓN EXITOSA: {len(channels)} canales encontrados", "CRITICAL")
                
                # Generar M3U especial para verificación
                m3u_file = extractor.generate_m3u_enhanced(channels, "tvplusgratis2_prueba")
                
                if m3u_file:
                    print(f"\n🎯 RESULTADO DE PRUEBA:")
                    print(f"   📺 Canales extraídos: {len(channels)}")
                    print(f"   📄 Archivo M3U: {m3u_file}")
                    
                    # Mostrar lista de canales encontrados
                    print(f"\n📋 CANALES ENCONTRADOS:")
                    for i, channel in enumerate(channels[:20], 1):  # Mostrar primeros 20
                        print(f"   {i:2d}. {channel['name']} - {channel['url'][:60]}...")
                    
                    if len(channels) > 20:
                        print(f"   ... y {len(channels) - 20} canales más")
                    
                    # Preguntar por verificación automática
                    verify = input(f"\n¿Verificar automáticamente los streams? (y/n): ").lower().strip()
                    if verify == 'y':
                        sample_size = min(len(channels), 10)
                        extractor.verify_streams_sample(m3u_file, sample_size)
                    
                    # Estadísticas de extracción
                    print(f"\n📊 ESTADÍSTICAS DE EXTRACCIÓN:")
                    print(f"   🌐 Requests totales: {extractor.request_count}")
                    print(f"   🚫 Bloqueos detectados: {extractor.blocked_count}")
                    print(f"   ✅ Tasa de éxito: {((extractor.request_count - extractor.blocked_count) / max(extractor.request_count, 1) * 100):.1f}%")
            else:
                extractor.log("❌ No se pudieron extraer canales de tvplusgratis2.com", "ERROR")
                print("\n💡 SUGERENCIAS:")
                print("   - Verificar conexión a internet")
                print("   - El sitio puede estar temporalmente inaccesible")
                print("   - Intentar más tarde o usar VPN")
        
        except Exception as e:
            extractor.log(f"💥 Error en prueba especial: {e}", "CRITICAL")
    
    elif choice == "4":
        # Modo debug
        test_url = input("\n👉 URL del canal a probar: ").strip()
        if test_url:
            site_name = urlparse(test_url).netloc
            site_config = None
            
            # Buscar configuración
            for name, config in extractor.site_configs.items():
                if name in site_name:
                    site_config = config
                    break
            
            if not site_config:
                site_config = {"anti_cloudflare": True, "requires_js": True}
            
            extractor.log(f"🧪 PROBANDO: {test_url}")
            
            # Método básico
            response = extractor.safe_request(test_url, site_config)
            if response:
                urls_basic = extractor.extract_video_urls_advanced(response.text, test_url)
                print(f"\n🔧 Método básico: {len(urls_basic)} URLs")
                for i, url in enumerate(urls_basic[:5], 1):
                    print(f"   {i}. {url}")
            
            # Playwright si disponible
            if PLAYWRIGHT_AVAILABLE:
                urls_pw = await extractor.extract_with_playwright(test_url, site_config)
                print(f"\n🎭 Playwright: {len(urls_pw)} URLs")
                for i, url in enumerate(urls_pw[:5], 1):
                    print(f"   {i}. {url}")
    
    elif choice == "5":
        # Verificar M3U existente
        m3u_files = [f for f in os.listdir('.') if f.endswith('.m3u')]
        if m3u_files:
            print(f"\n📋 ARCHIVOS M3U ENCONTRADOS:")
            for i, file in enumerate(m3u_files, 1):
                print(f"{i}. {file}")
            
            try:
                file_choice = int(input(f"\n👉 Seleccione archivo (1-{len(m3u_files)}): ")) - 1
                if 0 <= file_choice < len(m3u_files):
                    selected_file = m3u_files[file_choice]
                    sample_size = int(input("Número de streams a verificar (default: 10): ") or "10")
                    extractor.verify_streams_sample(selected_file, sample_size)
            except ValueError:
                print("❌ Entrada inválida")
        else:
            print("❌ No se encontraron archivos M3U")
    
    elif choice == "6":
        # Información de sitios
        print(f"\n📊 INFORMACIÓN DE SITIOS:")
        for site_name, config in extractor.site_configs.items():
            status = "✅ Verificado" if config.get("verified_working") else "⚠️ No verificado"
            cloudflare = "🛡️ Anti-Cloudflare" if config.get("anti_cloudflare") else "🔓 Sin protección"
            js = "🎭 Requiere JS" if config.get("requires_js") else "📄 HTML estático"
            
            print(f"\n🌐 {site_name.upper()}")
            print(f"   URL: {config['base_url']}")
            print(f"   Estado: {status}")
            print(f"   Protección: {cloudflare}")
            print(f"   Tecnología: {js}")
            print(f"   Formato URL: {config['url_format']}")
    
    elif choice == "7":
        # Ultra-rápido: Fuente principal
        extractor.log("⚡ MODO ULTRA-RÁPIDO: FUENTE PRINCIPAL")
        extractor.log("🎯 Extrayendo de embed.ksdjugfsddeports.fun con velocidad máxima")
        
        try:
            channels = await extractor.extract_main_source_fast()
            
            if channels:
                extractor.log(f"🚀 EXTRACCIÓN ULTRA-RÁPIDA COMPLETADA: {len(channels)} canales", "CRITICAL")
                
                # Generar M3U ultra-rápido con nombre específico (sin timestamp)
                m3u_file = extractor.generate_m3u_fixed_name(channels, "iptvfuenteprincipal.m3u")
                
                if m3u_file:
                    print(f"\n⚡ RESULTADO ULTRA-RÁPIDO:")
                    print(f"   📺 Canales extraídos: {len(channels)}")
                    print(f"   📄 Archivo M3U: {m3u_file}")
                    print(f"   ⏱️ Método: Extracción ultra-rápida de fuente principal")
                    
                    # Mostrar muestra de canales
                    print(f"\n📋 MUESTRA DE CANALES (primeros 10):")
                    for i, channel in enumerate(channels[:10], 1):
                        print(f"   {i:2d}. {channel['name']} - {channel['url'][:60]}...")
                    
                    if len(channels) > 10:
                        print(f"   ... y {len(channels) - 10} canales más")
                    
                    # Estadísticas de velocidad
                    print(f"\n📊 ESTADÍSTICAS ULTRA-RÁPIDAS:")
                    print(f"   🌐 Requests realizados: {extractor.request_count}")
                    print(f"   ⚡ Método de extracción: Ultra-rápido directo")
                    print(f"   🎯 Fuente: embed.ksdjugfsddeports.fun")
                    
                    # Preguntar por verificación con manejo de errores
                    try:
                        verify = input(f"\n¿Verificar una muestra rápida de streams? (y/n): ").lower().strip()
                        if verify == 'y':
                            sample_size = min(len(channels), 5)  # Muestra más pequeña para velocidad
                            extractor.verify_streams_sample(m3u_file, sample_size)
                        else:
                            print(f"\n✅ Archivo M3U listo para usar en Smart TV/SSIPTV")
                    except (EOFError, KeyboardInterrupt):
                        print(f"\n⚠️ Verificación saltada - Archivo M3U listo para usar")
            else:
                extractor.log("❌ No se pudieron extraer canales de la fuente principal", "ERROR")
                print("\n💡 SUGERENCIAS:")
                print("   - Verificar conexión a internet")
                print("   - La fuente principal puede estar temporalmente inaccesible")
                print("   - Intentar opción 1 (todos los sitios) como alternativa")
        
        except Exception as e:
            extractor.log(f"💥 Error en extracción ultra-rápida: {e}", "CRITICAL")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Extracción cancelada por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error crítico: {e}")
        print("💡 Tip: Asegúrese de tener instalado: pip install requests beautifulsoup4 cloudscraper")
