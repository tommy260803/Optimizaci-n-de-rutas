"""
Módulo para el registro centralizado de callbacks de la aplicación.
"""
import logging
import sys
from pathlib import Path

# Asegurarse de que el directorio raíz esté en el path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

logger = logging.getLogger(__name__)

def registrar_callbacks(app):
    """
    Registra todos los callbacks de la aplicación.
    
    Args:
        app: Instancia de la aplicación Dash.
    """
    try:
        logger.info("Registrando callbacks...")
        
        # Importar callbacks de los módulos
        try:
            from app.callbacks import ag_callbacks, mapa_callbacks, graficos_callbacks
            
            # Registrar callbacks de cada módulo
            ag_callbacks.registrar_callbacks(app)
            mapa_callbacks.registrar_callbacks(app)
            graficos_callbacks.registrar_callbacks(app)
            
            logger.info("Todos los callbacks se registraron exitosamente")
            
        except ImportError as e:
            logger.error(f"Error al importar módulos de callbacks: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error inesperado al registrar callbacks: {str(e)}")
        raise

# Hacer que la función esté disponible en el paquete
__all__ = ['registrar_callbacks']
