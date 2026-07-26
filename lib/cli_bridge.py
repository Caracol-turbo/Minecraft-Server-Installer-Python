import sys
import json
from pathlib import Path

# Agregar directorio raíz a sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from lib import api, download, playit
from lib.config import SERVERS_DIR

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)

    action = sys.argv[1]

    if action == "get_vanilla_versions":
        res = api.get_vanilla_versions()
        print(json.dumps(res))

    elif action == "get_paper_versions":
        res = api.get_paper_versions()
        print(json.dumps(res))

    elif action == "get_paper_builds":
        version = sys.argv[2] if len(sys.argv) > 2 else ""
        res = api.get_paper_builds(version)
        print(json.dumps(res))

    elif action == "get_purpur_versions":
        res = api.get_purpur_versions()
        print(json.dumps(res))

    elif action == "get_purpur_builds":
        version = sys.argv[2] if len(sys.argv) > 2 else ""
        res = api.get_purpur_builds(version)
        print(json.dumps(res))

    elif action == "get_fabric_versions":
        gver = api.get_fabric_game_versions()
        lver = api.get_fabric_loader_versions()
        iver = api.get_fabric_installer_versions()
        print(json.dumps({
            "game_versions": gver,
            "loader_versions": lver,
            "installer_versions": iver
        }))

    elif action == "get_forge_versions":
        res = api.get_forge_versions()
        print(json.dumps(res))

    elif action == "get_forge_builds":
        version = sys.argv[2] if len(sys.argv) > 2 else ""
        res = api.get_forge_builds(version)
        print(json.dumps(res))

    elif action == "get_neoforge_versions":
        res = api.get_neoforge_versions()
        print(json.dumps(res))

    elif action == "playit_status":
        res = playit.get_status()
        print(json.dumps(res))

    elif action == "playit_start":
        secret = sys.argv[2] if len(sys.argv) > 2 else None
        res = playit.start_playit(secret)
        print(json.dumps(res))

    elif action == "playit_stop":
        res = playit.stop_playit()
        print(json.dumps(res))

    elif action == "playit_save_secret":
        secret = sys.argv[2] if len(sys.argv) > 2 else ""
        ok = playit.save_secret(secret)
        print(json.dumps({"success": ok}))

    elif action == "create_server":
        # Argumentos: server_name, software, version, build/extra, ram
        if len(sys.argv) < 6:
            print(json.dumps({"success": False, "error": "Argumentos insuficientes"}))
            sys.exit(1)

        server_name = sys.argv[2]
        software = sys.argv[3]
        version = sys.argv[4]
        extra = sys.argv[5]  # build o loader_ver/forge build
        ram = sys.argv[6] if len(sys.argv) > 6 else "2G"

        target_dir = SERVERS_DIR / server_name
        if target_dir.exists():
            print(json.dumps({"success": False, "error": f"El servidor '{server_name}' ya existe."}))
            return

        target_dir.mkdir(parents=True, exist_ok=True)
        server_jar = target_dir / "server.jar"

        ok = False
        if software == "vanilla":
            ok = download.download_vanilla(version, server_jar)
        elif software == "paper":
            ok = download.download_paper(version, extra, server_jar)
        elif software == "purpur":
            ok = download.download_purpur(version, extra, server_jar)
        elif software == "fabric":
            parts = extra.split(":")
            loader_v = parts[0] if len(parts) > 0 else ""
            inst_v = parts[1] if len(parts) > 1 else ""
            ok = download.download_fabric(version, loader_v, inst_v, server_jar)
        elif software == "forge":
            ok = download.download_forge(version, extra, target_dir)
        elif software == "neoforge":
            ok = download.download_neoforge(version, target_dir)

        if ok:
            eula_file = target_dir / "eula.txt"
            eula_file.write_text("eula=true\n", encoding="utf-8")

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
        echo "-Xms1024M -Xmx{ram}" >> user_jvm_args.txt
    fi
    bash run.sh nogui
elif [ -f server.jar ]; then
    java -Xms1024M -Xmx{ram} -jar server.jar nogui
else
    FORGE_JAR=$(ls forge-*.jar neoforge-*.jar 2>/dev/null | head -n 1)
    if [ -n "$FORGE_JAR" ]; then
        java -Xms1024M -Xmx{ram} -jar "$FORGE_JAR" nogui
    else
        java -Xms1024M -Xmx{ram} -jar server.jar nogui
    fi
fi
"""
            start_script.write_text(script_content, encoding="utf-8")
            start_script.chmod(0o755)

            print(json.dumps({"success": True, "message": f"Servidor {server_name} ({software.capitalize()}) creado con éxito."}))
        else:
            if target_dir.exists():
                import shutil
                shutil.rmtree(target_dir, ignore_errors=True)
            print(json.dumps({"success": False, "error": "Fallo al descargar los archivos del servidor."}))


    else:
        print(json.dumps({"error": f"Acción desconocida: {action}"}))

if __name__ == "__main__":
    main()
