"""
Módulo con funciones de evaluación (fitness) para el problema de optimización de rutas.
"""
import numpy as np
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime, timedelta

# Importar configuración
from config import (
    PESO_DISTANCIA,
    PESO_TIEMPO,
    PESO_PENALIZACION
)

def calcular_distancia_total(ruta: List[int], matriz_distancias: pd.DataFrame) -> float:
    """
    Calcula la distancia total de una ruta incluyendo el regreso al depósito.
    
    Args:
        ruta: Lista de IDs de los puntos en el orden de visita.
        matriz_distancias: DataFrame con las distancias entre todos los pares de puntos.
        
    Returns:
        float: Distancia total en kilómetros.
    """
    if not ruta:
        return 0.0
        
    distancia_total = 0.0
    
    # Asegurarse de que la ruta comience y termine en el depósito (punto 0)
    ruta_completa = [0] + [p for p in ruta if p != 0] + [0]
    
    # Calcular la distancia entre cada par consecutivo de puntos
    for i in range(len(ruta_completa) - 1):
        from_id = ruta_completa[i]
        to_id = ruta_completa[i + 1]
        
        # Buscar la distancia en la matriz
        distancia = matriz_distancias[
            (matriz_distancias['from_id'] == from_id) & 
            (matriz_distancias['to_id'] == to_id)
        ]['distancia_km'].values[0]
        
        distancia_total += distancia
    
    return round(distancia_total, 4)

def calcular_tiempo_total(
    ruta: List[int], 
    matriz_distancias: pd.DataFrame, 
    df_puntos: pd.DataFrame
) -> float:
    """
    Calcula el tiempo total de una ruta incluyendo tiempos de viaje y servicio.
    
    Args:
        ruta: Lista de IDs de los puntos en el orden de visita.
        matriz_distancias: DataFrame con los tiempos de viaje entre puntos.
        df_puntos: DataFrame con los tiempos de servicio de cada punto.
        
    Returns:
        float: Tiempo total en minutos.
    """
    if not ruta:
        return 0.0
        
    tiempo_total = 0.0
    tiempo_actual = datetime.strptime('08:00', '%H:%M')
    
    # Asegurarse de que la ruta comience y termine en el depósito (punto 0)
    ruta_completa = [0] + [p for p in ruta if p != 0] + [0]
    
    for i in range(len(ruta_completa) - 1):
        from_id = ruta_completa[i]
        to_id = ruta_completa[i + 1]
        
        # Obtener tiempo de viaje
        tiempo_viaje = float(matriz_distancias[
            (matriz_distancias['from_id'] == from_id) &
            (matriz_distancias['to_id'] == to_id)
        ]['tiempo_min'].values[0])

        tiempo_actual += timedelta(minutes=tiempo_viaje)
        tiempo_total += tiempo_viaje

        # Si no es el último punto (que es el depósito), sumar tiempo de servicio
        if i < len(ruta_completa) - 2:  # -2 porque el último es el depósito
            punto_actual = df_puntos[df_puntos['id'] == to_id].iloc[0]
            tiempo_servicio = float(punto_actual['tiempo_servicio'])
            tiempo_total += tiempo_servicio
            tiempo_actual += timedelta(minutes=tiempo_servicio)
    
    return round(tiempo_total, 2)

def penalizar_capacidad(
    ruta: List[int], 
    df_puntos: pd.DataFrame, 
    capacidad_max: float
) -> float:
    """
    Calcula la penalización por exceder la capacidad del vehículo.
    
    Args:
        ruta: Lista de IDs de los puntos en el orden de visita.
        df_puntos: DataFrame con las demandas de cada punto.
        capacidad_max: Capacidad máxima del vehículo.
        
    Returns:
        float: Penalización por exceso de capacidad (0 si no hay exceso).
    """
    if not ruta:
        return 0.0
        
    # Calcular demanda total de la ruta
    demanda_total = df_puntos[df_puntos['id'].isin(ruta)]['demanda'].sum()
    
    # Calcular exceso de capacidad
    exceso = max(0, demanda_total - capacidad_max)
    
    # Retornar penalización proporcional al exceso
    return exceso * 10  # Factor de penalización

