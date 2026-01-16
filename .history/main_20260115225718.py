#!/usr/bin/env python
"""
Punto de entrada principal para la aplicación.
Compatible con Render y otros servicios de deployment.
"""
from app.app import app

if __name__ == '__main__':
    # Para ejecución local
    app.run_server(debug=True, host='0.0.0.0', port=8050)
