#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from iptv import IPTVExtractor

def test_stream_extraction():
    print("🧪 PRUEBA DE EXTRACCIÓN DE STREAMS DIRECTOS")
    print("=" * 60)
    
    extractor = IPTVExtractor()
    
    # Probar un canal específico que sabemos que funciona
    test_url = 'https://www.tvplusgratis2.com/espn-en-vivo.html'
    
    print(f"📺 Probando: ESPN")
    print(f"🔗 URL: {test_url}")
    
    try:
        content = extractor.make_request(test_url, use_proxy=False)
        
        if content:
            print(f"✅ Página cargada ({len(content)} caracteres)")
            
            # Extraer streams
            video_urls = extractor._extract_video_urls_from_content(content, test_url)
            
            print(f"\n📊 RESULTADOS:")
            print(f"🎬 URLs de video encontradas: {len(video_urls)}")
            
            if video_urls:
                for i, url in enumerate(video_urls, 1):
                    print(f"\n{i}. {url}")
                    
                    # Analizar tipo de URL
                    if '.m3u8' in url:
                        print("   📺 Tipo: HLS Stream (.m3u8) - ¡PERFECTO para SSIPTV!")
                    elif '.mp4' in url:
                        print("   🎞️  Tipo: Video directo (.mp4)")
                    elif '.ts' in url:
                        print("   📡 Tipo: Transport Stream (.ts)")
                    elif 'iframe' in url or 'embed' in url:
                        print("   🖼️  Tipo: iFrame embebido")
                    else:
                        print("   ❓ Tipo: Desconocido")
            else:
                print("❌ No se encontraron URLs de video")
                
                # Buscar manualmente algunas pistas
                print("\n🔍 Buscando pistas en el contenido...")
                if 'iframe' in content.lower():
                    print("   • Se detectaron iframes")
                if 'm3u8' in content.lower():
                    print("   • Se detectó texto 'm3u8' en la página")
                if 'player' in content.lower():
                    print("   • Se detectó un player de video")
                if 'stream' in content.lower():
                    print("   • Se detectó referencia a streams")
        else:
            print("❌ No se pudo cargar la página")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_stream_extraction()
