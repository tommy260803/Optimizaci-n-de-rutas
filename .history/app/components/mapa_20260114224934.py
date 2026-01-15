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

def crear_mapa_base(estilo_mapa: str = 'streets') -> go.Figure:
    """
    Crea un mapa base premium con estilo visual mejorado.

    Args:
        estilo_mapa: Estilo del mapa ('streets', 'satellite', 'dark', etc.)

    Returns:
        go.Figure: Figura de Plotly con el mapa base premium.
    """
    fig = go.Figure()

    # Configuración de estilos de mapa premium
    estilos_disponibles = {
        'streets': 'mapbox://styles/mapbox/streets-v11',
        'satellite': 'mapbox://styles/mapbox/satellite-v9',
        'dark': 'mapbox://styles/mapbox/dark-v10',
        'light': 'mapbox://styles/mapbox/light-v10',
        'satellite-streets': 'mapbox://styles/mapbox/satellite-streets-v11'
    }

    estilo_seleccionado = estilos_disponibles.get(estilo_mapa, estilos_disponibles['streets'])

    # Configuración del layout del mapa con estilo premium
    fig.update_layout(
        mapbox={
            'style': estilo_seleccionado,
            'center': {'lat': MAPA_CENTRO['lat'], 'lon': MAPA_CENTRO['lon']},
            'zoom': MAPA_ZOOM,
            'pitch': 0,  # Vista 2D para mejor claridad
            'bearing': 0
        },
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height=550,  # Altura aumentada para mejor visualización
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'center',
            'x': 0.5,
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': 'rgba(0, 0, 0, 0.2)',
            'borderwidth': 1,
            'font': dict(size=11, color='#1f2937')
        },
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo transparente
        plot_bgcolor='rgba(0,0,0,0)',
        # Configuración de animaciones
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    # Configuración adicional para mejor UX
    fig.update_mapboxes(
        accesstoken=None,  # Usar token si está disponible
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

    return fig

def agregar_deposito(fig: go.Figure, df_puntos: 'pd.DataFrame') -> go.Figure:
    """
    Agrega el marcador premium del depósito al mapa con diseño mejorado.

    Args:
        fig: Figura de Plotly existente.
        df_puntos: DataFrame con los puntos.

    Returns:
        go.Figure: Figura actualizada con el depósito premium.
    """
    deposito = df_puntos[df_puntos['id'] == 0].iloc[0]

    # Información detallada del depósito
    tooltip_deposito = f"""
    <b>🏭 {deposito['nombre']}</b><br>
    <b>Ubicación Central:</b> Trujillo, Perú<br>
    <b>Coordenadas:</b> {deposito['lat']:.4f}, {deposito['lon']:.4f}<br>
    <b>Horario:</b> {deposito['ventana_inicio']} - {deposito['ventana_fin']}<br>
    <b>Capacidad:</b> Ilimitada<br>
    <b>ID:</b> {deposito['id']}
    """

    fig.add_trace(
        go.Scattermapbox(
            lat=[deposito['lat']],
            lon=[deposito['lon']],
            mode='markers+text',
            marker=go.scattermapbox.Marker(
                size=20,
                color='#1f2937',  # Gris oscuro elegante
                symbol='star',
                opacity=0.95,
                line=dict(
                    width=3,
                    color='#fbbf24'  # Borde dorado
                )
            ),
            text=['🏭 Depósito'],
            textposition="top center",
            textfont=dict(
                size=12,
                color='white',
                family='Arial, sans-serif'
            ),
            hovertext=[tooltip_deposito],
            hoverinfo='text',
            name='🏭 Depósito Central',
            showlegend=True,
            hoverlabel=dict(
                bgcolor='rgba(31, 41, 55, 0.95)',
                bordercolor='#fbbf24',
                font=dict(color='white', size=12)
            )
        )
    )

    return fig

def agregar_ruta(
    fig: go.Figure,
    coordenadas: List[Tuple[float, float]],
    color: str,
    nombre: str,
    ancho: int = 3,
    animada: bool = False
) -> go.Figure:
    """
    Agrega una ruta al mapa, opcionalmente con animación de dibujo.

    Args:
        fig: Figura de Plotly existente.
        coordenadas: Lista de tuplas (lat, lon) que definen la ruta.
        color: Color de la línea.
        nombre: Nombre que aparecerá en la leyenda.
        ancho: Ancho de la línea en píxeles.
        animada: Si True, crea una ruta con efecto de dibujo progresivo.

    Returns:
        go.Figure: Figura actualizada con la ruta.
    """
    if not coordenadas:
        return fig

    # Separar coordenadas en listas de lat y lon
    lats = [coord[0] for coord in coordenadas]
    lons = [coord[1] for coord in coordenadas]

    if animada and len(coordenadas) > 2:
        # Crear ruta animada con segmentos progresivos
        return agregar_ruta_animada(fig, coordenadas, color, nombre, ancho)
    else:
        # Ruta normal
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(
                    width=ancho,
                    color=color,
                    dash='solid' if nombre == 'Ruta Optimizada' else 'dot'
                ),
                name=nombre,
                hoverinfo='text',
                hovertext=f'<b>{nombre}</b><br>Distancia total: {calcular_distancia_ruta(coordenadas):.2f} km',
                showlegend=True
            )
        )

    return fig

