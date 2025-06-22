import json
import os

class CocoWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.images = []
        self.annotations = []
        self.categories = []
        self.image_id = 0
        self.annotation_id = 0
        self.class_to_id = {}

    def add_category(self, name):
        if name not in self.class_to_id:
            category_id = len(self.categories) + 1
            self.class_to_id[name] = category_id
            self.categories.append({
                "id": category_id,
                "name": name,
                "supercategory": "lego"
            })

    def add_image(self, filename, width, height):
        self.image_id += 1
        self.images.append({
            "id": self.image_id,
            "file_name": filename,
            "width": width,
            "height": height
        })
        return self.image_id

    def add_annotation(self, image_id, category_name, bbox):
        self.annotation_id += 1
        if category_name not in self.class_to_id:
            self.add_category(category_name)

        category_id = self.class_to_id[category_name]

        xmin, ymin, xmax, ymax = bbox
        width = xmax - xmin
        height = ymax - ymin
        self.annotations.append({
            "id": self.annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "bbox": [xmin, ymin, width, height],
            "area": width * height,
            "iscrowd": 0
        })

    def save(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump({
                "images": self.images,
                "annotations": self.annotations,
                "categories": self.categories
            }, f, indent=2)
