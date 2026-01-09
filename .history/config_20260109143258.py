"""
Configuración global del proyecto de Optimización de Rutas con Algoritmos Genéticos.
"""
import os
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).parent.absolute()

# Rutas de archivos
DATA_PATH = os.path.join(BASE_DIR, 'data')
RESULTADOS_PATH = os.path.join(BASE_DIR, 'resultados')
RUTA_PUNTOS = os.path.join(DATA_PATH, 'rutas_simuladas.csv')
RUTA_DISTANCIAS = os.path.join(DATA_PATH, 'distancias.csv')

# Parámetros del algoritmo genético
DEFAULT_POBLACION = 100
DEFAULT_GENERACIONES = 500
DEFAULT_PROB_CRUZA = 0.8
DEFAULT_PROB_MUTACION = 0.2
DEFAULT_ELITISMO = 5

# Configuración del mapa
MAPA_CENTRO = {
    'lat': -12.0464,
    'lon': -77.0428,
    'name': 'Lima, Perú'
}
MAPA_ZOOM = 12

# Pesos para la función de fitness
PESO_DISTANCIA = 0.6
PESO_TIEMPO = 0.3
PESO_PENALIZACION = 0.1

# Configuración de visualización
ESTILO_MAPA = {
    'width': '100%',
    'height': '600px',
    'margin': '0 auto',
    'display': 'block'
}

# Configuración de la aplicación
APP_TITLE = "Optimización de Rutas con Algoritmos Genéticos"
APP_DESCRIPTION = """
    Herramienta para la optimización de rutas de reparto utilizando algoritmos genéticos.
    Desarrollado para el curso de Algoritmos Genéticos.
"""

# Asegurar que los directorios existan
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(RESULTADOS_PATH, exist_ok=True)
os.makedirs(os.path.join(RESULTADOS_PATH, 'graficos'), exist_ok=True)
os.makedirs(os.path.join(RESULTADOS_PATH, 'rutas_optimizadas'), exist_ok=True)
os.makedirs(os.path.join(RESULTADOS_PATH, 'logs'), exist_ok=True)
