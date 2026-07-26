import os
from pathlib import Path

# Directorio base del proyecto (raíz del repositorio)
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorio donde se almacenan los servidores de Minecraft
SERVERS_DIR = BASE_DIR / "servers"

# Archivo de log
LOG_FILE = BASE_DIR / "installer.log"

# Versión mínima de Java requerida
JAVA_MIN_VERSION = 21

# Directorio temporal
TEMP_DIR = BASE_DIR / "tmp"
