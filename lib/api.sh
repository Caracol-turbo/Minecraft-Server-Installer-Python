#!/bin/bash

MOJANG_MANIFEST_URL="https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

PAPER_API="https://fill.papermc.io/v3"
USER_AGENT="MinecraftServerInstaller/1.0 (https://github.com/TU_USUARIO/MinecraftServerInstaller)"

get_manifest() {

    curl -s "$MOJANG_MANIFEST_URL"

}

get_vanilla_versions() {

    get_manifest | jq -r '.versions[] | select(.type=="release") | .id'

}

get_version_json_url() {

    local VERSION="$1"

    get_manifest | jq -r \
        --arg VERSION "$VERSION" \
        '.versions[] | select(.id==$VERSION) | .url'

}

get_server_download_url() {

    local VERSION="$1"

    local VERSION_JSON_URL

    VERSION_JSON_URL=$(get_version_json_url "$VERSION")

    curl -s "$VERSION_JSON_URL" | jq -r '.downloads.server.url'

}

####################################
# Paper
####################################

get_paper_versions() {

    curl -s \
        -H "User-Agent: $USER_AGENT" \
        "$PAPER_API/projects/paper" \
    | jq -r '.versions | to_entries[] | .value[]'

}

get_paper_download_url() {

    local VERSION="$1"

    curl -s \
        -H "User-Agent: $USER_AGENT" \
        "$PAPER_API/projects/paper/versions/$VERSION/builds" \
    | jq -r 'first(.[] | select(.channel=="STABLE") | .downloads."server:default".url)'

}

####################################
# Purpur
####################################

get_purpur_versions() {

    curl -s https://api.purpurmc.org/v2/purpur \
    | jq -r '.versions[]' \
    | tac

}

get_latest_purpur_build() {

    local VERSION="$1"

    curl -s "https://api.purpurmc.org/v2/purpur/$VERSION" \
    | jq -r '.builds.latest'

}

get_purpur_download_url() {

    local VERSION="$1"

    local BUILD

    BUILD=$(get_latest_purpur_build "$VERSION")

    echo "https://api.purpurmc.org/v2/purpur/$VERSION/$BUILD/download"

}

####################################
# Fabric
####################################

get_fabric_versions() {

    curl -s https://meta.fabricmc.net/v2/versions/game \
    | jq -r '.[] | select(.stable == true) | .version'

}

get_latest_fabric_loader() {

    curl -s https://meta.fabricmc.net/v2/versions/loader \
    | jq -r '.[0].version'

}

get_latest_fabric_installer() {

    curl -s https://meta.fabricmc.net/v2/versions/installer \
    | jq -r '.[0].version'

}

####################################
# Forge
####################################

FORGE_PROMOTIONS="https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"

get_forge_versions() {

    curl -s "$FORGE_PROMOTIONS" \
    | jq -r '.promos
        | to_entries[]
        | select(.key | endswith("-recommended"))
        | .key
        | sub("-recommended$"; "")' \
    | sort -Vr

}

get_forge_version() {

    local VERSION="$1"

    curl -s "$FORGE_PROMOTIONS" \
    | jq -r --arg VERSION "$VERSION" \
    '.promos[$VERSION + "-recommended"]'

}

get_forge_download_url() {

    local MC_VERSION="$1"
    local FORGE_VERSION="$2"

    echo "https://maven.minecraftforge.net/net/minecraftforge/forge/${MC_VERSION}-${FORGE_VERSION}/forge-${MC_VERSION}-${FORGE_VERSION}-installer.jar"

}

####################################
# NeoForge
####################################


get_neoforge_versions() {

    curl -s https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml \
    | grep "<version>" \
    | sed -E 's/.*<version>(.*)<\/version>.*/\1/' \
    | grep -v "beta" \
    | cut -d. -f1,2 \
    | sed 's/^/1./' \
    | sort -Vu

}

get_neoforge_version() {

    local MC_VERSION="$1"
    local PREFIX="${MC_VERSION#1.}"

    curl -s https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml \
    | grep "<version>" \
    | sed -E 's/.*<version>(.*)<\/version>.*/\1/' \
    | grep "^${PREFIX}\." \
    | grep -v "beta" \
    | sort -V \
    | tail -n1

}
