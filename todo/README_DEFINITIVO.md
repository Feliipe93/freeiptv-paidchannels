# 🔥 IPTV Extractor Definitivo - Script Único Completo

Extractor avanzado de canales IPTV con técnicas anti-detección, eliminación de duplicados y compatibilidad completa con Smart TV/SSIPTV.

## ✨ Características Principales

- **🎯 Script único consolidado** - Toda la funcionalidad en un solo archivo
- **🛡️ Técnicas anti-detección avanzadas** - CloudScraper, headers rotativos, bypass de Cloudflare
- **🎭 Soporte JavaScript** - Playwright para sitios con contenido dinámico
- **🔍 Detección inteligente de duplicados** - Mantiene opciones múltiples cuando las URLs son diferentes
- **📺 URLs directas .m3u8** - Compatible con Smart TV y aplicaciones SSIPTV
- **🌐 4 sitios verificados** - tvplusgratis2.com, telegratishd.com, vertvcable.com, cablevisionhd.com
- **📊 Verificación de streams** - Prueba automática de funcionamiento
- **🎨 Interfaz mejorada** - Logging con colores y progreso en tiempo real

## 🚀 Instalación Rápida

### Opción 1: Instalador Automático (Recomendado)
```bash
# Ejecutar el instalador de dependencias
instalar_dependencias.bat
```

### Opción 2: Manual
```bash
# Dependencias básicas (requeridas)
pip install requests beautifulsoup4

# Dependencias avanzadas (recomendadas)
pip install cloudscraper playwright selenium
playwright install chromium
```

### Opción 3: Desde requirements.txt
```bash
pip install -r requirements.txt
playwright install chromium  # Solo si instalaste playwright
```

## 📋 Uso del Script

### Ejecutar el Script Principal
```bash
python iptv_definitivo.py
```

### Opciones Disponibles

1. **🌍 Extraer TODOS los sitios (Recomendado)**
   - Extrae canales de todos los sitios verificados
   - Detecta y maneja duplicados automáticamente
   - Genera M3U completo con canales organizados por fuente

2. **🎯 Extraer sitio específico**
   - Selecciona un sitio individual para extracción
   - Útil para pruebas o necesidades específicas

3. **🧪 Modo debug**
   - Prueba un canal específico
   - Muestra todos los métodos de extracción
   - Útil para desarrollo y troubleshooting

4. **📊 Verificar archivo M3U**
   - Prueba streams de un archivo M3U existente
   - Muestra estadísticas de funcionamiento
   - Configurable el número de streams a verificar

5. **❓ Información de sitios**
   - Muestra configuración de cada sitio
   - Estado de verificación y técnicas utilizadas

## 🎯 Sitios Soportados

| Sitio | Estado | Canales Típicos | Técnicas |
|-------|--------|-----------------|----------|
| tvplusgratis2.com | ✅ Verificado | 50+ | CloudScraper + JS |
| telegratishd.com | ✅ Verificado | 30+ | CloudScraper + JS |
| vertvcable.com | ✅ Verificado | 40+ | CloudScraper |
| cablevisionhd.com | ⚠️ En desarrollo | Variable | CloudScraper |

## 📁 Estructura de Archivos

```
iptv_extractor/
├── iptv_definitivo.py          # Script principal único
├── instalar_dependencias.bat   # Instalador automático
├── requirements.txt            # Lista de dependencias
├── README.md                   # Esta documentación
└── old/                        # Scripts anteriores (organizados)
    ├── iptv.py
    ├── verificar_todos_sitios.py
    └── ...otros archivos...
```

## 🎨 Características Técnicas

### Técnicas Anti-Detección
- **Headers rotativos** - User-agents aleatorios
- **CloudScraper** - Bypass automático de Cloudflare
- **Playwright** - Ejecución de JavaScript para sitios complejos
- **Rate limiting** - Pausas inteligentes entre requests
- **Session persistence** - Mantiene cookies y estado

### Extracción Avanzada
- **Múltiples patrones** - Regex optimizados para diferentes tipos de streams
- **Análisis JavaScript** - Extracción de URLs embebidas en código JS
- **Procesamiento de iframes** - Detección de players embebidos
- **Priorización automática** - Master playlists .m3u8 tienen prioridad
- **URLs de respaldo** - Guarda múltiples opciones por canal

### Manejo de Duplicados
- **Detección inteligente** - Normalización de nombres para comparación
- **Opciones múltiples** - Mantiene canales con URLs diferentes como "Opción 1", "Opción 2"
- **Agrupación por fuente** - Organiza canales por sitio de origen
- **Categorización automática** - Deportes, Noticias, Infantil, etc.

## 📊 Formato M3U Generado

```m3u
#EXTM3U
# Generado por IPTV Extractor Definitivo - 2024-01-XX XX:XX:XX
# Total de canales: XXX

# === TVPLUSGRATIS2.COM (XX canales) ===
#EXTINF:-1 tvg-logo="" group-title="Deportes",ESPN [tvplusgratis2]
https://stream.example.com/espn/master.m3u8

#EXTINF:-1 tvg-logo="" group-title="Noticias",CNN [tvplusgratis2]
https://stream.example.com/cnn/master.m3u8
```

## 🐛 Troubleshooting

### Errores Comunes

**Error: "Import playwright could not be resolved"**
```bash
# Instalar Playwright
pip install playwright
playwright install chromium
```

**Error: "Import cloudscraper could not be resolved"**
```bash
# Instalar CloudScraper
pip install cloudscraper
```

**Error: "No se encontraron canales"**
- Verificar conexión a internet
- Comprobar que los sitios estén accesibles
- Intentar con modo debug para un canal específico

**Streams no funcionan en TV/SSIPTV**
- Los streams .m3u8 pueden requerir headers específicos
- Algunos pueden tener restricciones geográficas
- Probar con diferentes aplicaciones IPTV

### Logs y Debug

El script incluye logging detallado:
- **INFO** (azul): Información general
- **SUCCESS** (verde): Operaciones exitosas
- **WARNING** (amarillo): Advertencias
- **ERROR** (rojo): Errores no críticos
- **CRITICAL** (rojo fondo): Errores críticos
- **DEBUG** (magenta): Información de depuración

## 🔄 Actualizaciones

Este script integra todas las mejoras desarrolladas durante el proyecto:
- ✅ URLs corregidas para todos los sitios
- ✅ Técnicas de series extractor incorporadas
- ✅ Sistema de detección de duplicados
- ✅ Verificación automática de streams
- ✅ Organización mejorada de archivos
- ✅ Interfaz de usuario optimizada

## 📞 Soporte

Para problemas o mejoras:
1. Verificar que todas las dependencias estén instaladas
2. Ejecutar en modo debug para canales específicos
3. Revisar los logs para identificar problemas
4. Comprobar la conectividad a los sitios

## 🎉 Uso Recomendado

1. **Primera vez**: Ejecutar `instalar_dependencias.bat`
2. **Extracción completa**: Opción 1 - Extraer todos los sitios
3. **Verificación**: Opción 4 - Verificar streams del M3U generado
4. **Uso en Smart TV**: Cargar el archivo .m3u en aplicación IPTV

¡Disfruta de tus canales IPTV! 🎬📺
