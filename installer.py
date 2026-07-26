#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess
from pathlib import Path

# Asegurar que el directorio raíz está en sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from lib.config import SERVERS_DIR
from lib.utils import (
    CYAN, NC, print_info, print_success, print_warning, print_error,
    check_dependencies, log
)
from lib import api
from lib import download

def show_banner():
    print(f"{CYAN}")
    print("==================================================")
    print("       MINECRAFT SERVER INSTALLER (PYTHON)        ")
    print("==================================================")
    print(f"{NC}")

def check_java():
    print_info("Comprobando Java...")
    try:
        result = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        version_output = result.stderr.splitlines()[0] if result.stderr else result.stdout.splitlines()[0]
        print_success(f"Java detectado: {version_output}")
    except Exception:
        print_warning("Java no está instalado o no está en el PATH.")

def prompt_select(options: list, prompt_msg: str = "Selecciona una opción: ") -> str:
    """Muestra un menú numerado y pide al usuario elegir un elemento."""
    for idx, opt in enumerate(options, 1):
        print(f"{idx}) {opt}")
    
    while True:
        try:
            choice = input(prompt_msg).strip()
            if choice.isdigit():
                val = int(choice)
                if 1 <= val <= len(options):
                    return str(options[val - 1])
            print_error("Opción no válida, inténtalo de nuevo.")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

def create_server():
    print("")
    print_info("--- Crear Nuevo Servidor ---")
    server_name = input("Nombre de la carpeta del servidor: ").strip()
    if not server_name:
        print_error("El nombre no puede estar vacío.")
        return

    target_dir = SERVERS_DIR / server_name
    if target_dir.exists():
        print_error(f"El servidor '{server_name}' ya existe en {target_dir}.")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    server_jar = target_dir / "server.jar"

    print("Selecciona el software:")
    print("1) Vanilla")
    print("2) Paper")
    print("3) Purpur")
    print("4) Fabric")
    print("5) Forge")
    print("6) NeoForge")
    sw_choice = input("Opción (1-6): ").strip()

    download_success = False

    if sw_choice == "1":
        print_info("Cargando versiones Vanilla...")
        versions = api.get_vanilla_versions()[:10]
        if versions:
            print("Últimas versiones disponibles:")
            selected_ver = prompt_select(versions)
            download_success = download.download_vanilla(selected_ver, server_jar)
        else:
            print_error("No se pudieron obtener las versiones de Vanilla.")

    elif sw_choice == "2":
        print_info("Cargando versiones Paper...")
        versions = api.get_paper_versions()[:10]
        if versions:
            selected_ver = prompt_select(versions, "Selecciona versión del juego: ")
            print_info(f"Cargando builds para Paper {selected_ver}...")
            builds = api.get_paper_builds(selected_ver)
            if builds:
                recent_builds = [str(b) for b in builds[-5:]]
                selected_build = prompt_select(recent_builds, "Selecciona número de build: ")
                download_success = download.download_paper(selected_ver, selected_build, server_jar)
            else:
                print_error("No se encontraron builds para la versión seleccionada.")
        else:
            print_error("No se pudieron obtener las versiones de Paper.")

    elif sw_choice == "3":
        print_info("Cargando versiones Purpur...")
        versions = api.get_purpur_versions()[-10:]
        if versions:
            selected_ver = prompt_select(versions, "Selecciona versión del juego: ")
            print_info(f"Cargando builds para Purpur {selected_ver}...")
            builds = api.get_purpur_builds(selected_ver)
            if builds:
                recent_builds = builds[-5:]
                selected_build = prompt_select(recent_builds, "Selecciona número de build: ")
                download_success = download.download_purpur(selected_ver, selected_build, server_jar)
            else:
                print_error("No se encontraron builds para la versión seleccionada.")
        else:
            print_error("No se pudieron obtener las versiones de Purpur.")

    elif sw_choice == "4":
        print_info("Cargando versiones Fabric...")
        game_vers = api.get_fabric_game_versions()[:5]
        if game_vers:
            print("Selecciona versión del juego:")
            selected_gver = prompt_select(game_vers)
            loader_vers = api.get_fabric_loader_versions()
            inst_vers = api.get_fabric_installer_versions()
            
            if loader_vers and inst_vers:
                loader_ver = loader_vers[0]
                inst_ver = inst_vers[0]
                print_info(f"Usando Fabric Loader {loader_ver} e Installer {inst_ver}")
                download_success = download.download_fabric(selected_gver, loader_ver, inst_ver, server_jar)
            else:
                print_error("No se pudieron obtener las versiones de Loader/Installer de Fabric.")
        else:
            print_error("No se pudieron obtener las versiones de Fabric.")

    elif sw_choice == "5":
        print_info("Cargando versiones de Minecraft para Forge...")
        versions = api.get_forge_versions()[:15]
        if versions:
            selected_ver = prompt_select(versions, "Selecciona versión del juego: ")
            print_info(f"Cargando compilaciones de Forge para {selected_ver}...")
            builds = api.get_forge_builds(selected_ver)
            if builds:
                build_opts = [f"{b['type'].capitalize()} ({b['version']})" for b in builds]
                selected_opt = prompt_select(build_opts, "Selecciona la versión de Forge: ")
                # Extraer número de versión
                selected_build = selected_opt.split("(")[1].replace(")", "").strip()
                download_success = download.download_forge(selected_ver, selected_build, target_dir)
            else:
                print_error("No se encontraron compilaciones de Forge para la versión seleccionada.")
        else:
            print_error("No se pudieron obtener las versiones de Forge.")

    elif sw_choice == "6":
        print_info("Cargando versiones de NeoForge...")
        versions = api.get_neoforge_versions()[:20]
        if versions:
            selected_ver = prompt_select(versions, "Selecciona la versión de NeoForge: ")
            download_success = download.download_neoforge(selected_ver, target_dir)
        else:
            print_error("No se pudieron obtener las versiones de NeoForge.")

    else:
        print_error("Opción no válida.")
        shutil.rmtree(target_dir, ignore_errors=True)
        return

    if download_success:
        eula_file = target_dir / "eula.txt"
        eula_file.write_text("eula=true\n", encoding="utf-8")
        print_success("EULA aceptado automáticamente (eula.txt).")

        ram_alloc = input("RAM a asignar (ej. 2G, 4G, 1024M) [Default: 2G]: ").strip()
        if not ram_alloc:
            ram_alloc = "2G"

        start_script = target_dir / "start.sh"
        script_content = f"""#!/usr/bin/env bash
if [ -f installer.jar ] && [ ! -f run.sh ] && [ ! -f user_jvm_args.txt ]; then
    echo "Ejecutando el instalador del servidor..."
    java -jar installer.jar --installServer
    rm -f installer.jar installer.jar.log
fi

if [ -f run.sh ]; then
    if [ -f user_jvm_args.txt ]; then
        sed -i '/-Xmx/d' user_jvm_args.txt
        echo "-Xms1024M -Xmx{ram_alloc}" >> user_jvm_args.txt
    fi
    bash run.sh nogui
elif [ -f server.jar ]; then
    java -Xms1024M -Xmx{ram_alloc} -jar server.jar nogui
else
    FORGE_JAR=$(ls forge-*.jar neoforge-*.jar 2>/dev/null | head -n 1)
    if [ -n "$FORGE_JAR" ]; then
        java -Xms1024M -Xmx{ram_alloc} -jar "$FORGE_JAR" nogui
    else
        java -Xms1024M -Xmx{ram_alloc} -jar server.jar nogui
    fi
fi
"""
        start_script.write_text(script_content, encoding="utf-8")
        start_script.chmod(0o755)

        print_success("Script start.sh creado con éxito.")
        print_success(f"¡Servidor '{server_name}' configurado en {target_dir}!")
    else:
        print_error("No se pudo descargar el archivo del servidor.")
        shutil.rmtree(target_dir, ignore_errors=True)


