"""
Callbacks para la visualización del mapa en la aplicación de optimización de rutas.
"""
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
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
            Input('store-datos', 'data')
        ]
    )
    def callback_actualizar_mapa(
        historial: Optional[Dict],
        datos: Optional[Dict]
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
            # Retornar mapa vacío si no hay datos
            from app.components.mapa import crear_mapa_base
            return crear_mapa_base()

        # Convertir datos a DataFrames
        df_puntos = pd.DataFrame(datos['puntos'])

        # Si no hay historial o está vacío, mostrar solo los puntos
        if not historial or not historial.get('mejores_individuos'):
            print("Actualizando mapa con solo puntos (sin rutas)")
            return crear_mapa_completo(df_puntos)

        try:
            # Obtener el mejor individuo del historial
            mejores_individuos = historial.get('mejores_individuos', [])
            if not mejores_individuos:
                print("Actualizando mapa con solo puntos (historial vacío)")
                return crear_mapa_completo(df_puntos)

            mejor_individuo = mejores_individuos[-1]
            print(f"Actualizando mapa con ruta optimizada: {mejor_individuo}")

            # Convertir la ruta a coordenadas
            ruta_optimizada = convertir_ruta_a_coordenadas(mejor_individuo, df_puntos)

            # Crear una ruta inicial aleatoria para comparación (solo si hay suficiente historial)
            ruta_inicial = None
            if len(mejores_individuos) > 1:
                primer_individuo = mejores_individuos[0]
                ruta_inicial = convertir_ruta_a_coordenadas(primer_individuo, df_puntos)

            # Crear el mapa con ambas rutas
            figura = crear_mapa_completo(
                df_puntos=df_puntos,
                ruta_inicial=ruta_inicial,
                ruta_optimizada=ruta_optimizada
            )

            return figura
        except Exception as e:
            print(f"Error al actualizar el mapa: {str(e)}")
            import traceback
            traceback.print_exc()
            # En caso de error, devolver mapa básico con puntos
            return crear_mapa_completo(df_puntos)

    @app.callback(
        Output('theme-icon', 'children'),
        Output('theme-toggle', 'value'),
        Input('theme-toggle', 'value'),
        State('theme-icon', 'children')
    )
    def callback_toggle_theme(is_dark, current_icon):
        """
        Cambia entre tema claro y oscuro.

        Args:
            is_dark: Estado actual del toggle (True = oscuro, False = claro)
            current_icon: Ícono actual

        Returns:
            tuple: (nuevo_ícono, nuevo_valor_toggle)
        """
        if is_dark:
            # Tema oscuro activado
            return "🌙", True
        else:
            # Tema claro activado
            return "🌞", False


# Compatibilidad: exponer `registrar_callbacks` para el registro centralizado
def registrar_callbacks(app):
    return registrar_mapa_callbacks(app)
