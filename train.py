from ultralytics import YOLO
import os
import subprocess

# === Configuration ===

# Path to your dataset directory
dataset_path = "dataset"  # Update this!

# Path to the YAML file describing dataset structure and class names
data_yaml = os.path.join(dataset_path, "lego.yaml")

# Model type (YOLOv8 Nano)
model_name = "yolov8n.pt"

# Training settings
epochs = 100
imgsz = 640
batch = -1  # Auto batch size

# === Step 1: Load pre-trained YOLOv8n model ===
model = YOLO(model_name)

# === Step 2: Train on custom LEGO dataset ===
model.train(
    data=data_yaml,
    epochs=epochs,
    imgsz=imgsz,
    batch=batch,
    name="lego_yolov8n"  # Save training under this name
)

# === Step 3: Validate the trained model ===
results = model.val()

# === Step 4: Export to ONNX format (for Hailo-8) ===
trained_model_path = "runs/detect/lego_yolov8n/weights/best.pt"
model = YOLO(trained_model_path)

# Export to ONNX (opset 11 required for Hailo tools)
model.export(format="onnx", opset=11)

print("Training and export completed. ONNX file saved as: best.onnx")
# 
# # Paths to model and output
# onnx_path = "best.onnx"
# output_dir = "compiled_model"
# hef_name = "yolov8n"
# 
# # Run Hailo model compiler
# subprocess.run([
#     "hailomc",
#     "--model-path", onnx_path,
#     "--target", "arch_hailo8",
#     "--output-dir", output_dir,
#     "--output-hef", f"{hef_name}.hef",
#     "--name", hef_name
# ], check=True)
# 
# print(f"✔️ Hailo model compiled to {output_dir}/{hef_name}.hef")