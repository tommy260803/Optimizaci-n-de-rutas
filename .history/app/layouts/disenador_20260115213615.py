"""
Layout del diseñador de datasets personalizados.
"""
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from typing import List, Dict, Any
import json

# Importar componentes de visualización
from app.components.mapa import crear_mapa_base

def crear_panel_disenador() -> dbc.Container:
    """
    Crea el panel completo del diseñador de datasets.

    Returns:
        dbc.Container: Contenedor con todas las funcionalidades del diseñador.
    """
    return dbc.Container(fluid=True, children=[
        # Sub-pestañas del diseñador
        dbc.Tabs([
            # Ingreso Manual
            dbc.Tab(label="Manual", tab_id="manual", children=[
                _crear_panel_manual()
            ]),

            # Importación CSV
            dbc.Tab(label="Importar CSV", tab_id="importar", children=[
                _crear_panel_importar()
            ]),

            # Generación Asistida
            dbc.Tab(label="Generar", tab_id="generar", children=[
                _crear_panel_generar()
            ]),
        ], id="tabs-disenador", active_tab="manual", className="mb-4"),

        # Vista previa y controles
        dbc.Row([
            # Mapa de vista previa
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Vista Previa del Dataset", className="custom-card-header"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="mapa-disenador",
                            figure=crear_mapa_base(),
                            config={'displayModeBar': True},
                            className="shadow-sm rounded"
                        )
                    ])
                ], className="h-100 custom-card")
            ], width=12, lg=8, className="mb-4"),

            # Panel de información y controles
            dbc.Col([
                _crear_panel_info_disenador()
            ], width=12, lg=4, className="mb-4")
        ]),

        # Stores específicos del diseñador
        dcc.Store(id='store-dataset-manual'),  # Datos del ingreso manual
        dcc.Store(id='store-dataset-importado'),  # Datos importados
        dcc.Store(id='store-dataset-generado'),  # Datos generados
        dcc.Store(id='store-dataset-preview'),  # Datos para preview
    ])

def _crear_panel_manual() -> dbc.Container:
    """
    Crea el panel de ingreso manual de puntos.

    Returns:
        dbc.Container: Panel con mapa clickeable y formulario.
    """
    return dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col([
                html.H5("Ingreso Manual de Puntos", className="mb-3"),
                html.P(
                    "Haz click en el mapa para agregar puntos de entrega. "
                    "Luego completa la información de cada punto.",
                    className="text-muted mb-4"
                ),

                # Lista de puntos agregados
                dbc.Card([
                    dbc.CardHeader("Puntos Agregados", className="custom-card-header"),
                    dbc.CardBody([
                        html.Div(id="lista-puntos-manual", children=[
                            html.P("No hay puntos agregados aún", className="text-muted text-center")
                        ])
                    ])
                ], className="mb-3"),

                # Botones de control
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Agregar Punto Manual",
                            id="btn-agregar-punto-manual",
                            className="btn-custom btn-primary-custom w-100 mb-2"
                        ),
                        dbc.Button(
                            "Limpiar Todos",
                            id="btn-limpiar-manual",
                            className="btn-custom btn-danger-custom w-100 mb-2"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Button(
                            "Guardar Dataset",
                            id="btn-guardar-manual",
                            className="btn-custom btn-success-custom w-100 mb-2"
                        ),
                        dbc.Button(
                            "Usar en Optimización",
                            id="btn-usar-manual",
                            className="btn-custom btn-info-custom w-100"
                        )
                    ], width=6)
                ])
            ], width=12)
        ]),

        # Modal para editar punto
        dbc.Modal([
            dbc.ModalHeader("Editar Punto de Entrega"),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Nombre del Punto", className="fw-bold"),
                        dbc.Input(id="input-nombre-punto", type="text", placeholder="Ej: Tienda Central"),
                    ], width=12, className="mb-3"),

                    dbc.Col([
                        dbc.Label("Dirección", className="fw-bold"),
                        dbc.Input(id="input-direccion-punto", type="text", placeholder="Ej: Calle Principal 123"),
                    ], width=12, className="mb-3"),

                    dbc.Col([
                        dbc.Label("Demanda (unidades)", className="fw-bold"),
                        dbc.Input(id="input-demanda-punto", type="number", min=1, max=10, value=1),
                    ], width=6, className="mb-3"),

                    dbc.Col([
                        dbc.Label("Tiempo de Servicio (min)", className="fw-bold"),
                        dbc.Input(id="input-tiempo-servicio", type="number", min=5, max=60, value=15),
                    ], width=6, className="mb-3"),

                    dbc.Col([
                        dbc.Label("Ventana de Tiempo", className="fw-bold"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Input(id="input-ventana-inicio", type="time", value="08:00"),
                            ], width=6),
                            dbc.Col([
                                dbc.Input(id="input-ventana-fin", type="time", value="18:00"),
                            ], width=6)
                        ])
                    ], width=12, className="mb-3"),
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="btn-cancelar-edicion", className="btn-secondary"),
                dbc.Button("Guardar", id="btn-guardar-edicion", className="btn-primary")
            ])
        ], id="modal-editar-punto", size="lg", is_open=False),

        # Store para punto siendo editado
        dcc.Store(id='store-punto-editando')
    ])

