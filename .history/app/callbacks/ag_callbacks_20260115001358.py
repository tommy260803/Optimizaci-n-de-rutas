"""
Callbacks para el control del algoritmo genético en la aplicación de optimización de rutas.
"""
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import threading
import time
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union

# Importar el algoritmo genético y generador de datos
from src.algoritmo_genetico import AlgoritmoGenetico
from src.generador_datos import GeneradorDatos, verificar_o_generar_datos
from src.funciones_fitness import fitness_completo
from src.operadores_geneticos import (
    seleccion_torneo, seleccion_ruleta,
    cruza_order, cruza_pmx,
    mutacion_swap, mutacion_inversion
)
from config import (
    RUTA_PUNTOS, RUTA_DISTANCIAS,
    DEFAULT_POBLACION, DEFAULT_GENERACIONES,
    DEFAULT_PROB_CRUZA, DEFAULT_PROB_MUTACION,
    PESO_DISTANCIA, PESO_TIEMPO, PESO_PENALIZACION
)

# Variables globales para el estado del algoritmo
global ag_instancia, ag_ejecutando, ag_thread
ag_instancia = None
ag_ejecutando = False
ag_thread = None

def registrar_callbacks(app):
    """
    Registra todos los callbacks relacionados con el algoritmo genético.
    
    Args:
        app: Instancia de la aplicación Dash.
    """
    @app.callback(
        Output('store-datos', 'data'),
        [Input('btn-generar', 'n_clicks')],
        [State('slider-puntos', 'value')]
    )
    def callback_generar_datos(n_clicks: Optional[int], num_puntos: int) -> Optional[Dict]:
        """
        Genera nuevos datos de puntos y distancias cuando se hace clic en el botón.
        
        Args:
            n_clicks: Número de veces que se ha hecho clic en el botón.
            num_puntos: Número de puntos a generar (sin contar el depósito).
            
        Returns:
            dict: Diccionario con los datos generados o None en caso de error.
        """
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
            
        try:
            # Crear instancia del generador
            generador = GeneradorDatos()
            
            # Generar puntos aleatorios (1 depósito + num_puntos de entrega)
            df_puntos = generador.generar_puntos_aleatorios(
                n_puntos=num_puntos + 1,  # +1 para incluir el depósito
                seed=None
            )
            
            # Calcular matriz de distancias
            matriz_distancias = generador.calcular_matriz_distancias(df_puntos)
            
            # Exportar a CSV
            generador.exportar_a_csv(df_puntos, matriz_distancias)
            
            # Retornar datos en formato compatible con dcc.Store
            return {
                'puntos': df_puntos.to_dict('records'),
                'distancias': matriz_distancias.to_dict('records')
            }
            
        except Exception as e:
            print(f"Error al generar datos: {str(e)}")
            return None

    @app.callback(
        [
            Output('store-ag-estado', 'data'),
            Output('interval-actualizacion', 'disabled'),
            Output('btn-iniciar', 'disabled'),
            Output('btn-pausar', 'disabled')
        ],
        [Input('btn-iniciar', 'n_clicks')],
        [
            State('slider-poblacion', 'value'),
            State('slider-generaciones', 'value'),
            State('slider-cruza', 'value'),
            State('slider-mutacion', 'value'),
            State('store-datos', 'data')
        ]
    )
    def callback_iniciar_algoritmo(
        n_clicks: Optional[int],
        tam_poblacion: int,
        num_generaciones: int,
        prob_cruza: float,
        prob_mutacion: float,
        datos: Dict
    ) -> tuple:
        """
        Inicia la ejecución del algoritmo genético en un hilo separado.
        
        Args:
            n_clicks: Número de veces que se ha hecho clic en el botón.
            tam_poblacion: Tamaño de la población.
            num_generaciones: Número de generaciones a ejecutar.
            prob_cruza: Probabilidad de cruza.
            prob_mutacion: Probabilidad de mutación.
            datos: Datos cargados en la aplicación.
            
        Returns:
            tuple: Estados actualizados de los componentes.
        """
        global ag_instancia, ag_ejecutando, ag_thread
        
        if n_clicks is None or n_clicks == 0 or not datos:
            raise PreventUpdate
            
        try:
            # Convertir datos de vuelta a DataFrames
            df_puntos = pd.DataFrame(datos['puntos'])
            matriz_distancias = pd.DataFrame(datos['distancias'])
            
            # Crear instancia del algoritmo genético
            ag_instancia = AlgoritmoGenetico(
                df_puntos=df_puntos,
                matriz_distancias=matriz_distancias,
                tamano_poblacion=tam_poblacion,
                num_generaciones=num_generaciones,
                prob_cruza=prob_cruza,
                prob_mutacion=prob_mutacion
            )
            
            # Función para ejecutar el algoritmo
            def ejecutar_algoritmo():
                global ag_ejecutando
                ag_ejecutando = True
                ag_instancia.ejecutar()
                ag_ejecutando = False
            
            # Iniciar el algoritmo en un hilo separado
            ag_thread = threading.Thread(target=ejecutar_algoritmo, daemon=True)
            ag_thread.start()
            
            # Retornar estados actualizados
            return (
                {'ejecutando': True, 'generacion_actual': 0},  # store-ag-estado
                False,  # interval-actualizacion disabled
                True,   # btn-iniciar disabled
                False   # btn-pausar disabled
            )
            
        except Exception as e:
            print(f"Error al iniciar el algoritmo: {str(e)}")
            raise PreventUpdate

    @app.callback(
        [
            Output('store-ag-estado', 'data', allow_duplicate=True),
            Output('interval-actualizacion', 'disabled', allow_duplicate=True),
            Output('btn-pausar', 'disabled', allow_duplicate=True),
            Output('btn-iniciar', 'disabled', allow_duplicate=True)
        ],
        [Input('btn-pausar', 'n_clicks')],
        prevent_initial_call=True
    )
    def callback_pausar(n_clicks: Optional[int]) -> tuple:
        """
        Pausa o reanuda la ejecución del algoritmo genético.
        
        Args:
            n_clicks: Número de veces que se ha hecho clic en el botón.
            
        Returns:
            tuple: Estados actualizados de los componentes.
        """
        global ag_instancia, ag_ejecutando
        
        if n_clicks is None or n_clicks == 0 or ag_instancia is None:
            raise PreventUpdate
            
        try:
            if ag_ejecutando:
                # Pausar la ejecución
                ag_instancia.pausar()
                ag_ejecutando = False
                return (
                    {'ejecutando': False, 'pausado': True},
                    True,   # Deshabilitar intervalo
                    False   # Habilitar botón de pausa
                )
            else:
                # Reanudar ejecución
                ag_instancia.reanudar()
                ag_ejecutando = True
                return (
                    {'ejecutando': True, 'pausado': False},
                    False,  # Habilitar intervalo
                    False   # Habilitar botón de pausa
                )
                
        except Exception as e:
            print(f"Error al pausar/reanudar: {str(e)}")
            raise PreventUpdate

    @app.callback(
        [
            Output('store-ag-estado', 'data', allow_duplicate=True),
            Output('store-historial', 'data', allow_duplicate=True),
            Output('interval-actualizacion', 'disabled', allow_duplicate=True),
            Output('btn-iniciar', 'disabled', allow_duplicate=True),
            Output('btn-pausar', 'disabled', allow_duplicate=True)
        ],
        [Input('btn-reiniciar', 'n_clicks')],
        prevent_initial_call=True
    )
    def callback_reiniciar(n_clicks: Optional[int]) -> tuple:
        """
        Reinicia el estado del algoritmo genético.
        
        Args:
            n_clicks: Número de veces que se ha hecho clic en el botón.
            
        Returns:
            tuple: Estados iniciales de los componentes.
        """
        global ag_instancia, ag_ejecutando, ag_thread
        
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
            
        try:
            # Detener la ejecución si está en curso
            if ag_instancia is not None:
                ag_instancia.detener()
                ag_instancia = None
                
            # Esperar a que el hilo termine
            if ag_thread is not None and ag_thread.is_alive():
                ag_thread.join(timeout=1.0)
                
            # Reiniciar variables globales
            ag_ejecutando = False
            ag_thread = None
            
            # Retornar estados iniciales
            return (
                None,  # Limpiar store-ag-estado
                None,  # Limpiar store-historial
                True,  # Deshabilitar intervalo
                False, # Habilitar botón iniciar
                True   # Deshabilitar botón pausar
            )
            
        except Exception as e:
            print(f"Error al reiniciar: {str(e)}")
            raise PreventUpdate

    @app.callback(
        [
            Output('store-historial', 'data'),
            Output('store-ag-estado', 'data', allow_duplicate=True),
            Output('interval-actualizacion', 'disabled', allow_duplicate=True),
            Output('btn-iniciar', 'disabled', allow_duplicate=True),
            Output('btn-pausar', 'disabled', allow_duplicate=True)
        ],
        [Input('interval-actualizacion', 'n_intervals')],
        [
            State('store-historial', 'data'),
            State('store-ag-estado', 'data'),
            State('interval-actualizacion', 'disabled'),
            State('btn-iniciar', 'disabled'),
            State('btn-pausar', 'disabled')
        ],
        prevent_initial_call=True
    )
    def callback_actualizar_progreso(
        n_intervals: int,
        historial_existente: Optional[Dict],
        estado_ag_existente: Optional[Dict],
        intervalo_disabled: bool,
        btn_iniciar_disabled: bool,
        btn_pausar_disabled: bool
    ) -> tuple:
        """
        Actualiza el progreso del algoritmo genético en intervalos regulares.

        Args:
            n_intervals: Número de intervalos transcurridos.
            historial_existente: Historial existente de ejecución.
            estado_ag_existente: Estado actual del algoritmo.
            intervalo_disabled: Estado actual del intervalo.
            btn_iniciar_disabled: Estado del botón iniciar.
            btn_pausar_disabled: Estado del botón pausar.

        Returns:
            tuple: (historial, estado_ag, intervalo_disabled, btn_iniciar_disabled, btn_pausar_disabled)
        """
        global ag_instancia, ag_ejecutando

        print(f"DEBUG: Callback de progreso ejecutándose - intervalo #{n_intervals}, disabled={intervalo_disabled}")

        # Si no hay instancia del algoritmo, retornar sin cambios
        if ag_instancia is None:
            print("DEBUG: No hay instancia de AG, saliendo del callback")
            raise PreventUpdate

        try:
            # Inicializar historial si no existe
            if historial_existente is None:
                historial = {
                    'mejores_fitness': [],
                    'fitness_promedio': [],
                    'peores_fitness': [],
                    'diversidad': [],
                    'generaciones': []
                }
            else:
                historial = historial_existente

            # Obtener estadísticas actuales con timeout
            try:
                if hasattr(ag_instancia, 'obtener_estadisticas'):
                    stats = ag_instancia.obtener_estadisticas()

                    # Agregar al historial
                    if stats:
                        historial['mejores_fitness'].append(stats.get('mejor_fitness', 0))
                        historial['fitness_promedio'].append(stats.get('fitness_promedio', 0))
                        historial['peores_fitness'].append(stats.get('peor_fitness', 0))
                        historial['diversidad'].append(stats.get('diversidad', 0))
                        historial['generaciones'].append(stats.get('generacion_actual', 0))

                        # Agregar mejores individuos si existe
                        if 'mejores_individuos' not in historial:
                            historial['mejores_individuos'] = []
                        if stats.get('mejor_individuo'):
                            historial['mejores_individuos'].append(stats['mejor_individuo'])

            except Exception as stats_error:
                print(f"Error al obtener estadísticas: {str(stats_error)}")
                # Continuar sin estadísticas si hay error

            # Verificar si el algoritmo terminó
            algoritmo_terminado = not ag_ejecutando and ag_instancia is not None and ag_instancia.ha_terminado()

            # Actualizar estado del algoritmo con información actual
            estado_ag_actualizado = estado_ag_existente or {}
            estado_ag_actualizado.update({
                'generacion_actual': ag_instancia.generacion_actual if ag_instancia else 0,
                'num_generaciones': ag_instancia.num_generaciones if ag_instancia else 500,
                'mejor_fitness': stats.get('mejor_fitness', 0) if stats else 0,
                'mejor_individuo': stats.get('mejor_individuo', []) if stats else []
            })

            if algoritmo_terminado:
                print(f"Algoritmo terminado - Generación final: {ag_instancia.generacion_actual}")
                # Deshabilitar intervalo y actualizar botones cuando termine
                return (
                    historial,
                    estado_ag_actualizado,  # Estado final
                    True,   # Deshabilitar intervalo
                    False,  # Habilitar botón iniciar
                    True    # Deshabilitar botón pausar
                )

            # Retornar estados actualizados durante ejecución
            return (
                historial,
                estado_ag_actualizado,  # Estado actualizado
                intervalo_disabled,
                btn_iniciar_disabled,
                btn_pausar_disabled
            )

        except Exception as e:
            print(f"Error en callback de actualización de progreso: {str(e)}")
            import traceback
            traceback.print_exc()
            # En caso de error grave, deshabilitar el intervalo para evitar bucles
            return (
                historial_existente or {},
                True,  # Deshabilitar intervalo por seguridad
                False, # Habilitar botón iniciar
                True   # Deshabilitar botón pausar
            )
    # Función callback_actualizar_progreso eliminada - ahora está arriba con mejor manejo de errores

    @app.callback(
        Output('download-resultados', 'data'),
        [Input('btn-exportar', 'n_clicks')],
        [
            State('store-historial', 'data'),
            State('store-datos', 'data'),
            State('store-ag-estado', 'data')
        ],
        prevent_initial_call=True
    )
    def callback_exportar_resultados(
        n_clicks: Optional[int],
        historial: Optional[Dict],
        datos: Optional[Dict],
        estado_ag: Optional[Dict]
    ):
        """
        Exporta los resultados de la optimización a un archivo JSON.

        Args:
            n_clicks: Número de veces que se ha hecho clic en el botón.
            historial: Datos del historial de ejecución.
            datos: Datos de puntos y distancias.
            estado_ag: Estado actual del algoritmo genético.

        Returns:
            Dict con datos para descarga.
        """
        if n_clicks is None or n_clicks == 0 or not historial or not datos:
            raise PreventUpdate

        try:
            import json
            from datetime import datetime

            # Preparar datos para exportación
            datos_exportacion = {
                'timestamp': datetime.now().isoformat(),
                'parametros_algoritmo': {
                    'tamano_poblacion': estado_ag.get('tamano_poblacion', 100) if estado_ag else 100,
                    'num_generaciones': estado_ag.get('num_generaciones', 500) if estado_ag else 500,
                    'prob_cruza': estado_ag.get('prob_cruza', 0.8) if estado_ag else 0.8,
                    'prob_mutacion': estado_ag.get('prob_mutacion', 0.2) if estado_ag else 0.2,
                },
                'mejor_fitness': estado_ag.get('mejor_fitness', 0) if estado_ag else 0,
                'mejor_ruta': estado_ag.get('mejor_individuo', []) if estado_ag else [],
                'historial_ejecucion': historial,
                'puntos_entrega': datos.get('puntos', []),
                'matriz_distancias': datos.get('distancias', [])
            }

            # Crear nombre de archivo con timestamp
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'resultados_optimizacion_{timestamp_str}.json'

            return dict(
                content=json.dumps(datos_exportacion, indent=2, ensure_ascii=False),
                filename=filename,
                mime='application/json',
                type='application/json'
            )

        except Exception as e:
            print(f"Error al exportar resultados: {str(e)}")
            raise PreventUpdate
