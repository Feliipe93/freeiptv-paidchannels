#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificador completo de estructuras de URL para todos los sitios IPTV
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time

def test_site_structure(site_name, base_url, test_channels):
    """Verifica la estructura de URLs de un sitio específico"""
    print(f"\n{'='*60}")
    print(f"🌐 VERIFICANDO {site_name.upper()}")
    print(f"{'='*60}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://google.com/',
    })
    
    try:
        # Verificar página principal
        print(f"📍 URL base: {base_url}")
        response = session.get(base_url, timeout=15)
        print(f"Status página principal: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ No se puede acceder a la página principal")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar patrones de canales en la página principal
        all_links = soup.find_all('a', href=True)
        channel_links = []
        
        # Patrones comunes para canales
        channel_patterns = [
            r'/ver/', r'/canal/', r'/channel/', r'/tv/', r'/stream/',
            r'/live/', r'/watch/', r'/player/', r'/embed/', r'-en-vivo'
        ]
        
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href and any(pattern in href.lower() for pattern in channel_patterns):
                full_url = urljoin(base_url, href)
                channel_links.append({
                    'url': full_url,
                    'text': text[:50],
                    'href': href
                })
        
        print(f"Canales encontrados en página principal: {len(channel_links)}")
        
        # Mostrar algunos ejemplos de estructura encontrada
        print(f"\n📋 ESTRUCTURA DE URLs ENCONTRADA:")
        for i, channel in enumerate(channel_links[:10]):
            print(f"  {i+1:2d}. {channel['text'][:30]:30} -> {channel['href']}")
        
        # Probar canales específicos
        print(f"\n🧪 PROBANDO CANALES ESPECÍFICOS:")
        working_channels = []
        
        for channel_info in test_channels:
            channel_name = channel_info['name']
            test_urls = channel_info['urls']
            
            print(f"\n📡 Canal: {channel_name}")
            
            found_working = False
            for i, test_url in enumerate(test_urls, 1):
                try:
                    print(f"   Probando formato {i}: {test_url}")
                    channel_response = session.get(test_url, timeout=10)
                    
                    if channel_response.status_code == 200:
                        print(f"   ✅ FUNCIONA (Status: {channel_response.status_code}, {len(channel_response.content)} bytes)")
                        working_channels.append({
                            'name': channel_name,
                            'url': test_url,
                            'content_length': len(channel_response.content)
                        })
                        found_working = True
                        break
                    else:
                        print(f"   ❌ Error {channel_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)[:50]}...")
            
            if not found_working:
                print(f"   ⚠️ Ningún formato funcionó para {channel_name}")
            
            time.sleep(1)  # Pausa entre requests
        
        # Resumen
        print(f"\n📊 RESUMEN PARA {site_name.upper()}:")
        print(f"   Total canales encontrados: {len(channel_links)}")
        print(f"   Canales de prueba funcionando: {len(working_channels)}")
        
        if working_channels:
            print(f"   ✅ Canales funcionando:")
            for channel in working_channels:
                print(f"      • {channel['name']} -> {channel['url']}")
        
        return working_channels
        
    except Exception as e:
        print(f"❌ Error general en {site_name}: {e}")
        return []

