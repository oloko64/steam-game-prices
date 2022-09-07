#!/usr/bin/env bash

# Check if the environment is already prepared.
if [[ -d dependencies ]]; then
    echo "The environment is already prepared. Recreating it..."
    sleep 2
    rm -rf ./dependencies
fi

# This script is used to prepare the environment for the build process.
mkdir dependencies
cd dependencies
wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
mv appimagetool-x86_64.AppImage appimagetool
python3 -m venv venv
source venv/bin/activate
pip install python-appimage
deactivate
