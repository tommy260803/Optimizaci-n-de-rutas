"""
Implementación del algoritmo genético para optimización de rutas.
"""
import random
import numpy as np
from typing import List, Tuple, Dict, Any, Callable, Optional
import pandas as pd
import logging

# Importar módulos locales
from .funciones_fitness import fitness_completo
from .operadores_geneticos import (
    seleccion_torneo,
    cruza_order,
    cruza_pmx,
    mutacion_swap,
    mutacion_inversion
)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlgoritmoGenetico:
    """Clase que implementa el algoritmo genético para optimización de rutas."""
    
    def __init__(
        self,
        matriz_distancias: pd.DataFrame,
        df_puntos: pd.DataFrame,
        tamano_poblacion: int = 100,
        num_generaciones: int = 500,
        prob_cruza: float = 0.8,
        prob_mutacion: float = 0.2,
        tamano_elitismo: int = 5,
        capacidad_vehiculo: float = 100.0,
        callback_progreso: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Inicializa el algoritmo genético con los parámetros dados.
        
        Args:
            matriz_distancias: DataFrame con las distancias entre puntos.
            df_puntos: DataFrame con información de los puntos de entrega.
            tamano_poblacion: Tamaño de la población.
            num_generaciones: Número de generaciones a ejecutar.
            prob_cruza: Probabilidad de cruza (0-1).
            prob_mutacion: Probabilidad de mutación (0-1).
            tamano_elitismo: Número de mejores individuos que pasan directamente a la siguiente generación.
            capacidad_vehiculo: Capacidad máxima del vehículo.
            callback_progreso: Función opcional para reportar progreso.
        """
        self.matriz_distancias = matriz_distancias
        self.df_puntos = df_puntos
        self.tamano_poblacion = tamano_poblacion
        self.num_generaciones = num_generaciones
        self.prob_cruza = prob_cruza
        self.prob_mutacion = prob_mutacion
        self.tamano_elitismo = tamano_elitismo
        self.capacidad_vehiculo = capacidad_vehiculo
        self.callback_progreso = callback_progreso
        
        # Inicializar estado
        self.poblacion = []
        self.mejor_individuo = None
        self.mejor_fitness = float('inf')
        self.historial = []
        self.generacion_actual = 0
        self.ejecutando = True
        
        # Obtener lista de IDs de puntos (excluyendo el depósito que tiene id=0)
        self.ids_puntos = [id_ for id_ in df_puntos['id'].unique() if id_ != 0]
        
        logger.info("Algoritmo Genético inicializado con %d puntos de entrega", len(self.ids_puntos))
    
    def inicializar_poblacion(self) -> None:
        """Inicializa la población con individuos aleatorios."""
        self.poblacion = []
        
        for _ in range(self.tamano_poblacion):
            # Crear una permutación aleatoria de los IDs de los puntos
            individuo = np.random.permutation(self.ids_puntos).tolist()
            self.poblacion.append(individuo)
        
        logger.info("Población inicializada con %d individuos", len(self.poblacion))
    
    def evaluar_individuo(self, individuo: List[int]) -> float:
        """
        Evalúa un individuo calculando su fitness.
        
        Args:
            individuo: Lista de IDs de puntos en el orden de visita.
            
        Returns:
            float: Valor de fitness (menor es mejor).
        """
        return fitness_completo(
            ruta=individuo,
            matriz_distancias=self.matriz_distancias,
            df_puntos=self.df_puntos,
            capacidad_max=self.capacidad_vehiculo
        )
    
    def evaluar_poblacion(self) -> List[Tuple[List[int], float]]:
        """
        Evalúa todos los individuos de la población actual.
        
        Returns:
            Lista de tuplas (individuo, fitness) ordenada por fitness ascendente.
        """
        evaluados = []
        
        for individuo in self.poblacion:
            fitness = self.evaluar_individuo(individuo)
            evaluados.append((individuo, fitness))
        
        # Ordenar por fitness (menor es mejor)
        evaluados.sort(key=lambda x: x[1])
        
        return evaluados
    
    def seleccionar_padres(self, poblacion_evaluada: List[Tuple[List[int], float]]) -> Tuple[List[int], List[int]]:
        """
        Selecciona dos padres de la población.
        
        Args:
            poblacion_evaluada: Lista de tuplas (individuo, fitness) ordenada.
            
        Returns:
            Tupla con dos individuos seleccionados como padres.
        """
        # Extraer individuos y fitness
        individuos = [ind for ind, _ in poblacion_evaluada]
        fitness = [fit for _, fit in poblacion_evaluada]
        
        # Usar selección por torneo
        padres = seleccion_torneo(
            poblacion=individuos,
            fitness=fitness,
            k=3,  # Tamaño del torneo
            num_padres=2
        )
        
        return padres[0], padres[1]
    
    def aplicar_cruza(self, padre1: List[int], padre2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Aplica el operador de cruce a dos padres.
        
        Args:
            padre1: Primer padre.
            padre2: Segundo padre.
            
        Returns:
            Tupla con los dos hijos resultantes.
        """
        # Usar Order Crossover (OX)
        return cruza_order(
            padre1=padre1,
            padre2=padre2,
            prob_cruza=self.prob_cruza
        )
    
    def aplicar_mutacion(self, individuo: List[int]) -> List[int]:
        """
        Aplica mutación a un individuo.
        
        Args:
            individuo: Individuo a mutar.
            
        Returns:
            Individuo mutado.
        """
        # Usar mutación por inversión
        return mutacion_inversion(
            individuo=individuo,
            prob_mutacion=self.prob_mutacion
        )
    
    def evolucionar_generacion(self) -> None:
        """Ejecuta una generación completa del algoritmo genético."""
        # Evaluar población actual
        poblacion_evaluada = self.evaluar_poblacion()
        
        # Aplicar elitismo: seleccionar los mejores individuos
        elite = [ind for ind, _ in poblacion_evaluada[:self.tamano_elitismo]]
        
        # Crear nueva población
        nueva_poblacion = elite.copy()
        
        # Generar nuevos individuos hasta completar la población
        while len(nueva_poblacion) < self.tamano_poblacion:
            # Seleccionar padres
            padre1, padre2 = self.seleccionar_padres(poblacion_evaluada)
            
            # Aplicar cruza
            hijo1, hijo2 = self.aplicar_cruza(padre1, padre2)
            
            # Aplicar mutación
            hijo1 = self.aplicar_mutacion(hijo1)
            hijo2 = self.aplicar_mutacion(hijo2)
            
            # Añadir a la nueva población
            nueva_poblacion.extend([hijo1, hijo2])
        
        # Asegurarse de no exceder el tamaño de población
        self.poblacion = nueva_poblacion[:self.tamano_poblacion]
        
        # Actualizar mejor individuo global
        mejor_actual, mejor_fitness_actual = poblacion_evaluada[0]
        if mejor_fitness_actual < self.mejor_fitness:
            self.mejor_individuo = mejor_actual.copy()
            self.mejor_fitness = mejor_fitness_actual
            logger.info("Nuevo mejor fitness encontrado: %.4f en generación %d", 
                       self.mejor_fitness, self.generacion_actual)
        
        # Almacenar estadísticas
        fitness_values = [fit for _, fit in poblacion_evaluada]
        self.historial.append({
            'generacion': self.generacion_actual,
            'mejor_fitness': min(fitness_values),
            'promedio_fitness': sum(fitness_values) / len(fitness_values),
            'peor_fitness': max(fitness_values),
        })
        
        # Llamar al callback de progreso si está definido
        if self.callback_progreso:
            self.callback_progreso(self.obtener_estadisticas())
        
        self.generacion_actual += 1
    
    def obtener_mejor_individuo(self) -> Tuple[List[int], float]:
        """
        Obtiene el mejor individuo encontrado hasta el momento.
        
        Returns:
            Tupla con (mejor_individuo, mejor_fitness).
        """
        return self.mejor_individuo, self.mejor_fitness
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre la ejecución actual.

        Returns:
            Diccionario con estadísticas.
        """
        if not self.historial:
            return {}

        ultimo = self.historial[-1]
        return {
            'generacion_actual': self.generacion_actual,
            'num_generaciones': self.num_generaciones,
            'mejor_fitness': self.mejor_fitness,
            'mejor_individuo': self.mejor_individuo,
            'fitness_promedio': ultimo['promedio_fitness'],
            'peor_fitness': ultimo['peor_fitness'],
            'tamano_poblacion': self.tamano_poblacion,
            'prob_cruza': self.prob_cruza,
            'prob_mutacion': self.prob_mutacion,
            'elitismo': self.tamano_elitismo
        }
    
    def pausar(self) -> None:
        """Detiene la ejecución del algoritmo."""
        self.ejecutando = False
        
    def reanudar(self) -> None:
        """Reanuda la ejecución del algoritmo."""
        self.ejecutando = True

    def detener(self) -> None:
        """Detiene completamente la ejecución del algoritmo."""
        self.ejecutando = False

    def ha_terminado(self) -> bool:
        """
        Verifica si el algoritmo ha terminado su ejecución.

        Returns:
            bool: True si el algoritmo ha terminado, False en caso contrario.
        """
        return self.generacion_actual >= self.num_generaciones or not self.ejecutando

    def ejecutar(self) -> Tuple[List[int], float, List[Dict[str, Any]]]:
        """
        Ejecuta el algoritmo genético.
        
        Returns:
            Tupla con (mejor_individuo, mejor_fitness, historial).
        """
        logger.info("Iniciando ejecución del algoritmo genético")
        
        # Inicializar población si es necesario
        if not self.poblacion:
            self.inicializar_poblacion()
        
        # Bucle principal de evolución
        while self.generacion_actual < self.num_generaciones and self.ejecutando:
            self.evolucionar_generacion()
        
        logger.info("Ejecución completada. Mejor fitness encontrado: %.4f", self.mejor_fitness)
        
        return self.mejor_individuo, self.mejor_fitness, self.historial
