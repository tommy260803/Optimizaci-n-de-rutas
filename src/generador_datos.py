"""
Módulo para generar datos de prueba para el problema de optimización de rutas.
"""
import os
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from pathlib import Path
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeneradorDatos:
    """Clase para generar datos simulados de puntos de entrega y calcular distancias."""
    
    def __init__(self, centro_lat=-12.0464, centro_lon=-77.0428, radio_km=15):
        """
        Inicializa el generador de datos con las coordenadas del centro y el radio.
        
        Args:
            centro_lat (float): Latitud del punto central (depósito).
            centro_lon (float): Longitud del punto central (depósito).
            radio_km (float): Radio en kilómetros para generar puntos aleatorios.
        """
        self.centro = (centro_lat, centro_lon)
        self.radio_km = radio_km
        self.rng = np.random.default_rng()
        
    def generar_puntos_aleatorios(self, n_puntos=20, seed=None):
        """
        Genera puntos aleatorios dentro de un radio alrededor del centro.
        
        Args:
            n_puntos (int): Número total de puntos a generar (incluyendo el depósito).
            seed (int, opcional): Semilla para reproducibilidad.
            
        Returns:
            pd.DataFrame: DataFrame con los puntos generados.
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)
            
        # Generar ángulos y distancias aleatorias
        angulos = self.rng.uniform(0, 2 * np.pi, n_puntos - 1)
        distancias = self.rng.uniform(0, self.radio_km, n_puntos - 1)
        
        # Convertir distancias a grados (aproximadamente 111.32 km por grado)
        dist_grados = distancias / 111.32
        
        # Calcular desplazamientos
        dlat = dist_grados * np.sin(angulos)
        dlon = dist_grados * np.cos(angulos)
        
        # Crear puntos
        puntos = [{
            'id': 0,
            'nombre': 'Depósito Central',
            'lat': self.centro[0],
            'lon': self.centro[1],
            'demanda': 0,
            'ventana_inicio': '08:00',
            'ventana_fin': '18:00',
            'tiempo_servicio': 0
        }]
        
        for i in range(1, n_puntos):
            lat = self.centro[0] + dlat[i-1]
            lon = self.centro[1] + dlon[i-1]
            puntos.append({
                'id': i,
                'nombre': f'Punto {i}',
                'lat': lat,
                'lon': lon,
                'demanda': self.rng.integers(1, 6),  # Demanda entre 1 y 5
                'ventana_inicio': f"{self.rng.integers(8, 12):02d}:00",
                'ventana_fin': f"{self.rng.integers(13, 19):02d}:00",
                'tiempo_servicio': self.rng.integers(5, 31)  # 5 a 30 minutos
            })
        
        return pd.DataFrame(puntos)
    
    def calcular_matriz_distancias(self, df_puntos):
        """
        Calcula la matriz de distancias y tiempos entre todos los pares de puntos.
        
        Args:
            df_puntos (pd.DataFrame): DataFrame con los puntos de entrega.
            
        Returns:
            pd.DataFrame: Matriz de distancias con columnas: from_id, to_id, distancia_km, tiempo_min
        """
        puntos = df_puntos[['id', 'lat', 'lon']].values
        n = len(puntos)
        datos = []
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    coord1 = (puntos[i][1], puntos[i][2])
                    coord2 = (puntos[j][1], puntos[j][2])
                    distancia_km = geodesic(coord1, coord2).kilometers
                    tiempo_min = (distancia_km / 30) * 60  # 30 km/h a minutos
                    
                    datos.append({
                        'from_id': int(puntos[i][0]),
                        'to_id': int(puntos[j][0]),
                        'distancia_km': round(distancia_km, 4),
                        'tiempo_min': round(tiempo_min, 2)
                    })
        
        return pd.DataFrame(datos)
    
    def exportar_a_csv(self, df_puntos, df_distancias, ruta_datos='data', prefijo=''):
        """
        Exporta los DataFrames a archivos CSV.
        
        Args:
            df_puntos (pd.DataFrame): DataFrame con los puntos de entrega.
            df_distancias (pd.DataFrame): Matriz de distancias.
            ruta_datos (str): Directorio donde se guardarán los archivos.
            prefijo (str): Prefijo opcional para los nombres de archivo.
        """
        os.makedirs(ruta_datos, exist_ok=True)
        
        # Asegurar que el prefijo termine con _ si no está vacío
        if prefijo and not prefijo.endswith('_'):
            prefijo += '_'
            
        # Guardar puntos
        ruta_puntos = os.path.join(ruta_datos, f'{prefijo}rutas_simuladas.csv')
        df_puntos.to_csv(ruta_puntos, index=False, encoding='utf-8')
        logger.info(f"Datos de puntos guardados en: {ruta_puntos}")
        
        # Guardar distancias
        ruta_distancias = os.path.join(ruta_datos, f'{prefijo}distancias.csv')
        df_distancias.to_csv(ruta_distancias, index=False, encoding='utf-8')
        logger.info(f"Matriz de distancias guardada en: {ruta_distancias}")


def verificar_o_generar_datos(n_puntos=20, seed=42, forzar_generacion=False):
    """
    Verifica si existen los archivos de datos y los genera si es necesario.
    
    Args:
        n_puntos (int): Número de puntos a generar si es necesario.
        seed (int): Semilla para reproducibilidad.
        forzar_generacion (bool): Si es True, regenera los archivos aunque existan.
        
    Returns:
        tuple: (ruta_puntos, ruta_distancias) con las rutas a los archivos generados.
    """
    from config import DATA_PATH
    
    ruta_puntos = os.path.join(DATA_PATH, 'rutas_simuladas.csv')
    ruta_distancias = os.path.join(DATA_PATH, 'distancias.csv')
    
    # Verificar si los archivos ya existen
    if not forzar_generacion and os.path.exists(ruta_puntos) and os.path.exists(ruta_distancias):
        logger.info("Archivos de datos encontrados. No es necesario generar nuevos.")
        return ruta_puntos, ruta_distancias
    
    # Generar nuevos datos
    logger.info("Generando nuevos datos de prueba...")
    generador = GeneradorDatos()
    
    logger.info(f"Generando {n_puntos} puntos de entrega...")
    df_puntos = generador.generar_puntos_aleatorios(n_puntos=n_puntos, seed=seed)
    
    logger.info("Calculando matriz de distancias...")
    df_distancias = generador.calcular_matriz_distancias(df_puntos)
    
    logger.info("Exportando datos a archivos CSV...")
    generador.exportar_a_csv(df_puntos, df_distancias, ruta_datos=DATA_PATH)
    
    logger.info("¡Datos generados exitosamente!")
    return ruta_puntos, ruta_distancias


if __name__ == "__main__":
    # Generar datos al ejecutar el script directamente
    verificar_o_generar_datos()
