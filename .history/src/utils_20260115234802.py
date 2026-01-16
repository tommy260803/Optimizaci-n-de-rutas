"""
Módulo con funciones de utilidad para el proyecto de optimización de rutas.
"""
import os
import pandas as pd
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar configuración
from config import DATA_PATH, RESULTADOS_PATH

def cargar_datos() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga los datos de entrada desde archivos CSV.
    
    Returns:
        Tupla con (df_puntos, matriz_distancias)
        
    Raises:
        FileNotFoundError: Si alguno de los archivos no existe.
    """
    try:
        # Rutas de los archivos
        ruta_puntos = os.path.join(DATA_PATH, 'rutas_simuladas.csv')
        ruta_distancias = os.path.join(DATA_PATH, 'distancias.csv')
        
        # Verificar que los archivos existen
        if not os.path.exists(ruta_puntos):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_puntos}")
        if not os.path.exists(ruta_distancias):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_distancias}")
        
        # Cargar datos
        logger.info("Cargando datos de entrada...")
        df_puntos = pd.read_csv(ruta_puntos)
        matriz_distancias = pd.read_csv(ruta_distancias)

        # Asegurar que las columnas 'id' sean numéricas
        df_puntos['id'] = pd.to_numeric(df_puntos['id'], errors='coerce')
        matriz_distancias['from_id'] = pd.to_numeric(matriz_distancias['from_id'], errors='coerce')
        matriz_distancias['to_id'] = pd.to_numeric(matriz_distancias['to_id'], errors='coerce')
        
        # Validar datos básicos
        if df_puntos.empty or matriz_distancias.empty:
            raise ValueError("Uno o más archivos de datos están vacíos")
            
        logger.info("Datos cargados exitosamente")
        return df_puntos, matriz_distancias
        
    except Exception as e:
        logger.error("Error al cargar los datos: %s", str(e))
        raise

def guardar_resultados(
    mejor_individuo: List[int],
    mejor_fitness: float,
    historial: List[Dict[str, Any]],
    df_puntos: pd.DataFrame,
    prefijo: str = ""
) -> Dict[str, str]:
    """
    Guarda los resultados de la ejecución del algoritmo.
    
    Args:
        mejor_individuo: Lista con la mejor ruta encontrada.
        mejor_fitness: Valor de fitness de la mejor ruta.
        historial: Lista de diccionarios con el historial de evolución.
        df_puntos: DataFrame con información de los puntos.
        prefijo: Prefijo opcional para los nombres de archivo.
        
    Returns:
        Diccionario con las rutas de los archivos guardados.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefijo = f"{prefijo}_" if prefijo else ""
        
        # Crear directorios si no existen
        os.makedirs(os.path.join(RESULTADOS_PATH, 'rutas_optimizadas'), exist_ok=True)
        os.makedirs(os.path.join(RESULTADOS_PATH, 'logs'), exist_ok=True)
        
        # Guardar mejor ruta
        ruta_archivo = os.path.join(
            RESULTADOS_PATH, 
            'rutas_optimizadas', 
            f"{prefijo}mejor_ruta_{timestamp}.csv"
        )
        
        # Crear DataFrame con la mejor ruta
        ruta_completa = [0] + mejor_individuo + [0]  # Agregar depósito al inicio y final
        df_ruta = pd.DataFrame({
            'orden': range(1, len(ruta_completa) + 1),
            'punto_id': ruta_completa
        })
        
        # Unir con información de los puntos
        df_ruta = df_ruta.merge(
            df_puntos[['id', 'nombre', 'lat', 'lon', 'demanda']],
            left_on='punto_id',
            right_on='id',
            how='left'
        )
        
        # Guardar ruta
        df_ruta.to_csv(ruta_archivo, index=False)
        logger.info("Mejor ruta guardada en: %s", ruta_archivo)
        
        # Guardar historial de evolución
        ruta_historial = os.path.join(
            RESULTADOS_PATH,
            'logs',
            f"{prefijo}historial_{timestamp}.csv"
        )
        
        df_historial = pd.DataFrame(historial)
        df_historial.to_csv(ruta_historial, index=False)
        logger.info("Historial de evolución guardado en: %s", ruta_historial)
        
        return {
            'ruta_archivo': ruta_archivo,
            'historial_archivo': ruta_historial
        }
        
    except Exception as e:
        logger.error("Error al guardar resultados: %s", str(e))
        raise

