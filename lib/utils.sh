#!/bin/bash

clear_screen() {
    clear
}

pause() {
    echo
    read -rp "Pulsa ENTER para continuar..."
}

show_title() {

    clear_screen

    echo "=========================================="
    echo "      Minecraft Server Installer"
    echo "=========================================="
    echo

}

show_error() {

    echo
    echo "[ERROR] $1"
    pause

}

show_success() {

    echo
    echo "[OK] $1"
    pause

}

select_option() {

    local MIN=$1
    local MAX=$2

    while true
    do
        read -rp "Opción: " OPTION

        if [[ "$OPTION" =~ ^[0-9]+$ ]] && [ "$OPTION" -ge "$MIN" ] && [ "$OPTION" -le "$MAX" ]; then
            return 0
        fi

        echo
        echo "Opción no válida."
        echo

    done

}

select_ram() {

    while true
    do

        echo
        read -rp "RAM para el servidor (GB): " RAM

        if [[ "$RAM" =~ ^[0-9]+$ ]] && [ "$RAM" -ge "$MIN_RAM" ] && [ "$RAM" -le "$MAX_RAM" ]; then
            return 0
        fi

        echo
        echo "Introduce un valor entre $MIN_RAM y $MAX_RAM GB."

    done

}
