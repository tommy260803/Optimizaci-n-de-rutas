#!/usr/bin/env python3
"""
Script de prueba para simular el despliegue en Render localmente.
"""
import os
import sys

# Simular variables de entorno de Render
os.environ['PORT'] = '8000'
os.environ['DEBUG'] = 'false'

# Simular el comando de Render
if __name__ == '__main__':
    print("🚀 Probando despliegue similar a Render...")
    print(f"PORT: {os.environ.get('PORT')}")
    print(f"DEBUG: {os.environ.get('DEBUG')}")

    # Importar y ejecutar la aplicación
    from app.app import app

    port = int(os.environ.get('PORT', 8000))
    print(f"🌐 Iniciando servidor en puerto {port}...")

    app.run_server(
        debug=False,
        host='0.0.0.0',
        port=port,
        dev_tools_ui=False,
        dev_tools_props_check=False
    )
