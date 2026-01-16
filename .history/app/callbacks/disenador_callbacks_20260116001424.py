"""
Callbacks para el diseñador de datasets personalizados.
"""
import logging
import base64
import io
import pandas as pd
import json
from typing import List, Dict, Any, Optional, Tuple
from dash import Input, Output, State, callback, no_update, ctx, ALL, html
import dash_bootstrap_components as dbc

from app.layouts.disenador import validar_dataset_manual, calcular_estadisticas_dataset
from src.generador_datos import GeneradorDatos

logger = logging.getLogger(__name__)

# Funciones auxiliares para callbacks (sin decoradores para evitar conflictos)

# Callbacks para importación CSV

@callback(
    [Output("store-archivo-csv", "data"),
     Output("info-archivo-csv", "children"),
     Output("mapeo-columnas", "children"),
     Output("btn-validar-csv", "disabled"),
     Output("preview-datos-csv", "children")],
    Input("upload-csv", "contents"),
    State("upload-csv", "filename")
)
def procesar_archivo_csv(contents, filename):
    """
    Procesa el archivo CSV subido y muestra información básica.
    """
    if not contents or not filename:
        return None, html.P("No se ha subido ningún archivo", className="text-muted"), \
               html.P("Sube un archivo CSV para ver las opciones de mapeo", className="text-muted text-center"), \
               True, html.P("Los datos aparecerán aquí después del mapeo", className="text-muted text-center")

    try:
        # Decodificar el contenido del archivo
        content_string = contents.split(',')[1]
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=None, engine='python')

        # Información del archivo
        info = html.Div([
            html.Strong(f"{filename}"),
            html.Br(),
            html.Small(f"Filas: {len(df)} | Columnas: {len(df.columns)}", className="text-muted"),
            html.Br(),
            html.Small(f"Columnas detectadas: {', '.join(df.columns.tolist())}", className="text-muted")
        ])

        # Crear interfaz de mapeo de columnas
        mapeo_ui = crear_interfaz_mapeo(df.columns.tolist())

        # Deshabilitar validación inicialmente
        return df.to_dict('records'), info, mapeo_ui, True, \
               html.P("Configura el mapeo de columnas y valida los datos", className="text-muted text-center")

    except Exception as e:
        error_msg = f"Error al procesar el archivo: {str(e)}"
        logger.error(error_msg)
        return None, html.Div(error_msg, className="text-danger"), \
               html.P("Error en el archivo", className="text-danger text-center"), \
               True, html.Div("No se pudieron cargar los datos", className="text-danger text-center")

def crear_interfaz_mapeo(columnas_df: List[str]) -> html.Div:
    """
    Crea la interfaz para mapear columnas del CSV.
    """
    campos_requeridos = [
        ('ID', 'id', 'Identificador único del punto'),
        ('Nombre', 'nombre', 'Nombre del punto'),
        ('Latitud', 'lat', 'Coordenada de latitud'),
        ('Longitud', 'lon', 'Coordenada de longitud'),
        ('Demanda', 'demanda', 'Cantidad a entregar'),
        ('Tiempo de Servicio', 'tiempo_servicio', 'Minutos para servicio'),
        ('Ventana Inicio', 'ventana_inicio', 'Hora de apertura (HH:MM)'),
        ('Ventana Fin', 'ventana_fin', 'Hora de cierre (HH:MM)')
    ]

    filas_mapeo = []
    for label, campo, descripcion in campos_requeridos:
        fila = dbc.Row([
            dbc.Col([
                dbc.Label(f"{label} *", className="fw-bold"),
                html.Small(descripcion, className="text-muted d-block")
            ], width=4),
            dbc.Col([
                dcc.Dropdown(
                    id=f"dropdown-mapeo-{campo}",
                    options=[{'label': col, 'value': col} for col in columnas_df] + [{'label': 'No mapear', 'value': None}],
                    value=None,
                    placeholder=f"Seleccionar columna para {campo}",
                    className="mb-2"
                )
            ], width=8)
        ], className="mb-3")
        filas_mapeo.append(fila)

    # Botón para aplicar mapeo
    filas_mapeo.append(
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Aplicar Mapeo",
                    id="btn-aplicar-mapeo",
                    className="btn-custom btn-primary-custom w-100"
                )
            ], width=12)
        ])
    )

    return html.Div(filas_mapeo)

