#!/bin/bash
#TODO: Move downloads and setup scripts to python
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
    mkdir -p ./rebrickable-data

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
    echo ">>> 'ldraw' folder already exists. Skipping Ldraw downloads."
fi

if [ ! -f "lego_parts.db" ]; then
    echo ">>> 'lego-data' folder not found. Downloading Lego data..."
    # see https://rebrickable.com/downloads/
    mkdir -p ./temp/rebrickable

    echo ">>> Downloading Lego category data"
    curl -L -o ./temp/rebrickable/themes.csv.zip "https://cdn.rebrickable.com/media/downloads/themes.csv.zip"
    curl -L -o ./temp/rebrickable/colors.csv.zip "https://cdn.rebrickable.com/media/downloads/colors.csv.zip"
    curl -L -o ./temp/rebrickable/part_categories.csv.zip "https://cdn.rebrickable.com/media/downloads/part_categories.csv.zip"
    curl -L -o ./temp/rebrickable/parts.csv.zip "https://cdn.rebrickable.com/media/downloads/parts.csv.zip"
    curl -L -o ./temp/rebrickable/part_relationships.csv.zip "https://cdn.rebrickable.com/media/downloads/part_relationships.csv.zip"
    curl -L -o ./temp/rebrickable/elements.csv.zip "https://cdn.rebrickable.com/media/downloads/elements.csv.zip"
    curl -L -o ./temp/rebrickable/sets.csv.zip "https://cdn.rebrickable.com/media/downloads/sets.csv.zip"
    curl -L -o ./temp/rebrickable/minifigs.csv.zip "https://cdn.rebrickable.com/media/downloads/minifigs.csv.zip"

    echo ">>> Unzipping lego category data"
    unzip -o ./temp/rebrickable/themes.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/colors.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/part_categories.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/parts.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/part_relationships.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/elements.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/sets.csv.zip -d ./temp/rebrickable
    unzip -o ./temp/rebrickable/minifigs.csv.zip -d ./temp/rebrickable

else
    echo ">>> 'lego_parts.db' already exists. Skipping Lego data downloads."
fi

# Run Blender setup script
echo ">>> Running setup.py in Blender"
"$BLENDER_PATH" --background --python ./setup.py

if [ ! -f "lego_parts.db" ]; then
  "$BLENDER_PATH" --background --python ./setup_sqlite.py
fi

echo ">>> Cleaning up temp files"
rm -rf ./temp

echo ">>> Setup complete at $(date)"
