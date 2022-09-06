# How to make the app image

## Download the Python images

Get a Python image from [here](https://github.com/niess/python-appimage/releases)

Get the appimagetool from [here](https://github.com/AppImage/AppImageKit/releases)

## Extract the image

```bash
chmod +x <python-appimage>

./<python-appimage> --appimage-extract
```

## Install the dependencies

```bash
./squashfs-root/AppRun -m pip install -r requirements.txt
```

## Move all the files to the AppDir

> Now copy the `app`, `.desktop`, `.png`, `AppRun` files to the AppDir.

## Create the AppImage

```bash
ARCH=x86_64 appimagetool <app-folder>
```
