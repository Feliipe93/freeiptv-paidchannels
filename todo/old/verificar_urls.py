#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time

def verificar_sitio(nombre, base_url):
    print(f"\n=== VERIFICANDO {nombre.upper()} ===")
    try:
        response = requests.get(base_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar enlaces de canales
            links = soup.find_all('a', href=True)
            channel_links = []
            
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and text:
                    # Filtros para identificar canales
                    if any(keyword in href.lower() for keyword in ['vivo', 'live', 'canal', 'channel', 'tv']):
                        if any(keyword in text.lower() for keyword in ['espn', 'fox', 'discovery', 'history', 'tnt', 'universal', 'cartoon', 'disney', 'nick', 'cnn', 'sports', 'deportes', 'caracol', 'rcn', 'telemundo', 'gol', 'liga']):
                            # Convertir a URL absoluta si es necesaria
                            if href.startswith('/'):
                                href = base_url.rstrip('/') + href
                            elif not href.startswith('http'):
                                href = base_url.rstrip('/') + '/' + href
                            channel_links.append((text, href))
            
            # Remover duplicados
            channel_links = list(dict.fromkeys(channel_links))
            
            print(f"Canales encontrados: {len(channel_links)}")
            for i, (name, url) in enumerate(channel_links[:10]):  # Mostrar primeros 10
                print(f"{i+1:2d}. {name[:40]:40s} -> {url}")
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")

# Verificar todos los sitios
sites = [
    ('tvplusgratis2.com', 'https://tvplusgratis2.com'),
    ('vertvcable.com', 'https://vertvcable.com'),
    ('cablevisionhd.com', 'https://www.cablevisionhd.com'),
    ('telegratishd.com', 'https://telegratishd.com')
]

for site_name, base_url in sites:
    verificar_sitio(site_name, base_url)
    time.sleep(2)  # Pausa entre sitios

print("\n=== VERIFICACIÓN COMPLETA ===")
