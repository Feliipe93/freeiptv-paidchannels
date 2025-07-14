#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def test_url(name, url):
    print(f"\n🔍 Probando: {name}")
    print(f"📄 URL: {url}")
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar iframes
            iframes = soup.find_all('iframe')
            print(f"🖼️  iframes encontrados: {len(iframes)}")
            
            # Buscar scripts de video
            scripts = soup.find_all('script')
            video_scripts = [s for s in scripts if s.string and any(keyword in s.string.lower() for keyword in ['m3u8', 'video', 'player', 'stream'])]
            print(f"🎬 Scripts de video: {len(video_scripts)}")
            
            print("✅ Página accesible")
        else:
            print("❌ Error de acceso")
            
    except Exception as e:
        print(f"💥 Error: {str(e)[:100]}")

# Probar algunas URLs corregidas
test_urls = [
    ('Sky Sports La Liga', 'https://www.tvplusgratis2.com/sky-sports-la-liga-en-vivo.html'),
    ('History Channel', 'https://www.telegratishd.com/history-en-vivo.html'),
    ('ESPN', 'https://vertvcable.com/espn-en-vivo/'),
    ('Fox Sports', 'https://www.cablevisionhd.com/fox-sports-en-vivo/')
]

print("🧪 PRUEBA DE URLs CORREGIDAS")
print("=" * 50)

for name, url in test_urls:
    test_url(name, url)

print("\n✅ PRUEBA COMPLETADA")