def _crear_panel_importar() -> dbc.Container:
    """
    Crea el panel de importación de datos desde CSV.

    Returns:
        dbc.Container: Panel con upload y mapeo de columnas.
    """
    return dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col([
                html.H5("Importar Dataset desde CSV", className="mb-3"),
                html.P(
                    "Sube un archivo CSV con tus datos de puntos de entrega. "
                    "El sistema detectará automáticamente las columnas.",
                    className="text-muted mb-4"
                ),

                # Upload de archivo
                dbc.Card([
                    dbc.CardHeader("Subir Archivo", className="custom-card-header"),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload-csv',
                            children=html.Div([
                                'Arrastra y suelta tu archivo CSV aquí o ',
                                html.A('haz click para seleccionar', className="text-primary fw-bold")
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        ),

                        # Información del archivo
                        html.Div(id="info-archivo-csv", className="mt-3")
                    ])
                ], className="mb-3"),

                # Mapeo de columnas
                dbc.Card([
                    dbc.CardHeader("Mapeo de Columnas", className="custom-card-header"),
                    dbc.CardBody([
                        html.Div(id="mapeo-columnas", children=[
                            html.P("Sube un archivo CSV para ver las opciones de mapeo", className="text-muted text-center")
                        ])
                    ])
                ], className="mb-3"),

                # Vista previa de datos
                dbc.Card([
                    dbc.CardHeader("Vista Previa de Datos", className="custom-card-header"),
                    dbc.CardBody([
                        html.Div(id="preview-datos-csv", children=[
                            html.P("Los datos aparecerán aquí después del mapeo", className="text-muted text-center")
                        ])
                    ])
                ], className="mb-3"),

                # Botones de control
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Validar Datos",
                            id="btn-validar-csv",
                            className="btn-custom btn-warning-custom w-100 mb-2",
                            disabled=True
                        ),
                        dbc.Button(
                            "Limpiar",
                            id="btn-limpiar-csv",
                            className="btn-custom btn-danger-custom w-100"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Button(
                            "Guardar Dataset",
                            id="btn-guardar-csv",
                            className="btn-custom btn-success-custom w-100 mb-2",
                            disabled=True
                        ),
                        dbc.Button(
                            "Usar en Optimización",
                            id="btn-usar-csv",
                            className="btn-custom btn-info-custom w-100",
                            disabled=True
                        )
                    ], width=6)
                ])
            ], width=12)
        ]),

        # Stores para importación
        dcc.Store(id='store-archivo-csv'),
        dcc.Store(id='store-mapeo-columnas'),
        dcc.Store(id='store-datos-csv-procesados')
    ])

