#!/bin/sh
set -e

if [ ! -e "$BLENDER_PATH" ]; then
    VER=$(echo "$BLENDER_VERSION" | sed -e 's/\.[0-9]*$//')
    URL="https://download.blender.org/release/Blender$VER/blender-$BLENDER_VERSION-linux-x64.tar.xz"

    echo "Downloading $URL to $BLENDER_PATH ..."
    mkdir -p "$BLENDER_PATH"
    curl -L "$URL" | tar -xJ -C "$BLENDER_PATH" --strip-components 1

    TGT="$HOME/.config/blender/$BLENDER_VERSION/scripts/addons"
    echo "Installing the Addon to $TGT ..."
    mkdir -p $TGT
    ln -s tests $TGT/

    URL="https://pypi.python.org/packages/53/fe/9e0fbdbca15c2c1253379c3a694f4315a420555e7874445b06edeaeacaea/coverage-4.2.tar.gz#md5=1e09362a3f35d589f942359441050a6e"
    TGT="$BLENDER_PATH/$VER/python/lib/python$BLENDER_PYTHON_VERSION/"
    echo "Downloading $URL to $TGT ..."
    test -d "$TGT" # assert the target is exist
    curl -L "$URL" | tar -xz
    mv coverage-4.2/coverage "$TGT"
    rm -rf coverage-4.2
fi