def manage_servers():
    print_info("--- Gestionar Servidores ---")
    if not SERVERS_DIR.exists():
        print_warning(f"No hay servidores creados en {SERVERS_DIR}.")
        return

    servers = [d.name for d in SERVERS_DIR.iterdir() if d.is_dir()]
    if not servers:
        print_warning(f"No hay servidores creados en {SERVERS_DIR}.")
        return

    print("Servidores disponibles:")
    selected_srv = prompt_select(servers, "Elige un servidor: ")
    srv_dir = SERVERS_DIR / selected_srv

    print(f"Servidor seleccionado: {selected_srv}")
    print("1) Arrancar servidor")
    print("2) Editar server.properties")
    print("3) Volver")
    
    m_choice = input("Opción: ").strip()
    if m_choice == "1":
        start_sh = srv_dir / "start.sh"
        if start_sh.exists():
            print_info(f"Iniciando servidor {selected_srv}...")
            try:
                subprocess.run(["./start.sh"], cwd=srv_dir)
            except Exception as e:
                print_error(f"Error al iniciar el servidor: {e}")
        else:
            print_error(f"No se encontró start.sh en {srv_dir}")

    elif m_choice == "2":
        props_file = srv_dir / "server.properties"
        if props_file.exists():
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(props_file)])
        else:
            print_error("No existe server.properties aún.")

    else:
        return

def manage_playit():
    from lib import playit
    print_info("--- Configurar Túnel Playit.gg ---")
    status = playit.get_status()
    print(f"Estado del túnel: {'🟢 ACTIVO' if status['running'] else '🔴 DETENIDO'}")
    if status['secret_set']:
        print("Clave secreta configurada: SÍ")
    else:
        print("Clave secreta configurada: NO")

    if status['tunnels']:
        print("Direcciones públicas activas:")
        for t in status['tunnels']:
            print(f"  👉 {t}")

    if status['claim_url']:
        print(f"\n¡Enlace de reclamación Playit!: {status['claim_url']}")

    print("\nOpciones:")
    print("1) Iniciar túnel Playit")
    print("2) Detener túnel Playit")
    print("3) Ingresar / Cambiar Clave Secreta (Secret Key)")
    print("4) Volver")

    choice = input("Opción: ").strip()
    if choice == "1":
        res = playit.start_playit()
        if res.get("success"):
            print_success(res.get("message", "Playit iniciado"))
        else:
            print_error(res.get("error", "Error al iniciar Playit"))
    elif choice == "2":
        res = playit.stop_playit()
        print_success(res.get("message", "Playit detenido"))
    elif choice == "3":
        key = input("Introduce tu Secret Key de Playit.gg: ").strip()
        playit.save_secret(key)
        print_success("Clave secreta guardada correctamente.")
    else:
        return

def main():
    SERVERS_DIR.mkdir(parents=True, exist_ok=True)
    show_banner()
    if not check_dependencies():
        sys.exit(1)
    check_java()

    while True:
        print("\n==================================")
        print("           MENÚ PRINCIPAL         ")
        print("==================================")
        print("1) Crear nuevo servidor")
        print("2) Gestionar servidores")
        print("3) Configurar Túnel Playit.gg")
        print("4) Salir")
        
        choice = input("Elige una opción: ").strip()
        if choice == "1":
            create_server()
        elif choice == "2":
            manage_servers()
        elif choice == "3":
            manage_playit()
        elif choice == "4":
            print_info("¡Hasta luego!")
            sys.exit(0)
        else:
            print_error("Opción no válida.")

if __name__ == "__main__":
    main()
