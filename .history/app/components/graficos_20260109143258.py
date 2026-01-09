"""
Componentes de visualización de gráficos para la aplicación de optimización de rutas.
"""
import plotly.graph_objects as go
from dash import dcc
from typing import List, Dict, Any

def crear_grafico_convergencia_vacio() -> dcc.Graph:
    """
    Crea un gráfico de convergencia vacío.
    
    Returns:
        dcc.Graph: Componente de gráfico de convergencia vacío.
    """
    fig = go.Figure()
    
    fig.update_layout(
        title='Evolución del Fitness',
        xaxis_title='Generación',
        yaxis_title='Fitness',
        template='plotly_white',
        height=400,
        margin={'l': 50, 'r': 20, 't': 50, 'b': 50},
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        }
    )
    
    return dcc.Graph(
        id='grafico-convergencia',
        figure=fig,
        config={'displayModeBar': True}
    )

def actualizar_grafico_convergencia(historial: List[Dict[str, Any]]) -> go.Figure:
    """
    Actualiza el gráfico de convergencia con datos del historial.
    
    Args:
        historial: Lista de diccionarios con datos de cada generación.
        
    Returns:
        go.Figure: Figura actualizada con los datos de convergencia.
    """
    if not historial:
        return crear_grafico_convergencia_vacio()
    
    # Extraer datos del historial
    generaciones = [h.get('generacion', 0) for h in historial]
    mejores_fitness = [h.get('mejor_fitness', 0) for h in historial]
    fitness_promedio = [h.get('fitness_promedio', 0) for h in historial]
    
    fig = go.Figure()
    
    # Agregar línea de mejor fitness
    fig.add_trace(
        go.Scatter(
            x=generaciones,
            y=mejores_fitness,
            mode='lines+markers',
            name='Mejor Fitness',
            line=dict(color='green', width=2),
            marker=dict(size=6)
        )
    )
    
    # Agregar línea de fitness promedio
    fig.add_trace(
        go.Scatter(
            x=generaciones,
            y=fitness_promedio,
            mode='lines+markers',
            name='Fitness Promedio',
            line=dict(color='orange', width=2, dash='dash'),
            marker=dict(size=4)
        )
    )
    
    # Actualizar layout
    fig.update_layout(
        title='Evolución del Fitness por Generación',
        xaxis_title='Generación',
        yaxis_title='Valor de Fitness',
        template='plotly_white',
        height=400,
        margin={'l': 50, 'r': 20, 't': 50, 'b': 50},
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1
        },
        hovermode='x unified'
    )
    
    return fig

def crear_grafico_diversidad(datos_diversidad: List[Dict[str, Any]]) -> go.Figure:
    """
    Crea un gráfico de diversidad genética.
    
    Args:
        datos_diversidad: Lista de diccionarios con datos de diversidad por generación.
        
    Returns:
        go.Figure: Figura con el gráfico de diversidad.
    """
    if not datos_diversidad:
        return go.Figure()
    
    # Extraer datos
    generaciones = [d.get('generacion', 0) for d in datos_diversidad]
    diversidades = [d.get('diversidad', 0) for d in datos_diversidad]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=generaciones,
            y=diversidades,
            mode='lines+markers',
            name='Diversidad Genética',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        )
    )
    
    fig.update_layout(
        title='Diversidad Genética de la Población',
        xaxis_title='Generación',
        yaxis_title='Diversidad (Desviación Estándar del Fitness)',
        template='plotly_white',
        height=350,
        margin={'l': 50, 'r': 20, 't': 50, 'b': 50},
        showlegend=True
    )
    
    return fig