def _crear_panel_generar() -> dbc.Container:
    """
    Crea el panel de generación asistida de datasets.

    Returns:
        dbc.Container: Panel con wizard para generar datos.
    """
    return dbc.Container(fluid=True, children=[
        dbc.Row([
            dbc.Col([
                html.H5("Generación Asistida de Datasets", className="mb-3"),
                html.P(
                    "Crea datasets personalizados usando plantillas predefinidas "
                    "o configura parámetros avanzados.",
                    className="text-muted mb-4"
                ),

                # Templates predefinidos
                dbc.Card([
                    dbc.CardHeader("Plantillas Rápidas", className="custom-card-header"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("🏪 Pequeño Comercio", className="card-title"),
                                        html.P("10-15 puntos, demanda baja-moderada", className="card-text small"),
                                        dbc.Button(
                                            "Seleccionar",
                                            id="btn-template-pequeno",
                                            className="btn-custom btn-outline-primary btn-sm w-100 mt-2"
                                        )
                                    ])
                                ], className="text-center mb-3")
                            ], width=4),

                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("🏭 Cadena de Suministro", className="card-title"),
                                        html.P("20-30 puntos, demanda variable", className="card-text small"),
                                        dbc.Button(
                                            "Seleccionar",
                                            id="btn-template-mediano",
                                            className="btn-custom btn-outline-primary btn-sm w-100 mt-2"
                                        )
                                    ])
                                ], className="text-center mb-3")
                            ], width=4),

                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("🌆 Ciudad Completa", className="card-title"),
                                        html.P("40-50 puntos, distribución urbana", className="card-text small"),
                                        dbc.Button(
                                            "Seleccionar",
                                            id="btn-template-grande",
                                            className="btn-custom btn-outline-primary btn-sm w-100 mt-2"
                                        )
                                    ])
                                ], className="text-center mb-3")
                            ], width=4)
                        ])
                    ])
                ], className="mb-3"),

                # Configuración avanzada
                dbc.Card([
                    dbc.CardHeader("Configuración Avanzada", className="custom-card-header"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Número de Puntos", className="fw-bold"),
                                dcc.Slider(
                                    id='slider-num-puntos-generar',
                                    min=5,
                                    max=100,
                                    step=5,
                                    value=20,
                                    marks={5: '5', 50: '50', 100: '100'},
                                    tooltip={"placement": "bottom", "always_visible": True}
                                )
                            ], width=12, className="mb-3"),

                            dbc.Col([
                                dbc.Label("Distribución Geográfica", className="fw-bold"),
                                dcc.Dropdown(
                                    id='dropdown-distribucion',
                                    options=[
                                        {'label': 'Centro de Trujillo', 'value': 'centro'},
                                        {'label': 'Distritos Varios', 'value': 'distritos'},
                                        {'label': 'Área Urbana Completa', 'value': 'urbana'},
                                        {'label': 'Personalizada', 'value': 'personalizada'}
                                    ],
                                    value='centro',
                                    className="mb-3"
                                )
                            ], width=12, className="mb-3"),

                            dbc.Col([
                                dbc.Label("Tipo de Demanda", className="fw-bold"),
                                dcc.Dropdown(
                                    id='dropdown-demanda',
                                    options=[
                                        {'label': 'Uniforme (1-3 unidades)', 'value': 'uniforme_baja'},
                                        {'label': 'Variable (1-5 unidades)', 'value': 'variable'},
                                        {'label': 'Alta (3-8 unidades)', 'value': 'alta'},
                                        {'label': 'Mixta', 'value': 'mixta'}
                                    ],
                                    value='variable',
                                    className="mb-3"
                                )
                            ], width=12, className="mb-3")
                        ]),

                        dbc.Button(
                            "🎲 Generar Dataset",
                            id="btn-generar-dataset",
                            className="btn-custom btn-primary-custom w-100"
                        )
                    ])
                ], className="mb-3"),

                # Botones de control
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "🔄 Regenerar",
                            id="btn-regenerar-dataset",
                            className="btn-custom btn-warning-custom w-100 mb-2",
                            disabled=True
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Button(
                            "💾 Guardar Dataset",
                            id="btn-guardar-generado",
                            className="btn-custom btn-success-custom w-100 mb-2",
                            disabled=True
                        ),
                        dbc.Button(
                            "🚀 Usar en Optimización",
                            id="btn-usar-generado",
                            className="btn-custom btn-info-custom w-100",
                            disabled=True
                        )
                    ], width=6)
                ])
            ], width=12)
        ]),

        # Stores para generación
        dcc.Store(id='store-template-seleccionado'),
        dcc.Store(id='store-config-generacion'),
        dcc.Store(id='store-dataset-generado')
    ])

