import copy
import bpy
import os
import tempfile
from PIL import Image
from math import radians
from lib.renderer.utils import *
from lib.renderer.lighting import setup_lighting
from lib.renderer.render_options import Material, BackgroundType
from lib.annotation_writer import *
from io_scene_importldraw.loadldraw.loadldraw import LegoColours, BlenderMaterials
import glob
import random
import math

# Render Lego parts
# This class is responsible for rendering a single image
# for a single part. It abstracts Blender and LDraw models
class Renderer:
    def __init__(self, ldraw_path = "./ldraw"):
        self.ldraw_path = ldraw_path
        self.ldraw_parts_path = os.path.join(ldraw_path, "parts")
        self.ldraw_unofficial_parts_path = os.path.join(ldraw_path, "unofficial", "parts")
        self.has_imported_at_least_once = False
        self.class_to_id = {}
        
    def render_part(self, ldraw_part_id, options):
        self.import_part(ldraw_part_id, options)

        part = bpy.data.objects[0].children[0]
        camera = bpy.data.objects['Camera']
        
        print(options.background_type)

        # Do this after import b/c the importer overwrites some of these settings
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = options.render_samples
        bpy.context.scene.cycles.max_bounces = 15 if options.material == Material.TRANSPARENT else 2
        bpy.context.scene.render.resolution_x = options.render_width
        bpy.context.scene.render.resolution_y = options.render_height
        bpy.context.scene.render.film_transparent = True if options.background_type == BackgroundType.TRANSPARENT else False
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 0 # turn off ambient lighting

        rotation = options.part_rotation_radian
        rotation = (rotation[0]+ radians(270), rotation[1], rotation[2] + radians(90)) # parts feel in a natural orientation with 90 degree z rotation
        part.rotation_euler = rotation
        
        if not options.background_type == BackgroundType.TRANSPARENT and not options.background_type == BackgroundType.WHITE:
            self.set_background_image(options.background_type)
            
        place_object_on_ground(part)
        setup_lighting(options)

        # The importer does not handle instructions look properly
        # If we skip the line that errors, we still need to re-enable these:
        # https://github.com/TobyLobster/ImportLDraw/issues/76
        if options.instructions:
            for layer in bpy.context.scene.view_layers:
                for collection in layer.layer_collection.children:
                    collection.exclude = False

        # Aim and position the camera so the part is centered in the frame.
        # The importer can do this for us but we rotate and move the part
        # after importing so would need to do it again anyways.
        select_hierarchy(part)
        camera.data.type = 'PERSP' # I prefer perspective even for instructions
        camera.data.lens = 120 # Long focal length so perspective is minor
        set_height_by_angle(camera, options.camera_height)
        aim_towards_origin(camera)
        bpy.ops.view3d.camera_to_view_selected()
        zoom_camera(camera, options.zoom)


        # Render
        bpy.context.scene.render.image_settings.file_format = options.format.value
        bpy.context.scene.render.image_settings.quality = 90 # for jpeg
        bpy.context.scene.render.filepath = options.image_filename
        bpy.ops.render.render(write_still=True)

        # Did we render a larger size, if so resize
        if options.width != options.render_width:
            image = Image.open(options.image_filename)
            image.thumbnail((options.width, options.height), Image.LANCZOS)
            image.save(options.image_filename)

        # Save a Blender file so we can debug this script
        if options.blender_filename:
            bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(options.blender_filename))
            
        # Save the bounding box coordinates in YOLO format
        if options.label_filename:
            bounding_box = get_2d_bounding_box(part, camera).to_yolo(options.width, options.height)
            write_label_file(options.label_filename, bounding_box, options.part_class_id)

    def import_part(self, ldraw_part_id, options):
        self.clear_scene()

        part_filename = os.path.abspath(os.path.join(self.ldraw_parts_path, f"{ldraw_part_id}.dat"))
        if not os.path.exists(part_filename):
            part_filename = os.path.abspath(os.path.join(self.ldraw_unofficial_parts_path, f"{ldraw_part_id}.dat"))
            if not os.path.exists(part_filename):
                raise FileNotFoundError(f"Part file not found: {part_filename}")


        # Set the part color
        #
        # We want to use our own colors that seem to be more realistic. The importer plugin doesn't
        # support out of the box so we access some internals to create/modify a color reserved for us.
        #
        # Colors are tricky because:
        #   - the importer uses the LDraw color to determine color and material (e.g. transparent)
        #   - a part may have multiple materials (slopes 3039) and colors (hinged attenna 73587p01)
        #   - colors are re-read from LDConfig.ldr each time the importer is invoked
        ldraw_color = 99999
        linearRGBA = LegoColours.hexDigitsToLinearRGBA(options.part_color.replace('#', ''), 1.0)
        LegoColours.colours[99999] = {
            "name": "lego-rendering-placeholder-color",
            "colour": linearRGBA[0:3],
            "alpha": 0.5 if options.material == Material.TRANSPARENT else 1,
            "luminance": 0.0,
            "material": "RUBBER" if options.material == Material.RUBBER else "BASIC",
        }

        name = ""
        with tempfile.NamedTemporaryFile(suffix=".ldr", mode='w+', delete=False) as temp:
            temp.write("0 Untitled Model\n")
            temp.write("0 Name:  UntitledModel\n")
            temp.write("0 Author:\n")
            temp.write("0 CustomBrick\n")
            temp.write(f"1 {ldraw_color} 30.000000 -24.000000 -20.000000 1.000000 0.000000 0.000000 0.000000 1.000000 0.000000 0.000000 0.000000 1.000000 {ldraw_part_id}.dat\n")

            name = temp.name

        with open(name, 'r') as file:
            data = file.read()
            print("-----")
            print(data)
            print("-----")

        # Import the part into the scene
        # https://github.com/TobyLobster/ImportLDraw/blob/09dd286d294672c816d33e70ac10146beb69693c/importldraw.py
        bpy.ops.import_scene.importldraw(filepath=name, **{
            "ldrawPath": os.path.abspath(self.ldraw_path),
            "addEnvironment": False if options.background_type == BackgroundType.TRANSPARENT else True,                  # add a white ground plane
            "resPrims": options.res_prisms,          # high resolution primitives
            "useLogoStuds": options.use_logo_studs,  # LEGO logo on studs
            "look": options.look.value,              # normal (realistic) or instructions (line art)
            "colourScheme": "ldraw",
        })

        bpy.ops.object.select_all(action='DESELECT')
        os.remove(name)
        self.has_imported_at_least_once = True

    def clear_scene(self):
        bpy.ops.object.select_all(action='DESELECT')

        # Select all objects in the current scene
        for obj in bpy.context.scene.objects:
            if obj.type not in {'CAMERA'}:
                obj.select_set(True)

        # Delete selected objects
        bpy.ops.object.delete()

        # Delete materials because we reuse the same LDraw color
        # for all renders but change the LDRConfig to change the
        # rendered color
        for datablock in [bpy.data.meshes, bpy.data.materials, bpy.data.textures, bpy.data.images]:
            for block in datablock:
                datablock.remove(block, do_unlink=True)

        # Clear caches. For the same reason above (LDRConfig changes)
        if self.has_imported_at_least_once:
            LegoColours()
            BlenderMaterials.clearCache()

    #TODO: make this methed switch between different backgrounds
    def set_background_image(self, background_type=BackgroundType.IMAGE):  
        ground = bpy.data.objects.get("LegoGroundPlane")
        if not ground:
            print("LegoGroundPlane not found.")
            return
    
        # Load random image
        image_dir = os.path.abspath("./lib/backgrounds")
        images = glob.glob(os.path.join(image_dir, "*.jpg")) + glob.glob(os.path.join(image_dir, "*.png"))
        if not images:
            print(f"No background images found in: {image_dir}")
            return
    
        img_path = random.choice(images)
        print(f"Using background image: {img_path}")
        img = bpy.data.images.load(img_path)
    
        # Create or reuse material
        mat_name = "LegoGroundPlaneMaterial"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
    
        # Assign material only to the ground plane
        if ground.data.materials:
            ground.data.materials[0] = mat
        else:
            ground.data.materials.append(mat)
    
        # Clear and set up new nodes
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
    
        # Create nodes
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_image.image = img
    
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        output = nodes.new('ShaderNodeOutputMaterial')
    
        tex_coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
    
        # Link nodes
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
        print("Updated texture on LegoGroundPlane.")

        ground.scale = (.006, .006, 1)  # X and Y scaled down, Z left unchanged
        bpy.context.view_layer.objects.active = ground
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        print("Background image applied to LegoGroundPlane.")