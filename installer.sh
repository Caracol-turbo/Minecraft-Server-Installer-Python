#!/bin/bash

source lib/config.sh
source lib/utils.sh
source lib/api.sh
source lib/download.sh

main_menu() {

    while true
    do

        show_title

        echo "1) Vanilla"
        echo "2) Paper"
        echo "3) Purpur"
        echo "4) Fabric"
        echo "5) Forge"
        echo "6) NeoForge"
        echo "0) Salir"
        echo

        select_option 0 6

        case "$OPTION" in
            1) SOFTWARE="vanilla"; break ;;
            2) SOFTWARE="paper"; break ;;
            3) SOFTWARE="purpur"; break ;;
            4) SOFTWARE="fabric"; break ;;
            5) SOFTWARE="forge"; break ;;
            6) SOFTWARE="neoforge"; break ;;
            0) exit 0 ;;
        esac

    done

}

select_vanilla_version() {

    show_title

    echo "Versiones disponibles"
    echo

    mapfile -t VERSIONS < <(get_vanilla_versions)

    LIMIT=64

    if [ ${#VERSIONS[@]} -lt $LIMIT ]; then
        LIMIT=${#VERSIONS[@]}
    fi

    for ((i=0; i<LIMIT; i++))
    do
        printf "%2d) %s\n" $((i+1)) "${VERSIONS[$i]}"
    done

    echo

    select_option 1 "$LIMIT"

    VERSION="${VERSIONS[$((OPTION-1))]}"

}

select_paper_version() {

    show_title

    echo "Versiones de Paper"
    echo

    mapfile -t VERSIONS < <(get_paper_versions)

    LIMIT=64

    if [ ${#VERSIONS[@]} -lt $LIMIT ]; then
        LIMIT=${#VERSIONS[@]}
    fi

    for ((i=0; i<LIMIT; i++))
    do
        printf "%2d) %s\n" $((i+1)) "${VERSIONS[$i]}"
    done

    echo

    select_option 1 "$LIMIT"

    VERSION="${VERSIONS[$((OPTION-1))]}"

}

select_purpur_version() {

    show_title

    echo "Versiones de Purpur"
    echo

    mapfile -t VERSIONS < <(get_purpur_versions)

    LIMIT=64

    if [ ${#VERSIONS[@]} -lt $LIMIT ]; then
        LIMIT=${#VERSIONS[@]}
    fi

    for ((i=0; i<LIMIT; i++))
    do
        printf "%2d) %s\n" $((i+1)) "${VERSIONS[$i]}"
    done

    echo

    select_option 1 "$LIMIT"

    VERSION="${VERSIONS[$((OPTION-1))]}"

}

select_fabric_version() {

    show_title

    echo "Versiones de Fabric"
    echo

    mapfile -t VERSIONS < <(get_fabric_versions)

    LIMIT=60

    if [ ${#VERSIONS[@]} -lt $LIMIT ]; then
        LIMIT=${#VERSIONS[@]}
    fi

    for ((i=0; i<LIMIT; i++))
    do
        printf "%2d) %s\n" $((i+1)) "${VERSIONS[$i]}"
    done

    echo

    select_option 1 "$LIMIT"

    VERSION="${VERSIONS[$((OPTION-1))]}"

}

select_forge_version() {

    show_title

    echo "Versiones de Forge"
    echo

    mapfile -t VERSIONS < <(get_forge_versions)

    LIMIT=25

    if [ ${#VERSIONS[@]} -lt $LIMIT ]; then
        LIMIT=${#VERSIONS[@]}
    fi

    for ((i=0; i<LIMIT; i++))
    do
        printf "%2d) %s\n" $((i+1)) "${VERSIONS[$i]}"
    done

    echo

    select_option 1 "$LIMIT"

    VERSION="${VERSIONS[$((OPTION-1))]}"

}
select_neoforge_version() {

    show_title

    echo "Versiones de Minecraft (NeoForge)"
    echo

    mapfile -t ALL_VERSIONS < <(get_vanilla_versions)

    XML=$(curl -s https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml)

    VERSIONS=()

    for VERSION in "${ALL_VERSIONS[@]}"
    do
        PREFIX="${VERSION#1.}"

        if echo "$XML" | grep -q "<version>${PREFIX}\."; then
            VERSIONS+=("$VERSION")
        fi
    done

    LIMIT=64

    if [ ${#VERSIONS[@]} -lt $LIMIT ]; then
        LIMIT=${#VERSIONS[@]}
    fi

    for ((i=0; i<LIMIT; i++))
    do
        printf "%2d) %s\n" $((i+1)) "${VERSIONS[$i]}"
    done

    echo

    select_option 1 "$LIMIT"

    VERSION="${VERSIONS[$((OPTION-1))]}"

}

# paso de documentar cosas bro

main() {

    main_menu

    case "$SOFTWARE" in

        vanilla)

            select_vanilla_version

            echo
            read -rp "Nombre del servidor: " SERVER_NAME

            select_ram

            download_vanilla

            pause

            ;;

        paper)

            select_paper_version

            echo
            read -rp "Nombre del servidor: " SERVER_NAME

            select_ram

            download_paper

            pause

            ;;

            purpur)

    select_purpur_version

    echo
    read -rp "Nombre del servidor: " SERVER_NAME

    select_ram

    download_purpur

    pause

    ;;

    fabric)

    select_fabric_version

    echo
    read -rp "Nombre del servidor: " SERVER_NAME

    select_ram

    download_fabric

    pause

    ;;

    forge)

    select_forge_version

    echo
    read -rp "Nombre del servidor: " SERVER_NAME

    select_ram

    download_forge

    pause

    ;;

    neoforge)

    select_neoforge_version

    echo
    read -rp "Nombre del servidor: " SERVER_NAME

    select_ram

    download_neoforge

    pause

    ;;

        *)

            echo
            echo "Ese software todavía no está implementado."

            pause

            ;;

    esac

}

main
