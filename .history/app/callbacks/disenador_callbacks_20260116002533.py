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
            prevent_initial_call='initial_duplicate'
        )
        def agregar_punto_directo(click_data, btn_agregar, dataset_actual):
            """
            Agrega un punto directamente al dataset sin abrir modal.
            """
            print(f"🎯 CLICK CALLBACK: click_data={click_data is not None}, btn_agregar={btn_agregar}")

            # Inicializar dataset si no existe
            if dataset_actual is None:
                dataset_actual = []

            # Si hay click_data, es un click en el mapa
            if click_data and 'points' in click_data and click_data['points']:
                print("🗺️ CLICK EN MAPA DETECTADO")
                lat = click_data['points'][0]['lat']
                lon = click_data['points'][0]['lon']

                nuevo_punto = {
                    'id': len(dataset_actual) + 1,
                    'nombre': f'Punto {len(dataset_actual) + 1}',
                    'lat': lat,
                    'lon': lon,
                    'demanda': 1,
                    'tiempo_servicio': 15,
                    'ventana_inicio': '08:00',
                    'ventana_fin': '18:00'
                }

                dataset_actual.append(nuevo_punto)
                print(f"✅ PUNTO AGREGADO: {nuevo_punto}")
                return dataset_actual

            # Si hay btn_agregar, es el botón manual
            if btn_agregar:
                print("🔘 BOTÓN MANUAL PRESIONADO")
                nuevo_punto = {
                    'id': len(dataset_actual) + 1,
                    'nombre': f'Punto {len(dataset_actual) + 1}',
                    'lat': -8.1117 + (len(dataset_actual) * 0.001),
                    'lon': -79.0288 + (len(dataset_actual) * 0.001),
                    'demanda': 1,
                    'tiempo_servicio': 15,
                    'ventana_inicio': '08:00',
                    'ventana_fin': '18:00'
                }

                dataset_actual.append(nuevo_punto)
                print(f"✅ PUNTO MANUAL AGREGADO: {nuevo_punto}")
                return dataset_actual

            print("❓ NINGÚN TRIGGER DETECTADO")
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
            prevent_initial_call='initial_duplicate'
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
            [Output("modal-editar-punto", "is_open", allow_duplicate=True),
             Output("store-punto-editando", "data", allow_duplicate=True),
             Output("input-nombre-punto", "value", allow_duplicate=True),
             Output("input-direccion-punto", "value", allow_duplicate=True),
             Output("input-demanda-punto", "value", allow_duplicate=True),
             Output("input-tiempo-servicio", "value", allow_duplicate=True),
             Output("input-ventana-inicio", "value", allow_duplicate=True),
             Output("input-ventana-fin", "value", allow_duplicate=True)],
            Input({"type": "btn-editar-punto", "index": ALL}, "n_clicks"),
            State("store-dataset-manual", "data"),
            prevent_initial_call='initial_duplicate'
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
            Output("store-dataset-manual", "data", allow_duplicate=True),
            [Input("btn-guardar-edicion", "n_clicks"),
             Input("btn-limpiar-manual", "n_clicks")],
            [State("store-dataset-manual", "data"),
             State("store-punto-editando", "data"),
             State("input-nombre-punto", "value"),
             State("input-direccion-punto", "value"),
             State("input-demanda-punto", "value"),
             State("input-tiempo-servicio", "value"),
             State("input-ventana-inicio", "value"),
             State("input-ventana-fin", "value")],
            prevent_initial_call='initial_duplicate'
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
            [Output("modal-editar-punto", "is_open", allow_duplicate=True),
             Output("store-punto-editando", "data", allow_duplicate=True),
             Output("input-nombre-punto", "value", allow_duplicate=True),
             Output("input-direccion-punto", "value", allow_duplicate=True),
             Output("input-demanda-punto", "value", allow_duplicate=True),
             Output("input-tiempo-servicio", "value", allow_duplicate=True),
             Output("input-ventana-inicio", "value", allow_duplicate=True),
             Output("input-ventana-fin", "value", allow_duplicate=True)],
            [Input("btn-cancelar-edicion", "n_clicks")],
            prevent_initial_call='initial_duplicate'
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
