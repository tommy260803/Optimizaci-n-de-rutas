"""
Layout del panel de controles para la interfaz de usuario.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
from config import (
    DEFAULT_POBLACION,
    DEFAULT_GENERACIONES,
    DEFAULT_PROB_CRUZA,
    DEFAULT_PROB_MUTACION,
    DEFAULT_ELITISMO
)

def crear_panel_controles() -> dbc.Card:
    """
    Crea el panel de controles para la interfaz de usuario.
    
    Returns:
        dbc.Card: Componente Card con todos los controles.
    """
    return dbc.Card([
        dbc.CardHeader(
            "Parámetros del Algoritmo Genético",
            className="font-weight-bold"
        ),
        dbc.CardBody([
            # Tamaño de Población
            html.Div([
                html.Label("Tamaño de Población", className="form-label"),
                dcc.Slider(
                    id='slider-poblacion',
                    min=50,
                    max=500,
                    step=50,
                    value=DEFAULT_POBLACION,
                    marks={i: str(i) for i in range(50, 501, 100)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className="mb-4"),
            
            # Número de Generaciones
            html.Div([
                html.Label("Número de Generaciones", className="form-label"),
                dcc.Slider(
                    id='slider-generaciones',
                    min=100,
                    max=1000,
                    step=100,
                    value=DEFAULT_GENERACIONES,
                    marks={i: str(i) for i in range(100, 1001, 200)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className="mb-4"),
            
            # Probabilidad de Cruza
            html.Div([
                html.Label("Probabilidad de Cruza", className="form-label"),
                dcc.Slider(
                    id='slider-cruza',
                    min=0,
                    max=1,
                    step=0.1,
                    value=DEFAULT_PROB_CRUZA,
                    marks={0: '0.0', 0.5: '0.5', 1: '1.0'},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className="mb-4"),
            
            # Probabilidad de Mutación
            html.Div([
                html.Label("Probabilidad de Mutación", className="form-label"),
                dcc.Slider(
                    id='slider-mutacion',
                    min=0,
                    max=1,
                    step=0.05,
                    value=DEFAULT_PROB_MUTACION,
                    marks={0: '0.0', 0.5: '0.5', 1: '1.0'},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className="mb-4"),
            
            # Número de Puntos
            html.Div([
                html.Label("Número de Puntos", className="form-label"),
                dcc.Slider(
                    id='slider-puntos',
                    min=10,
                    max=50,
                    step=5,
                    value=20,
                    marks={i: str(i) for i in range(10, 51, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className="mb-4"),
            
            html.Hr(),
            
            # Botones de control
            dbc.Button(
                "Generar Nuevos Datos",
                id='btn-generar',
                color="info",
                className="mb-2 w-100"
            ),
            
            dbc.Button(
                "Iniciar Optimización",
                id='btn-iniciar',
                color="success",
                className="mb-2 w-100"
            ),
            
            dbc.Button(
                "Pausar",
                id='btn-pausar',
                color="warning",
                className="mb-2 w-100",
                disabled=True
            ),
            
            dbc.Button(
                "Reiniciar",
                id='btn-reiniciar',
                color="danger",
                className="mb-2 w-100"
            ),
            
            dbc.Button(
                "Exportar Resultados",
                id='btn-exportar',
                color="secondary",
                className="w-100"
            )
        ])
    ], className="shadow-sm")
