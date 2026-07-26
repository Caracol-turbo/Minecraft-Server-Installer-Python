import urllib.request
import sys
from pathlib import Path
from lib import api
from lib.utils import print_info, print_success, print_error, log

def download_file(url: str, dest_path: Path) -> bool:
    """Descarga un archivo desde una URL mostrando el progreso."""
    print_info(f"Descargando desde: {url}")
    log(f"Iniciando descarga: {url} -> {dest_path}")
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Minecraft-Server-Installer/1.0 (Python)"}
        )
        with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
            total_size_hdr = response.getheader('Content-Length')
            total_size = int(total_size_hdr) if total_size_hdr else None
            
            downloaded = 0
            block_size = 8192
            
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)
                
                if total_size:
                    percent = downloaded * 100 / total_size
                    sys.stdout.write(f"\rProgreso: [{percent:6.2f}%] ({downloaded}/{total_size} bytes)")
                    sys.stdout.flush()
            
            if total_size:
                sys.stdout.write("\n")
                
        print_success(f"Descarga completada en {dest_path}")
        log(f"Descarga exitosa: {dest_path}")
        return True
    except Exception as e:
        print_error(f"Error en la descarga: {e}")
        log(f"Error en la descarga de {url}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False

def download_vanilla(version: str, dest_path: Path) -> bool:
    print_info(f"Obteniendo URL de Vanilla {version}...")
    url = api.get_vanilla_download_url(version)
    if url:
        return download_file(url, dest_path)
    else:
        print_error(f"No se pudo encontrar la descarga para Vanilla {version}")
        return False

def download_paper(version: str, build: str, dest_path: Path) -> bool:
    url = api.get_paper_download_url(version, build)
    return download_file(url, dest_path)

def download_purpur(version: str, build: str, dest_path: Path) -> bool:
    url = api.get_purpur_download_url(version, build)
    return download_file(url, dest_path)

def download_fabric(game_ver: str, loader_ver: str, inst_ver: str, dest_path: Path) -> bool:
    url = api.get_fabric_download_url(game_ver, loader_ver, inst_ver)
    return download_file(url, dest_path)

def download_forge(mc_version: str, forge_version: str, target_dir: Path) -> bool:
    url = api.get_forge_download_url(mc_version, forge_version)
    installer_path = target_dir / "installer.jar"
    print_info(f"Descargando instalador de Forge {mc_version}-{forge_version}...")
    if download_file(url, installer_path):
        # Intentar ejecutar la instalación del servidor si java está disponible
        print_info("Ejecutando instalador de servidor Forge...")
        import subprocess
        try:
            res = subprocess.run(["java", "-jar", "installer.jar", "--installServer"], cwd=target_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                print_success("Instalación de Forge completada con éxito.")
                if installer_path.exists():
                    installer_path.unlink()
            else:
                print_warning("El instalador no pudo ejecutarse directamente. Se ejecutará en la primera arrancada con start.sh")
        except Exception:
            print_warning("Java no detectado en el entorno actual. El instalador se ejecutará automáticamente al iniciar el servidor.")
        return True
    return False

def download_neoforge(neoforge_version: str, target_dir: Path) -> bool:
    url = api.get_neoforge_download_url(neoforge_version)
    installer_path = target_dir / "installer.jar"
    print_info(f"Descargando instalador de NeoForge {neoforge_version}...")
    if download_file(url, installer_path):
        print_info("Ejecutando instalador de servidor NeoForge...")
        import subprocess
        try:
            res = subprocess.run(["java", "-jar", "installer.jar", "--installServer"], cwd=target_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                print_success("Instalación de NeoForge completada con éxito.")
                if installer_path.exists():
                    installer_path.unlink()
            else:
                print_warning("El instalador se ejecutará en el primer inicio a través de start.sh")
        except Exception:
            print_warning("Java no detectado en el entorno actual. El instalador se ejecutará automáticamente al iniciar el servidor.")
        return True
    return False

