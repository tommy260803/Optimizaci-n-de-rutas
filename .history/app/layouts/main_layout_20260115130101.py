"""
Layout principal de la aplicación de optimización de rutas.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Importar componentes personalizados
from .controles import crear_panel_controles
from .metricas import crear_panel_metricas
from .disenador import crear_panel_disenador

# Importar componentes de visualización
from app.components.graficos import crear_grafico_convergencia_vacio
from app.components.mapa import crear_mapa_base
from app.components.tablas import crear_tabla_resultados_vacia

def crear_layout() -> dbc.Container:
    """
    Crea el layout principal de la aplicación.

    Returns:
        dbc.Container: Contenedor principal con todos los elementos de la interfaz.
    """
    return dbc.Container(fluid=True, children=[
        # Body container con id para cambio de tema
        html.Div(id="app-body", children=[
        # Header premium con animaciones
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.H1([
                        html.I(className="fas fa-route me-3", style={"color": "#2563eb"}, title="Sistema de optimización de rutas"),
                        html.Span("Optimización de Rutas de Reparto en Trujillo con Algoritmos Genéticos", style={"fontFamily": "'Poppins', sans-serif", "fontWeight": "700"})
                    ], className="app-title"),
                    html.P(
                        "Herramienta inteligente para optimizar rutas de reparto en la ciudad de Trujillo utilizando algoritmos genéticos avanzados. "
                        "Minimiza tiempo y costo de entrega con visualización en tiempo real y análisis predictivo.",
                        className="app-subtitle"
                    ),
                    # Información adicional
                    html.Div([
                        html.Small([
                            html.I(className="fas fa-magic me-2", style={"color": "#60a5fa"}),
                            html.Span("Optimización Inteligente de Rutas", style={"fontFamily": "'Inter', sans-serif"})
                        ], className="text-white-50")
                    ], className="mt-3")
                ], width=12)
            ])
        ], className="app-header glass-effect"),

        # Indicador de estado
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span(className="status-indicator status-idle"),
                    html.Small("Estado: ", className="text-dark fw-bold"),
                    html.Small("Listo para iniciar", id="status-text", className="text-dark fw-bold")
                ], className="text-center mb-3")
            ], width=12)
        ]),
        
        # Pestañas principales
        dbc.Tabs([
            # Pestaña de Optimización
            dbc.Tab(label="🚛 Optimización", tab_id="optimizacion", children=[
                # Controles en fila superior
                dbc.Row([
                    dbc.Col(
                        crear_panel_controles(),
                        width=12,
                        className="mb-4 controls-panel custom-card"
                    )
                ]),

                # Mapa y métricas en fila central
                dbc.Row([
                    # Mapa
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Mapa de Rutas Optimizadas", className="custom-card-header"),
                            dbc.CardBody(
                                dcc.Loading(
                                    id="loading-map",
                                    type="default",
                                    children=[
                                        dcc.Graph(
                                            id="mapa-rutas",
                                            figure=crear_mapa_base(),
                                            config={'displayModeBar': True},
                                            className="shadow-sm rounded"
                                        )
                                    ]
                                )
                            )
                        ], className="h-100 custom-card")
                    ], width=12, lg=8, className="mb-4"),

                    # Panel de métricas
                    dbc.Col([
                        crear_panel_metricas()
                    ], width=12, lg=4, className="mb-4")
                ]),

                # Gráfico y tabla en fila inferior
                dbc.Row([
                    # Gráfico de convergencia
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Evolución del Fitness", className="custom-card-header"),
                            dbc.CardBody(
                                dcc.Loading(
                                    id="loading-chart",
                                    type="default",
                                    children=[
                                        dcc.Graph(
                                            id="grafico-convergencia",
                                            figure=crear_grafico_convergencia_vacio(),
                                            config={'displayModeBar': True},
                                            className="shadow-sm rounded"
                                        )
                                    ]
                                )
                            )
                        ], className="h-100 custom-card")
                    ], width=12, lg=6, className="mb-4"),

                    # Tabla de resultados
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Mejores Rutas Encontradas", className="custom-card-header"),
                            dbc.CardBody(
                                crear_tabla_resultados_vacia()
                            )
                        ], className="h-100 custom-card")
                    ], width=12, lg=6, className="mb-4")
                ]),
            ]),

            # Pestaña de Visualización Completa
            dbc.Tab(label="🗺️ Ruta Completa", tab_id="ruta-completa", children=[
                dbc.Container(fluid=True, children=[
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H4("🚛 Visualización Detallada de la Ruta Óptima", className="text-primary mb-4"),
                                html.P(
                                    "Esta visualización muestra la secuencia completa de visita de la ruta óptima encontrada por el algoritmo genético. "
                                    "Cada número indica el orden de visita, comenzando desde el depósito (🏭) y regresando al mismo punto.",
                                    className="text-muted mb-4"
                                )
                            ])
                        ], width=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    dcc.Loading(
                                        id="loading-ruta-completa",
                                        type="default",
                                        children=[
                                            dcc.Graph(
                                                id="mapa-ruta-completa",
                                                figure=go.Figure(),  # Se actualizará con callback
                                                config={'displayModeBar': True},
                                                className="shadow-sm rounded"
                                            )
                                        ]
                                    )
                                )
                            ], className="shadow-sm")
                        ], width=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("📋 Información de la Ruta", className="text-primary mt-4 mb-3"),
                                html.Div(id="info-ruta-completa", children=[
                                    html.P("Ejecuta el algoritmo para ver la información detallada de la ruta óptima.",
                                           className="text-muted")
                                ])
                            ])
                        ], width=12)
                    ])
                ], className="mt-4")
            ]),

            # Pestaña de Diseñador de Datasets
            dbc.Tab(label="🎨 Diseñador de Datasets", tab_id="disenador", children=[
                crear_panel_disenador()
            ]),
        ], id="tabs-principales", active_tab="optimizacion", className="mb-4"),
        
        # Componentes de almacenamiento
        dcc.Store(id='store-datos'),  # Almacena los datos cargados
        dcc.Store(id='store-ag-estado'),  # Estado del algoritmo genético
        dcc.Store(id='store-historial'),  # Historial de ejecución

        # Componente para descarga de resultados
        dcc.Download(id='download-resultados'),

        # Intervalo para actualizaciones en tiempo real
        dcc.Interval(
            id='interval-actualizacion',
            interval=2000,  # milisegundos (2 segundos - balanceado)
            n_intervals=0,
            disabled=True
        )
        ], className="mt-4")  # Cerrar el div app-body
    ])  # Cerrar el Container
