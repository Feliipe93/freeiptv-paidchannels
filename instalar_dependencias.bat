@echo off
echo 🔥 INSTALADOR DE DEPENDENCIAS - IPTV EXTRACTOR DEFINITIVO 🔥
echo.

echo 📦 Instalando dependencias básicas (requeridas)...
pip install requests beautifulsoup4 lxml

echo.
echo 🛡️ Instalando protecciones anti-detección...
pip install cloudscraper fake-useragent

echo.
echo 🎭 Instalando Playwright para sitios JavaScript (opcional)...
pip install playwright
playwright install chromium

echo.
echo 🌐 Instalando Selenium como respaldo (opcional)...
pip install selenium

echo.
echo 🔧 Instalando utilidades adicionales...
pip install aiohttp js2py PyExecJS

echo.
echo ✅ INSTALACIÓN COMPLETADA
echo.
echo 💡 IMPORTANTE: 
echo    - Las dependencias básicas son suficientes para funcionamiento
echo    - Las opcionales mejoran significativamente la tasa de éxito
echo    - Fake-useragent mejora la rotación de User-Agents
echo    - CloudScraper es esencial para bypass de Cloudflare
echo.
echo 🚀 Ahora puedes ejecutar: python iptv_definitivo.py
echo.
pause
