"""
Layout del panel de métricas para la interfaz de usuario.
"""
from dash import html
import dash_bootstrap_components as dbc

def crear_panel_metricas() -> dbc.Card:
    """
    Crea el panel de métricas en tiempo real.

    Returns:
        dbc.Card: Componente Card con las métricas.
    """
    return dbc.Card([
        dbc.CardHeader(
            "Métricas en Tiempo Real",
            className="custom-card-header"
        ),
        dbc.CardBody([
            # Primera fila de métricas principales
            dbc.Row([
                # Distancia Total
                dbc.Col([
                    html.Div([
                        html.H4(
                            "--",
                            id="metrica-distancia",
                            className="mb-1"
                        ),
                        html.P("Distancia Total", className="text-muted mb-0")
                    ], className="text-center")
                ], width=4, className="mb-3"),
                
                # Tiempo Estimado
                dbc.Col([
                    html.Div([
                        html.H4(
                            "--",
                            id="metrica-tiempo",
                            className="mb-1"
                        ),
                        html.P("Tiempo Estimado", className="text-muted mb-0")
                    ], className="text-center")
                ], width=4, className="mb-3"),
                
                # Generación Actual
                dbc.Col([
                    html.Div([
                        html.H4(
                            "0/0",
                            id="metrica-generacion",
                            className="mb-1"
                        ),
                        html.P("Generación Actual", className="text-muted mb-0")
                    ], className="text-center")
                ], width=4, className="mb-3")
            ], className="mb-4"),
            
            html.Hr(className="my-2"),
            
            # Segunda fila de métricas adicionales
            dbc.Row([
                # Mejora vs Inicial
                dbc.Col([
                    html.Div([
                        html.H5(
                            "--",
                            id="metrica-mejora",
                            className="mb-1"
                        ),
                        html.P("Mejora vs Inicial", className="text-muted mb-0")
                    ], className="text-center")
                ], width=4, className="mb-2"),
                
                # Mejor Fitness
                dbc.Col([
                    html.Div([
                        html.H5(
                            "--",
                            id="metrica-fitness",
                            className="mb-1"
                        ),
                        html.P("Mejor Fitness", className="text-muted mb-0")
                    ], className="text-center")
                ], width=4, className="mb-2"),
                
                # Diversidad
                dbc.Col([
                    html.Div([
                        html.H5(
                            "--",
                            id="metrica-diversidad",
                            className="mb-1"
                        ),
                        html.P("Diversidad", className="text-muted mb-0")
                    ], className="text-center")
                ], width=4, className="mb-2")
            ])
        ])
    ], className="h-100 shadow-sm")
