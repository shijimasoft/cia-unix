#!/bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

CTRDECRYPT_VER=1.1.0
CTRTOOL_VER=1.2.0
MAKEROM_VER=0.18.4

# Darwin
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Apple Silicon
    echo " * Downloading ${BOLD}ctrdecrypt${NORMAL}"
    wget "https://github.com/shijimasoft/ctrdecrypt/releases/download/v${CTRDECRYPT_VER}/ctrdecrypt-macos-universal.zip" -q
    echo " * Extracting ${BOLD}ctrdecrypt${NORMAL}"
    unzip -qq "ctrdecrypt-macos-universal.zip" -d "ctrdecrypt-macos-universal"
    mv "ctrdecrypt-macos-universal/ctrdecrypt" "${SCRIPT_DIR}/ctrdecrypt"
    if [[ $(uname -m) == 'arm64' ]]; then
        echo " * Downloading ${BOLD}ctrtool${NORMAL}"
        wget "https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v${CTRTOOL_VER}/ctrtool-v${CTRTOOL_VER}-macos_arm64.zip" -q
        echo " * Extracting ${BOLD}ctrtool${NORMAL}"
        unzip -qq "ctrtool-v${CTRTOOL_VER}-macos_arm64.zip" -d "ctrtool-v${CTRTOOL_VER}-macos_arm64"
        mv "ctrtool-v${CTRTOOL_VER}-macos_arm64/ctrtool" "${SCRIPT_DIR}/ctrtool"
        echo " * Downloading ${BOLD}makerom${NORMAL}"
        wget "https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v${MAKEROM_VER}/makerom-v${MAKEROM_VER}-macos_arm64.zip" -q
        echo " * Extracting ${BOLD}makerom${NORMAL}"
        unzip -qq "makerom-v${MAKEROM_VER}-macos_arm64.zip" -d "makerom-v${MAKEROM_VER}-macos_arm64"
        mv "makerom-v${MAKEROM_VER}-macos_arm64/makerom" "${SCRIPT_DIR}/makerom"
    # x86_64
    else
        echo " * Downloading ${BOLD}ctrtool${NORMAL}"
        wget "https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v${CTRTOOL_VER}/ctrtool-v${CTRTOOL_VER}-macos_x86_64.zip" -q
        echo " * Extracting ${BOLD}ctrtool${NORMAL}"
        unzip -qq "ctrtool-v${CTRTOOL_VER}-macos_x86_64.zip" -d "ctrtool-v${CTRTOOL_VER}-macos_x86_64"
        mv "ctrtool-v${CTRTOOL_VER}-macos_x86_64/ctrtool" "${SCRIPT_DIR}/ctrtool"
        echo " * Downloading ${BOLD}makerom${NORMAL}"
        wget "https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v${MAKEROM_VER}/makerom-v${MAKEROM_VER}-macos_x86_64.zip" -q
        echo " * Extracting ${BOLD}makerom${NORMAL}"
        unzip -qq "makerom-v${MAKEROM_VER}-macos_x86_64.zip" -d "makerom-v${MAKEROM_VER}-macos_x86_64"
        mv "makerom-v${MAKEROM_VER}-macos_x86_64/makerom" "${SCRIPT_DIR}/makerom"
    fi

# Linux (x86_64)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo " * Downloading ${BOLD}ctrdecrypt${NORMAL}"
    wget "https://github.com/shijimasoft/ctrdecrypt/releases/download/v${CTRDECRYPT_VER}/ctrdecrypt-linux-x86_64.zip" -q
    echo " * Extracting ${BOLD}ctrdecrypt${NORMAL}"
    unzip -qq "ctrdecrypt-linux-x86_64.zip" -d "ctrdecrypt-linux-x86_64"
    mv "ctrdecrypt-linux-x86_64/ctrdecrypt" "${SCRIPT_DIR}/ctrdecrypt"
    echo " * Downloading ${BOLD}ctrtool${NORMAL}"
    wget "https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v${CTRTOOL_VER}/ctrtool-v${CTRTOOL_VER}-ubuntu_x86_64.zip" -q
    echo " * Extracting ${BOLD}ctrtool${NORMAL}"
    unzip -qq "ctrtool-v${CTRTOOL_VER}-ubuntu_x86_64.zip" -d "ctrtool-v${CTRTOOL_VER}-ubuntu_x86_64"
    mv "ctrtool-v${CTRTOOL_VER}-ubuntu_x86_64/ctrtool" "${SCRIPT_DIR}/ctrtool"
    echo " * Downloading ${BOLD}makerom${NORMAL}"
    wget "https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v${MAKEROM_VER}/makerom-v${MAKEROM_VER}-ubuntu_x86_64.zip" -q
    echo " * Extracting ${BOLD}makerom${NORMAL}"
    unzip -qq "makerom-v${MAKEROM_VER}-ubuntu_x86_64.zip" -d "makerom-v${MAKEROM_VER}-ubuntu_x86_64"
    mv "makerom-v${MAKEROM_VER}-ubuntu_x86_64/makerom" "${SCRIPT_DIR}/makerom"
fi

if [[ ! -f "seeddb.bin" ]]; then
    echo " * Downloading ${BOLD}seeddb.bin${NORMAL}"
    wget "https://github.com/ihaveamac/3DS-rom-tools/raw/master/seeddb/seeddb.bin" -q
fi

echo " * Cleaning up"
rm -rf "ctrdecrypt-"*
rm -rf "ctrtool-v${CTRTOOL_VER}-"*
rm -rf "makerom-v${MAKEROM_VER}-"*

chmod +x ctrdecrypt ctrtool makerom

echo
