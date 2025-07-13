import random
import sqlite3
from time import sleep
import sys
import os

# This script runs under Blender's python environment. Add the current
# directly to the path so we can import our own modules
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Prepending {dir_path} to Python path...")
sys.path.insert(0, dir_path)

from lib.renderer.renderer import Renderer
from lib.renderer.render_options import *
from lib.colors import RebrickableColors
from lib.db_functions import *
from lib.annotation_writer import *

renderer = Renderer()
part_id = "4282"

db_part_color = get_random_color_for_part(part_id)

if db_part_color is None:
    print(f"Skipping part {part_id} due to no color found.")

color = f"{db_part_color[0]}"
is_transparent = db_part_color[1].lower() == "true"

create_yaml([part_id])

options = RenderOptions(
    image_filename = f"dataset/images/test/{part_id}.png",
    label_filename = f"dataset/labels/test/{part_id}.txt",
    blender_filename = f"dataset/images/test/{part_id}.blend",
    quality = Quality.NORMAL,
    lighting_style = LightingStyle.DEFAULT,
    part_color = color,
    material = Material.TRANSPARENT if is_transparent else Material.PLASTIC,
    light_angle = 160,
    part_rotation=(0, 0, random.uniform(0, 360)),
    camera_height=50,
    background_type=BackgroundType.IMAGE,
    zoom=1
)

renderer.render_part(part_id, options)