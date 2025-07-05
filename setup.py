import bpy
import subprocess
import sys
import os
import urllib.request

def log(message):
    print(f"[SETUP] {message}")

def run_and_log(description, command):
    log(f"Starting: {description}")
    result = subprocess.run(command)
    log(f"Finished: {description} with return code {result.returncode}")
    if result.returncode != 0:
        raise RuntimeError(f"{description} failed")

def addon_exists(module_name):
    return module_name in bpy.context.preferences.addons

# --- Reset Blender to factory state
log("Reading factory settings")
bpy.ops.wm.read_factory_settings(use_empty=True)

# --- Check and install the ImportLDraw addon if needed
addon_module = "io_scene_importldraw"
addon_zip_path = "./temp/importldraw.zip"

if not addon_exists(addon_module):
    url = "https://github.com/TobyLobster/ImportLDraw/releases/download/v1.2.1/importldraw1.2.1.zip"
    addon_zip_path = "./temp/importldraw.zip"

    # Create the temp directory if it doesn't exist
    os.makedirs(os.path.dirname(addon_zip_path), exist_ok=True)

    print(">>> Downloading ImportLDraw plugin...")
    urllib.request.urlretrieve(url, addon_zip_path)
    print(">>> Download complete.")

    if os.path.exists(addon_zip_path):
        log(f"Installing ImportLDraw addon from {addon_zip_path}")
        bpy.ops.preferences.addon_install(filepath=addon_zip_path)
        bpy.ops.preferences.addon_enable(module=addon_module)
        log("ImportLDraw addon installed and enabled.")
    else:
        log(f"❌ Addon zip not found at {addon_zip_path}. Skipping installation.")
else:
    log("✅ ImportLDraw addon is already installed and enabled.")

# Set Cycles as the render engine
bpy.context.scene.render.engine = 'CYCLES'

# Enable GPU compute
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'  # or 'OPTIX' or 'HIP'

# Refresh the device list
bpy.context.preferences.addons['cycles'].preferences.get_devices()

# Enable your desired GPU device
for device in bpy.context.preferences.addons['cycles'].preferences.devices:
    device.use = device.type == 'CUDA'  # or 'OPTIX', depending on your GPU

# Set render device to GPU
bpy.context.scene.cycles.device = 'GPU'

# --- Set up Python packages
run_and_log("Bootstrapping ensurepip", [sys.executable, "-m", "ensurepip"])
run_and_log("Installing Pillow", [sys.executable, "-m", "pip", "install", "pillow"])