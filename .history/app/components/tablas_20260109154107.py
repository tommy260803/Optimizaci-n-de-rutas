"""
Componentes de tablas para la aplicación de optimización de rutas.
"""
from dash import dash_table
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from src.utils import convertir_ruta_a_coordenadas

# Definir estilos para las tablas
ESTILO_TABLA = {
    'height': '300px',
    'overflowY': 'auto',
    'width': '100%',
    'minWidth': '100%',
}

ESTILO_CELDA = {
    'textAlign': 'left',
    'padding': '8px',
    'fontFamily': 'Arial, sans-serif',
    'border': '1px solid #e0e0e0',
}

ESTILO_CABECERA = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'textAlign': 'center',
    'border': '1px solid #dee2e6',
}

def crear_tabla_resultados_vacia() -> dash_table.DataTable:
    """
    Crea una tabla de resultados vacía.
    
    Returns:
        dash_table.DataTable: Tabla vacía con las columnas configuradas.
    """
    columnas = [
        {'name': 'Rank', 'id': 'rank', 'type': 'numeric'},
        {'name': 'Ruta', 'id': 'ruta', 'type': 'text'},
        {'name': 'Distancia (km)', 'id': 'distancia', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Tiempo', 'id': 'tiempo', 'type': 'text'},
        {'name': 'Fitness', 'id': 'fitness', 'type': 'numeric', 'format': {'specifier': '.3f'}},
    ]
    
    return dash_table.DataTable(
        id='tabla-resultados',
        columns=columnas,
        data=[],  # Datos vacíos inicialmente
        style_table=ESTILO_TABLA,
        style_cell=ESTILO_CELDA,
        style_header=ESTILO_CABECERA,
        page_size=10,
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                'border': '1px solid blue'
            }
        ],
        style_cell_conditional=[
            {'if': {'column_id': 'rank'}, 'width': '10%'},
            {'if': {'column_id': 'ruta'}, 'width': '40%'},
            {'if': {'column_id': 'distancia'}, 'width': '15%'},
            {'if': {'column_id': 'tiempo'}, 'width': '20%'},
            {'if': {'column_id': 'fitness'}, 'width': '15%'},
        ],
        sort_action='native',
        sort_mode='single',
        row_selectable='single',
        selected_rows=[],
    )

def preparar_datos_tabla(
    individuos_fitness: List[Tuple[List[int], float]],
    matriz_distancias: pd.DataFrame,
    df_puntos: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepara los datos para la tabla de resultados.
    
    Args:
        individuos_fitness: Lista de tuplas (individuo, fitness).
        matriz_distancias: DataFrame con las distancias entre puntos.
        df_puntos: DataFrame con información de los puntos.
        
    Returns:
        pd.DataFrame: Datos formateados para la tabla.
    """
    if not individuos_fitness:
        return pd.DataFrame()
    
    # Ordenar por fitness (menor es mejor)
    individuos_ordenados = sorted(individuos_fitness, key=lambda x: x[1])
    
    # Tomar los 10 mejores
    top_individuos = individuos_ordenados[:10]
    
    datos = []
    
    for i, (individuo, fitness) in enumerate(top_individuos, 1):
        # Formatear ruta (mostrar primeros 5 puntos + ... si es necesario)
        if len(individuo) > 5:
            ruta_str = ' → '.join(str(x) for x in individuo[:3]) + '...' + ' → '.join(str(x) for x in individuo[-2:])
        else:
            ruta_str = ' → '.join(str(x) for x in individuo)
        
        # Calcular métricas
        distancia_total = 0.0
        tiempo_total = 0.0
        
        # Asegurarse de que la ruta comience y termine en el depósito (id=0)
        ruta_completa = [0] + [p for p in individuo if p != 0] + [0]
        
        # Calcular distancia y tiempo total
        for j in range(len(ruta_completa) - 1):
            from_id = ruta_completa[j]
            to_id = ruta_completa[j + 1]
            
            # Obtener distancia y tiempo de viaje
            viaje = matriz_distancias[
                (matriz_distancias['from_id'] == from_id) & 
                (matriz_distancias['to_id'] == to_id)
            ].iloc[0]
            
            distancia_total += viaje['distancia_km']
            tiempo_total += viaje['tiempo_min']
            
            # Sumar tiempo de servicio si no es el último punto
            if j < len(ruta_completa) - 2:  # -2 porque el último es el depósito
                punto_actual = df_puntos[df_puntos['id'] == to_id].iloc[0]
                tiempo_total += punto_actual['tiempo_servicio']
        
        # Formatear tiempo
        horas = int(tiempo_total // 60)
        minutos = int(tiempo_total % 60)
        tiempo_str = f"{horas}h {minutos:02d}min" if horas > 0 else f"{minutos}min"
        
        # Agregar a los datos
        datos.append({
            'rank': i,
            'ruta': ruta_str,
            'distancia': round(distancia_total, 2),
            'tiempo': tiempo_str,
            'fitness': round(fitness, 3)
        })
    
    return pd.DataFrame(datos)
