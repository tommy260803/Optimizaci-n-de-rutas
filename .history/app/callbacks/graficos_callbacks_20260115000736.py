"""
Callbacks para la visualización de gráficos en la aplicación de optimización de rutas.
"""
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

# Importar componentes de visualización
from app.components.graficos import (
    actualizar_grafico_convergencia,
    crear_grafico_convergencia_vacio
)
from app.components.tablas import preparar_datos_tabla
from app.components.utils import (
    formatear_distancia,
    formatear_tiempo
)

def registrar_graficos_callbacks(app):
    """
    Registra todos los callbacks relacionados con los gráficos y métricas.
    
    Args:
        app: Instancia de la aplicación Dash.
    """
    @app.callback(
        Output('grafico-convergencia', 'figure'),
        [Input('store-historial', 'data')]
    )
    def callback_actualizar_convergencia(historial: Optional[Dict]) -> Dict:
        """
        Actualiza el gráfico de convergencia con los datos del historial.
        
        Args:
            historial: Datos del historial de ejecución.
            
        Returns:
            dict: Figura de Plotly con el gráfico de convergencia.
        """
        if not historial or 'mejores_fitness' not in historial or not historial['mejores_fitness']:
            return crear_grafico_convergencia_vacio().to_dict()
            
        try:
            # Formatear el historial para el gráfico
            datos_grafico = []
            for i in range(len(historial['mejores_fitness'])):
                datos_grafico.append({
                    'generacion': historial.get('generaciones', [])[i] if 'generaciones' in historial else i,
                    'mejor_fitness': historial['mejores_fitness'][i],
                    'fitness_promedio': historial.get('fitness_promedio', [0])[i] if 'fitness_promedio' in historial else 0,
                    'peor_fitness': historial.get('peores_fitness', [0])[i] if 'peores_fitness' in historial else 0,
                    'diversidad': historial.get('diversidad', [0])[i] if 'diversidad' in historial else 0
                })

            # Si no hay datos de generaciones, crear índices
            if not any(d['generacion'] != 0 for d in datos_grafico):
                for i, dato in enumerate(datos_grafico):
                    dato['generacion'] = i
                
            return actualizar_grafico_convergencia(datos_grafico)
            
        except Exception as e:
            print(f"Error al actualizar gráfico de convergencia: {str(e)}")
            return crear_grafico_convergencia_vacio().to_dict()

    @app.callback(
        [
            Output('metrica-distancia', 'children'),
            Output('metrica-tiempo', 'children'),
            Output('metrica-generacion', 'children'),
            Output('metrica-mejora', 'children'),
            Output('metrica-fitness', 'children'),
            Output('metrica-diversidad', 'children')
        ],
        [
            Input('store-historial', 'data'),
            Input('store-datos', 'data'),
            Input('store-ag-estado', 'data'),
            Input('interval-actualizacion', 'disabled')  # Trigger cuando termine el algoritmo
        ]
    )
    def callback_actualizar_metricas(
        historial: Optional[Dict],
        datos: Optional[Dict],
        estado_ag: Optional[Dict],
        intervalo_disabled: bool = False  # Nuevo parámetro, no se usa
    ) -> Tuple[str, str, str, str, str, str]:
        """
        Actualiza las métricas mostradas en la interfaz.
        
        Args:
            historial: Datos del historial de ejecución.
            datos: Datos de puntos y distancias.
            estado_ag: Estado actual del algoritmo genético.
            
        Returns:
            tuple: Tupla con los valores formateados de las métricas.
        """
        # Valores por defecto
        distancia = "--"
        tiempo = "--"
        generacion = "0/0"
        mejora = "--"
        fitness = "--"
        diversidad = "--"
        
        try:
            if not historial or not datos:
                return distancia, tiempo, generacion, mejora, fitness, diversidad
                
            # Obtener el mejor individuo del historial
            if 'mejores_individuos' in historial and historial['mejores_individuos']:
                mejor_individuo = historial['mejores_individuos'][-1]
                
                # Calcular distancia total
                if 'distancias' in datos and mejor_individuo:
                    df_distancias = pd.DataFrame(datos['distancias'])
                    distancia_total = 0.0
                    tiempo_total = 0.0
                    
                    # Calcular distancia y tiempo de la ruta completa
                    ruta_completa = [0] + list(mejor_individuo) + [0]  # Agregar depósito al inicio y final
                    for i in range(len(ruta_completa) - 1):
                        from_id = ruta_completa[i]
                        to_id = ruta_completa[i + 1]
                        
                        # Obtener distancia y tiempo del viaje
                        viaje = df_distancias[
                            (df_distancias['from_id'] == from_id) & 
                            (df_distancias['to_id'] == to_id)
                        ].iloc[0]
                        
                        distancia_total += viaje.get('distancia_km', 0)
                        tiempo_total += viaje.get('tiempo_min', 0)
                        
                        # Sumar tiempo de servicio si no es el último punto
                        if i < len(ruta_completa) - 2:  # -2 porque el último es el depósito
                            df_puntos = pd.DataFrame(datos['puntos'])
                            punto_actual = df_puntos[df_puntos['id'] == to_id].iloc[0]
                            tiempo_total += punto_actual.get('tiempo_servicio', 0)
                    
                    # Formatear valores
                    distancia = formatear_distancia(distancia_total)
                    tiempo = formatear_tiempo(tiempo_total)
            
            # Calcular generación actual/total
            if estado_ag and 'generacion_actual' in estado_ag and 'num_generaciones' in estado_ag:
                generacion = f"{estado_ag['generacion_actual']}/{estado_ag['num_generaciones']}"
            
            # Calcular mejora
            if 'mejores_fitness' in historial and len(historial['mejores_fitness']) > 1:
                fitness_inicial = historial['mejores_fitness'][0]
                fitness_actual = historial['mejores_fitness'][-1]
                
                if fitness_inicial != 0:
                    porcentaje_mejora = ((fitness_inicial - fitness_actual) / abs(fitness_inicial)) * 100
                    mejora = f"{porcentaje_mejora:.1f}%"
                
                fitness = f"{fitness_actual:.3f}"
            
            # Calcular diversidad
            if 'diversidad' in historial and historial['diversidad']:
                diversidad = f"{historial['diversidad'][-1]:.4f}"
            
            return distancia, tiempo, generacion, mejora, fitness, diversidad
            
        except Exception as e:
            print(f"Error al actualizar métricas: {str(e)}")
            return distancia, tiempo, generacion, mejora, fitness, diversidad

    @app.callback(
        Output('tabla-resultados', 'data'),
        [
            Input('store-historial', 'data'),
            Input('store-datos', 'data')
        ]
    )
    def callback_actualizar_tabla(
        historial: Optional[Dict],
        datos: Optional[Dict]
    ) -> List[Dict]:
        """
        Actualiza la tabla de resultados con los mejores individuos encontrados.

        Args:
            historial: Datos del historial de ejecución.
            datos: Datos de puntos y distancias.

        Returns:
            list: Lista de diccionarios con los datos de la tabla.
        """
        if not historial or not datos or 'distancias' not in datos or 'puntos' not in datos:
            return []

        # Si no hay mejores individuos, retornar tabla vacía
        if 'mejores_individuos' not in historial or not historial['mejores_individuos']:
            return []

        try:
            # Convertir datos a DataFrames
            df_puntos = pd.DataFrame(datos['puntos'])
            matriz_distancias = pd.DataFrame(datos['distancias'])

            # Obtener los mejores individuos con sus fitness del historial
            mejores_individuos = []
            fitness_values = []

            # Los mejores individuos están en mejores_individuos
            # Los valores de fitness están en mejores_fitness
            if 'mejores_fitness' in historial and len(historial['mejores_fitness']) > 0:
                # Crear lista de tuplas (individuo, fitness) para los mejores encontrados
                for i, individuo in enumerate(historial['mejores_individuos']):
                    if i < len(historial['mejores_fitness']):
                        mejores_individuos.append((individuo, historial['mejores_fitness'][i]))
                        fitness_values.append(historial['mejores_fitness'][i])

            if not mejores_individuos:
                return []

            # Tomar los 10 mejores individuos ordenados por fitness (menor es mejor)
            mejores_individuos.sort(key=lambda x: x[1])
            top_individuos = mejores_individuos[:10]

            # Preparar datos para la tabla usando la función existente
            df_resultados = preparar_datos_tabla(
                individuos_fitness=top_individuos,
                matriz_distancias=matriz_distancias,
                df_puntos=df_puntos
            )

            # Convertir a formato para DataTable
            return df_resultados.to_dict('records')

        except Exception as e:
            print(f"Error al actualizar tabla de resultados: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


# Compatibilidad: exponer `registrar_callbacks` para el registro centralizado
def registrar_callbacks(app):
    return registrar_graficos_callbacks(app)
