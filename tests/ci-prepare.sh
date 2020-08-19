#!/bin/sh
set -e

DIR="blender/$BLENDER_VERSION"
if [ ! -e "$DIR/blender" ]; then
    PYTHON_VERSION="3.7"
    ARC="blender-$BLENDER_VERSION.4-linux64.tar.xz"

    mkdir -p "$DIR"
    wget "http://download.blender.org/release/Blender$BLENDER_VERSION/$ARC"
    tar xf $ARC -C "$DIR" --strip-components 1

    TGT="$HOME/.config/blender/$BLENDER_VERSION/scripts/addons"
    mkdir -p $TGT
    ln -s animation_retarget.py $TGT/

    wget https://pypi.python.org/packages/53/fe/9e0fbdbca15c2c1253379c3a694f4315a420555e7874445b06edeaeacaea/coverage-4.2.tar.gz#md5=1e09362a3f35d589f942359441050a6e
    tar zxf coverage-4.2.tar.gz
    mv coverage-4.2/coverage "$DIR/$BLENDER_VERSION/python/lib/python$PYTHON_VERSION/"
    rm -rf coverage-4.2
fi
