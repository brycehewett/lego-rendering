import random
import sqlite3
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
from lib.colors import RebrickableColors

def get_parts(part_count = 20):
    cursor = conn.cursor()
    query = """SELECT * FROM parts_popular LIMIT 1"""
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def get_random_color_for_part(part_num):
    cursor = conn.cursor()
    query = """
            SELECT c.rgb, c.is_trans
            FROM elements e
                     JOIN colors c ON e.color_id = c.id
            WHERE e.part_num = ?
            GROUP BY c.rgb
            ORDER BY RANDOM()
                LIMIT 1; \
            """
    cursor.execute(query, (part_num,))
    result = cursor.fetchone()
    cursor.close()
    return result  # Example: (3, "Red")


db_path = "lego_parts.db"
conn = sqlite3.connect(db_path)
parts = get_parts()
renderer = Renderer(ldraw_path="./ldraw")

# Define the rotation ranges for training data (you can tweak step values as needed)
x_angles = range(0, 360, 90)  # 0, 90, 180, 270
y_angles = range(0, 360, 90)
z_angles = range(0, 360, 90)  # Or use random.uniform(0, 360) if you want randomness

for part in parts:
    part_id = part[0]
    # Iterate over combinations of angles
    for i, (x, y, z) in enumerate(itertools.product(x_angles, y_angles, z_angles)):
        db_part_color = get_random_color_for_part(part_id)

        if db_part_color is None:
            print(f"Skipping part {part_id} due to no color found.")
            continue
    
        color = f"{db_part_color[0]}"
        is_transparent = db_part_color[1].lower() == "true"

        print(f"COLOR: {color}")
        print(f"Transparent: {is_transparent}")
        
        options = RenderOptions(
            image_filename = f"dataset/images/{part_id}_{i}.png",
            quality = Quality.NORMAL,
            lighting_style = LightingStyle.DEFAULT,
            part_color = color,
            material = Material.TRANSPARENT if is_transparent else Material.PLASTIC,
            light_angle = 160,
            part_rotation=(x, y, z),
            camera_height=50,
            zoom=1,
            look=Look.NORMAL,
            width=244,
            height=244,
        )

        renderer.render_part(part_id, options)
        
    renderer.coco_writer.save()

