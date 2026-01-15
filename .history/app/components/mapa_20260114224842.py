"""
Componentes de visualización de mapas para la aplicación de optimización de rutas.
Mejoras visuales: puntos diferenciados por distrito, colores únicos, tamaños dinámicos.
"""
import plotly.graph_objects as go
from config import MAPA_CENTRO, MAPA_ZOOM
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

# Configuración visual de distritos para puntos diferenciados
CONFIGURACION_DISTRITOS = {
    'Centro': {
        'color': '#1f2937',  # Gris oscuro elegante
        'icono': '🏛️',
        'hover_color': '#374151',
        'descripcion': 'Centro Histórico - Área comercial principal'
    },
    'Trujillo Viejo': {
        'color': '#7c3aed',  # Púrpura
        'icono': '🏰',
        'hover_color': '#8b5cf6',
        'descripcion': 'Trujillo Viejo - Zona histórica colonial'
    },
    'Mansiche': {
        'color': '#059669',  # Verde esmeralda
        'icono': '🏘️',
        'hover_color': '#10b981',
        'descripcion': 'Mansiche - Distrito residencial'
    },
    'La Esperanza': {
        'color': '#dc2626',  # Rojo coral
        'icono': '🏠',
        'hover_color': '#ef4444',
        'descripcion': 'La Esperanza - Zona urbana moderna'
    },
    'El Porvenir': {
        'color': '#ea580c',  # Naranja
        'icono': '🏙️',
        'hover_color': '#f97316',
        'descripcion': 'El Porvenir - Distrito en expansión'
    },
    'Florencia': {
        'color': '#c2410c',  # Naranja oscuro
        'icono': '🌺',
        'hover_color': '#ea580c',
        'descripcion': 'Florencia de Mora - Distrito residencial'
    },
    'Larco': {
        'color': '#7c2d12',  # Marrón rojizo
        'icono': '🏛️',
        'hover_color': '#9a3412',
        'descripcion': 'Victor Larco Herrera - Distrito comercial'
    },
    'Huanchaco': {
        'color': '#0891b2',  # Cyan
        'icono': '🏖️',
        'hover_color': '#06b6d4',
        'descripcion': 'Huanchaco - Distrito costero turístico'
    }
}

def obtener_configuracion_distrito(nombre: str) -> Dict[str, Any]:
    """
    Obtiene la configuración visual para un distrito específico.

    Args:
        nombre: Nombre del distrito.

    Returns:
        Dict con configuración visual del distrito.
    """
    # Buscar el distrito en el nombre del punto
    for distrito, config in CONFIGURACION_DISTRITOS.items():
        if distrito.lower() in nombre.lower():
            return config

    # Distrito por defecto si no se encuentra
    return {
        'color': '#6b7280',
        'icono': '📍',
        'hover_color': '#9ca3af',
        'descripcion': 'Distrito genérico'
    }

def calcular_tamano_dinamico(demanda: int, demanda_min: int = 1, demanda_max: int = 5) -> int:
    """
    Calcula el tamaño dinámico del marcador basado en la demanda.

    Args:
        demanda: Valor de demanda del punto.
        demanda_min: Valor mínimo de demanda esperado.
        demanda_max: Valor máximo de demanda esperado.

    Returns:
        int: Tamaño del marcador en píxeles.
    """
    # Normalizar demanda entre 0 y 1
    demanda_norm = (demanda - demanda_min) / (demanda_max - demanda_min)
    demanda_norm = max(0, min(1, demanda_norm))  # Clamp entre 0 y 1

    # Tamaño base: 12px, máximo: 24px para demanda alta
    tamano_base = 12
    tamano_max = 24
    return int(tamano_base + (tamano_max - tamano_base) * demanda_norm)


def agregar_ruta(
    fig: go.Figure,
    coordenadas: List[Tuple[float, float]],
    color: str,
    nombre: str,
    ancho: int = 3
) -> go.Figure:
    """
    Agrega una ruta al mapa.

    Args:
        fig: Figura de Plotly existente.
        coordenadas: Lista de tuplas (lat, lon) que definen la ruta.
        color: Color de la línea.
        nombre: Nombre que aparecerá en la leyenda.
        ancho: Ancho de la línea en píxeles.

    Returns:
        go.Figure: Figura actualizada con la ruta.
    """
    if not coordenadas:
        return fig

    # Separar coordenadas en listas de lat y lon
    lats = [coord[0] for coord in coordenadas]
    lons = [coord[1] for coord in coordenadas]

    fig.add_trace(
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(
                width=ancho,
                color=color
            ),
            name=nombre,
            hoverinfo='none',
            showlegend=True
        )
    )

    return fig

def crear_mapa_completo(
    df_puntos: 'pd.DataFrame', 
    ruta_inicial: Optional[List[Tuple[float, float]]] = None,
    ruta_optimizada: Optional[List[Tuple[float, float]]] = None
) -> go.Figure:
    """
    Crea un mapa completo con depósito, puntos de entrega y rutas.
    
    Args:
        df_puntos: DataFrame con los puntos de entrega.
        ruta_inicial: Coordenadas de la ruta inicial (opcional).
        ruta_optimizada: Coordenadas de la ruta optimizada (opcional).
        
    Returns:
        go.Figure: Figura de Plotly con el mapa completo.
    """
    # Crear mapa base
    fig = crear_mapa_base()
    
    # Agregar puntos de entrega
    fig = agregar_puntos_entrega(fig, df_puntos)
    
    # Agregar depósito
    fig = agregar_deposito(fig, df_puntos)
    
    # Agregar rutas si existen
    if ruta_inicial:
        fig = agregar_ruta(
            fig=fig,
            coordenadas=ruta_inicial,
            color='gray',
            nombre='Ruta Inicial',
            ancho=2
        )

    if ruta_optimizada:
        fig = agregar_ruta(
            fig=fig,
            coordenadas=ruta_optimizada,
            color='green',
            nombre='Ruta Optimizada',
            ancho=4
        )
    
    # Actualizar layout para mejor visualización
    fig.update_layout(
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'center',
            'x': 0.5,
            'bgcolor': 'rgba(255, 255, 255, 0.7)'
        }
    )
    
    return fig
