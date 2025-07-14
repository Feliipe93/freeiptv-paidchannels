# 🎬 IPTV Extractor Avanzado

Herramienta avanzada para extraer y verificar streams IPTV de múltiples páginas web con protección anti-bot y verificación de proxies.

## 🚀 Características

- ✅ Extracción de múltiples páginas simultáneamente
- 🔄 Múltiples métodos de extracción (requests, cloudscraper, selenium)
- 🌐 Manejo automático de proxies
- 🛡️ Evasión de protecciones anti-bot
- 📊 Verificación de streams en tiempo real
- 💾 Múltiples formatos de guardado (combinado/separado)
- 🎯 Interfaz de menú interactiva
- 🔍 Detección de streams en JavaScript y Base64

## 📋 Páginas Soportadas

1. **tvplusgratis2.com** - Canales gratuitos
2. **vertvcable.com** - Streams de cable
3. **cablevisionhd.com** - Canales HD
4. **telegratishd.com** - Streams telegram

## 🛠️ Instalación

### Método 1: Instalación Automática (Recomendado)
```bash
# Ejecutar el instalador
install.bat
```

### Método 2: Instalación Manual
```bash
# Instalar dependencias
pip install -r requirements.txt

# Instalar Chrome (si no lo tienes)
# Descargar desde: https://www.google.com/chrome/
```

## 📦 Dependencias

- **requests** - Peticiones HTTP básicas
- **beautifulsoup4** - Parser HTML
- **lxml** - Parser XML/HTML rápido
- **selenium** - Automatización del navegador
- **cloudscraper** - Evasión de CloudFlare
- **js2py** - Ejecución de JavaScript
- **PyExecJS** - Motor JavaScript alternativo

## 🎮 Uso

```bash
python iptv.py
```

### Menú Principal
1. **Extraer streams** - Extraer de páginas web
2. **Verificar M3U** - Verificar archivo existente
3. **Salir** - Terminar programa

### Opciones de Extracción
- **Individual** - Una página específica
- **Múltiple** - Varias páginas (ej: 1,2,4)
- **Todas** - Todas las páginas disponibles

### Opciones de Verificación
- **Verificar** - Comprobar que los streams funcionen
- **Sin verificar** - Guardar directamente
- **Cancelar** - Volver al menú

### Opciones de Guardado
- **Archivo único** - Todos los streams en un M3U
- **Archivos separados** - Un M3U por página
- **Ambos** - Combinado + separados
- **No guardar** - Solo mostrar resultados

## 🔧 Características Técnicas

### Métodos de Extracción
1. **Requests estándar** - Peticiones HTTP normales
2. **CloudScraper** - Evasión de CloudFlare
3. **Selenium** - Navegador automatizado
4. **Análisis de JavaScript** - Extracción de código JS
5. **Decodificación Base64** - Streams codificados
6. **Análisis de iframes** - Contenido embebido

### Manejo de Proxies
- Carga automática de proxies gratuitos
- Rotación automática de proxies
- Verificación de funcionamiento
- Fallback sin proxy

### Evasión Anti-Bot
- Headers realistas rotativos
- User-Agent aleatorio
- Delays entre peticiones
- Ejecución de JavaScript
- Ocultación de automatización

## 📁 Archivos Generados

- `iptv_combined.m3u` - Todos los streams
- `iptv_tvplusgratis2.m3u` - Solo tvplusgratis2
- `iptv_vertvcable.m3u` - Solo vertvcable
- `iptv_cablevisionhd.m3u` - Solo cablevisionhd
- `iptv_telegratishd.m3u` - Solo telegratishd

## 🔍 Formato M3U Generado

```m3u
#EXTM3U
#EXTINF:-1 tvg-name="Canal 1" tvg-logo="" group-title="TVPLUSGRATIS2",Canal 1
http://example.com/stream1.m3u8
#EXTINF:-1 tvg-name="Canal 2" tvg-logo="" group-title="VERTVCABLE",Canal 2
http://example.com/stream2.m3u8
```

## ⚡ Optimizaciones

- Verificación paralela de streams (10 hilos)
- Cache de peticiones
- Timeout configurables
- Progreso visual en tiempo real
- Manejo de errores robusto

## 🐛 Solución de Problemas

### Error: ChromeDriver no encontrado
```bash
# Descargar ChromeDriver manualmente
# https://chromedriver.chromium.org/
# Colocar en PATH o en carpeta del proyecto
```

### Error: No se encontraron streams
- Verificar conexión a internet
- Intentar con proxy diferente
- Verificar que las páginas estén accesibles
- Probar con diferentes métodos de extracción

### Error: Verificación lenta
- Reducir número de hilos (max_workers)
- Usar verificación con requests en lugar de ffprobe
- Verificar solo algunos streams como muestra

## 📊 Estadísticas de Extracción

El programa mostrará:
- Número de streams extraídos por página
- Streams online vs offline
- Tiempo de verificación
- Errores encontrados

## 🔐 Consideraciones de Seguridad

- Usar proxies para evitar bloqueos de IP
- Respetar robots.txt de las páginas
- No sobrecargar los servidores
- Uso responsable de la herramienta

## 📝 Notas

- Los streams extraídos son directos (compatibles con SSIPTV)
- La verificación puede tomar tiempo dependiendo de la cantidad
- Algunos streams pueden requerir geolocalización específica
- La disponibilidad de streams puede cambiar frecuentemente

## 🤝 Contribuciones

Si encuentras bugs o quieres agregar nuevas páginas:
1. Reportar issues detallados
2. Proponer mejoras en los métodos de extracción
3. Compartir nuevas páginas de streams
4. Optimizaciones de rendimiento

## ⚠️ Disclaimer

Esta herramienta es solo para fines educativos y de investigación. El usuario es responsable del uso que le dé y debe cumplir con las leyes locales y términos de servicio de las páginas web.
