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
        'icono': '[C]',
        'hover_color': '#374151',
        'descripcion': 'Centro Histórico - Área comercial principal'
    },
    'Trujillo Viejo': {
        'color': '#7c3aed',  # Púrpura
        'icono': '[TV]',
        'hover_color': '#8b5cf6',
        'descripcion': 'Trujillo Viejo - Zona histórica colonial'
    },
    'Mansiche': {
        'color': '#059669',  # Verde esmeralda
        'icono': '[M]',
        'hover_color': '#10b981',
        'descripcion': 'Mansiche - Distrito residencial'
    },
    'La Esperanza': {
        'color': '#dc2626',  # Rojo coral
        'icono': '[LE]',
        'hover_color': '#ef4444',
        'descripcion': 'La Esperanza - Zona urbana moderna'
    },
    'El Porvenir': {
        'color': '#ea580c',  # Naranja
        'icono': '[EP]',
        'hover_color': '#f97316',
        'descripcion': 'El Porvenir - Distrito en expansión'
    },
    'Florencia': {
        'color': '#c2410c',  # Naranja oscuro
        'icono': '[F]',
        'hover_color': '#ea580c',
        'descripcion': 'Florencia de Mora - Distrito residencial'
    },
    'Larco': {
        'color': '#7c2d12',  # Marrón rojizo
        'icono': '[VLH]',
        'hover_color': '#9a3412',
        'descripcion': 'Victor Larco Herrera - Distrito comercial'
    },
    'Huanchaco': {
        'color': '#0891b2',  # Cyan
        'icono': '[H]',
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
        'icono': '[GEN]',
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

    # Configurar para capturar clicks
    fig.update_layout(
        clickmode='event+select'
    )

    return fig

def crear_visualizacion_ruta_completa(df_puntos: 'pd.DataFrame', ruta_optimizada: List[int]) -> go.Figure:
    """
    Crea una visualización completa y bonita de la ruta óptima.

    Args:
        df_puntos: DataFrame con todos los puntos.
        ruta_optimizada: Lista de IDs de puntos en orden óptimo.

    Returns:
        go.Figure: Visualización completa de la ruta.
    """
    fig = go.Figure()

    # Crear la ruta completa: depósito -> puntos -> depósito
    ruta_completa = [0] + ruta_optimizada + [0]  # 0 es el depósito

    # Obtener coordenadas de la ruta
    coordenadas_ruta = []
    for punto_id in ruta_completa:
        punto = df_puntos[df_puntos['id'] == punto_id].iloc[0]
        coordenadas_ruta.append((float(punto['lat']), float(punto['lon'])))

    # Dibujar la ruta principal
    lats_ruta = [coord[0] for coord in coordenadas_ruta]
    lons_ruta = [coord[1] for coord in coordenadas_ruta]

    fig.add_trace(
        go.Scattermapbox(
            lat=lats_ruta,
            lon=lons_ruta,
            mode='lines+markers',
            line=dict(width=4, color='#10b981'),
            marker=dict(size=8, color='#059669', symbol='circle'),
            name='Ruta Optima Completa',
            hoverinfo='text',
            hovertext=[f'<b>Punto {i+1}:</b> {ruta_completa[i]}' for i in range(len(ruta_completa))],
            showlegend=True
        )
    )

    # Agregar números de secuencia en cada punto con alta visibilidad
    for i, punto_id in enumerate(ruta_completa):
        punto = df_puntos[df_puntos['id'] == punto_id].iloc[0]

        # Color especial para el depósito
        if punto_id == 0:
            color_marcador = '#1f2937'  # Gris oscuro
            simbolo = 'DEP'
            tamano = 26
        else:
            color_marcador = '#dc2626'  # Rojo brillante
            simbolo = f'{i}'
            tamano = 22

        fig.add_trace(
            go.Scattermapbox(
                lat=[float(punto['lat'])],
                lon=[float(punto['lon'])],
                mode='markers+text',
                marker=dict(
                    size=tamano,
                    color=color_marcador,
                    symbol='circle',
                    line=dict(width=3, color='white')  # Borde blanco grueso
                ),
                text=[simbolo],
                textposition="middle center",
                textfont=dict(
                    size=12 if punto_id == 0 else 14,  # DEP más pequeño
                    color='white',
                    family='Arial Black'
                ),
                name=f'Punto {i+1}: {punto["nombre"]}',
                hovertext=f'<b>Punto {i+1}</b><br><b>ID:</b> {punto_id}<br><b>Nombre:</b> {punto["nombre"]}',
                hoverinfo='text',
                showlegend=False
            )
        )

    # Agregar flechas indicando la dirección usando texto Unicode
    for i in range(len(coordenadas_ruta) - 1):
        coord1 = coordenadas_ruta[i]
        coord2 = coordenadas_ruta[i + 1]

        # Calcular punto medio para la flecha
        lat_medio = (coord1[0] + coord2[0]) / 2
        lon_medio = (coord1[1] + coord2[1]) / 2

        # Calcular ángulo correcto entre los puntos
        angulo = calcular_angulo_entre_puntos(coord1, coord2)

        # Determinar símbolo de flecha basado en el ángulo
        if 337.5 <= angulo <= 360 or 0 <= angulo < 22.5:
            flecha = '↑'  # Norte
        elif 22.5 <= angulo < 67.5:
            flecha = '↗'  # Noreste
        elif 67.5 <= angulo < 112.5:
            flecha = '→'  # Este
        elif 112.5 <= angulo < 157.5:
            flecha = '↘'  # Sureste
        elif 157.5 <= angulo < 202.5:
            flecha = '↓'  # Sur
        elif 202.5 <= angulo < 247.5:
            flecha = '↙'  # Suroeste
        elif 247.5 <= angulo < 292.5:
            flecha = '←'  # Oeste
        else:
            flecha = '↖'  # Noroeste

        # Información del paso
        punto_origen = ruta_completa[i]
        punto_destino = ruta_completa[i + 1]

        fig.add_trace(
            go.Scattermapbox(
                lat=[lat_medio],
                lon=[lon_medio],
                mode='text',
                text=[flecha],
                textfont=dict(
                    size=20,  # Tamaño grande para visibilidad
                    color='#dc2626'  # Rojo brillante
                ),
                name=f'Paso {i+1} → {i+2}',
                hovertext=f'<b>Paso {i+1} → {i+2}</b><br>De punto {punto_origen} a {punto_destino}<br>Dirección: {angulo:.1f}° ({flecha})',
                hoverinfo='text',
                showlegend=False
            )
        )

    # Calcular zoom óptimo para esta ruta
    lat_centro, lon_centro, zoom_optimo = calcular_zoom_optimo(df_puntos)

    # Configurar layout
    fig.update_layout(
        mapbox={
            'style': 'open-street-map',
            'center': {'lat': lat_centro, 'lon': lon_centro},
            'zoom': zoom_optimo,
        },
        margin={'l': 0, 'r': 0, 't': 40, 'b': 40},
        height=600,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.9)',
        ),
        title=dict(
            text='<b>Ruta Optima Completa - Secuencia de Visita</b>',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=16, color='#1f2937')
        ),
        annotations=[
            dict(
                text=f'<b>Ruta Óptima:</b> {" → ".join([f"P{str(id).zfill(1)}" for id in ruta_completa])}',
                x=0.5,
                y=0.02,
                xref='paper',
                yref='paper',
                xanchor='center',
                yanchor='bottom',
                showarrow=False,
                font=dict(size=12, color='#374151'),
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#d1d5db',
                borderwidth=1,
                borderpad=4
            )
        ]
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
        text="<b>Sin Datos Disponibles</b><br><br>" +
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

    return fig

