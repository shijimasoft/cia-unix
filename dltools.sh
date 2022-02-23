#!/bin/bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo " * Downloading ${BOLD}ctrtool${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v0.7/ctrtool-v0.7-macos_x86_64.zip -q
    echo " * Extracting ${BOLD}ctrtool${NORMAL}"
    unzip -qq ctrtool-v0.7-macos_x86_64.zip -d ctrtool-v0.7-macos_x86_64
    mv ctrtool-v0.7-macos_x86_64/ctrtool "$SCRIPT_DIR/ctrtool"
    echo " * Downloading ${BOLD}makerom${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v0.18/makerom-v0.18-macos_x86_64.zip -q
    echo " * Extracting ${BOLD}makerom${NORMAL}"
    unzip -qq makerom-v0.18-macos_x86_64.zip -d makerom-v0.18-macos_x86_64
    mv makerom-v0.18-macos_x86_64/makerom "$SCRIPT_DIR/makerom"

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo " * Downloading ${BOLD}ctrtool${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v0.7/ctrtool-v0.7-ubuntu_x86_64.zip -q
    echo " * Extracting ${BOLD}ctrtool${NORMAL}"
    unzip -qq ctrtool-v0.7-ubuntu_x86_64.zip -d ctrtool-v0.7-ubuntu_x86_64
    mv ctrtool-v0.7-ubuntu_x86_64/ctrtool "$SCRIPT_DIR/ctrtool"
    echo " * Downloading ${BOLD}makerom${NORMAL}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v0.18/makerom-v0.18-ubuntu_x86_64.zip -q
    echo " * Extracting ${BOLD}makerom${NORMAL}"
    unzip -qq makerom-v0.18-ubuntu_x86_64.zip -d makerom-v0.18-ubuntu_x86_64
    mv makerom-v0.18-ubuntu_x86_64/makerom "$SCRIPT_DIR/makerom"
fi

echo " * Cleaning up"
rm -rf ctrtool-v0.7-*
rm -rf makerom-v0.18-*