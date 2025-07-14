#!/usr/bin/env python3

# Prueba directa de extracción de tvplusgratis2
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from iptv import IPTVExtractor

def test_tvplusgratis2():
    print("🧪 PRUEBA DIRECTA DE TVPLUSGRATIS2")
    print("=" * 50)
    
    extractor = IPTVExtractor()
    
    # Probar solo unas pocas URLs para verificar
    test_channels = [
        {'name': 'Sky Sports La Liga', 'logo': '', 'url': 'https://www.tvplusgratis2.com/sky-sports-la-liga-en-vivo.html'},
        {'name': 'ESPN', 'logo': '', 'url': 'https://www.tvplusgratis2.com/espn-en-vivo.html'},
        {'name': 'History', 'logo': '', 'url': 'https://www.tvplusgratis2.com/history-en-vivo.html'}
    ]
    
    print(f"📺 Probando {len(test_channels)} canales...")
    
    streams = []
    for i, channel in enumerate(test_channels, 1):
        print(f"\n📡 Canal {i}: {channel['name']}")
        
        try:
            content = extractor.make_request(channel['url'], use_proxy=False)
            
            if content:
                print(f"   ✅ Página accesible ({len(content)} caracteres)")
                
                # Buscar contenido de video básico
                if 'iframe' in content.lower():
                    print("   🎬 iframes detectados")
                if 'm3u8' in content.lower():
                    print("   📺 Enlaces m3u8 detectados")
                if 'player' in content.lower():
                    print("   ▶️  Player detectado")
                    
                streams.append({
                    'name': channel['name'],
                    'url': channel['url'],
                    'source': 'tvplusgratis2'
                })
            else:
                print("   ❌ No se pudo acceder")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)[:100]}")
    
    print(f"\n📊 RESULTADO: {len(streams)} canales procesados exitosamente")
    
    if streams:
        print("\n📺 CANALES PROCESADOS:")
        for stream in streams:
            print(f"   • {stream['name']} -> {stream['url']}")
    
    return streams

if __name__ == "__main__":
    test_tvplusgratis2()