def convertir_ruta_a_coordenadas(
    ruta: List[int],
    df_puntos: pd.DataFrame
) -> List[Tuple[float, float]]:
    """
    Convierte una ruta (lista de IDs) a una lista de coordenadas (lat, lon).
    
    Args:
        ruta: Lista de IDs de puntos en el orden de visita.
        df_puntos: DataFrame con información de los puntos.
        
    Returns:
        Lista de tuplas (latitud, longitud) incluyendo el depósito al inicio y final.
    """
    if not ruta:
        return []
    
    # Asegurarse de que la ruta comience y termine en el depósito (id=0)
    ruta_completa = [0] + [p for p in ruta if p != 0] + [0]
    
    coordenadas = []
    for punto_id in ruta_completa:
        punto = df_puntos[df_puntos['id'] == punto_id].iloc[0]
        coordenadas.append((punto['lat'], punto['lon']))
    
    return coordenadas

def calcular_metricas(
    ruta: List[int],
    matriz_distancias: pd.DataFrame,
    df_puntos: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calcula métricas para una ruta dada.
    
    Args:
        ruta: Lista de IDs de puntos en el orden de visita.
        matriz_distancias: DataFrame con las distancias entre puntos.
        df_puntos: DataFrame con información de los puntos.
        
    Returns:
        Diccionario con las métricas calculadas.
    """
    if not ruta:
        return {
            'distancia_total': 0.0,
            'tiempo_total': 0.0,
            'puntos_visitados': 0,
            'demanda_total': 0,
            'tiempo_servicio_total': 0.0
        }
    
    # Asegurarse de que la ruta comience y termine en el depósito (id=0)
    ruta_completa = [0] + [p for p in ruta if p != 0] + [0]
    
    # Calcular distancia total
    distancia_total = 0.0
    tiempo_total = 0.0
    tiempo_actual = datetime.strptime('08:00', '%H:%M')
    
    for i in range(len(ruta_completa) - 1):
        from_id = ruta_completa[i]
        to_id = ruta_completa[i + 1]
        
        # Obtener distancia y tiempo de viaje
        viaje = matriz_distancias[
            (matriz_distancias['from_id'] == from_id) & 
            (matriz_distancias['to_id'] == to_id)
        ].iloc[0]
        
        distancia_total += viaje['distancia_km']
        tiempo_viaje = viaje['tiempo_min']
        tiempo_total += tiempo_viaje
        tiempo_actual += timedelta(minutes=tiempo_viaje)
        
        # Si no es el último punto (que es el depósito), sumar tiempo de servicio
        if i < len(ruta_completa) - 2:  # -2 porque el último es el depósito
            punto_actual = df_puntos[df_puntos['id'] == to_id].iloc[0]
            tiempo_servicio = punto_actual['tiempo_servicio']
            tiempo_total += tiempo_servicio
            tiempo_actual += timedelta(minutes=tiempo_servicio)
    
    # Calcular demanda total
    demanda_total = df_puntos[df_puntos['id'].isin(ruta)]['demanda'].sum()
    
    # Calcular tiempo total de servicio
    tiempo_servicio_total = df_puntos[df_puntos['id'].isin(ruta)]['tiempo_servicio'].sum()
    
    return {
        'distancia_total': round(distancia_total, 2),
        'tiempo_total': round(tiempo_total, 2),
        'puntos_visitados': len(ruta),
        'demanda_total': int(demanda_total),
        'tiempo_servicio_total': round(tiempo_servicio_total, 2)
    }

def formatear_tiempo(minutos: float) -> str:
    """
    Formatea un tiempo en minutos a un string legible.
    
    Args:
        minutos: Tiempo en minutos.
        
    Returns:
        String formateado (ej. "2h 30min").
    """
    if pd.isna(minutos) or minutos is None:
        return "N/A"
        
    horas = int(minutos // 60)
    mins = int(round(minutos % 60))
    
    if horas > 0 and mins > 0:
        return f"{horas}h {mins:02d}min"
    elif horas > 0:
        return f"{horas}h"
    else:
        return f"{mins}min"

def formatear_distancia(km: float) -> str:
    """
    Formatea una distancia a un string con dos decimales y unidad.
    
    Args:
        km: Distancia en kilómetros.
        
    Returns:
        String formateado (ej. "12.34 km").
    """
    if pd.isna(km) or km is None:
        return "N/A"
    return f"{km:.2f} km"

# Para compatibilidad con versiones antiguas de Python
from datetime import timedelta

# Asegurarse de que los directorios existen
os.makedirs(os.path.join(RESULTADOS_PATH, 'rutas_optimizadas'), exist_ok=True)
os.makedirs(os.path.join(RESULTADOS_PATH, 'logs'), exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)
