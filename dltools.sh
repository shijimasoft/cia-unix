#!/bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

CTRTOOL_VER=1.1.0
MAKEROM_VER=0.18.3

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo " * Downloading ${BOLD}ctrtool${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v$CTRTOOL_VER/ctrtool-v$CTRTOOL_VER-macos_x86_64.zip -q
    echo " * Extracting ${BOLD}ctrtool${NORMAL}"
    unzip -qq ctrtool-v$CTRTOOL_VER-macos_x86_64.zip -d ctrtool-v$CTRTOOL_VER-macos_x86_64
    mv ctrtool-v$CTRTOOL_VER-macos_x86_64/ctrtool "$SCRIPT_DIR/ctrtool"
    echo " * Downloading ${BOLD}makerom${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v$MAKEROM_VER/makerom-v$MAKEROM_VER-macos_x86_64.zip -q
    echo " * Extracting ${BOLD}makerom${NORMAL}"
    unzip -qq makerom-v$MAKEROM_VER-macos_x86_64.zip -d makerom-v$MAKEROM_VER-macos_x86_64
    mv makerom-v$MAKEROM_VER-macos_x86_64/makerom "$SCRIPT_DIR/makerom"

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo " * Downloading ${BOLD}ctrtool${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v$CTRTOOL_VER/ctrtool-v$CTRTOOL_VER-ubuntu_x86_64.zip -q
    echo " * Extracting ${BOLD}ctrtool${NORMAL}"
    unzip -qq ctrtool-v$CTRTOOL_VER-ubuntu_x86_64.zip -d ctrtool-v$CTRTOOL_VER-ubuntu_x86_64
    mv ctrtool-v$CTRTOOL_VER-ubuntu_x86_64/ctrtool "$SCRIPT_DIR/ctrtool"
    echo " * Downloading ${BOLD}makerom${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v$MAKEROM_VER/makerom-v$MAKEROM_VER-ubuntu_x86_64.zip -q
    echo " * Extracting ${BOLD}makerom${NORMAL}"
    unzip -qq makerom-v$MAKEROM_VER-ubuntu_x86_64.zip -d makerom-v$MAKEROM_VER-ubuntu_x86_64
    mv makerom-v$MAKEROM_VER-ubuntu_x86_64/makerom "$SCRIPT_DIR/makerom"
fi

if [[ ! -f "decrypt.py" ]]; then
    echo " * Downloading ${BOLD}decrypt.py${NORMAL}"
    wget https://raw.githubusercontent.com/shijimasoft/cia-unix/main/decrypt.py -q
fi

echo " * Cleaning up"
rm -rf ctrtool-v$CTRTOOL_VER-*
rm -rf makerom-v$MAKEROM_VER-*

chmod +x ctrtool makerom

echo
