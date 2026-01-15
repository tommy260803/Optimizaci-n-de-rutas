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

def crear_mapa_base() -> go.Figure:
    """
    Crea un mapa base de Plotly con configuración inicial.
    
    Returns:
        go.Figure: Figura de Plotly con el mapa base.
    """
    fig = go.Figure()
    
    # Configuración del layout del mapa
    fig.update_layout(
        mapbox={
            'style': 'open-street-map',
            'center': {'lat': MAPA_CENTRO['lat'], 'lon': MAPA_CENTRO['lon']},
            'zoom': MAPA_ZOOM
        },
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height=500,
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'center',
            'x': 0.5
        }
    )
    
    return fig

def agregar_puntos_entrega(fig: go.Figure, df_puntos: 'pd.DataFrame') -> go.Figure:
    """
    Agrega marcadores diferenciados para los puntos de entrega al mapa.
    Cada distrito tiene colores, íconos y tamaños únicos basados en demanda.

    Args:
        fig: Figura de Plotly existente.
        df_puntos: DataFrame con los puntos de entrega.

    Returns:
        go.Figure: Figura actualizada con los puntos de entrega diferenciados.
    """
    # Filtrar puntos que no son el depósito
    puntos_entrega = df_puntos[df_puntos['id'] != 0].copy()

    if puntos_entrega.empty:
        return fig

    # Calcular estadísticas de demanda para tamaños dinámicos
    demanda_min = puntos_entrega['demanda'].min()
    demanda_max = puntos_entrega['demanda'].max()

    # Agrupar puntos por distrito para trazas separadas
    distritos_agrupados = {}

    for _, punto in puntos_entrega.iterrows():
        config_distrito = obtener_configuracion_distrito(punto['nombre'])

        distrito_key = None
        for distrito in CONFIGURACION_DISTRITOS.keys():
            if distrito.lower() in punto['nombre'].lower():
                distrito_key = distrito
                break

        if distrito_key is None:
            distrito_key = 'default'

        if distrito_key not in distritos_agrupados:
            distritos_agrupados[distrito_key] = []

        # Calcular tamaño dinámico basado en demanda
        tamano = calcular_tamano_dinamico(
            punto['demanda'],
            demanda_min,
            demanda_max
        )

        # Crear información rica para tooltip
        tooltip_info = f"""
        <b>{config_distrito['icono']} {punto['nombre']}</b><br>
        <b>Distrito:</b> {config_distrito['descripcion']}<br>
        <b>Demanda:</b> {punto['demanda']} unidades<br>
        <b>Tiempo de Servicio:</b> {punto['tiempo_servicio']} min<br>
        <b>Ventana de Tiempo:</b> {punto['ventana_inicio']} - {punto['ventana_fin']}<br>
        <b>ID:</b> {punto['id']}
        """

        punto_info = {
            'lat': punto['lat'],
            'lon': punto['lon'],
            'tamano': tamano,
            'color': config_distrito['color'],
            'hover_color': config_distrito['hover_color'],
            'icono': config_distrito['icono'],
            'tooltip': tooltip_info,
            'demanda': punto['demanda']
        }

        distritos_agrupados[distrito_key].append(punto_info)

    # Agregar una traza por distrito
    for distrito, puntos in distritos_agrupados.items():
        if not puntos:
            continue

        config_distrito = obtener_configuracion_distrito(distrito) if distrito != 'default' else CONFIGURACION_DISTRITOS['Centro']

        lats = [p['lat'] for p in puntos]
        lons = [p['lon'] for p in puntos]
        tamanos = [p['tamano'] for p in puntos]
        colores = [p['color'] for p in puntos]
        tooltips = [p['tooltip'] for p in puntos]
        iconos = [p['icono'] for p in puntos]

        # Crear texto combinado con ícono y nombre
        textos = [f"{icono} Distrito {distrito}" for icono in iconos]

        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers+text',
                marker=go.scattermapbox.Marker(
                    size=tamanos,
                    color=colores,
                    opacity=0.85,
                    sizemode='diameter'
                ),
                text=textos,
                textposition="bottom center",
                textfont=dict(
                    size=10,
                    color='white',
                    family='Arial, sans-serif'
                ),
                hovertext=tooltips,
                hoverinfo='text',
                name=f'{config_distrito["icono"]} {distrito}',
                showlegend=True,
                # Configuración de animación de entrada
                hoverlabel=dict(
                    bgcolor='rgba(0, 0, 0, 0.8)',
                    bordercolor='white',
                    font=dict(color='white', size=12)
                )
            )
        )

    
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
