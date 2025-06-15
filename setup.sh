#!/bin/bash

set -euo pipefail

echo ">>> Starting Blender setup at $(date)"

# Set Blender paths
BLENDER_PATH=$(which blender)

echo ">>> Blender binary: $BLENDER_PATH"
BLENDER_PYTHON=$($BLENDER_PATH --background --python-expr "import sys; print(sys.executable)")
echo ">>> Blender Python path: $BLENDER_PYTHON"

if [ ! -d "./ldraw" ]; then
    echo ">>> 'ldraw' folder not found. Downloading LDraw data..."

    mkdir -p ./temp
    mkdir -p ./ldraw/unofficial

    echo ">>> Downloading LDraw complete.zip"
    curl -L -o ./temp/complete.zip "https://library.ldraw.org/library/updates/complete.zip"

    echo ">>> Downloading LDraw unofficial.zip"
    curl -L -o ./temp/unofficial.zip "https://library.ldraw.org/library/unofficial/ldrawunf.zip"

    echo ">>> Unzipping LDraw libraries"
    unzip -o ./temp/complete.zip -d ./
    unzip -o ./temp/unofficial.zip -d ./ldraw/unofficial
    
    #Remove unsupported materials
    grep -Ev 'MATERIAL (FABRIC)' ./ldraw/LDConfig.ldr > ./ldraw/LDConfig.tmp && mv ./ldraw/LDConfig.tmp ./ldraw/LDConfig.ldr
    grep -Ev 'MATERIAL (FABRIC)' ./ldraw/LDCfgalt.ldr > ./ldraw/LDCfgalt.tmp && mv ./ldraw/LDCfgalt.tmp ./ldraw/LDCfgalt.ldr

else
    echo ">>> 'ldraw' folder already exists. Skipping downloads."
fi

# Run Blender setup script
echo ">>> Running setup.py in Blender"
"$BLENDER_PATH" --background --python ./setup.py

echo ">>> Cleaning up temp files"
rm -rf ./temp

echo ">>> Setup complete at $(date)"
