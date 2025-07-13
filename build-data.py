import random
from time import sleep
import sys
import os
import itertools
import random

# This script runs under Blender's python environment. Add the current
# directly to the path so we can import our own modules
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Prepending {dir_path} to Python path...")
sys.path.insert(0, dir_path)

from lib.renderer.renderer import Renderer
from lib.renderer.render_options import RenderOptions, Quality, LightingStyle, Look, Material
from lib.renderer.render_options import BackgroundType
from lib.db_functions import * 
from lib.annotation_writer import *

parts = get_parts(30)
renderer = Renderer()

background_distribution = {
    BackgroundType.WHITE: 50,
    BackgroundType.IMAGE: 50,
}

background_types = list(background_distribution.keys())
weights = list(background_distribution.values())

create_yaml(parts)

# Define the rotation ranges for training data (you can tweak step values as needed)
x_angles = range(0, 360, 90)  # 0, 90, 180, 270
y_angles = range(0, 360, 90)
z_angles = range(0, 360, 90)  # Or use random.uniform(0, 360) if you want randomness

for partIndex, part in enumerate(parts):
    print(f"Rendering {part}...")
    # Iterate over combinations of angles
    for variantIndex, (x, y, z) in enumerate(itertools.product(x_angles, y_angles, z_angles)):
        background_type = random.choices(background_types, weights=weights)[0]
        db_part_color = get_random_color_for_part(part)

        if db_part_color is None:
            print(f"Skipping part {part} due to no color found.")
            continue
    
        color = f"{db_part_color[0]}"
        is_transparent = db_part_color[1].lower() == "true"

        options = RenderOptions(
            image_filename = f"dataset/all_images/{part}_{variantIndex}.png",
            label_filename = f"dataset/all_labels/{part}_{variantIndex}.txt",
            part_class_id=partIndex,
            quality = Quality.NORMAL,
            lighting_style = random.choices([LightingStyle.DEFAULT, LightingStyle.HARD], [72, 25])[0],
            part_color = color,
            material = Material.TRANSPARENT if is_transparent else Material.PLASTIC,
            light_angle = random.uniform(0, 360),
            part_rotation=(x, y, z),
            camera_height=random.uniform(15, 90),
            background_type = background_type
        )

        renderer.render_part(part, options)

split_lego_dataset(
    images_dir='dataset/all_images/',
    labels_dir='dataset/all_labels/',
    output_dir='dataset/',
    val_ratio=0.15  # 15% validation
)