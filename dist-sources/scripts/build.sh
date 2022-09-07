#!/usr/bin/env bash

# Check if the environment is already prepared.
if [[ ! -d dependencies ]]; then
    echo "The environment is not prepared. Please run make prepare-env first."
    exit 1
fi

# This script is used to build the AppImage.
source ./dependencies/venv/bin/activate

cp ../requirements.txt ./python-appimage/requirements.txt
python-appimage build app python-appimage -p 3.10
./steam-prices-x86_64.AppImage --appimage-extract
mkdir -p squashfs-root/app/src
mkdir -p squashfs-root/app/geckodriver

pushd squashfs-root/app/geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
tar -xvf geckodriver-v0.31.0-linux64.tar.gz
rm geckodriver-v0.31.0-linux64.tar.gz
popd

cp -r ../src squashfs-root/app
ARCH=x86_64 ./dependencies/appimagetool squashfs-root
rm -rf squashfs-root

deactivate