def penalizar_ventanas_tiempo(
    ruta: List[int], 
    df_puntos: pd.DataFrame, 
    matriz_distancias: pd.DataFrame
) -> float:
    """
    Calcula la penalización por violaciones de ventanas de tiempo.
    
    Args:
        ruta: Lista de IDs de los puntos en el orden de visita.
        df_puntos: DataFrame con las ventanas de tiempo de cada punto.
        matriz_distancias: DataFrame con los tiempos de viaje entre puntos.
        
    Returns:
        float: Penalización total por violaciones de ventanas de tiempo.
    """
    if not ruta:
        return 0.0
        
    penalizacion = 0.0
    tiempo_actual = datetime.strptime('08:00', '%H:%M')
    
    # Asegurarse de que la ruta comience y termine en el depósito (punto 0)
    ruta_completa = [0] + [p for p in ruta if p != 0] + [0]
    
    for i in range(1, len(ruta_completa) - 1):  # Empezamos en 1 para saltar el depósito inicial
        punto_anterior = ruta_completa[i-1]
        punto_actual = ruta_completa[i]
        
        # Obtener tiempo de viaje desde el punto anterior al actual
        tiempo_viaje = matriz_distancias[
            (matriz_distancias['from_id'] == punto_anterior) & 
            (matriz_distancias['to_id'] == punto_actual)
        ]['tiempo_min'].values[0]
        
        tiempo_actual += timedelta(minutes=tiempo_viaje)
        
        # Obtener información del punto actual
        punto_data = df_puntos[df_puntos['id'] == punto_actual].iloc[0]
        ventana_inicio = datetime.strptime(punto_data['ventana_inicio'], '%H:%M')
        ventana_fin = datetime.strptime(punto_data['ventana_fin'], '%H:%M')
        
        # Ajustar las ventanas al mismo día que tiempo_actual
        ventana_inicio = tiempo_actual.replace(
            hour=ventana_inicio.hour, 
            minute=ventana_inicio.minute
        )
        ventana_fin = tiempo_actual.replace(
            hour=ventana_fin.hour, 
            minute=ventana_fin.minute
        )
        
        # Verificar violación de ventana de tiempo
        if tiempo_actual < ventana_inicio:
            # Llegada temprana
            penalizacion += (ventana_inicio - tiempo_actual).total_seconds() / 60  # minutos de espera
        elif tiempo_actual > ventana_fin:
            # Llegada tardía
            penalizacion += (tiempo_actual - ventana_fin).total_seconds() / 60  # minutos de retraso
        
        # Sumar tiempo de servicio
        tiempo_actual += timedelta(minutes=punto_data['tiempo_servicio'])
    
    return round(penalizacion, 2)

def fitness_completo(
    ruta: List[int], 
    matriz_distancias: pd.DataFrame, 
    df_puntos: pd.DataFrame, 
    capacidad_max: float,
    peso_distancia: float = PESO_DISTANCIA,
    peso_tiempo: float = PESO_TIEMPO,
    peso_penalizacion: float = PESO_PENALIZACION
) -> float:
    """
    Función de fitness que combina distancia, tiempo y penalizaciones.
    
    Args:
        ruta: Lista de IDs de los puntos en el orden de visita.
        matriz_distancias: DataFrame con distancias y tiempos entre puntos.
        df_puntos: DataFrame con información de los puntos de entrega.
        capacidad_max: Capacidad máxima del vehículo.
        peso_distancia: Peso para el componente de distancia.
        peso_tiempo: Peso para el componente de tiempo.
        peso_penalizacion: Peso para las penalizaciones.
        
    Returns:
        float: Valor de fitness (menor es mejor).
    """
    # Calcular métricas individuales
    distancia_total = calcular_distancia_total(ruta, matriz_distancias)
    tiempo_total = calcular_tiempo_total(ruta, matriz_distancias, df_puntos)
    penalizacion_capacidad = penalizar_capacidad(ruta, df_puntos, capacidad_max)
    penalizacion_ventanas = penalizar_ventanas_tiempo(ruta, df_puntos, matriz_distancias)
    
    # Normalizar las métricas (usando valores máximos razonables)
    max_distancia = matriz_distancias['distancia_km'].sum() * 2  # Ruta muy larga
    max_tiempo = matriz_distancias['tiempo_min'].sum() * 2  # Tiempo muy largo
    
    distancia_norm = min(distancia_total / max_distancia, 1.0)
    tiempo_norm = min(tiempo_total / max_tiempo, 1.0)
    
    # Calcular penalización total (sin normalizar)
    penalizacion_total = penalizacion_capacidad + penalizacion_ventanas
    
    # Calcular fitness ponderado
    fitness = (
        peso_distancia * distancia_norm +
        peso_tiempo * tiempo_norm +
        peso_penalizacion * min(penalizacion_total / 100, 1.0)  # Normalizar penalización
    )
    
    return round(fitness, 6)
