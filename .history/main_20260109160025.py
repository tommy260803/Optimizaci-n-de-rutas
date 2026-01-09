"""
Punto de entrada principal para la aplicación de Optimización de Rutas con Algoritmos Genéticos.
"""
import os
import sys
import time
from pathlib import Path

# Añadir el directorio src al path para los imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Importar el generador de datos
from src.generador_datos import verificar_o_generar_datos

# Configuración de rutas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
RESULTADOS_DIR = BASE_DIR / 'resultados'
GRAFICOS_DIR = RESULTADOS_DIR / 'graficos'
RUTAS_OPTIMIZADAS_DIR = RESULTADOS_DIR / 'rutas_optimizadas'
LOGS_DIR = RESULTADOS_DIR / 'logs'

def verificar_estructura() -> None:
    """
    Verifica y crea la estructura de directorios necesaria para la aplicación.
    """
    try:
        # Crear directorios si no existen
        for directorio in [DATA_DIR, RESULTADOS_DIR, GRAFICOS_DIR, RUTAS_OPTIMIZADAS_DIR, LOGS_DIR]:
            os.makedirs(directorio, exist_ok=True)
            print(f"✓ Directorio verificado: {directorio}")
            
        print("\n✅ Estructura de directorios verificada correctamente.")
        
    except Exception as e:
        print(f"\n❌ Error al verificar la estructura de directorios: {str(e)}")
        sys.exit(1)

def inicializar_datos() -> bool:
    """
    Inicializa los datos necesarios para la aplicación.
    
    Returns:
        bool: True si la inicialización fue exitosa, False en caso contrario.
    """
    try:
        print("\n🔍 Verificando datos iniciales...")
        
        # Verificar o generar datos iniciales
        verificar_o_generar_datos()
        
        print("✅ Datos iniciales verificados correctamente.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al inicializar los datos: {str(e)}")
        return False

def mostrar_banner() -> None:
    """Muestra el banner de bienvenida de la aplicación."""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║       OPTIMIZACIÓN DE RUTAS CON ALGORITMOS GENÉTICOS      ║
    ║                     Versión 1.0.0                         ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == "__main__":
    try:
        # Mostrar banner de bienvenida
        mostrar_banner()
        
        # Verificar estructura de directorios
        print("\n🔍 Verificando estructura de directorios...")
        verificar_estructura()
        
        # Inicializar datos
        if not inicializar_datos():
            print("\n⚠️  Algunos datos no se pudieron inicializar correctamente.")
        
        # Importar la aplicación (aquí para evitar importaciones circulares)
        print("\n🚀 Iniciando la aplicación...")
from app.app import app

# Agregar archivos CSS y JS personalizados
app.css.append_css({"external_url": "/assets/custom_styles.css"})
app.scripts.append_script({"external_url": "/assets/custom_scripts.js"})

# Mostrar información de acceso
print("\n" + "="*60)
print("✅ Aplicación lista con diseño mejorado")
print(f"🌐 Accede en: http://127.0.0.1:8050")
print("="*60 + "\n")
print("Presiona Ctrl+C para detener la aplicación\n")

# Iniciar el servidor
app.run_server(debug=True, host='0.0.0.0', port=8050)
        
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación detenida por el usuario. ¡Hasta pronto!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)
