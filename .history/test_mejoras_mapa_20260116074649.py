#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en las flechas y centrado de números.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.components.mapa import calcular_angulo_entre_puntos
import numpy as np

def test_calcular_angulo():
    """Prueba la función de cálculo de ángulos."""
    print("🔍 Probando cálculo de ángulos entre puntos GPS...")

    # Test cases: (coord1, coord2, expected_direction)
    test_cases = [
        # Norte
        ((-8.1, -79.0), (-8.0, -79.0), "Norte"),
        # Sur
        ((-8.0, -79.0), (-8.1, -79.0), "Sur"),
        # Este
        ((-8.0, -79.0), (-8.0, -78.9), "Este"),
        # Oeste
        ((-8.0, -78.9), (-8.0, -79.0), "Oeste"),
        # Noreste
        ((-8.1, -79.0), (-8.0, -78.9), "Noreste"),
        # Suroeste
        ((-8.0, -78.9), (-8.1, -79.0), "Suroeste"),
    ]

    for coord1, coord2, expected in test_cases:
        angulo = calcular_angulo_entre_puntos(coord1, coord2)
        print(".1f")

    print("✅ Pruebas de ángulos completadas\n")

def test_direccion_flechas():
    """Simula cómo se verían las flechas en una ruta de ejemplo."""
    print("🎯 Simulando dirección de flechas en ruta de ejemplo...")

    # Coordenadas de ejemplo en Trujillo
    ruta_coords = [
        (-8.1117, -79.0288),  # Depósito
        (-8.105, -79.025),   # Punto 1
        (-8.095, -79.015),   # Punto 2
        (-8.085, -79.005),   # Punto 3
        (-8.1117, -79.0288),  # Regreso al depósito
    ]

    print("Ruta simulada:")
    for i, coord in enumerate(ruta_coords):
        print(f"  Punto {i}: {coord}")

    print("\nDirecciones calculadas:")
    for i in range(len(ruta_coords) - 1):
        coord1 = ruta_coords[i]
        coord2 = ruta_coords[i + 1]
        angulo = calcular_angulo_entre_puntos(coord1, coord2)

        # Determinar dirección cardinal aproximada
        if 337.5 <= angulo <= 360 or 0 <= angulo < 22.5:
            direccion = "Norte"
        elif 22.5 <= angulo < 67.5:
