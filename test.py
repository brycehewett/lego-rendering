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
from lib.renderer.render_options import RenderOptions, Quality, LightingStyle, Look, Material
from lib.colors import RebrickableColors

renderer = Renderer(ldraw_path="./ldraw", annotation_path = "./dataset/annotations/instances_test.json")

color = RebrickableColors.Purple.value

part = 3001

options = RenderOptions(
    image_filename = f"dataset/test-images/{part}.png",
    blender_filename = f"dataset/test-images/{part}.blend",
    quality = Quality.NORMAL,
    lighting_style = LightingStyle.DEFAULT,
    part_color = color.best_hex,
    material = Material.TRANSPARENT if color.is_transparent else Material.PLASTIC,
    light_angle = 160,
    part_rotation=(0, 0, random.uniform(0, 360)),
    camera_height=50,
    zoom=1,
    look=Look.NORMAL,
    width=244,
    height=244,
)

renderer.render_part(part, options)

renderer.coco_writer.save()