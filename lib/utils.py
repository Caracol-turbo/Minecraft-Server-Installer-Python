import sys
import shutil
import subprocess
from datetime import datetime
from lib.config import LOG_FILE

# Códigos de colores ANSI
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color

def log(message: str) -> None:
    """Registra un mensaje con marca de tiempo en el archivo LOG_FILE."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"{RED}[ERROR LOG]{NC} No se pudo escribir en el log: {e}")

def print_info(message: str) -> None:
    print(f"{CYAN}[INFO]{NC} {message}")

def print_success(message: str) -> None:
    print(f"{GREEN}[ÉXITO]{NC} {message}")

def print_warning(message: str) -> None:
    print(f"{YELLOW}[ADVERTENCIA]{NC} {message}")

def print_error(message: str) -> None:
    print(f"{RED}[ERROR]{NC} {message}")

def confirm(prompt: str) -> bool:
    """Pide confirmación al usuario (s/n)."""
    try:
        choice = input(f"{prompt} (s/n): ").strip().lower()
        return choice in ("s", "y")
    except (KeyboardInterrupt, EOFError):
        return False

def check_dependencies() -> bool:
    """Verifica las dependencias del sistema necesarias."""
    deps = ["java"]
    missing = []
    for dep in deps:
        if shutil.which(dep) is None:
            missing.append(dep)
    
    if missing:
        print_error(f"Faltan dependencias necesarias: {' '.join(missing)}")
        return False
    return True
