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

    URL="https://files.pythonhosted.org/packages/74/fb/f481628033d42f6f6021af8a9a13d913707221e139567f39b09b337421b9/coverage-6.3.2.tar.gz"
    TGT="$BLENDER_PATH/$VER/python/lib/python$BLENDER_PYTHON_VERSION/"
    echo "Downloading $URL to $TGT ..."
    test -d "$TGT" # assert the target is exist
    curl -L "$URL" | tar -xz
    mv coverage-6.3.2/coverage "$TGT"
    rm -rf coverage-6.3.2
fi
