#!/usr/bin/env python3
import subprocess
import sys

# Simular entrada de opción 7
process = subprocess.Popen([sys.executable, 'iptv_definitivo.py'], 
                          stdin=subprocess.PIPE, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          text=True)

# Enviar "7" como entrada
stdout, stderr = process.communicate(input="7\n")

print("STDOUT:")
print(stdout)
print("\nSTDERR:")
print(stderr)
print(f"\nReturn code: {process.returncode}")
