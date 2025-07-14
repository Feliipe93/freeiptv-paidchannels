#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import json
import time

def quick_analyze(url, site_name):
    """Análisis rápido de una página web"""
    print(f"\n🔍 ANALIZANDO {site_name.upper()}: {url}")
    print("="*60)
    
    try:
        # Headers realistas
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Status: {response.status_code}")
        print(f"📏 Tamaño: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Análisis básico
            print(f"\n📊 ESTRUCTURA:")
            print(f"   🏷️  Título: {soup.title.string if soup.title else 'N/A'}")
            print(f"   📜 Scripts: {len(soup.find_all('script'))}")
            print(f"   🖼️  iFrames: {len(soup.find_all('iframe'))}")
            print(f"   🎥 Videos: {len(soup.find_all('video'))}")
            print(f"   🔗 Enlaces: {len(soup.find_all('a'))}")
            
            # Buscar patrones de streams
            print(f"\n🎯 BÚSQUEDA DE STREAMS:")
            
            # Patrones comunes
            patterns = {
                'm3u8': r'["\']([^"\']*\.m3u8[^"\']*)["\']',
                'ts': r'["\']([^"\']*\.ts[^"\']*)["\']',
                'stream_urls': r'["\']([^"\']*stream[^"\']*\.(m3u8|ts)[^"\']*)["\']',
                'source': r'source\s*:\s*["\']([^"\']+)["\']',
                'src': r'src\s*:\s*["\']([^"\']+)["\']',
            }
            
            all_streams = []
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    print(f"   {pattern_name}: {len(matches)} encontrados")
                    for match in matches[:3]:  # Mostrar solo los primeros 3
                        url_match = match if isinstance(match, str) else match[0]
                        if any(ext in url_match.lower() for ext in ['.m3u8', '.ts', 'stream']):
                            all_streams.append(url_match)
                            print(f"      🔗 {url_match}")
            
            # Análisis de scripts interesantes
            print(f"\n📜 SCRIPTS RELEVANTES:")
            scripts = soup.find_all('script')
            interesting_scripts = 0
            
            for script in scripts:
                if script.string:
                    content = script.string.lower()
                    score = content.count('m3u8') + content.count('stream') + content.count('source') + content.count('video')
                    if score > 0:
                        interesting_scripts += 1
                        if interesting_scripts <= 3:  # Mostrar solo los primeros 3
                            print(f"   📝 Script relevante (score: {score}):")
                            preview = script.string[:200] + "..." if len(script.string) > 200 else script.string
                            print(f"      {preview}")
            
            # Análisis de iframes
            print(f"\n🖼️  IFRAMES:")
            iframes = soup.find_all('iframe')
            for i, iframe in enumerate(iframes[:3]):  # Solo los primeros 3
                src = iframe.get('src', 'N/A')
                print(f"   {i+1}. {src}")
                
                # Si es una URL válida, intentar analizarla
                if src.startswith('http'):
                    try:
                        iframe_response = requests.get(src, headers=headers, timeout=10)
                        if iframe_response.status_code == 200:
                            iframe_streams = re.findall(r'["\']([^"\']*\.m3u8[^"\']*)["\']', iframe_response.text, re.IGNORECASE)
                            if iframe_streams:
                                print(f"      🎯 Streams en iframe: {len(iframe_streams)}")
                                for stream in iframe_streams[:2]:
                                    print(f"         🔗 {stream}")
                    except:
                        print(f"      ❌ No se pudo analizar iframe")
            
            # Buscar divs/elementos con clases relacionadas a video
            print(f"\n📺 ELEMENTOS DE VIDEO:")
            video_elements = soup.find_all(attrs={"class": re.compile(r"video|stream|player|canal|tv", re.I)})
            print(f"   Elementos con clases de video: {len(video_elements)}")
            
            for elem in video_elements[:5]:
                classes = ' '.join(elem.get('class', []))
                print(f"   🎬 {elem.name}.{classes}")
            
            # Resumen
            print(f"\n📊 RESUMEN PARA {site_name.upper()}:")
            print(f"   🎯 Total streams potenciales: {len(all_streams)}")
            print(f"   📜 Scripts interesantes: {interesting_scripts}")
            print(f"   🖼️  iFrames: {len(iframes)}")
            print(f"   📺 Elementos de video: {len(video_elements)}")
            
            # Guardar streams encontrados
            if all_streams:
                filename = f"{site_name}_streams_found.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Streams encontrados en {url}\n")
                    f.write("="*50 + "\n")
                    for stream in all_streams:
                        f.write(f"{stream}\n")
                print(f"   💾 Streams guardados en: {filename}")
            
            return all_streams
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error analizando {site_name}: {e}")
        return []

def main():
    pages = [
        ('https://www.tvplusgratis2.com/', 'tvplusgratis2'),
        ('https://www.vertvcable.com/', 'vertvcable'),
        ('https://www.cablevisionhd.com/', 'cablevisionhd'),
        ('https://www.telegratishd.com/', 'telegratishd')
    ]
    
    print("🔍 ANÁLISIS RÁPIDO DE PÁGINAS IPTV")
    print("="*50)
    
    all_found_streams = []
    
    for url, name in pages:
        streams = quick_analyze(url, name)
        all_found_streams.extend(streams)
        time.sleep(2)  # Pausa entre análisis
    
    print(f"\n🎉 ANÁLISIS COMPLETO FINALIZADO")
    print(f"📊 Total de streams encontrados: {len(all_found_streams)}")
    
    if all_found_streams:
        print(f"\n🔗 ALGUNOS STREAMS ENCONTRADOS:")
        for i, stream in enumerate(all_found_streams[:10]):
            print(f"   {i+1}. {stream}")
        
        # Guardar todo en un archivo resumen
        with open("all_streams_analysis.txt", 'w', encoding='utf-8') as f:
            f.write("ANÁLISIS COMPLETO DE STREAMS IPTV\n")
            f.write("="*50 + "\n\n")
            for stream in all_found_streams:
                f.write(f"{stream}\n")
        
        print(f"\n💾 Todos los streams guardados en: all_streams_analysis.txt")
    
    print(f"\n💡 PRÓXIMOS PASOS:")
    print(f"   1. Revisar los archivos generados")
    print(f"   2. Identificar patrones comunes")
    print(f"   3. Desarrollar extractores específicos")
    print(f"   4. Probar streams encontrados")

if __name__ == "__main__":
    main()