@callback(
    [Output("store-mapeo-columnas", "data"),
     Output("store-datos-csv-procesados", "data"),
     Output("preview-datos-csv", "children"),
     Output("btn-validar-csv", "disabled", allow_duplicate=True)],
    Input("btn-aplicar-mapeo", "n_clicks"),
    [State("store-archivo-csv", "data"),
     State("dropdown-mapeo-id", "value"),
     State("dropdown-mapeo-nombre", "value"),
     State("dropdown-mapeo-lat", "value"),
     State("dropdown-mapeo-lon", "value"),
     State("dropdown-mapeo-demanda", "value"),
     State("dropdown-mapeo-tiempo_servicio", "value"),
     State("dropdown-mapeo-ventana_inicio", "value"),
     State("dropdown-mapeo-ventana_fin", "value")],
    prevent_initial_call=True
)
def aplicar_mapeo_csv(btn_aplicar, datos_csv, id_col, nombre_col, lat_col, lon_col, demanda_col, tiempo_col, ventana_inicio_col, ventana_fin_col):
    """
    Aplica el mapeo de columnas y procesa los datos CSV.
    """
    if not btn_aplicar or not datos_csv:
        return no_update, no_update, no_update, no_update

    try:
        # Crear diccionario de mapeo
        mapeo = {
            'id': id_col,
            'nombre': nombre_col,
            'lat': lat_col,
            'lon': lon_col,
            'demanda': demanda_col,
            'tiempo_servicio': tiempo_col,
            'ventana_inicio': ventana_inicio_col,
            'ventana_fin': ventana_fin_col
        }

        # Filtrar mapeos válidos
        mapeo_valido = {k: v for k, v in mapeo.items() if v is not None}

        # Procesar datos
        puntos_procesados = []
        for i, fila in enumerate(datos_csv):
            punto = {'id': i}

            # Aplicar mapeo
            for campo_app, columna_csv in mapeo_valido.items():
                if columna_csv in fila:
                    punto[campo_app] = fila[columna_csv]

            # Valores por defecto para campos faltantes
            punto.setdefault('nombre', f'Punto {i}')
            punto.setdefault('lat', -8.1117)
            punto.setdefault('lon', -79.0288)
            punto.setdefault('demanda', 1)
            punto.setdefault('tiempo_servicio', 15)
            punto.setdefault('ventana_inicio', '08:00')
            punto.setdefault('ventana_fin', '18:00')

            puntos_procesados.append(punto)

        # Crear preview de tabla
        df_preview = pd.DataFrame(puntos_procesados).head(10)
        preview = dbc.Table.from_dataframe(df_preview, striped=True, bordered=True, hover=True, size="sm")

        return mapeo, puntos_procesados, preview, False

    except Exception as e:
        error_msg = f"Error al aplicar mapeo: {str(e)}"
        logger.error(error_msg)
        return None, None, html.Div(error_msg, className="text-danger"), True

# Callbacks para generación asistida

@callback(
    Output("store-template-seleccionado", "data"),
    [Input("btn-template-pequeno", "n_clicks"),
     Input("btn-template-mediano", "n_clicks"),
     Input("btn-template-grande", "n_clicks")],
    prevent_initial_call=True
)
def seleccionar_template(btn_pequeno, btn_mediano, btn_grande):
    """
    Selecciona un template predefinido para generación.
    """
    triggered = ctx.triggered_id

    templates = {
        "btn-template-pequeno": {"tipo": "pequeno", "n_puntos": 12, "descripcion": "Pequeño Comercio"},
        "btn-template-mediano": {"tipo": "mediano", "n_puntos": 25, "descripcion": "Cadena de Suministro"},
        "btn-template-grande": {"tipo": "grande", "n_puntos": 45, "descripcion": "Ciudad Completa"}
    }

    if triggered in templates:
        return templates[triggered]

    return no_update

