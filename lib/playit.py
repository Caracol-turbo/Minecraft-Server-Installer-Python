import os
import sys
import time
import subprocess
import re
import urllib.request
from pathlib import Path
from lib.config import BASE_DIR

BIN_DIR = BASE_DIR / "bin"
PLAYIT_BIN = BIN_DIR / "playit"
SECRET_FILE = BASE_DIR / "playit_secret.txt"
LOG_FILE = BASE_DIR / "playit.log"
PID_FILE = BASE_DIR / "playit.pid"

PLAYIT_DOWNLOAD_URL = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"

def ensure_playit_binary() -> bool:
    """Asegura que el ejecutable de Playit.gg esté descargado y sea ejecutable."""
    if PLAYIT_BIN.exists() and os.access(PLAYIT_BIN, os.X_OK):
        return True

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[Playit] Descargando binario desde {PLAYIT_DOWNLOAD_URL}...")
    try:
        req = urllib.request.Request(
            PLAYIT_DOWNLOAD_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req) as resp, open(PLAYIT_BIN, "wb") as f:
            f.write(resp.read())
        PLAYIT_BIN.chmod(0o755)
        print("[Playit] Binario instalado correctamente.")
        return True
    except Exception as e:
        print(f"[Playit] Error al descargar binario: {e}")
        return False

def is_running() -> bool:
    """Comprueba si el proceso playit está actualmente en ejecución."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Comprobar si el proceso existe
            os.kill(pid, 0)
            return True
        except (ValueError, OSError):
            if PID_FILE.exists():
                PID_FILE.unlink()
    
    # Comprobación de respaldo con pgrep / ps
    try:
        res = subprocess.run(["pgrep", "-f", "playit"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return True
    except Exception:
        pass
    return False

def save_secret(secret_key: str) -> bool:
    """Guarda la clave secreta de Playit."""
    secret_key = secret_key.strip()
    if secret_key:
        SECRET_FILE.write_text(secret_key, encoding="utf-8")
        return True
    elif SECRET_FILE.exists():
        SECRET_FILE.unlink()
    return False

def get_secret() -> str:
    """Obtiene la clave secreta guardada si existe."""
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip()
    return ""

def start_playit(secret_key: str = None) -> dict:
    """Inicia el agente Playit.gg."""
    if not ensure_playit_binary():
        return {"success": False, "error": "No se pudo preparar el binario de Playit"}

    if is_running():
        return {"success": True, "message": "Playit ya se encuentra en ejecución"}

    if secret_key is not None:
        save_secret(secret_key)

    saved_secret = get_secret()

    cmd = [str(PLAYIT_BIN), "--log-path", str(LOG_FILE)]
    if saved_secret:
        cmd.extend(["--secret", saved_secret])

    # Limpiar archivo de log previo si existe
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    try:
        log_fd = open(LOG_FILE, "a")
        proc = subprocess.Popen(
            cmd,
            stdout=log_fd,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        PID_FILE.write_text(str(proc.pid))
        
        # Esperar un par de segundos para generar los primeros logs (claim code o conexiones)
        time.sleep(2)
        
        return {"success": True, "message": "Servicio de túnel Playit iniciado", "pid": proc.pid}
    except Exception as e:
        return {"success": False, "error": f"Error al iniciar Playit: {str(e)}"}

def stop_playit() -> dict:
    """Detiene el proceso Playit."""
    stopped = False
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 15)  # SIGTERM
            stopped = True
        except Exception:
            pass
        if PID_FILE.exists():
            PID_FILE.unlink()

    # pkill de respaldo
    try:
        subprocess.run(["pkill", "-f", "playit"], capture_output=True)
        stopped = True
    except Exception:
        pass

    return {"success": True, "message": "Playit detenido correctamente"}

def get_status() -> dict:
    """Devuelve el estado detallado de Playit, incluyendo claim URL y túneles activos."""
    running = is_running()
    saved_secret = get_secret()
    claim_url = ""
    tunnels = []
    logs = ""

    if LOG_FILE.exists():
        try:
            logs = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
            # Buscar Claim URL
            claim_match = re.search(r"https://playit\.gg/claim/[a-zA-Z0-9-]+", logs)
            if claim_match:
                claim_url = claim_match.group(0)

            # Buscar direcciones de túnel asignadas (e.g. xxx.gl.at.ply.gg:12345 o xxx.ply.gg:12345)
            tunnel_matches = re.findall(r"([a-zA-Z0-9.-]+\.(?:gl\.at\.ply\.gg|ply\.gg|playit\.gg)(?::\d+)?)", logs)
            if tunnel_matches:
                # Filtrar duplicados manteniendo orden
                seen = set()
                for t in tunnel_matches:
                    if t not in seen and not t.startswith("https://"):
                        seen.add(t)
                        tunnels.append(t)
        except Exception:
            pass

    return {
        "running": running,
        "secret_set": bool(saved_secret),
        "secret_key": saved_secret,
        "claim_url": claim_url,
        "tunnels": tunnels,
        "logs": logs[-1000:] if logs else ""  # Últimos 1000 caracteres de log
    }
