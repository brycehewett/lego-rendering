import os
import shutil
import random
from collections import defaultdict

def create_yaml(part_names, yaml_path="dataset/lego.yaml", val_path="images/val", train_path="images/train"):
    os.makedirs(os.path.dirname(yaml_path), exist_ok=True)  # ensure directory exists
    with open(yaml_path, "w") as f:
        f.write(f"train: {train_path}\n")
        f.write(f"val: {val_path}\n\n")
        f.write(f"nc: {len(part_names)}\n")
        f.write("names: [")
        f.write(", ".join(f"'{name}'" for name in part_names))
        f.write("]\n")

    print(f"[OK] Wrote YOLO dataset config to: {yaml_path}")

def write_label_file(filename, bounding_box, class_id=0):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # ensure directory exists

    with open(filename, "w") as f:
        f.write(f"{class_id} {bounding_box[0]:.3f} {bounding_box[1]:.3f} {bounding_box[2]:.3f} {bounding_box[3]:.3f}\n")
    print(f"[OK] Wrote label to: {filename}")

def split_lego_dataset(images_dir, labels_dir, output_dir, val_ratio=0.2, seed=42):
    random.seed(seed)
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png'))]
    label_map = defaultdict(list)

    # Group images by class (based on YOLO .txt label files)
    for img_file in image_files:
        label_file = os.path.splitext(img_file)[0] + ".txt"
        label_path = os.path.join(labels_dir, label_file)
        if not os.path.exists(label_path):
            continue

        with open(label_path) as f:
            class_ids = {line.split()[0] for line in f.readlines() if line.strip()}
            for class_id in class_ids:
                label_map[class_id].append(img_file)

    train_set = set()
    val_set = set()

    # Stratified split by class
    for class_id, files in label_map.items():
        random.shuffle(files)
        val_count = max(1, int(len(files) * val_ratio))
        val_set.update(files[:val_count])
        train_set.update(files[val_count:])

    def copy_split(image_list, split):
        img_out = os.path.join(output_dir, 'images', split)
        lbl_out = os.path.join(output_dir, 'labels', split)
        os.makedirs(img_out, exist_ok=True)
        os.makedirs(lbl_out, exist_ok=True)

        for img_file in image_list:
            label_file = os.path.splitext(img_file)[0] + '.txt'
            shutil.copy(os.path.join(images_dir, img_file), os.path.join(img_out, img_file))
            shutil.copy(os.path.join(labels_dir, label_file), os.path.join(lbl_out, label_file))

    copy_split(train_set, 'train')
    copy_split(val_set, 'val')

    print(f"Split complete: {len(train_set)} train, {len(val_set)} val")