def main():
    """Verificar todos los sitios IPTV"""
    print("🔍 VERIFICADOR COMPLETO DE SITIOS IPTV")
    print("=" * 70)
    
    # Configuración de todos los sitios a verificar
    sites_to_test = {
        "tvplusgratis2.com": {
            "base_url": "https://tvplusgratis2.com",
            "test_channels": [
                {
                    "name": "ESPN",
                    "urls": [
                        "https://tvplusgratis2.com/espn-en-vivo.html",
                        "https://tvplusgratis2.com/espn-en-vivo",
                        "https://tvplusgratis2.com/ver/espn",
                        "https://tvplusgratis2.com/canal/espn"
                    ]
                },
                {
                    "name": "Sky Sports La Liga", 
                    "urls": [
                        "https://tvplusgratis2.com/sky-sports-la-liga-en-vivo.html",
                        "https://tvplusgratis2.com/sky-sports-la-liga-en-vivo",
                        "https://tvplusgratis2.com/ver/sky-sports-la-liga",
                        "https://tvplusgratis2.com/canal/sky-sports-la-liga"
                    ]
                },
                {
                    "name": "History Channel",
                    "urls": [
                        "https://tvplusgratis2.com/history-channel-en-vivo.html",
                        "https://tvplusgratis2.com/history-en-vivo.html",
                        "https://tvplusgratis2.com/history-channel-en-vivo",
                        "https://tvplusgratis2.com/ver/history-channel"
                    ]
                }
            ]
        },
        
        "telegratishd.com": {
            "base_url": "https://telegratishd.com",
            "test_channels": [
                {
                    "name": "ESPN",
                    "urls": [
                        "https://telegratishd.com/espn-en-vivo.html",
                        "https://telegratishd.com/espn-en-vivo",
                        "https://telegratishd.com/ver/espn",
                        "https://telegratishd.com/canal/espn",
                        "https://telegratishd.com/espn"
                    ]
                },
                {
                    "name": "Fox Sports",
                    "urls": [
                        "https://telegratishd.com/fox-sports-en-vivo.html",
                        "https://telegratishd.com/fox-sports-en-vivo",
                        "https://telegratishd.com/ver/fox-sports",
                        "https://telegratishd.com/canal/fox-sports",
                        "https://telegratishd.com/fox-sports"
                    ]
                },
                {
                    "name": "Discovery Channel",
                    "urls": [
                        "https://telegratishd.com/discovery-channel-en-vivo.html",
                        "https://telegratishd.com/discovery-channel-en-vivo",
                        "https://telegratishd.com/ver/discovery-channel",
                        "https://telegratishd.com/canal/discovery-channel",
                        "https://telegratishd.com/discovery-channel"
                    ]
                }
            ]
        },
        
        "vertvcable.com": {
            "base_url": "https://vertvcable.com",
            "test_channels": [
                {
                    "name": "ESPN",
                    "urls": [
                        "https://vertvcable.com/espn",
                        "https://vertvcable.com/ver/espn",
                        "https://vertvcable.com/canal/espn",
                        "https://vertvcable.com/espn-en-vivo",
                        "https://vertvcable.com/live/espn"
                    ]
                },
                {
                    "name": "CNN",
                    "urls": [
                        "https://vertvcable.com/cnn",
                        "https://vertvcable.com/ver/cnn", 
                        "https://vertvcable.com/canal/cnn",
                        "https://vertvcable.com/cnn-en-vivo",
                        "https://vertvcable.com/live/cnn"
                    ]
                },
                {
                    "name": "Fox Sports",
                    "urls": [
                        "https://vertvcable.com/fox-sports",
                        "https://vertvcable.com/ver/fox-sports",
                        "https://vertvcable.com/canal/fox-sports", 
                        "https://vertvcable.com/fox-sports-en-vivo",
                        "https://vertvcable.com/live/fox-sports"
                    ]
                }
            ]
        },
        
        "cablevisionhd.com": {
            "base_url": "https://cablevisionhd.com",
            "test_channels": [
                {
                    "name": "ESPN",
                    "urls": [
                        "https://cablevisionhd.com/espn",
                        "https://cablevisionhd.com/ver/espn",
                        "https://cablevisionhd.com/canal/espn",
                        "https://cablevisionhd.com/espn-en-vivo",
                        "https://cablevisionhd.com/watch/espn"
                    ]
                },
                {
                    "name": "National Geographic",
                    "urls": [
                        "https://cablevisionhd.com/national-geographic",
                        "https://cablevisionhd.com/ver/national-geographic",
                        "https://cablevisionhd.com/canal/national-geographic",
                        "https://cablevisionhd.com/nat-geo",
                        "https://cablevisionhd.com/natgeo"
                    ]
                },
                {
                    "name": "Discovery",
                    "urls": [
                        "https://cablevisionhd.com/discovery",
                        "https://cablevisionhd.com/ver/discovery",
                        "https://cablevisionhd.com/canal/discovery",
                        "https://cablevisionhd.com/discovery-channel",
                        "https://cablevisionhd.com/watch/discovery"
                    ]
                }
            ]
        }
    }
    
    # Verificar todos los sitios
    all_results = {}
    
    for site_name, config in sites_to_test.items():
        try:
            working_channels = test_site_structure(
                site_name, 
                config["base_url"], 
                config["test_channels"]
            )
            all_results[site_name] = working_channels
            
            # Pausa entre sitios
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error verificando {site_name}: {e}")
            all_results[site_name] = []
    
    # Resumen final
    print(f"\n{'='*70}")
    print("📋 RESUMEN FINAL DE VERIFICACIÓN")
    print(f"{'='*70}")
    
    total_working = 0
    for site_name, channels in all_results.items():
        print(f"\n🌐 {site_name.upper()}:")
        if channels:
            print(f"   ✅ {len(channels)} canales funcionando")
            for channel in channels:
                print(f"      • {channel['name']}")
            total_working += len(channels)
        else:
            print(f"   ❌ Ningún canal funcionando")
    
    print(f"\n🎯 TOTAL DE CANALES FUNCIONANDO: {total_working}")
    
    # Generar recomendaciones de corrección
    print(f"\n🔧 RECOMENDACIONES DE CORRECCIÓN:")
    for site_name, channels in all_results.items():
        if channels:
            # Analizar patrón de URLs funcionando
            working_urls = [ch['url'] for ch in channels]
            
            # Determinar patrón común
            if any('.html' in url for url in working_urls):
                print(f"   {site_name}: Usar formato .html")
            elif any('/ver/' in url for url in working_urls):
                print(f"   {site_name}: Usar formato /ver/")
            elif any('/canal/' in url for url in working_urls):
                print(f"   {site_name}: Usar formato /canal/")
            else:
                print(f"   {site_name}: Usar formato directo sin extensión")

if __name__ == "__main__":
    main()
