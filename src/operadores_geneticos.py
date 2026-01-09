"""
Módulo con operadores genéticos para el algoritmo de optimización de rutas.
"""
import random
from typing import List, Tuple, Dict, Any
import numpy as np

def seleccion_torneo(
    poblacion: List[Any], 
    fitness: List[float], 
    k: int = 3,
    num_padres: int = 2
) -> List[Any]:
    """
    Selección por torneo de tamaño k.
    
    Args:
        poblacion: Lista de individuos de la población.
        fitness: Lista de valores de fitness para cada individuo.
        k: Tamaño del torneo.
        num_padres: Número de padres a seleccionar.
        
    Returns:
        Lista de individuos seleccionados como padres.
    """
    padres = []
    
    for _ in range(num_padres):
        # Seleccionar k individuos al azar
        torneo_indices = random.sample(range(len(poblacion)), k)
        torneo_fitness = [fitness[i] for i in torneo_indices]
        
        # Seleccionar el mejor del torneo (menor fitness es mejor)
        mejor_idx = torneo_indices[np.argmin(torneo_fitness)]
        padres.append(poblacion[mejor_idx])
    
    return padres

def seleccion_ruleta(
    poblacion: List[Any], 
    fitness: List[float],
    num_padres: int = 2
) -> List[Any]:
    """
    Selección por ruleta con probabilidades inversamente proporcionales al fitness.
    
    Args:
        poblacion: Lista de individuos de la población.
        fitness: Lista de valores de fitness para cada individuo.
        num_padres: Número de padres a seleccionar.
        
    Returns:
        Lista de individuos seleccionados como padres.
    """
    # Convertir fitness a valores positivos (inversos para minimización)
    max_fitness = max(fitness) + 1e-10  # Evitar división por cero
    fitness_inv = [max_fitness - f for f in fitness]
    
    # Normalizar para obtener probabilidades
    total = sum(fitness_inv)
    if total == 0:
        # Si todos los fitness son iguales, selección aleatoria uniforme
        return random.choices(poblacion, k=num_padres)
        
    probabilidades = [f/total for f in fitness_inv]
    
    # Seleccionar padres usando ruleta
    return random.choices(
        poblacion, 
        weights=probabilidades, 
        k=num_padres
    )

def cruza_order(
    padre1: List[int], 
    padre2: List[int],
    prob_cruza: float = 1.0
) -> Tuple[List[int], List[int]]:
    """
    Operador de cruce Order Crossover (OX).
    
    Args:
        padre1: Primer padre.
        padre2: Segundo padre.
        prob_cruza: Probabilidad de que ocurra el cruce.
        
    Returns:
        Tupla con los dos hijos resultantes.
    """
    if random.random() > prob_cruza or len(padre1) <= 2:
        return padre1.copy(), padre2.copy()
    
    n = len(padre1)
    
    # Seleccionar dos puntos de corte aleatorios
    punto1, punto2 = sorted(random.sample(range(n), 2))
    
    def crear_hijo(p1, p2, start, end):
        hijo = [None] * n
        # Copiar el segmento del padre 1 al hijo
        hijo[start:end+1] = p1[start:end+1]
        
        # Llenar los espacios restantes con los genes del padre 2
        # en el orden en que aparecen, excluyendo los ya copiados
        pos = (end + 1) % n
        for gen in p2[end+1:] + p2[:end+1]:
            if gen not in hijo:
                hijo[pos] = gen
                pos = (pos + 1) % n
                if pos == start:
                    break
        
        return hijo
    
    # Crear los dos hijos
    hijo1 = crear_hijo(padre1, padre2, punto1, punto2)
    hijo2 = crear_hijo(padre2, padre1, punto1, punto2)
    
    return hijo1, hijo2

def cruza_pmx(
    padre1: List[int], 
    padre2: List[int],
    prob_cruza: float = 1.0
) -> Tuple[List[int], List[int]]:
    """
    Operador de cruce Partially Mapped Crossover (PMX).
    
    Args:
        padre1: Primer padre.
        padre2: Segundo padre.
        prob_cruza: Probabilidad de que ocurra el cruce.
        
    Returns:
        Tupla con los dos hijos resultantes.
    """
    if random.random() > prob_cruza or len(padre1) <= 2:
        return padre1.copy(), padre2.copy()
    
    n = len(padre1)
    
    # Seleccionar dos puntos de corte aleatorios
    punto1, punto2 = sorted(random.sample(range(n), 2))
    
    def crear_hijo(p1, p2, start, end):
        # Inicializar el hijo con None
        hijo = [None] * n
        
        # Copiar el segmento del padre 1 al hijo
        segmento = p1[start:end+1]
        hijo[start:end+1] = segmento
        
        # Crear mapeo entre los segmentos de los padres
        mapeo = {}
        for i in range(end - start + 1):
            gen_p1 = p1[start + i]
            gen_p2 = p2[start + i]
            if gen_p1 != gen_p2:  # Solo mapear si son diferentes
                mapeo[gen_p2] = gen_p1
        
        # Llenar las posiciones restantes del hijo
        for i in range(n):
            if i < start or i > end:  # Solo para posiciones fuera del segmento
                gen = p2[i]
                while gen in mapeo:  # Aplicar mapeo recursivamente
                    gen = mapeo[gen]
                hijo[i] = gen
        
        return hijo
    
    # Crear los dos hijos
    hijo1 = crear_hijo(padre1, padre2, punto1, punto2)
    hijo2 = crear_hijo(padre2, padre1, punto1, punto2)
    
    return hijo1, hijo2

def mutacion_swap(
    individuo: List[int], 
    prob_mutacion: float
) -> List[int]:
    """
    Operador de mutación por intercambio (swap).
    
    Args:
        individuo: Individuo a mutar.
        prob_mutacion: Probabilidad de que ocurra la mutación.
        
    Returns:
        Individuo mutado.
    """
    if random.random() > prob_mutacion or len(individuo) < 2:
        return individuo.copy()
    
    # Hacer una copia del individuo
    mutado = individuo.copy()
    
    # Seleccionar dos posiciones aleatorias diferentes
    i, j = random.sample(range(len(mutado)), 2)
    
    # Intercambiar los genes en las posiciones seleccionadas
    mutado[i], mutado[j] = mutado[j], mutado[i]
    
    return mutado

def mutacion_inversion(
    individuo: List[int], 
    prob_mutacion: float
) -> List[int]:
    """
    Operador de mutación por inversión.
    
    Args:
        individuo: Individuo a mutar.
        prob_mutacion: Probabilidad de que ocurra la mutación.
        
    Returns:
        Individuo mutado.
    """
    if random.random() > prob_mutacion or len(individuo) < 2:
        return individuo.copy()
    
    # Hacer una copia del individuo
    mutado = individuo.copy()
    
    # Seleccionar dos posiciones aleatorias diferentes
    i, j = sorted(random.sample(range(len(mutado)), 2))
    
    # Invertir el segmento entre las posiciones seleccionadas
    mutado[i:j+1] = reversed(mutado[i:j+1])
    
    return mutado
