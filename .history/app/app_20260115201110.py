"""
Módulo principal de la aplicación de Optimización de Rutas con Algoritmos Genéticos.
"""
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Añadir el directorio raíz al path para imports absolutos
sys.path.append(str(Path(__file__).parent.parent))

from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def crear_app():
    """
    Crea y configura la aplicación Dash.
    
    Returns:
        Dash: Instancia de la aplicación configurada.
    """
    try:
        # Importaciones dentro de la función para evitar importaciones circulares
        from app.layouts.main_layout import crear_layout as crear_layout_principal
        from app.callbacks import registrar_callbacks
        
        logger.info("Creando aplicación Dash...")
        
        # Crear la aplicación con Bootstrap
        app = Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
            ],
            suppress_callback_exceptions=True,
            title="Optimización de Rutas",
            update_title="Cargando..."
        )
        
        # Configurar el layout
        logger.info("Configurando layout principal...")
        app.layout = crear_layout_principal()
        
        # Registrar callbacks
        logger.info("Registrando callbacks...")
        registrar_callbacks(app)
        
        logger.info("Aplicación creada exitosamente")
        return app
        
    except Exception as e:
        logger.error(f"Error al crear la aplicación: {str(e)}")
        raise

# Crear instancia de la aplicación
app = crear_app()

# Para ejecución directa
if __name__ == '__main__':
    logger.info("Iniciando servidor...")
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run_server(debug=debug, host='0.0.0.0', port=port)
