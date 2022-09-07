#!/usr/bin/env bash

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