def agregar_puntos_entrega(fig: go.Figure, df_puntos: 'pd.DataFrame') -> go.Figure:
    """
    Agrega marcadores diferenciados para los puntos de entrega al mapa.
    Cada punto tiene color, ícono y tamaño únicos basados en su distrito y demanda.

    Args:
        fig: Figura de Plotly existente.
        df_puntos: DataFrame con los puntos de entrega.

    Returns:
        go.Figure: Figura actualizada con los puntos de entrega diferenciados.
    """
    # Filtrar puntos que no son el depósito
    puntos_entrega = df_puntos[df_puntos['id'] != 0].copy()

    # print(f"DEBUG: Encontrados {len(puntos_entrega)} puntos de entrega")

    if puntos_entrega.empty:
        # print("DEBUG: No hay puntos de entrega para mostrar")
        return fig

    # Calcular estadísticas de demanda para tamaños dinámicos
    demanda_min = puntos_entrega['demanda'].min()
    demanda_max = puntos_entrega['demanda'].max()

    # print(f"DEBUG: Demanda min={demanda_min}, max={demanda_max}")

    # Crear listas para todos los puntos
    lats = []
    lons = []
    tamanos = []
    colores = []
    textos = []
    tooltips = []

    for i, (_, punto) in enumerate(puntos_entrega.iterrows()):
        # Obtener configuración del distrito
        config_distrito = obtener_configuracion_distrito(punto['nombre'])

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
        <b>ID:</b> {punto['id']}
        """

        # Agregar datos del punto - mostrar el ID del punto en lugar del índice
        lats.append(float(punto['lat']))
        lons.append(float(punto['lon']))
        tamanos.append(max(tamano, 8))  # Tamaño mínimo de 8px
        colores.append(config_distrito['color'])
        textos.append(f"{punto['id']}")  # Mostrar el ID real del punto
        tooltips.append(tooltip_info.strip())

        # print(f"DEBUG: Punto {i+1}: lat={punto['lat']}, lon={punto['lon']}, color={config_distrito['color']}")

    # Agregar una sola traza con todos los puntos diferenciados (fuera del bucle)
    if lats:
        # print(f"DEBUG: Agregando {len(lats)} puntos al mapa")
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers+text',
                marker=dict(
                    size=tamanos,
                    color=colores,
                    opacity=0.9
                ),
                text=textos,
                textposition="middle center",
                textfont=dict(
                    size=12,
                    color='black',
                    family='Arial Black'
                ),
                hovertext=tooltips,
                hoverinfo='text',
                name='Puntos de Entrega',
                showlegend=True,
                hoverlabel=dict(
                    bgcolor='rgba(255, 255, 255, 0.95)',
                    bordercolor='#333',
                    font=dict(size=12)
                )
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
    # Verificar que existe el depósito
    deposito_filtrado = df_puntos[df_puntos['id'] == 0]
    if deposito_filtrado.empty:
        print("WARNING: No se encontró el depósito (id=0) en los datos")
        return fig

    deposito = deposito_filtrado.iloc[0]

    # print(f"DEBUG: Agregando depósito en lat={deposito['lat']}, lon={deposito['lon']}")

    # Información detallada del depósito
    tooltip_deposito = f"""
    <b>DEP {deposito['nombre']}</b><br>
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
            name='Deposito Central',
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
            name=f'{nombre} (Animada)',
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
                'label': 'Reproducir Ruta',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 500, 'redraw': True},
                    'fromcurrent': True,
                    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                    'mode': 'immediate'
                }]
            }, {
                'label': 'Pausar',
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

def calcular_angulo_entre_puntos(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calcula el ángulo en grados entre dos puntos GPS para orientar flechas.

    Args:
        coord1: Tupla (lat, lon) del punto inicial.
        coord2: Tupla (lat, lon) del punto final.

    Returns:
        float: Ángulo en grados (0 = Norte, 90 = Este, 180 = Sur, 270 = Oeste).
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convertir a radianes
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lon_rad = np.radians(lon2 - lon1)

    # Calcular el ángulo usando fórmula de navegación
    x = np.sin(delta_lon_rad) * np.cos(lat2_rad)
    y = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(delta_lon_rad)

    # Ángulo en radianes
    angle_rad = np.arctan2(x, y)

    # Convertir a grados y ajustar para que 0 = Norte
    angle_deg = np.degrees(angle_rad)

    # Normalizar a 0-360 grados
    angle_deg = (angle_deg + 360) % 360

    return angle_deg

def calcular_zoom_optimo(df_puntos: 'pd.DataFrame') -> Tuple[float, float, float]:
    """
    Calcula el zoom óptimo y centro del mapa para mostrar todos los puntos.
    Manteniendo un zoom más cercano para mejor visualización.

    Args:
        df_puntos: DataFrame con los puntos.

    Returns:
        tuple: (lat_centro, lon_centro, zoom)
    """
    if df_puntos.empty:
        return MAPA_CENTRO['lat'], MAPA_CENTRO['lon'], MAPA_ZOOM

    # Obtener coordenadas de todos los puntos
    lats = df_puntos['lat'].values
    lons = df_puntos['lon'].values

    # Calcular centro
    lat_centro = (lats.min() + lats.max()) / 2
    lon_centro = (lons.min() + lons.max()) / 2

    # Calcular zoom basado en la dispersión de puntos
    # Mantener zoom más cercano para mejor visualización de puntos
    lat_range = lats.max() - lats.min()
    lon_range = lons.max() - lons.min()

    # Fórmula mejorada: mantener zoom más cercano
    max_range = max(lat_range, lon_range)

    if max_range < 0.005:  # Muy cerca
        zoom = 15
    elif max_range < 0.02:  # Cerca
        zoom = 13
    elif max_range < 0.08:  # Moderado
        zoom = 11
    elif max_range < 0.3:  # Lejos
        zoom = 9
    else:  # Muy lejos
        zoom = 8

    # Zoom mínimo para asegurar buena visibilidad de puntos
    zoom = max(zoom, 10)  # Nunca menos de zoom 10

    return lat_centro, lon_centro, zoom

def crear_mapa_completo(
    df_puntos: 'pd.DataFrame',
    ruta_inicial: Optional[List[Tuple[float, float]]] = None,
    ruta_optimizada: Optional[List[Tuple[float, float]]] = None,
    ajustar_zoom: bool = False
) -> go.Figure:
    """
    Crea un mapa completo con depósito, puntos de entrega y rutas.

    Args:
        df_puntos: DataFrame con los puntos de entrega.
        ruta_inicial: Coordenadas de la ruta inicial (opcional).
        ruta_optimizada: Coordenadas de la ruta optimizada (opcional).
        ajustar_zoom: Si True, calcula zoom óptimo para mostrar todos los puntos.

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

    # Ajustar zoom si se solicita
    if ajustar_zoom and not df_puntos.empty:
        lat_centro, lon_centro, zoom_optimo = calcular_zoom_optimo(df_puntos)
        fig.update_layout(
            mapbox={
                'center': {'lat': lat_centro, 'lon': lon_centro},
                'zoom': zoom_optimo,
            }
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
