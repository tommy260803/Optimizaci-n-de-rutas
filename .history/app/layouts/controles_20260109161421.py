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
            className="custom-card-header"
        ),
        dbc.CardBody([
            # Grupo 1: Configuración de datos
            html.Div([
                html.H6("Configuración de Datos", className="text-primary mb-3 fw-bold"),
                html.Div([
                    html.Label("Número de Puntos de Entrega", className="slider-label"),
                    dcc.Slider(
                        id='slider-puntos',
                        min=10,
                        max=50,
                        step=5,
                        value=20,
                        marks={10: '10', 20: '20', 30: '30', 40: '40', 50: '50'},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className="custom-slider"
                    )
                ], className="slider-container"),

                dbc.Button(
                    "Generar Nuevos Datos",
                    id='btn-generar',
                    className="btn-custom btn-primary-custom w-100 mt-3"
                ),
            ], className="mb-4"),

            html.Hr(className="my-3"),

            # Grupo 2: Parámetros del algoritmo
            html.Div([
                html.H6("Parámetros del Algoritmo Genético", className="text-primary mb-3 fw-bold"),

                # Primera fila: Población y Generaciones
                dbc.Row([
                    dbc.Col([
                        html.Label("Tamaño Población", className="slider-label"),
                        dcc.Slider(
                            id='slider-poblacion',
                            min=50,
                            max=500,
                            step=50,
                            value=DEFAULT_POBLACION,
                            marks={50: '50', 200: '200', 350: '350', 500: '500'},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="custom-slider"
                        )
                    ], width=6, className="pe-2"),

                    dbc.Col([
                        html.Label("Número Generaciones", className="slider-label"),
                        dcc.Slider(
                            id='slider-generaciones',
                            min=100,
                            max=1000,
                            step=100,
                            value=DEFAULT_GENERACIONES,
                            marks={100: '100', 400: '400', 700: '700', 1000: '1000'},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="custom-slider"
                        )
                    ], width=6, className="ps-2")
                ], className="mb-3"),

                # Segunda fila: Probabilidades
                dbc.Row([
                    dbc.Col([
                        html.Label("Probabilidad Cruza", className="slider-label"),
                        dcc.Slider(
                            id='slider-cruza',
                            min=0,
                            max=1,
                            step=0.1,
                            value=DEFAULT_PROB_CRUZA,
                            marks={0: '0.0', 0.5: '0.5', 1: '1.0'},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="custom-slider"
                        )
                    ], width=6, className="pe-2"),

                    dbc.Col([
                        html.Label("🧬 Probabilidad Mutación", className="slider-label"),
                        dcc.Slider(
                            id='slider-mutacion',
                            min=0,
                            max=1,
                            step=0.05,
                            value=DEFAULT_PROB_MUTACION,
                            marks={0: '0.0', 0.5: '0.5', 1: '1.0'},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="custom-slider"
                        )
                    ], width=6, className="ps-2")
                ])
            ], className="mb-4"),

            html.Hr(className="my-3"),

            # Grupo 3: Controles de ejecución
            html.Div([
                html.H6("🎮 Control de Ejecución", className="text-primary mb-3 fw-bold"),

                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "▶️ Iniciar Optimización",
                            id='btn-iniciar',
                            className="btn-custom btn-success-custom w-100 mb-2"
                        ),

                        dbc.Button(
                            "⏸️ Pausar",
                            id='btn-pausar',
                            className="btn-custom btn-warning-custom w-100 mb-2",
                            disabled=True
                        )
                    ], width=6),

                    dbc.Col([
                        dbc.Button(
                            "🔄 Reiniciar",
                            id='btn-reiniciar',
                            className="btn-custom btn-danger-custom w-100 mb-2"
                        ),

                        dbc.Button(
                            "💾 Exportar Resultados",
                            id='btn-exportar',
                            className="btn-custom btn-secondary-custom w-100"
                        )
                    ], width=6)
                ])
            ])
        ])
    ], className="shadow-sm")