@callback(
    [Output("store-config-generacion", "data"),
     Output("btn-generar-dataset", "disabled")],
    [Input("slider-num-puntos-generar", "value"),
     Input("dropdown-distribucion", "value"),
     Input("dropdown-demanda", "value"),
     Input("store-template-seleccionado", "data")],
    prevent_initial_call=True
)
def actualizar_config_generacion(n_puntos, distribucion, tipo_demanda, template):
    """
    Actualiza la configuración para generación de datasets.
    """
    config = {
        "n_puntos": n_puntos or 20,
        "distribucion": distribucion or "centro",
        "tipo_demanda": tipo_demanda or "variable",
        "template": template
    }

    # Si hay template seleccionado, usar sus valores
    if template:
        config.update(template)

    return config, False

@callback(
    [Output("store-dataset-generado", "data"),
     Output("btn-regenerar-dataset", "disabled"),
     Output("btn-guardar-generado", "disabled"),
     Output("btn-usar-generado", "disabled")],
    Input("btn-generar-dataset", "n_clicks"),
    State("store-config-generacion", "data"),
    prevent_initial_call=True
)
def generar_dataset_asistido(btn_generar, config):
    """
    Genera un dataset usando la configuración especificada.
    """
    if not btn_generar or not config:
        return no_update, no_update, no_update, no_update

    try:
        # Configurar el generador
        centro_lat = -8.1117
        centro_lon = -79.0288

        # Ajustar centro según distribución
        if config.get("distribucion") == "distritos":
            # Centro ligeramente desplazado para cubrir más distritos
            centro_lat = -8.12
            centro_lon = -79.03
        elif config.get("distribucion") == "urbana":
            # Centro más amplio
            centro_lat = -8.11
            centro_lon = -79.02

        generador = GeneradorDatos(centro_lat=centro_lat, centro_lon=centro_lon)

        # Generar datos
        n_puntos = config.get("n_puntos", 20)
        df_puntos = generador.generar_puntos_aleatorios(n_puntos=n_puntos, seed=42)

        # Convertir a formato de lista de diccionarios
        puntos_generados = df_puntos.to_dict('records')

        # Aplicar tipo de demanda si especificado
        tipo_demanda = config.get("tipo_demanda", "variable")
        for punto in puntos_generados:
            if punto['id'] != 0:  # No modificar depósito
                if tipo_demanda == "uniforme_baja":
                    punto['demanda'] = np.random.randint(1, 4)
                elif tipo_demanda == "alta":
                    punto['demanda'] = np.random.randint(3, 9)
                elif tipo_demanda == "mixta":
                    punto['demanda'] = np.random.choice([1, 2, 5, 8], p=[0.4, 0.3, 0.2, 0.1])
                # Para "variable" mantener valores originales

        return puntos_generados, False, False, False

    except Exception as e:
        logger.error(f"Error generando dataset: {str(e)}")
        return [], True, True, True

# Callbacks para el mapa de preview

