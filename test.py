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

def get_parts(part_count = 20):
    cursor = conn.cursor()
    query = """SELECT * FROM parts_popular LIMIT 20"""
    cursor.execute(query)
    result = cursor.fetchall()[0]
    cursor.close()
    return result

db_path = "lego_parts.db"
conn = sqlite3.connect(db_path)
parts = get_parts()
renderer = Renderer(ldraw_path="./ldraw")

for part in parts:
    print(part)
    color = RebrickableColors.Purple.value

    options = RenderOptions(
        image_filename = f"renders/{part}.png",
        bounding_box_filename = f"renders/{part}.txt",
        blender_filename = f"renders/{part}.blend",
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