def agregar_ruta_animada(
    fig: go.Figure,
    coordenadas: List[Tuple[float, float]],
    color: str,
    nombre: str,
    ancho: int = 4
) -> go.Figure:
    """
    Crea una ruta animada que se dibuja progresivamente.

    Args:
        fig: Figura de Plotly existente.
        coordenadas: Lista de tuplas (lat, lon) que definen la ruta completa.
        color: Color de la línea animada.
        nombre: Nombre que aparecerá en la leyenda.
        ancho: Ancho de la línea en píxeles.

    Returns:
        go.Figure: Figura actualizada con la ruta animada.
    """
    if len(coordenadas) < 3:
        # Para rutas cortas, usar ruta normal
        return agregar_ruta(fig, coordenadas, color, nombre, ancho, animada=False)

    # Crear segmentos de la ruta para animación
    segmentos = []
    for i in range(2, len(coordenadas) + 1):
        segmento = coordenadas[:i]
        segmentos.append(segmento)

    # Crear frames para animación
    frames = []
    for segmento in segmentos:
        lats_segmento = [coord[0] for coord in segmento]
        lons_segmento = [coord[1] for coord in segmento]

        frame = go.Frame(
            data=[
                go.Scattermapbox(
                    lat=lats_segmento,
                    lon=lons_segmento,
                    mode='lines',
                    line=dict(width=ancho, color=color),
                    name=nombre
                )
            ],
            name=f'frame_{len(segmentos) - len(frames)}'
        )
        frames.append(frame)

    # Agregar la ruta completa inicialmente
    lats_completa = [coord[0] for coord in coordenadas]
    lons_completa = [coord[1] for coord in coordenadas]

    fig.add_trace(
        go.Scattermapbox(
            lat=lats_completa,
            lon=lons_completa,
            mode='lines',
            line=dict(
                width=ancho,
                color=color
            ),
            name=f'🎬 {nombre} (Animada)',
            hoverinfo='text',
            hovertext=f'<b>{nombre} (Animada)</b><br>Distancia total: {calcular_distancia_ruta(coordenadas):.2f} km<br>Haz click para ver animación',
            showlegend=True
        )
    )

    # Agregar frames para animación
    fig.frames = frames

    # Configurar animación
    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'buttons': [{
                'label': '▶️ Reproducir Ruta',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 500, 'redraw': True},
                    'fromcurrent': True,
                    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                    'mode': 'immediate'
                }]
            }, {
                'label': '⏸️ Pausar',
                'method': 'animate',
                'args': [[None], {
                    'frame': {'duration': 0, 'redraw': False},
                    'mode': 'immediate'
                }]
            }]
        }]
    )

    return fig

def calcular_distancia_ruta(coordenadas: List[Tuple[float, float]]) -> float:
    """
    Calcula la distancia total de una ruta en kilómetros.

    Args:
        coordenadas: Lista de tuplas (lat, lon).

    Returns:
        float: Distancia total en kilómetros.
    """
    if len(coordenadas) < 2:
        return 0.0

    distancia_total = 0.0
    for i in range(len(coordenadas) - 1):
        coord1 = coordenadas[i]
        coord2 = coordenadas[i + 1]
        distancia_total += geodesic(coord1, coord2).kilometers

