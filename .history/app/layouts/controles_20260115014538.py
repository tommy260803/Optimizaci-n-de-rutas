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
                html.H6([
                    html.I(className="fas fa-database me-2 info-icon", title="Configuración de datos de entrada para el algoritmo"),
                    "Configuración de Datos"
                ], className="text-primary mb-3 fw-bold"),
                html.Div([
                    html.Label([
                        html.I(className="fas fa-map-marker-alt me-2 text-muted", title="Cantidad de puntos de entrega a optimizar en la ruta"),
                        "Número de Puntos de Entrega"
                    ], className="slider-label"),
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

                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2", title="Genera nuevos puntos de entrega aleatorios"),
                    "Generar Nuevos Datos"
                ], id='btn-generar', className="btn-custom btn-primary-custom btn-ripple w-100 mt-3"),
            ], className="mb-4"),

            html.Hr(className="my-3"),

            # Grupo 2: Parámetros del algoritmo
            html.Div([
                html.H6([
                    html.I(className="fas fa-cogs me-2 info-icon", title="Configuración avanzada del algoritmo genético"),
                    "Parámetros del Algoritmo Genético"
                ], className="text-primary mb-3 fw-bold"),

                # Primera fila: Población y Generaciones
                dbc.Row([
                    dbc.Col([
                        html.Label([
                            html.I(className="fas fa-users me-2 text-muted", title="Cantidad de soluciones candidatas en cada generación"),
                            "Tamaño Población"
                        ], className="slider-label"),
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
                        html.Label([
                            html.I(className="fas fa-clock me-2 text-muted"),
                            "Número Generaciones"
                        ], className="slider-label"),
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
                        html.Label([
                            html.I(className="fas fa-random me-2 text-muted"),
                            "Probabilidad Cruza"
                        ], className="slider-label"),
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
                        html.Label([
                            html.I(className="fas fa-dna me-2 text-muted"),
                            "Probabilidad Mutación"
                        ], className="slider-label"),
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
                html.H6([
                    html.I(className="fas fa-play-circle me-2 info-icon"),
                    "Control de Ejecución"
                ], className="text-primary mb-3 fw-bold"),

                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-play me-2"),
                            "Iniciar Optimización"
                        ], id='btn-iniciar', className="btn-custom btn-success-custom btn-glow w-100 mb-2"),

                        dbc.Button([
                            html.I(className="fas fa-pause me-2"),
                            "Pausar"
                        ], id='btn-pausar', className="btn-custom btn-warning-custom btn-pulse w-100 mb-2", disabled=True)
                    ], width=6),

                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-redo me-2"),
                            "Reiniciar"
                        ], id='btn-reiniciar', className="btn-custom btn-danger-custom btn-bounce w-100 mb-2"),

                        dbc.Button([
                            html.I(className="fas fa-download me-2"),
                            "Exportar Resultados"
                        ], id='btn-exportar', className="btn-custom btn-secondary-custom btn-ripple w-100")
                    ], width=6)
                ])
            ])
        ])
    ], className="shadow-sm")
