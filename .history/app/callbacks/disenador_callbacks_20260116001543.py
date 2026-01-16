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

# Funciones auxiliares para callbacks (sin decoradores para evitar conflictos)

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