@callback(
    Output("mapa-disenador", "figure"),
    [Input("store-dataset-manual", "data"),
     Input("store-datos-csv-procesados", "data"),
     Input("store-dataset-generado", "data"),
     Input("tabs-disenador", "active_tab")],
    prevent_initial_call=False
)
def actualizar_mapa_disenador(dataset_manual, dataset_csv, dataset_generado, tab_activa, mapa_id=None):
    """
    Actualiza el mapa del diseñador con los puntos actuales.
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Callback actualizar_mapa_disenador ejecutado - Tab: {tab_activa}")

    from app.components.mapa import crear_mapa_completo, crear_mapa_base

    # Determinar qué dataset mostrar según la pestaña activa
    dataset_activo = None
    if tab_activa == "manual":
        dataset_activo = dataset_manual
    elif tab_activa == "importar":
        dataset_activo = dataset_csv
    elif tab_activa == "generar":
        dataset_activo = dataset_generado

    # Si no hay dataset activo, devolver mapa base
    if not dataset_activo:
        logger.info("No hay dataset activo, devolviendo mapa base")
        return crear_mapa_base()

    try:
        logger.info(f"Procesando dataset con {len(dataset_activo)} puntos")

        # Convertir dataset a DataFrame de pandas
        df_puntos = pd.DataFrame(dataset_activo)

        # Asegurar que las columnas necesarias existan
        columnas_requeridas = ['id', 'nombre', 'lat', 'lon', 'demanda', 'tiempo_servicio', 'ventana_inicio', 'ventana_fin']
        for col in columnas_requeridas:
            if col not in df_puntos.columns:
                if col == 'id':
                    df_puntos[col] = range(len(df_puntos))
                elif col in ['lat', 'lon']:
                    df_puntos[col] = -8.1117 if col == 'lat' else -79.0288
                elif col == 'demanda':
                    df_puntos[col] = 1
                elif col == 'tiempo_servicio':
                    df_puntos[col] = 15
                elif col == 'ventana_inicio':
                    df_puntos[col] = '08:00'
                elif col == 'ventana_fin':
                    df_puntos[col] = '18:00'
                else:
                    df_puntos[col] = f'Valor por defecto'

        # Asegurar que el depósito tenga id=0 si existe
        if 0 not in df_puntos['id'].values:
            logger.info("Agregando depósito automáticamente")
            deposito = pd.DataFrame([{
                'id': 0,
                'nombre': 'Depósito Central',
                'lat': -8.1117,
                'lon': -79.0288,
                'demanda': 0,
                'tiempo_servicio': 0,
                'ventana_inicio': '08:00',
                'ventana_fin': '18:00'
            }])
            df_puntos = pd.concat([deposito, df_puntos], ignore_index=True)

        # Convertir id a numérico para asegurar compatibilidad
        df_puntos['id'] = pd.to_numeric(df_puntos['id'], errors='coerce')

        logger.info(f"DataFrame final tiene {len(df_puntos)} filas")
        logger.info(f"IDs en dataset: {sorted(df_puntos['id'].unique())}")

        # Usar la función estándar para crear el mapa
        mapa = crear_mapa_completo(df_puntos)
        logger.info("Mapa creado exitosamente")
        return mapa

    except Exception as e:
        logger.error(f"Error actualizando mapa diseñador: {str(e)}")
        import traceback
        traceback.print_exc()
        return crear_mapa_base()

# Callbacks para estadísticas y validaciones

@callback(
    [Output("stats-dataset", "children"),
     Output("validaciones-dataset", "children")],
    [Input("store-dataset-manual", "data"),
     Input("store-datos-csv-procesados", "data"),
     Input("store-dataset-generado", "data"),
     Input("tabs-disenador", "active_tab")]
)
def actualizar_info_dataset(dataset_manual, dataset_csv, dataset_generado, tab_activa):
    """
    Actualiza las estadísticas y validaciones del dataset actual.
    """
    # Determinar qué dataset mostrar según la pestaña activa
    dataset_activo = None
    if tab_activa == "manual":
        dataset_activo = dataset_manual
    elif tab_activa == "importar":
        dataset_activo = dataset_csv
    elif tab_activa == "generar":
        dataset_activo = dataset_generado

    if not dataset_activo:
        return [
            html.P("No hay dataset cargado", className="text-muted small"),
            html.P("Las validaciones aparecerán aquí", className="text-muted small")
        ]

    # Calcular estadísticas
    stats = calcular_estadisticas_dataset(dataset_activo)

    if stats:
        stats_html = [
            html.P(f"Total de puntos: {stats['n_puntos']}", className="small mb-1"),
            html.P(f"Puntos de entrega: {stats['n_clientes']}", className="small mb-1"),
            html.P(f"Demanda total: {stats['demanda_total']}", className="small mb-1"),
            html.P(f"Demanda promedio: {stats['demanda_promedio']}", className="small mb-1"),
            html.P(f"Área cubierta: {stats['area_lat']:.3f}° × {stats['area_lon']:.3f}°", className="small mb-1")
        ]
    else:
        stats_html = [html.P("Error calculando estadísticas", className="text-danger small")]

    # Validar dataset
    validacion = validar_dataset_manual(dataset_activo)

    if validacion["valido"]:
        color_val = "success"
        icono_val = "✓"
        texto_val = "Dataset válido"
    else:
        color_val = "danger"
        icono_val = "✗"
        texto_val = "Dataset inválido"

    validaciones_html = [
        html.Div([
            html.Span(f"{icono_val} {texto_val}", className=f"text-{color_val} fw-bold small"),
        ], className="mb-2")
    ]

    if validacion["errores"]:
        validaciones_html.append(html.Div([
            html.Strong("Errores:", className="text-danger small"),
            html.Ul([html.Li(error, className="text-danger small") for error in validacion["errores"]])
        ]))

    if validacion["warnings"]:
        validaciones_html.append(html.Div([
            html.Strong("Advertencias:", className="text-warning small"),
            html.Ul([html.Li(warn, className="text-warning small") for warn in validacion["warnings"]])
        ]))

    return stats_html, validaciones_html

# Callback para usar dataset en optimización

@callback(
    Output("store-datos", "data"),
    [Input("btn-usar-manual", "n_clicks"),
     Input("btn-usar-csv", "n_clicks"),
     Input("btn-usar-generado", "n_clicks")],
    [State("store-dataset-manual", "data"),
     State("store-datos-csv-procesados", "data"),
     State("store-dataset-generado", "data"),
     State("tabs-disenador", "active_tab")],
    prevent_initial_call=True
)
def usar_dataset_en_optimizacion(btn_manual, btn_csv, btn_generado, dataset_manual, dataset_csv, dataset_generado, tab_activa):
    """
    Transfiere el dataset del diseñador al store principal para usar en optimización.
    """
    triggered = ctx.triggered_id

    dataset_a_usar = None

    if triggered == "btn-usar-manual":
        dataset_a_usar = dataset_manual
    elif triggered == "btn-usar-csv":
        dataset_a_usar = dataset_csv
    elif triggered == "btn-usar-generado":
        dataset_a_usar = dataset_generado

    if dataset_a_usar:
        # Convertir a formato esperado por el algoritmo genético
        # Agregar depósito si no existe
        deposito_existe = any(p.get('id') == 0 for p in dataset_a_usar)
        if not deposito_existe:
            deposito = {
                'id': 0,
                'nombre': 'Depósito Central',
                'lat': -8.1117,
                'lon': -79.0288,
                'demanda': 0,
                'tiempo_servicio': 0,
                'ventana_inicio': '08:00',
                'ventana_fin': '18:00'
            }
            dataset_a_usar.insert(0, deposito)

        return dataset_a_usar

    return no_update

# Función para registrar todos los callbacks del diseñador
def registrar_callbacks_disenador(app):
    """
    Registra todos los callbacks del diseñador de datasets manualmente.
    """
    try:
        # Importar aquí para evitar problemas de importación circular
        from app.components.mapa import crear_mapa_completo, crear_mapa_base

        # 1. Callback para agregar puntos directamente (click en mapa y botón)
        @app.callback(
            Output("store-dataset-manual", "data", allow_duplicate=True),
            [Input("mapa-disenador", "clickData"),
             Input("btn-agregar-punto-manual", "n_clicks")],
            [State("store-dataset-manual", "data")],
            prevent_initial_call=True
        )
        def agregar_punto_directo(click_data, btn_agregar, dataset_actual):
            """
            Agrega un punto directamente al dataset sin abrir modal.
            """
            from dash import ctx

            triggered = ctx.triggered_id if ctx.triggered else None

            if not triggered:
                return no_update

            # Inicializar dataset si no existe
            if dataset_actual is None:
                dataset_actual = []

            if triggered == "mapa-disenador" and click_data:
                # Obtener coordenadas del click
                lat = click_data['points'][0]['lat']
                lon = click_data['points'][0]['lon']

                # Crear nuevo punto
                nuevo_punto = {
                    'id': len(dataset_actual) + 1,  # ID incremental
                    'nombre': f'Punto {len(dataset_actual) + 1}',
                    'lat': lat,
                    'lon': lon,
                    'demanda': 1,
                    'tiempo_servicio': 15,
                    'ventana_inicio': '08:00',
                    'ventana_fin': '18:00'
                }

                # Agregar punto al dataset
                dataset_actual.append(nuevo_punto)
                print(f"DEBUG: Punto agregado por click en mapa: {nuevo_punto}")
                return dataset_actual

            elif triggered == "btn-agregar-punto-manual":
                # Agregar punto manual (coordenadas por defecto cerca del centro)
                nuevo_punto = {
                    'id': len(dataset_actual) + 1,  # ID incremental
                    'nombre': f'Punto {len(dataset_actual) + 1}',
                    'lat': -8.1117 + (len(dataset_actual) * 0.001),  # Pequeña variación para no solapar
                    'lon': -79.0288 + (len(dataset_actual) * 0.001),
                    'demanda': 1,
                    'tiempo_servicio': 15,
                    'ventana_inicio': '08:00',
                    'ventana_fin': '18:00'
                }

                # Agregar punto al dataset
                dataset_actual.append(nuevo_punto)
                print(f"DEBUG: Punto agregado por botón manual: {nuevo_punto}")
                return dataset_actual

            return no_update

        # 2. Callback para actualizar la lista de puntos
        @app.callback(
            Output("lista-puntos-manual", "children"),
            Input("store-dataset-manual", "data")
        )
        def actualizar_lista_puntos(dataset):
            """
            Actualiza la lista visual de puntos agregados.
            """
            if not dataset:
                return html.P("No hay puntos agregados aún", className="text-muted text-center")

            items = []
            for punto in dataset:
                item = dbc.ListGroupItem([
                    html.Div([
                        html.Strong(f"{punto.get('nombre', f'Punto {punto.get('id', 0)}')}"),
                        html.Br(),
                        html.Small([
                            f"ID: {punto.get('id', 0)} | ",
                            ".3f"                    ".3f"                    f" | Demanda: {punto.get('demanda', 0)}"
                        ], className="text-muted"),
                        dbc.Button(
                            "Editar",
                            id={"type": "btn-editar-punto", "index": punto.get('id', 0)},
                            className="btn btn-outline-primary btn-sm ms-2",
                            size="sm"
                        ),
                        dbc.Button(
                            "Eliminar",
                            id={"type": "btn-eliminar-punto", "index": punto.get('id', 0)},
                            className="btn btn-outline-danger btn-sm ms-1",
                            size="sm"
                        )
                    ], className="d-flex justify-content-between align-items-center")
                ], className="mb-2")
                items.append(item)

            return dbc.ListGroup(items)

        # 3. Callback para eliminar puntos
        @app.callback(
            Output("store-dataset-manual", "data", allow_duplicate=True),
            Input({"type": "btn-eliminar-punto", "index": ALL}, "n_clicks"),
            State("store-dataset-manual", "data"),
            prevent_initial_call=True
        )
        def eliminar_punto_manual(btns_eliminar, dataset_actual):
            """
            Elimina un punto del dataset manual.
            """
            from dash import ctx

            if not ctx.triggered or not dataset_actual:
                return no_update

            # Encontrar cuál botón fue presionado
            triggered = ctx.triggered[0]
            button_id = triggered['prop_id'].split('.')[0]  # Obtener el ID completo

            # Parsear el ID del botón
            if 'btn-eliminar-punto' in button_id:
                try:
                    id_punto = int(button_id.split('"index":')[1].split('}')[0])
                    dataset_filtrado = [p for p in dataset_actual if p.get('id') != id_punto]
                    return dataset_filtrado
                except (ValueError, IndexError) as e:
                    print(f"Error parseando ID del botón eliminar: {e}")
                    return no_update

            return no_update

        # 4. Callback para editar puntos (abre modal)
        @app.callback(
            [Output("modal-editar-punto", "is_open"),
             Output("store-punto-editando", "data"),
             Output("input-nombre-punto", "value"),
             Output("input-direccion-punto", "value"),
             Output("input-demanda-punto", "value"),
             Output("input-tiempo-servicio", "value"),
             Output("input-ventana-inicio", "value"),
             Output("input-ventana-fin", "value")],
            Input({"type": "btn-editar-punto", "index": ALL}, "n_clicks"),
            State("store-dataset-manual", "data"),
            prevent_initial_call=True
        )
        def editar_punto_manual(btns_editar, dataset_actual):
            """
            Abre el modal para editar un punto existente.
            """
            from dash import ctx

            if not ctx.triggered or not dataset_actual:
                return [no_update] * 8

            # Encontrar cuál botón fue presionado
            triggered = ctx.triggered[0]
            button_id = triggered['prop_id'].split('.')[0]  # Obtener el ID completo

            # Parsear el ID del botón
            if 'btn-editar-punto' in button_id:
                try:
                    id_punto = int(button_id.split('"index":')[1].split('}')[0])
                    punto = next((p for p in dataset_actual if p.get('id') == id_punto), None)
                    if punto:
                        return [
                            True,  # Abrir modal
                            punto,  # Datos del punto siendo editado
                            punto.get('nombre', ''),
                            punto.get('direccion', ''),
                            punto.get('demanda', 1),
                            punto.get('tiempo_servicio', 15),
                            punto.get('ventana_inicio', '08:00'),
                            punto.get('ventana_fin', '18:00')
                        ]
                except (ValueError, IndexError) as e:
                    print(f"Error parseando ID del botón editar: {e}")

            return [no_update] * 8

        # 5. Callback para guardar punto editado
        @app.callback(
            Output("store-dataset-manual", "data"),
            [Input("btn-guardar-edicion", "n_clicks"),
             Input("btn-limpiar-manual", "n_clicks")],
            [State("store-dataset-manual", "data"),
             State("store-punto-editando", "data"),
             State("input-nombre-punto", "value"),
             State("input-direccion-punto", "value"),
             State("input-demanda-punto", "value"),
             State("input-tiempo-servicio", "value"),
             State("input-ventana-inicio", "value"),
             State("input-ventana-fin", "value")]
        )
        def guardar_punto_manual(btn_guardar, btn_limpiar, dataset_actual, punto_editando, nombre, direccion, demanda, tiempo_servicio, ventana_inicio, ventana_fin):
            """
            Guarda un punto editado en el dataset manual.
            """
            from dash import ctx

            if not ctx.triggered:
                return no_update

            triggered = ctx.triggered_id

            if triggered == "btn-limpiar-manual":
                return []

            if triggered == "btn-guardar-edicion" and punto_editando:
                # Actualizar datos del punto
                punto_actualizado = punto_editando.copy()
                punto_actualizado.update({
                    'nombre': nombre or punto_editando.get('nombre', ''),
                    'direccion': direccion or '',
                    'demanda': demanda or 1,
                    'tiempo_servicio': tiempo_servicio or 15,
                    'ventana_inicio': ventana_inicio or '08:00',
                    'ventana_fin': ventana_fin or '18:00'
                })

                # Agregar o actualizar en el dataset
                dataset = dataset_actual or []
                punto_existente = next((p for p in dataset if p.get('id') == punto_editando.get('id')), None)

                if punto_existente:
                    # Actualizar punto existente
                    for i, p in enumerate(dataset):
                        if p.get('id') == punto_editando.get('id'):
                            dataset[i] = punto_actualizado
                            break
                else:
                    # Agregar nuevo punto
                    dataset.append(punto_actualizado)

                return dataset

            return no_update

        # 6. Callback para cerrar modal
        @app.callback(
            [Output("modal-editar-punto", "is_open"),
             Output("store-punto-editando", "data"),
             Output("input-nombre-punto", "value"),
             Output("input-direccion-punto", "value"),
             Output("input-demanda-punto", "value"),
             Output("input-tiempo-servicio", "value"),
             Output("input-ventana-inicio", "value"),
             Output("input-ventana-fin", "value")],
            [Input("btn-cancelar-edicion", "n_clicks")],
            prevent_initial_call=True
        )
        def cerrar_modal(btn_cancelar):
            """
            Cierra el modal de edición.
            """
            return False, None, "", "", 1, 15, "08:00", "18:00"

        # 7. Callback del mapa (ya registrado arriba, pero lo mantenemos aquí para completitud)
        @app.callback(
            Output("mapa-disenador", "figure"),
            [Input("store-dataset-manual", "data"),
             Input("store-datos-csv-procesados", "data"),
             Input("store-dataset-generado", "data"),
             Input("tabs-disenador", "active_tab")]
        )
        def actualizar_mapa_disenador_manual(dataset_manual, dataset_csv, dataset_generado, tab_activa):
            """
            Actualiza el mapa del diseñador con los puntos actuales (versión manual).
            """
            print(f"DEBUG: Callback mapa diseñador ejecutado - Tab: {tab_activa}")

            # Determinar qué dataset mostrar según la pestaña activa
            dataset_activo = None
            if tab_activa == "manual":
                dataset_activo = dataset_manual
                print(f"DEBUG: Usando dataset manual: {len(dataset_activo) if dataset_activo else 0} puntos")
            elif tab_activa == "importar":
                dataset_activo = dataset_csv
                print(f"DEBUG: Usando dataset CSV: {len(dataset_activo) if dataset_activo else 0} puntos")
            elif tab_activa == "generar":
                dataset_activo = dataset_generado
                print(f"DEBUG: Usando dataset generado: {len(dataset_activo) if dataset_activo else 0} puntos")

            # Si no hay dataset activo, devolver mapa base
            if not dataset_activo:
                print("DEBUG: No hay dataset activo, devolviendo mapa base")
                return crear_mapa_base()

            try:
                print(f"DEBUG: Procesando dataset con {len(dataset_activo)} puntos")

                # Convertir dataset a DataFrame de pandas
                df_puntos = pd.DataFrame(dataset_activo)

                # Asegurar que las columnas necesarias existan
                columnas_requeridas = ['id', 'nombre', 'lat', 'lon', 'demanda', 'tiempo_servicio', 'ventana_inicio', 'ventana_fin']
                for col in columnas_requeridas:
                    if col not in df_puntos.columns:
                        if col == 'id':
                            df_puntos[col] = range(len(df_puntos))
                        elif col in ['lat', 'lon']:
                            df_puntos[col] = -8.1117 if col == 'lat' else -79.0288
                        elif col == 'demanda':
                            df_puntos[col] = 1
                        elif col == 'tiempo_servicio':
                            df_puntos[col] = 15
                        elif col == 'ventana_inicio':
                            df_puntos[col] = '08:00'
                        elif col == 'ventana_fin':
                            df_puntos[col] = '18:00'
                        else:
                            df_puntos[col] = f'Valor por defecto'

                # Asegurar que el depósito tenga id=0 si existe
                if 0 not in df_puntos['id'].values:
                    print("DEBUG: Agregando depósito automáticamente")
                    deposito = pd.DataFrame([{
                        'id': 0,
                        'nombre': 'Depósito Central',
                        'lat': -8.1117,
                        'lon': -79.0288,
                        'demanda': 0,
                        'tiempo_servicio': 0,
                        'ventana_inicio': '08:00',
                        'ventana_fin': '18:00'
                    }])
                    df_puntos = pd.concat([deposito, df_puntos], ignore_index=True)

                # Convertir id a numérico para asegurar compatibilidad
                df_puntos['id'] = pd.to_numeric(df_puntos['id'], errors='coerce')

                print(f"DEBUG: DataFrame final tiene {len(df_puntos)} filas")
                print(f"DEBUG: IDs en dataset: {sorted(df_puntos['id'].unique())}")

                # Usar la función estándar para crear el mapa
                mapa = crear_mapa_completo(df_puntos)
                print("DEBUG: Mapa creado exitosamente")
                return mapa

            except Exception as e:
                print(f"DEBUG: Error actualizando mapa diseñador: {str(e)}")
                import traceback
                traceback.print_exc()
                return crear_mapa_base()

        print("✓ Todos los callbacks del diseñador registrados manualmente")

    except Exception as e:
        print(f"✗ Error registrando callbacks del diseñador: {e}")
        import traceback
        traceback.print_exc()
