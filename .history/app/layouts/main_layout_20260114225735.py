"""
Layout principal de la aplicación de optimización de rutas.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

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
        # Header premium con animaciones
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.H1(
                        "🚛 Optimización de Rutas de Reparto en Trujillo con Algoritmos Genéticos",
                        className="app-title"
                    ),
                    html.P(
                        "Herramienta inteligente para optimizar rutas de reparto en la ciudad de Trujillo utilizando algoritmos genéticos avanzados. "
                        "Minimiza tiempo y costo de entrega con visualización en tiempo real y análisis predictivo.",
                        className="app-subtitle"
                    ),
                    # Toggle de tema
                    html.Div([
                        html.Span("🌞", id="theme-icon", style={"cursor": "pointer", "fontSize": "1.5rem"}),
                        dbc.Switch(
                            id='theme-toggle',
                            value=False,
                            className="ms-2"
                        ),
                        html.Small("Tema oscuro", className="ms-2 text-white-50")
                    ], className="mt-3 d-flex align-items-center")
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

            # Pestaña de Diseñador de Datasets
            dbc.Tab(label="🎨 Diseñador de Datasets", tab_id="disenador", children=[
                # Aquí irá el contenido del diseñador
                dbc.Row([
                    dbc.Col([
                        html.Div("Funcionalidad de diseñador próximamente disponible", className="text-center text-muted p-4")
                    ], width=12)
                ])
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
            interval=2000,  # milisegundos (2 segundos)
            n_intervals=0,
            disabled=True
        )
    ], className="mt-4")