def _crear_panel_info_disenador() -> dbc.Card:
    """
    Crea el panel lateral con información y estadísticas del dataset.

    Returns:
        dbc.Card: Panel con información del dataset actual.
    """
    return dbc.Card([
        dbc.CardHeader("Información del Dataset", className="custom-card-header"),
        dbc.CardBody([
            # Estadísticas básicas
            html.Div([
                html.H6("📊 Estadísticas", className="mb-3"),
                html.Div(id="stats-dataset", children=[
                    html.P("No hay dataset cargado", className="text-muted small")
                ])
            ], className="mb-4"),

            # Validaciones
            html.Div([
                html.H6("✅ Validaciones", className="mb-3"),
                html.Div(id="validaciones-dataset", children=[
                    html.P("Las validaciones aparecerán aquí", className="text-muted small")
                ])
            ], className="mb-4"),

            # Acciones rápidas
            html.Div([
                html.H6("⚡ Acciones Rápidas", className="mb-3"),
                dbc.Button(
                    "📋 Ver como Tabla",
                    id="btn-ver-tabla-dataset",
                    className="btn-custom btn-outline-secondary btn-sm w-100 mb-2",
                    disabled=True
                ),
                dbc.Button(
                    "📥 Exportar CSV",
                    id="btn-exportar-dataset",
                    className="btn-custom btn-outline-secondary btn-sm w-100 mb-2",
                    disabled=True
                ),
                dbc.Button(
                    "🔄 Cargar Dataset Anterior",
                    id="btn-cargar-anterior",
                    className="btn-custom btn-outline-secondary btn-sm w-100",
                    disabled=True
                )
            ])
        ])
    ], className="h-100 custom-card")

# Funciones auxiliares para callbacks

def validar_dataset_manual(puntos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Valida un dataset creado manualmente.

    Args:
        puntos: Lista de puntos del dataset.

    Returns:
        Dict con resultados de validación.
    """
    errores = []
    warnings = []

    if not puntos:
        errores.append("El dataset está vacío")
        return {"valido": False, "errores": errores, "warnings": warnings}

    # Verificar depósito
    deposito = next((p for p in puntos if p.get('id') == 0), None)
    if not deposito:
        errores.append("Falta el punto de depósito (ID 0)")

    # Verificar coordenadas
    for punto in puntos:
        if 'lat' not in punto or 'lon' not in punto:
            errores.append(f"El punto {punto.get('id', 'desconocido')} no tiene coordenadas")
        elif not (-90 <= punto['lat'] <= 90) or not (-180 <= punto['lon'] <= 180):
            errores.append(f"Coordenadas inválidas para punto {punto.get('id', punto.get('nombre', 'desconocido'))}")

    # Verificar demandas
    for punto in puntos:
        if punto.get('id', 0) != 0 and punto.get('demanda', 0) <= 0:
            warnings.append(f"Demanda cero o negativa para punto {punto.get('id', punto.get('nombre', 'desconocido'))}")

    return {
        "valido": len(errores) == 0,
        "errores": errores,
        "warnings": warnings
    }

def calcular_estadisticas_dataset(puntos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula estadísticas básicas del dataset.

    Args:
        puntos: Lista de puntos del dataset.

    Returns:
        Dict con estadísticas.
    """
    if not puntos:
        return {}

    n_puntos = len(puntos)
    n_clientes = n_puntos - 1  # Excluyendo depósito

    demandas = [p.get('demanda', 0) for p in puntos if p.get('id', 0) != 0]
    demanda_total = sum(demandas)
    demanda_promedio = demanda_total / len(demandas) if demandas else 0

    # Área geográfica
    lats = [p['lat'] for p in puntos if 'lat' in p]
    lons = [p['lon'] for p in puntos if 'lon' in p]

    if lats and lons:
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)
        area_lat = lat_max - lat_min
        area_lon = lon_max - lon_min
    else:
        area_lat = area_lon = 0

    return {
        "n_puntos": n_puntos,
        "n_clientes": n_clientes,
        "demanda_total": demanda_total,
        "demanda_promedio": round(demanda_promedio, 2),
        "area_lat": round(area_lat, 4),
        "area_lon": round(area_lon, 4)
    }
