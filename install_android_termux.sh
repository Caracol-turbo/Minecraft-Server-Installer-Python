#!/usr/bin/env bash
# =========================================================
# Script de instalación y ejecución para Android (Termux)
# =========================================================

set -e

echo "======================================================"
echo "  Instalador de Minecraft Server Manager para Android"
echo "======================================================"
echo ""

# 1. Actualizar paquetes e instalar dependencias básicas
echo "[1/4] Actualizando paquetes e instalando Python, OpenJDK y Node.js..."
pkg update -y
pkg install -y python nodejs-lts openjdk-21 git wget curl

# 2. Configurar permisos de almacenamiento en Android (si es necesario)
echo "[2/4] Solicitando permisos de almacenamiento..."
termux-setup-storage || true

# 3. Dar permisos de ejecución a las herramientas del proyecto
echo "[3/4] Configurando permisos de ejecución del proyecto..."
chmod +x installer.py lib/*.sh start.sh 2>/dev/null || true

echo "[4/4] ¡Instalación en Android completada con éxito!"
echo ""
echo "======================================================"
echo " Opciones de inicio en tu dispositivo Android:"
echo " 1) Modo Consola Interactiva:"
echo "    python3 installer.py"
echo ""
echo " 2) Modo Panel Web (Abre localhost:3000 en el navegador):"
echo "    node server.js"
echo "======================================================"
