import json
import os
import sqlite3

class CocoWriter:
    def __init__(self, output_file, db_path="lego_parts.db"):
        self.output_file = output_file
        self.images = []
        self.annotations = []
        self.image_id = 0
        self.annotation_id = 0
        self.class_to_id = {}
        self.conn = sqlite3.connect(db_path)
        self.categories = []        

    def load_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("""
                       SELECT p.part_num, p.name, c.name
                       FROM parts p
                                JOIN part_categories c ON p.part_cat_id = c.id
                       """)
        
        rows = cursor.fetchall()
        for (part_num, part_name, parent_category) in rows:
            self.class_to_id[part_num] = part_num
            self.categories.append({
                "id": part_num,
                "name": part_name,  # category = part_num
                "supercategory": parent_category
            })

    def get_canonical_part_num(self, part_num):
        cursor = self.conn.cursor()
        query = """
                WITH RECURSIVE variant_chain(child, parent) AS (
                    SELECT child_part_num, parent_part_num
                    FROM part_relationships
                    WHERE child_part_num = ? AND rel_type IN ('P', 'M', 'T', 'A')

                    UNION

                    SELECT r.child_part_num, r.parent_part_num
                    FROM part_relationships r
                             JOIN variant_chain vc ON vc.parent = r.child_part_num
                    WHERE r.rel_type IN ('P', 'M', 'T', 'A')
                )
                SELECT COALESCE(MAX(parent), ?) AS canonical_part_num
                FROM variant_chain; \
                """
        cursor.execute(query, (part_num, part_num))
        result = cursor.fetchone()
        return result[0] if result else part_num

    def add_image(self, filename, width, height):
        self.image_id += 1
        image = {
            "id": self.image_id,
            "file_name": filename,
            "width": width,
            "height": height
        }
        self.images.append(image)
        return self.image_id

    def add_annotation(self, image_id, part_num, bbox):
        canonical_part = self.get_canonical_part_num(part_num)
        cursor = self.conn.cursor()
        cursor.execute("""
                       SELECT p.part_num, p.name, c.name
                       FROM parts p
                                JOIN part_categories c ON p.part_cat_id = c.id
                       WHERE p.part_num = ?
                       """, (canonical_part,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Canonical part '{canonical_part}' not found.")
    
        part_num, part_name, category_name = row
    
        if part_num not in self.class_to_id:
            # Assign a new category_id
            new_category_id = max(self.class_to_id.values(), default=0) + 1
            self.class_to_id[part_num] = new_category_id
    
            # Add new category to list
            self.categories.append({
                "id": new_category_id,
                "name": part_num,
                "supercategory": category_name  # or category_name if you want grouping
            })
    
        category_id = self.class_to_id[part_num]
    
        self.annotation_id += 1
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
        data = {
            "images": self.images,
            "annotations": self.annotations,
            "categories": self.categories
        }
    
        # Create the directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=4)