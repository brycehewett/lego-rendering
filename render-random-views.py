import copy
import random
import traceback
import bpy
import sys
import os
import csv

# This script runs under Blender's python environment. Add the current
# directly to the path so we can import our own modules
dir_path = os.path.dirname(os.path.realpath(__file__))
print(f"Prepending {dir_path} to Python path...")
sys.path.insert(0, dir_path)

from lib.renderer.dat import ldraw_dat_exists
from lib.renderer.renderer import Renderer
from lib.renderer.render_options import Material, RenderOptions, Quality, LightingStyle, Look, Format
from lib.colors import RebrickableColors, random_color_from_ids

classifed_parts_csv_file = '../lego-inventory/tag-v3.csv'
other_parts_csv_file = '../lego-inventory/sorter-2500.csv'
RENDER_DIR ="./renders/random-views"
NUM_IMAGES_PER_CLASSIFED_PART = 50
NUM_IMAGES_PER_OTHER_PART = 5
NUM_IMAGES_OVERRIDES = {
  "3048a": 250,
  "43722": 250,
  "98138pr0027": 250,
  "98138pr0013": 250,
  "93095": 250,
  "53540": 250,
  "99207": 250,
  "98138pr0018": 250,
  "99207": 250,
  "98138pr0008": 250,
  "24246": 250,
  "2432": 250,
  "98138pr0022": 250,
  "39739": 250
}

def read_csv_file(csv_file_path):
  rows = []
  with open(csv_file_path, mode='r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      for row in csv_reader:
          canonical_part_num = row['canonical_part_num']
          ldraw_id = row['ldraw_id']
          color_ids = [int(color_id.strip()) for color_id in row['color_ids'].split(",")]
          material_id = row['material_id']
          rows.append((canonical_part_num, ldraw_id, color_ids, material_id))
  return rows

def calculate_items_to_render(rows, num_images_per_part):
    items = []
    for (part_num, ldraw_id, color_ids, material_id) in rows:
      if ldraw_id in ("70501a", "109481"):
        print(f"------ WARNING: Skipping {part_num}, problem with LDraw file")
        continue

      if not ldraw_dat_exists(ldraw_id):
        print(f"------ WARNING: Skipping {part_num}, LDraw file does not exist")
        continue

      num_images = NUM_IMAGES_OVERRIDES[part_num] if part_num in NUM_IMAGES_OVERRIDES else num_images_per_part
      for i in range(num_images):
        base_options = RenderOptions(
            format = Format.JPEG,
            lighting_style = LightingStyle.DEFAULT,
            look=Look.NORMAL,
            width=224,
            height=224,
        )

        image_filename = os.path.join(RENDER_DIR, str(part_num), f"{part_num}_random{i:02}.jpg")
        label_filename = os.path.join(RENDER_DIR, str(part_num), f"{part_num}_random{i:02}.txt")
        if os.path.exists(image_filename) and os.path.exists(label_filename):
          print(f"------ Skipping {image_filename}, already exists")
          continue

        color = random_color_from_ids(color_ids)
        material = Material.TRANSPARENT if color.is_transparent else material_id

        options = copy.copy(base_options)
        options.image_filename = image_filename
        options.label_filename = label_filename
        options.quality = Quality.NORMAL
        options.light_angle = random.uniform(0, 360)
        options.part_rotation = (random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))
        options.camera_height = random.uniform(15, 90)
        options.zoom=random.uniform(.99, 1.0)
        options.part_color = color.best_hex
        options.material = material

        items.append((i, options, ldraw_id))

    random.shuffle(items)
    return sorted(items, key=lambda x: x[0])

os.makedirs(RENDER_DIR, exist_ok=True)
renderer = Renderer(ldraw_path="./ldraw")
rows = read_csv_file(classifed_parts_csv_file)
items = calculate_items_to_render(rows, NUM_IMAGES_PER_CLASSIFED_PART)
rows = read_csv_file(other_parts_csv_file)
items += calculate_items_to_render(rows, NUM_IMAGES_PER_OTHER_PART)

print(f"------ {len(items)} images to render")

for (i, options, ldraw_id) in items:
  try:
    # Check filesystem again in case another process is rendering as well
    if os.path.exists(options.image_filename) and os.path.exists(options.label_filename):
      print(f"------ Skipping {options.image_filename}, already exists")
      continue
    if os.path.exists(options.image_filename) and not os.path.exists(options.label_filename):
      print(f"------ Regenerating {options.image_filename} with bounding box")
      os.remove(options.image_filename)

    print(f"------ Rendering {options.image_filename}...")
    renderer.render_part(ldraw_id, options)
  except Exception as e:
    print(f"------ ERROR: {options.image_filename} failed to render: {e}")
    traceback.print_exc()
    continue
