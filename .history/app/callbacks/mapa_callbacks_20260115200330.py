"""
Callbacks para la visualización del mapa en la aplicación de optimización de rutas.
"""
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import html
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

# Importar componentes de visualización
from app.components.mapa import crear_mapa_completo
from app.components.tablas import convertir_ruta_a_coordenadas

def registrar_mapa_callbacks(app):
    """
    Registra todos los callbacks relacionados con el mapa.
    
    Args:
        app: Instancia de la aplicación Dash.
    """
    @app.callback(
        Output('mapa-rutas', 'figure'),
        [
            Input('store-historial', 'data'),
            Input('store-datos', 'data'),
            Input('store-ag-estado', 'data'),
            Input('checkbox-zoom-auto', 'value')
        ]
    )
    def callback_actualizar_mapa(
        historial: Optional[Dict],
        datos: Optional[Dict],
        estado_ag: Optional[Dict],
        zoom_auto: bool = True
    ) -> Dict:
        """
        Actualiza el mapa con la mejor ruta encontrada o solo los puntos si no hay rutas.

        Args:
            historial: Datos del historial de ejecución.
            datos: Datos de puntos y distancias.

        Returns:
            dict: Figura de Plotly con el mapa actualizado.
        """
        # Verificar que existen datos
        if not datos or 'puntos' not in datos:
            # Retornar mapa con mensaje informativo si no hay datos
            from app.components.mapa import crear_mapa_sin_datos
            return crear_mapa_sin_datos()

        # Convertir datos a DataFrames
        df_puntos = pd.DataFrame(datos['puntos'])

        # Si no hay historial o está vacío, mostrar solo los puntos
        if not historial or not historial.get('mejores_individuos'):
            return crear_mapa_completo(df_puntos)

        try:
            # Obtener el mejor individuo del historial
            mejores_individuos = historial.get('mejores_individuos', [])
            if not mejores_individuos:
                return crear_mapa_completo(df_puntos)

            # Obtener el mejor individuo (menor fitness)
            mejor_individuo = min(mejores_individuos, key=lambda x: x[1])[0]

            # Convertir la ruta a coordenadas
            ruta_optimizada = convertir_ruta_a_coordenadas(mejor_individuo, df_puntos)

            # Crear una ruta inicial aleatoria para comparación (solo si hay suficiente historial)
            ruta_inicial = None
            if len(mejores_individuos) > 1:
                primer_individuo = mejores_individuos[0][0]
                ruta_inicial = convertir_ruta_a_coordenadas(primer_individuo, df_puntos)

            # Determinar si ajustar zoom (durante ejecución del algoritmo y si está activado)
            ajustar_zoom = zoom_auto and estado_ag and estado_ag.get('ejecutando', False) and estado_ag.get('generacion_actual', 0) > 0

            # Crear el mapa con ambas rutas
            figura = crear_mapa_completo(
                df_puntos=df_puntos,
                ruta_inicial=ruta_inicial,
                ruta_optimizada=ruta_optimizada,
                ajustar_zoom=ajustar_zoom
            )

            return figura
        except Exception as e:
            print(f"Error al actualizar el mapa: {str(e)}")
            import traceback
            traceback.print_exc()
            # En caso de error, devolver mapa básico con puntos
            return crear_mapa_completo(df_puntos)




    @app.callback(
        Output('mapa-ruta-completa', 'figure'),
        Output('info-ruta-completa', 'children'),
        [
            Input('store-historial', 'data'),
            Input('store-datos', 'data')
        ]
    )
    def callback_visualizacion_ruta_completa(historial, datos):
        """
        Actualiza la visualización completa de la ruta óptima.
        """
        # Verificar que existen datos
        if not datos or 'puntos' not in datos:
            # Retornar mapa vacío con mensaje informativo
            from app.components.mapa import crear_mapa_sin_datos
            info_vacia = html.P("Primero genere nuevos puntos de entrega para ver la ruta completa.",
                               className="text-muted")
            return crear_mapa_sin_datos(), info_vacia

        # Convertir datos a DataFrames
        df_puntos = pd.DataFrame(datos['puntos'])

        # Verificar que hay historial con mejores individuos
        if not historial or 'mejores_individuos' not in historial or not historial['mejores_individuos']:
            from app.components.mapa import crear_mapa_sin_datos
            info_sin_ruta = html.P("Ejecuta el algoritmo genético para visualizar la ruta óptima completa.",
                                  className="text-muted")
            return crear_mapa_sin_datos(), info_sin_ruta

        try:
            # Obtener la mejor ruta del historial
            mejores_individuos = historial['mejores_individuos']
            if not mejores_individuos:
                from app.components.mapa import crear_mapa_sin_datos
                info_sin_ruta = html.P("No se encontraron rutas óptimas.",
                                      className="text-muted")
                return crear_mapa_sin_datos(), info_sin_ruta

            # Tomar la mejor ruta (primera en la lista ordenada)
            mejor_ruta = mejores_individuos[0]  # Solo la ruta, sin el fitness

            # Crear visualización completa
            from app.components.mapa import crear_visualizacion_ruta_completa
            figura_completa = crear_visualizacion_ruta_completa(df_puntos, mejor_ruta)

            # Crear información detallada de la ruta
            ruta_completa = [0] + mejor_ruta + [0]  # Agregar depósito
            info_detallada = html.Div([
                html.P([
                    html.Strong("🏭 Ruta Óptima Completa:"),
                    f" {len(ruta_completa)} puntos totales"
                ], className="mb-2"),
                html.P([
                    html.Strong("📍 Secuencia de visita:"),
                    f" {' → '.join([f'P{str(id).zfill(1)}' for id in ruta_completa])}"
                ], className="mb-2 text-break"),
                html.P([
                    html.Strong("🎯 Puntos de entrega:"),
                    f" {len(mejor_ruta)} ubicaciones"
                ], className="mb-2"),
                html.Div([
                    html.Strong("📋 Detalle por punto:"),
                    html.Ul([
                        html.Li([
                            f"Posición {i+1}: ",
                            html.Span(f"P{ruta_completa[i]}", className="fw-bold"),
                            f" ({df_puntos[df_puntos['id'] == ruta_completa[i]]['nombre'].iloc[0]})"
                        ]) for i in range(len(ruta_completa))
                    ], className="mt-2")
                ])
            ])

            return figura_completa, info_detallada

        except Exception as e:
            print(f"Error en visualización completa: {str(e)}")
            import traceback
            traceback.print_exc()

            from app.components.mapa import crear_mapa_sin_datos
            info_error = html.P("Error al generar la visualización completa.",
                               className="text-danger")
            return crear_mapa_sin_datos(), info_error

# Compatibilidad: exponer `registrar_callbacks` para el registro centralizado
def registrar_callbacks(app):
    return registrar_mapa_callbacks(app)
