"""
Módulo para los callbacks de la aplicación web.
"""
from .registro_callbacks import registrar_callbacks
from . import disenador_callbacks

__all__ = ['registrar_callbacks', 'disenador_callbacks']
