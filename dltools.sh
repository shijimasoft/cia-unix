#!/bin/bash
bold=$(tput bold)
normal=$(tput sgr0)

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo " * Downloading ${bold}ctrtool${normal}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v0.7/ctrtool-v0.7-macos_x86_64.zip -q
    echo " * Extracting ${bold}ctrtool${normal}"
    unzip -qq ctrtool-v0.7-macos_x86_64.zip -d ctrtool-v0.7-macos_x86_64
    mv ctrtool-v0.7-macos_x86_64/ctrtool $(cd "$(dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)/ctrtool
    echo " * Downloading ${bold}makerom${normal}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v0.18/makerom-v0.18-macos_x86_64.zip -q
    echo " * Extracting ${bold}makerom${normal}"
    unzip -qq makerom-v0.18-macos_x86_64.zip -d makerom-v0.18-macos_x86_64
    mv makerom-v0.18-macos_x86_64/makerom $(cd "$(dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)/makerom
    
    echo " * Cleaning up"
    rm -rf ctrtool-v0.7-macos_x86_64.zip ctrtool-v0.7-macos_x86_64
    rm -rf makerom-v0.18-macos_x86_64.zip makerom-v0.18-macos_x86_64

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo " * Downloading ${bold}ctrtool${normal}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v0.7/ctrtool-v0.7-ubuntu_x86_64.zip -q
    echo " * Extracting ${bold}ctrtool${normal}"
    unzip -qq ctrtool-v0.7-ubuntu_x86_64.zip -d ctrtool-v0.7-ubuntu_x86_64
    mv ctrtool-v0.7-ubuntu_x86_64/ctrtool $(cd "$(dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)/ctrtool
    echo " * Downloading ${bold}makerom${normal}"
    wget https://github.com/3DSGuy/Project_CTR/releases/download/makerom-v0.18/makerom-v0.18-ubuntu_x86_64.zip -q
    echo " * Extracting ${bold}makerom${normal}"
    unzip -qq makerom-v0.18-ubuntu_x86_64.zip -d makerom-v0.18-ubuntu_x86_64
    mv makerom-v0.18-ubuntu_x86_64/makerom $(cd "$(dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)/makerom

    echo " * Cleaning up"
    rm -rf ctrtool-v0.7-ubuntu_x86_64.zip ctrtool-v0.7-ubuntu_x86_64
    rm -rf makerom-v0.18-ubuntu_x86_64.zip makerom-v0.18-ubuntu_x86_64
fi