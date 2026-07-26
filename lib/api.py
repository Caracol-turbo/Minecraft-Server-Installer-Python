import json
import urllib.request
from typing import List, Optional, Any
from lib.utils import print_error, log

def _fetch_json(url: str) -> Optional[Any]:
    """Función auxiliar para realizar solicitudes HTTP y parsear la respuesta JSON."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Minecraft-Server-Installer/1.0 (Python)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode("utf-8")
                return json.loads(data)
    except Exception as e:
        log(f"Error al obtener datos de {url}: {e}")
        print_error(f"Error al conectar con la API ({url}): {e}")
    return None

# --- API Mojang / Vanilla ---

def get_vanilla_versions() -> List[str]:
    """Obtiene la lista de versiones estables de Minecraft Vanilla."""
    url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    data = _fetch_json(url)
    if data and "versions" in data:
        return [v["id"] for v in data["versions"] if v.get("type") == "release"]
    return []

def get_vanilla_download_url(version: str) -> Optional[str]:
    """Obtiene la URL de descarga directa del ejecutable del servidor Vanilla para una versión."""
    url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    manifest = _fetch_json(url)
    if not manifest or "versions" not in manifest:
        return None
    
    version_entry = next((v for v in manifest["versions"] if v.get("id") == version), None)
    if not version_entry or "url" not in version_entry:
        return None
    
    version_details = _fetch_json(version_entry["url"])
    if version_details and "downloads" in version_details and "server" in version_details["downloads"]:
        return version_details["downloads"]["server"].get("url")
    return None

# --- API PaperMC ---

def get_paper_versions() -> List[str]:
    """Obtiene la lista de versiones de Minecraft soportadas por Paper."""
    url = "https://api.papermc.io/v2/projects/paper"
    data = _fetch_json(url)
    if data and "versions" in data:
        return list(reversed(data["versions"]))
    return []

def get_paper_builds(version: str) -> List[int]:
    """Obtiene los números de compilación (builds) para una versión de Paper."""
    url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
    data = _fetch_json(url)
    if data and "builds" in data:
        return data["builds"]
    return []

def get_paper_download_url(version: str, build: Any) -> str:
    """Construye la URL de descarga para Paper."""
    return f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"

# --- API Purpur ---

def get_purpur_versions() -> List[str]:
    """Obtiene la lista de versiones soportadas por Purpur."""
    url = "https://api.purpurmc.org/v2/purpur"
    data = _fetch_json(url)
    if data and "versions" in data:
        return data["versions"]
    return []

def get_purpur_builds(version: str) -> List[str]:
    """Obtiene las compilaciones (builds) para una versión de Purpur."""
    url = f"https://api.purpurmc.org/v2/purpur/{version}"
    data = _fetch_json(url)
    if data and "builds" in data and "all" in data["builds"]:
        return [str(b) for b in data["builds"]["all"]]
    return []

def get_purpur_download_url(version: str, build: str) -> str:
    """Construye la URL de descarga para Purpur."""
    return f"https://api.purpurmc.org/v2/purpur/{version}/{build}/download"

# --- API Fabric ---

def get_fabric_game_versions() -> List[str]:
    """Obtiene las versiones del juego compatibles con Fabric."""
    url = "https://meta.fabricmc.net/v2/versions/game"
    data = _fetch_json(url)
    if data and isinstance(data, list):
        return [item["version"] for item in data if item.get("stable") is True]
    return []

def get_fabric_installer_versions() -> List[str]:
    """Obtiene las versiones del instalador de Fabric."""
    url = "https://meta.fabricmc.net/v2/versions/installer"
    data = _fetch_json(url)
    if data and isinstance(data, list):
        return [item["version"] for item in data]
    return []

def get_fabric_loader_versions() -> List[str]:
    """Obtiene las versiones del Loader de Fabric."""
    url = "https://meta.fabricmc.net/v2/versions/loader"
    data = _fetch_json(url)
    if data and isinstance(data, list):
        return [item["version"] for item in data]
    return []

def get_fabric_download_url(game_ver: str, loader_ver: str, inst_ver: str) -> str:
    """Construye la URL de descarga directa para el JAR de servidor Fabric."""
    return f"https://meta.fabricmc.net/v2/versions/loader/{game_ver}/{loader_ver}/{inst_ver}/server/jar"

# --- API Forge ---

def get_forge_versions() -> List[str]:
    """Obtiene las versiones de Minecraft compatibles con Forge."""
    url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
    data = _fetch_json(url)
    if data and "promos" in data:
        mc_versions = set()
        for key in data["promos"].keys():
            parts = key.rsplit("-", 1)
            if len(parts) == 2 and parts[0][0].isdigit():
                mc_versions.add(parts[0])
        # Ordenar versiones numéricamente
        return sorted(list(mc_versions), reverse=True)
    return []

def get_forge_builds(mc_version: str) -> List[dict]:
    """Obtiene las compilaciones de Forge (recommended / latest) para una versión de Minecraft."""
    url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
    data = _fetch_json(url)
    builds = []
    if data and "promos" in data:
        promos = data["promos"]
        rec = promos.get(f"{mc_version}-recommended")
        lat = promos.get(f"{mc_version}-latest")
        if rec:
            builds.append({"type": "recommended", "version": rec})
        if lat and lat != rec:
            builds.append({"type": "latest", "version": lat})
        elif lat and not rec:
            builds.append({"type": "latest", "version": lat})
    return builds

def get_forge_download_url(mc_version: str, forge_version: str) -> str:
    """Construye la URL del instalador JAR de Forge."""
    return f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar"

# --- API NeoForge ---

def get_neoforge_versions() -> List[str]:
    """Obtiene la lista de versiones disponibles de NeoForge."""
    url = "https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge"
    data = _fetch_json(url)
    if data and "versions" in data:
        versions = [v for v in data["versions"] if "alpha" not in v and "snapshot" not in v]
        return list(reversed(versions))
    return []

def get_neoforge_download_url(neoforge_version: str) -> str:
    """Construye la URL del instalador JAR de NeoForge."""
    return f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{neoforge_version}/neoforge-{neoforge_version}-installer.jar"

