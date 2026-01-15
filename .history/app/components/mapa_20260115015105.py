"""
Componentes de visualización de mapas para la aplicación de optimización de rutas.
Mejoras visuales: puntos diferenciados por distrito, colores únicos, tamaños dinámicos.
"""
import plotly.graph_objects as go
from config import MAPA_CENTRO, MAPA_ZOOM
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from geopy.distance import geodesic

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

    # Configuración de estilos de mapa - usando open-street-map que no requiere token
    estilos_disponibles = {
        'open-street-map': 'open-street-map',
        'carto-positron': 'carto-positron',
        'carto-darkmatter': 'carto-darkmatter',
        'stamen-terrain': 'stamen-terrain',
        'stamen-toner': 'stamen-toner'
    }

    estilo_seleccionado = estilos_disponibles.get(estilo_mapa, 'open-street-map')

    # Configuración del layout del mapa con estilo premium
    fig.update_layout(
        mapbox={
            'style': estilo_seleccionado,
            'center': {'lat': MAPA_CENTRO['lat'], 'lon': MAPA_CENTRO['lon']},
            'zoom': MAPA_ZOOM + 1,  # Aumentar zoom para ver mejor los puntos
            'pitch': 0,  # Vista 2D para mejor claridad
            'bearing': 0
        },
        margin={'l': 0, 'r': 0, 't': 40, 'b': 80},  # Más espacio para la leyenda
        height=550,  # Altura aumentada para mejor visualización
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,  # Posición debajo del mapa
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='rgba(0, 0, 0, 0.3)',
            borderwidth=2,
            font=dict(size=12, color='#1f2937'),
            itemsizing='constant'
        ),
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

def crear_mapa_sin_datos() -> go.Figure:
    """
    Crea un mapa con mensaje informativo cuando no hay datos disponibles.

    Returns:
        go.Figure: Figura de Plotly con mensaje informativo.
    """
    fig = go.Figure()

    # Agregar anotación de texto en el centro del mapa
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text="<b>📍 Sin Datos Disponibles</b><br><br>" +
             "Primero genere nuevos puntos de entrega<br>" +
             "usando el botón 'Generar Nuevos Datos'",
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            size=16,
            color="#64748b",
            family="Inter, sans-serif"
        ),
        align="center",
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#e2e8f0",
        borderwidth=2,
        borderpad=10
    )

    # Configurar layout básico
    fig.update_layout(
        mapbox={
            'style': 'open-street-map',
            'center': {'lat': MAPA_CENTRO['lat'], 'lon': MAPA_CENTRO['lon']},
            'zoom': MAPA_ZOOM,
        },
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height=550,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )


        # Crear información rica para tooltip
        tooltip_info = f"""
        <b>{config_distrito['icono']} {punto['nombre']}</b><br>
        <b>Distrito:</b> {config_distrito['descripcion']}<br>
        <b>Demanda:</b> {punto['demanda']} unidades<br>
        <b>ID:</b> {punto['id']}
        """

        # Agregar datos del punto
        lats.append(float(punto['lat']))
        lons.append(float(punto['lon']))
        tamanos.append(max(tamano, 8))  # Tamaño mínimo de 8px
        colores.append(config_distrito['color'])
        textos.append(f"{i+1}")
        tooltips.append(tooltip_info.strip())

        # print(f"DEBUG: Punto {i+1}: lat={punto['lat']}, lon={punto['lon']}, color={config_distrito['color']}")

    # Agregar una sola traza con todos los puntos diferenciados
    if lats:
        # print(f"DEBUG: Agregando {len(lats)} puntos al mapa")
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers',
                marker=dict(
                    size=tamanos,
                    color=colores,
                    opacity=0.9
                ),
                text=textos,
                hovertext=tooltips,
                hoverinfo='text',
                name='Puntos de Entrega',
                showlegend=True
            )
        )
        # print("DEBUG: Puntos agregados exitosamente al mapa")

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

    # print(f"DEBUG: Agregando depósito en lat={deposito['lat']}, lon={deposito['lon']}")

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
            lat=[float(deposito['lat'])],
            lon=[float(deposito['lon'])],
            mode='markers',
            marker=dict(
                size=25,
                color='#1f2937',
                symbol='star',
                opacity=1.0
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
                    color=color
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

    return distancia_total

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
