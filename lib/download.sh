#!/bin/bash

download_vanilla() {

    echo
    echo "[1/4] Obteniendo URL de descarga..."

    URL=$(get_server_download_url "$VERSION")

    if [ -z "$URL" ] || [ "$URL" = "null" ]; then
        echo
        echo "No se pudo obtener la URL de descarga."
        return 1
    fi

    SERVER_PATH="$SERVERS_DIR/$SERVER_NAME"

    mkdir -p "$SERVER_PATH"
    mkdir -p "$SERVER_PATH/logs"

    echo
    echo "[2/4] Descargando server.jar..."

    curl -L "$URL" -o "$SERVER_PATH/$SERVER_JAR"

    echo
    echo "[3/4] Aceptando la EULA..."

    echo "eula=true" > "$SERVER_PATH/eula.txt"

    echo
    echo "[4/4] Creando start.sh..."

    cat > "$SERVER_PATH/$START_SCRIPT" << EOF
#!/bin/bash

java -Xms${RAM}G -Xmx${RAM}G -jar $SERVER_JAR nogui
EOF

    chmod +x "$SERVER_PATH/$START_SCRIPT"

    echo
    echo "=========================================="
    echo "Servidor instalado correctamente."
    echo "=========================================="

}

download_paper() {

    echo
    echo "[1/4] Obteniendo URL de descarga..."

    URL=$(get_paper_download_url "$VERSION")

    SERVER_PATH="$SERVERS_DIR/$SERVER_NAME"

    mkdir -p "$SERVER_PATH"
    mkdir -p "$SERVER_PATH/logs"

    echo
    echo "[2/4] Descargando Paper..."

    curl -L "$URL" -o "$SERVER_PATH/$SERVER_JAR"

    echo
    echo "[3/4] Aceptando la EULA..."

    echo "eula=true" > "$SERVER_PATH/eula.txt"

    echo
    echo "[4/4] Creando start.sh..."

    cat > "$SERVER_PATH/$START_SCRIPT" << EOF
#!/bin/bash

java -Xms${RAM}G -Xmx${RAM}G -jar $SERVER_JAR nogui
EOF

    chmod +x "$SERVER_PATH/$START_SCRIPT"

    echo
    echo "Paper instalado correctamente."

}

download_purpur() {

    echo
    echo "[1/4] Obteniendo URL de descarga..."

    URL=$(get_purpur_download_url "$VERSION")

    SERVER_PATH="$SERVERS_DIR/$SERVER_NAME"

    mkdir -p "$SERVER_PATH"
    mkdir -p "$SERVER_PATH/logs"

    echo
    echo "[2/4] Descargando Purpur..."

    curl -L "$URL" -o "$SERVER_PATH/$SERVER_JAR"

    echo
    echo "[3/4] Aceptando la EULA..."

    echo "eula=true" > "$SERVER_PATH/eula.txt"

    echo
    echo "[4/4] Creando start.sh..."

    cat > "$SERVER_PATH/$START_SCRIPT" << EOF
#!/bin/bash

java -Xms${RAM}G -Xmx${RAM}G -jar $SERVER_JAR nogui
EOF

    chmod +x "$SERVER_PATH/$START_SCRIPT"

    echo
    echo "Purpur instalado correctamente."

}

download_fabric() {

    echo
    echo "[1/5] Obteniendo versiones..."

    LOADER=$(get_latest_fabric_loader)
    INSTALLER=$(get_latest_fabric_installer)

    SERVER_PATH="$SERVERS_DIR/$SERVER_NAME"

    mkdir -p "$SERVER_PATH"
    mkdir -p "$SERVER_PATH/logs"

    echo
    echo "[2/5] Descargando Fabric Installer..."

    curl -L \
    "https://meta.fabricmc.net/v2/versions/loader/$VERSION/$LOADER/$INSTALLER/server/jar" \
    -o "$SERVER_PATH/$SERVER_JAR"

    echo
    echo "[3/5] Aceptando la EULA..."

    echo "eula=true" > "$SERVER_PATH/eula.txt"

    echo
    echo "[4/5] Creando start.sh..."

    cat > "$SERVER_PATH/$START_SCRIPT" << EOF
#!/bin/bash

java -Xms${RAM}G -Xmx${RAM}G -jar $SERVER_JAR nogui
EOF

    chmod +x "$SERVER_PATH/$START_SCRIPT"

    echo
    echo "[5/5] Fabric instalado correctamente."

}

