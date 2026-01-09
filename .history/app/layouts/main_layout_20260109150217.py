"""
Layout principal de la aplicación de optimización de rutas.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

# Importar componentes personalizados
from .controles import crear_panel_controles
from .metricas import crear_panel_metricas

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
        # Título y descripción
        dbc.Row([
            dbc.Col([
                html.H1(
                    "Optimización de Rutas de Reparto en Trujillo con Algoritmos Genéticos",
                    className="text-center mb-3"
                ),
                html.P(
                    "Herramienta para optimizar rutas de reparto en la ciudad de Trujillo utilizando algoritmos genéticos. "
                    "Seleccione los parámetros y haga clic en 'Iniciar Optimización' para comenzar.",
                    className="text-muted text-center mb-4"
                ),
                html.Hr(className="my-2")
            ], width=12)
        ]),
        
        # Fila principal con controles y mapa
        dbc.Row([
            # Panel de controles
            dbc.Col(
                crear_panel_controles(),
                width=12, lg=3,
                className="mb-4"
            ),
            
            # Mapa
            dbc.Col([
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
            ], width=12, lg=9, className="mb-4")
        ], className="mb-4"),
        
        # Fila con gráfico de convergencia y métricas
        dbc.Row(className="mt-4", children=[
            # Gráfico de convergencia
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Evolución del Algoritmo", className="font-weight-bold"),
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
                ], className="h-100 shadow-sm")
            ], width=12, lg=8, className="mb-4"),
            
            # Panel de métricas
            dbc.Col([
                crear_panel_metricas()
            ], width=12, lg=4, className="mb-4")
        ]),
        
        # Tabla de resultados
        dbc.Row(className="mt-4", children=[
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Mejores Rutas Encontradas", className="font-weight-bold"),
                    dbc.CardBody(crear_tabla_resultados_vacia())
                ], className="shadow-sm")
            ], width=12)
        ]),
        
        # Componentes de almacenamiento
        dcc.Store(id='store-datos'),  # Almacena los datos cargados
        dcc.Store(id='store-ag-estado'),  # Estado del algoritmo genético
        dcc.Store(id='store-historial'),  # Historial de ejecución
        dcc.Store(id='store-poblacion-actual'),  # Población actual

        # Componente para descarga de resultados
        dcc.Download(id='download-resultados'),

        # Intervalo para actualizaciones en tiempo real
        dcc.Interval(
            id='interval-actualizacion',
            interval=500,  # milisegundos
            n_intervals=0,
            disabled=True
        )
    ], className="mt-4")
