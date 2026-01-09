"""
Componentes de visualización de mapas para la aplicación de optimización de rutas.
"""
import plotly.graph_objects as go
from config import MAPA_CENTRO, MAPA_ZOOM
import pandas as pd
from typing import List, Tuple, Optional

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
    Agrega marcadores para los puntos de entrega al mapa.
    
    Args:
        fig: Figura de Plotly existente.
        df_puntos: DataFrame con los puntos de entrega.
        
    Returns:
        go.Figure: Figura actualizada con los puntos de entrega.
    """
    # Filtrar puntos que no son el depósito
    puntos_entrega = df_puntos[df_puntos['id'] != 0]
    
    if not puntos_entrega.empty:
        fig.add_trace(
            go.Scattermapbox(
                lat=puntos_entrega['lat'],
                lon=puntos_entrega['lon'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=10,
                    color='blue',
                    opacity=0.8
                ),
                text=puntos_entrega['nombre'] + '<br>Demanda: ' + puntos_entrega['demanda'].astype(str),
                hoverinfo='text',
                name='Puntos de entrega',
                showlegend=True
            )
        )
    
    return fig

def agregar_deposito(fig: go.Figure, df_puntos: 'pd.DataFrame') -> go.Figure:
    """
    Agrega el marcador del depósito al mapa.
    
    Args:
        fig: Figura de Plotly existente.
        df_puntos: DataFrame con los puntos.
        
    Returns:
        go.Figure: Figura actualizada con el depósito.
    """
    deposito = df_puntos[df_puntos['id'] == 0].iloc[0]
    
    fig.add_trace(
        go.Scattermapbox(
            lat=[deposito['lat']],
            lon=[deposito['lon']],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=15,
                color='red',
                symbol='star',
                opacity=0.9
            ),
            text=['Depósito Central'],
            hoverinfo='text',
            name='Depósito',
            showlegend=True
        )
    )
    
    return fig

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
            dash='dot'
        )
    
    if ruta_optimizada:
        fig = agregar_ruta(
            fig=fig,
            coordenadas=ruta_optimizada,
            color='green',
            nombre='Ruta Optimizada',
            dash='solid'
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
