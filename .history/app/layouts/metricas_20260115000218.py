"""
Layout del panel de métricas para la interfaz de usuario.
"""
from dash import html
import dash_bootstrap_components as dbc

def crear_panel_metricas() -> dbc.Card:
    """
    Crea el panel de métricas en tiempo real con animaciones escalonadas.

    Returns:
        dbc.Card: Componente Card con las métricas premium.
    """
    return dbc.Card([
        dbc.CardHeader(
            "📊 Métricas en Tiempo Real",
            className="custom-card-header"
        ),
        dbc.CardBody([
            # Primera fila de métricas principales
            dbc.Row([
                # Distancia Total
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-route me-2"),
                            html.H4(
                                "--",
                                id="metrica-distancia",
                                className="mb-1"
                            )
                        ], className="metric-card hover-lift p-3")
                    ], className="text-center stagger-animation")
                ], width=4, className="mb-3"),

                # Tiempo Estimado
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-clock me-2"),
                            html.H4(
                                "--",
                                id="metrica-tiempo",
                                className="mb-1"
                            )
                        ], className="metric-card hover-lift p-3")
                    ], className="text-center stagger-animation")
                ], width=4, className="mb-3"),

                # Generación Actual
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-dna me-2"),
                            html.H4(
                                "0/0",
                                id="metrica-generacion",
                                className="mb-1 d-inline"
                            ),
                            html.Small(" gen", className="text-muted")
                        ], className="metric-card hover-lift p-3")
                    ], className="text-center stagger-animation")
                ], width=4, className="mb-3")
            ], className="mb-4"),

            html.Hr(className="my-3"),

            # Segunda fila de métricas adicionales
            dbc.Row([
                # Mejora vs Inicial
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line me-2"),
                            html.H5(
                                "--",
                                id="metrica-mejora",
                                className="mb-1 d-inline"
                            ),
                            html.Small("%", className="text-muted")
                        ], className="metric-card hover-lift p-2")
                    ], className="text-center stagger-animation")
                ], width=4, className="mb-2"),

                # Mejor Fitness
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-trophy me-2"),
                            html.H5(
                                "--",
                                id="metrica-fitness",
                                className="mb-1 d-inline"
                            ),
                            html.Small(" pts", className="text-muted")
                        ], className="metric-card hover-lift p-2")
                    ], className="text-center stagger-animation")
                ], width=4, className="mb-2"),

                # Diversidad
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-users me-2"),
                            html.H5(
                                "--",
                                id="metrica-diversidad",
                                className="mb-1 d-inline"
                            ),
                            html.Small(" var", className="text-muted")
                        ], className="metric-card hover-lift p-2")
                    ], className="text-center stagger-animation")
                ], width=4, className="mb-2")
            ]),

            # Indicador de progreso
            html.Div([
                html.Div(className="progress-indicator mt-3")
            ], id="progress-container", style={"display": "none"})
        ])
    ], className="h-100 shadow-sm glass-effect")
