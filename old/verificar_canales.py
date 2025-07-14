#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def verificar_canales_tvplus():
    """Verifica qué canales de tvplusgratis2 existen realmente"""
    
    # URLs que sabemos que funcionan desde la verificación inicial
    canales_verificados = [
        'aym-sports-en-vivo.html',
        'azteca-deportes-en-vivo.html', 
        'tvc-deportes-en-vivo.html',
        'sky-sports-la-liga-en-vivo.html',
        'liga-1-en-vivo.html',
        'liga-1-max-en-vivo.html',
        'gol-peru-en-vivo.html',
        'tnt-sports-en-vivo.html',
        'tnt-sports-chile-en-vivo.html',
        'fox-sports-premium-en-vivo.html',
        'tyc-sports-en-vivo.html',
        'directv-sports-en-vivo.html',
        'directv-sports-2-en-vivo.html',
        'directv-sports-plus-en-vivo.html',
        'espn-premium-en-vivo.html',
        'espn-en-vivo.html',
        'espn-2-en-vivo.html',
        'espn-3-en-vivo.html',
        'espn-4-en-vivo.html',
        'espn-5-en-vivo.html',
        'espn-6-en-vivo.html',
        'espn-7-en-vivo.html',
        'espn-extra-en-vivo.html',
        'fox-sports-en-vivo.html',
        'fox-sports-2-en-vivo.html', 
        'fox-sports-3-en-vivo.html',
        'cartoon-network-en-vivo.html',
        'disney-channel-en-vivo.html',
        'disney-junior-en-vivo.html',
        'nickelodeon-en-vivo.html',
        'discovery-channel-en-vivo.html',
        'discovery-kids-en-vivo.html',
        'animal-planet-en-vivo.html',
        'nat-geo-en-vivo.html',
        'universal-channel-en-vivo.html',
        'tnt-en-vivo.html',
        'star-channel-en-vivo.html',
        'warner-channel-en-vivo.html',
        'fx-en-vivo.html',
        'cnn-en-espanol-en-vivo.html',
        'telemundo-en-vivo.html',
        'univision-en-vivo.html'
    ]
    
    base_url = 'https://www.tvplusgratis2.com/'
    
    print("🔍 VERIFICANDO CANALES DE TVPLUSGRATIS2")
    print("=" * 60)
    
    working_channels = []
    failed_channels = []
    
    for i, canal in enumerate(canales_verificados, 1):
        url = base_url + canal
        name = canal.replace('-en-vivo.html', '').replace('-', ' ').title()
        
        print(f"📡 {i:2d}/42: {name}")
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                print(f"     ✅ OK")
                working_channels.append({'name': name, 'url': url})
            else:
                print(f"     ❌ Error {response.status_code}")
                failed_channels.append({'name': name, 'url': url, 'error': response.status_code})
                
        except Exception as e:
            print(f"     💥 Error: {str(e)[:50]}")
            failed_channels.append({'name': name, 'url': url, 'error': str(e)[:50]})
    
    print(f"\n📊 RESULTADOS:")
    print(f"✅ Canales funcionando: {len(working_channels)}")
    print(f"❌ Canales con error: {len(failed_channels)}")
    
    if failed_channels:
        print(f"\n❌ CANALES CON PROBLEMAS:")
        for canal in failed_channels:
            print(f"   • {canal['name']} - {canal['error']}")
    
    return working_channels, failed_channels

if __name__ == "__main__":
    working, failed = verificar_canales_tvplus()