download_forge() {

    echo
    echo "[1/6] Obteniendo versión de Forge..."

    FORGE_VERSION=$(get_forge_version "$VERSION")

    if [ -z "$FORGE_VERSION" ] || [ "$FORGE_VERSION" = "null" ]; then
        echo
        echo "No existe una versión recomendada de Forge para Minecraft $VERSION."
        return 1
    fi

    URL=$(get_forge_download_url "$VERSION" "$FORGE_VERSION")

    SERVER_PATH="$SERVERS_DIR/$SERVER_NAME"

    mkdir -p "$SERVER_PATH"

    echo
    echo "[2/6] Descargando Forge Installer..."

    curl -L "$URL" -o "$SERVER_PATH/forge-installer.jar"

    echo
    echo "[3/6] Instalando Forge..."

    cd "$SERVER_PATH" || return 1

    java -jar forge-installer.jar --installServer

    if [ $? -ne 0 ]; then
        echo
        echo "La instalación de Forge ha fallado."
        return 1
    fi

    echo
    echo "[4/6] Aceptando la EULA..."

    echo "eula=true" > eula.txt

    echo
    echo "[5/6] Creando start.sh..."

    cat > "$START_SCRIPT" << EOF
#!/bin/bash

cd "\$(dirname "\$0")"

chmod +x run.sh

./run.sh
EOF

    chmod +x "$START_SCRIPT"

    echo
    echo "[6/6] Forge instalado correctamente."

}

download_neoforge() {

    echo
    echo "[1/6] Obteniendo versión de NeoForge..."

    NEOFORGE_VERSION=$(get_neoforge_version "$VERSION")

    echo
    echo "Minecraft : $VERSION"
    echo "NeoForge  : $NEOFORGE_VERSION"
    echo

    if [ -z "$NEOFORGE_VERSION" ]; then
        echo
        echo "No existe una versión de NeoForge para Minecraft $VERSION."
        return 1
    fi

    URL="https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE_VERSION/neoforge-$NEOFORGE_VERSION-installer.jar"

    SERVER_PATH="$SERVERS_DIR/$SERVER_NAME"

    mkdir -p "$SERVER_PATH"

    echo
    echo "[2/6] Descargando NeoForge Installer..."

    curl -L "$URL" -o "$SERVER_PATH/neoforge-installer.jar"

    FILESIZE=$(stat -c%s "$SERVER_PATH/neoforge-installer.jar")

    echo
    echo "Tamaño del instalador: $FILESIZE bytes"

    if [ "$FILESIZE" -lt 5000000 ]; then
        echo
        echo "La descarga ha fallado."
        return 1
    fi

    echo
    echo "[3/6] Instalando NeoForge..."

    cd "$SERVER_PATH" || return 1

    java -jar neoforge-installer.jar --installServer

    if [ $? -ne 0 ]; then
        echo
        echo "La instalación de NeoForge ha fallado."
        return 1
    fi

    echo
    echo "[4/6] Aceptando la EULA..."

    echo "eula=true" > eula.txt

    echo
    echo "[5/6] Creando start.sh..."

    cat > "$START_SCRIPT" << EOF
#!/bin/bash

cd "\$(dirname "\$0")"

chmod +x run.sh

./run.sh
EOF

    chmod +x "$START_SCRIPT"

    echo
    echo "[6/6] NeoForge instalado correctamente."

}
