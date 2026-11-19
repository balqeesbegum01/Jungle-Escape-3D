
import bpy
import math
import os
from mathutils import Vector

# ==========================================
# TEMPLE RUN STYLE HUMAN CHARACTER
# JUNGLE ESCAPE GAME
# ==========================================

# CLEAR SCENE
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ==========================================
# MATERIALS
# ==========================================

def make_material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[
        "Base Color"
    ].default_value = (*color, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs[
        "Roughness"
    ].default_value = roughness
    return mat

skin = make_material("Natural Skin", (0.55, 0.29, 0.16))
shirt = make_material("Blue Adventure Shirt", (0.025, 0.12, 0.65))
pants = make_material("Dark Trousers", (0.025, 0.025, 0.04))
shoes = make_material("White Sneakers", (0.95, 0.95, 0.95))
hair = make_material("Dark Hair", (0.025, 0.015, 0.01))
eyes = make_material("Dark Eyes", (0.01, 0.005, 0.002))
belt = make_material("Brown Belt", (0.18, 0.07, 0.025))

# Store body parts for joining
body_parts = []

# ==========================================
# SPHERE BODY PART
# ==========================================

def make_sphere(name, location, scale, mat, bone):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=16,
        location=location
    )

    obj = bpy.context.object
    obj.name = name
    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()

    # Assign all vertices to the correct bone
    group = obj.vertex_groups.new(name=bone)

    group.add(
        list(range(len(obj.data.vertices))),
        1.0,
        'REPLACE'
    )

    body_parts.append(obj)
    return obj

# ==========================================
# CYLINDER BODY PART
# ==========================================

def make_limb(name, start, end, radius, mat, bone):
    start = Vector(start)
    end = Vector(end)

    direction = end - start
    middle = (start + end) / 2

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=radius,
        depth=direction.length,
        location=middle
    )

    obj = bpy.context.object
    obj.name = name

    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')

    bpy.ops.object.transform_apply(
        location=False,
        rotation=True,
        scale=True
    )

    obj.data.materials.append(mat)

    bevel = obj.modifiers.new("Rounded Limb", "BEVEL")
    bevel.width = radius * 0.35
    bevel.segments = 3

    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bpy.ops.object.shade_smooth()

    group = obj.vertex_groups.new(name=bone)
    group.add(
        list(range(len(obj.data.vertices))),
        1.0,
        'REPLACE'
    )

    body_parts.append(obj)
    return obj

# ==========================================
# HEAD
# ==========================================

make_sphere(
    "Human Head",
    (0, 0, 2.12),
    (0.25, 0.23, 0.31),
    skin,
    "head"
)

# Hair
make_sphere(
    "Hair Top",
    (0, 0, 2.34),
    (0.26, 0.24, 0.15),
    hair,
    "head"
)

# Ears
for side in [-1, 1]:
    make_sphere(
        "Ear",
        (side * 0.25, 0, 2.12),
        (0.07, 0.09, 0.10),
        skin,
        "head"
    )

# Nose
make_sphere(
    "Nose",
    (0, 0.225, 2.12),
    (0.055, 0.07, 0.075),
    skin,
    "head"
)

# Eyes
for side in [-1, 1]:
    make_sphere(
        "Eye",
        (side * 0.09, 0.205, 2.19),
        (0.035, 0.025, 0.035),
        eyes,
        "head"
    )

# ==========================================
# NECK AND BODY
# ==========================================

make_limb(
    "Neck",
    (0, 0, 1.78),
    (0, 0, 1.92),
    0.09,
    skin,
    "neck"
)

# Chest
make_sphere(
    "Upper Chest",
    (0, 0, 1.51),
    (0.32, 0.19, 0.34),
    shirt,
    "spine"
)

# Waist
make_sphere(
    "Waist",
    (0, 0, 1.12),
    (0.25, 0.17, 0.19),
    shirt,
    "spine"
)

# Belt
make_limb(
    "Belt",
    (-0.22, 0, 1.13),
    (0.22, 0, 1.13),
    0.045,
    belt,
    "spine"
)

# ==========================================
# SHOULDERS AND ARMS
# ==========================================

for side, suffix in [(-1, ".L"), (1, ".R")]:

    shoulder = (side * 0.31, 0, 1.66)
    elbow = (side * 0.43, 0, 1.36)
    wrist = (side * 0.46, 0, 1.09)
    hand = (side * 0.46, 0.015, 1.00)

    upper_bone = "upper_arm" + suffix
    lower_bone = "forearm" + suffix
    hand_bone = "hand" + suffix

    # Shoulder
    make_sphere(
        "Shoulder",
        shoulder,
        (0.14, 0.15, 0.16),
        shirt,
        "spine"
    )

    # Upper arm
    make_sphere(
        "Upper Arm",
        ((shoulder[0] + elbow[0]) / 2, 0, 1.51),
        (0.105, 0.115, 0.22),
        shirt,
        upper_bone
    )

    # Elbow
    make_sphere(
        "Elbow",
        elbow,
        (0.085, 0.09, 0.09),
        skin,
        lower_bone
    )

    # Forearm
    make_limb(
        "Forearm",
        elbow,
        wrist,
        0.075,
        skin,
        lower_bone
    )

    # Hand
    make_sphere(
        "Hand",
        hand,
        (0.085, 0.075, 0.11),
        skin,
        hand_bone
    )

# ==========================================
# LEGS
# ==========================================

for side, suffix in [(-1, ".L"), (1, ".R")]:

    hip = (side * 0.14, 0, 1.02)
    knee = (side * 0.15, 0, 0.57)
    ankle = (side * 0.15, 0, 0.19)

    thigh_bone = "thigh" + suffix
    shin_bone = "shin" + suffix
    foot_bone = "foot" + suffix

    # Upper leg
    make_sphere(
        "Thigh",
        (side * 0.15, 0, 0.80),
        (0.145, 0.15, 0.28),
        pants,
        thigh_bone
    )

    # Knee
    make_sphere(
        "Knee",
        knee,
        (0.12, 0.13, 0.13),
        pants,
        shin_bone
    )

    # Lower leg
    make_limb(
        "Lower Leg",
        knee,
        ankle,
        0.105,
        pants,
        shin_bone
    )

    # Shoes
    make_sphere(
        "White Sneakers",
        (side * 0.15, 0.09, 0.11),
        (0.14, 0.27, 0.11),
        shoes,
        foot_bone
    )

# ==========================================
# CREATE HUMAN ARMATURE
# ==========================================

arm_data = bpy.data.armatures.new("Human Skeleton")
armature = bpy.data.objects.new("Human Rig", arm_data)

bpy.context.collection.objects.link(armature)

bpy.context.view_layer.objects.active = armature
armature.select_set(True)

bpy.ops.object.mode_set(mode='EDIT')

bones = {}

def add_bone(name, head, tail, parent=None):
    bone = arm_data.edit_bones.new(name)
    bone.head = head
    bone.tail = tail

    if parent:
        bone.parent = arm_data.edit_bones[parent]

    bones[name] = bone
    return bone

# Root and body
add_bone("root", (0, 0, 0.8), (0, 0, 1.0))
add_bone("spine", (0, 0, 1.0), (0, 0, 1.75), "root")
add_bone("neck", (0, 0, 1.75), (0, 0, 1.94), "spine")
add_bone("head", (0, 0, 1.94), (0, 0, 2.30), "neck")

# Arms
for side, suffix in [(-1, ".L"), (1, ".R")]:
    add_bone(
        "upper_arm" + suffix,
        (side * 0.31, 0, 1.66),
        (side * 0.43, 0, 1.36),
        "spine"
    )

    add_bone(
        "forearm" + suffix,
        (side * 0.43, 0, 1.36),
        (side * 0.46, 0, 1.09),
        "upper_arm" + suffix
    )

    add_bone(
        "hand" + suffix,
        (side * 0.46, 0, 1.09),
        (side * 0.46, 0, 0.97),
        "forearm" + suffix
    )

# Legs
for side, suffix in [(-1, ".L"), (1, ".R")]:
    add_bone(
        "thigh" + suffix,
        (side * 0.14, 0, 1.02),
        (side * 0.15, 0, 0.57),
        "root"
    )

    add_bone(
        "shin" + suffix,
        (side * 0.15, 0, 0.57),
        (side * 0.15, 0, 0.19),
        "thigh" + suffix
    )

    add_bone(
        "foot" + suffix,
        (side * 0.15, 0, 0.19),
        (side * 0.15, 0.27, 0.10),
        "shin" + suffix
    )

bpy.ops.object.mode_set(mode='OBJECT')

# ==========================================
# JOIN BODY PARTS
# ==========================================

bpy.ops.object.select_all(action='DESELECT')

for obj in body_parts:
    obj.select_set(True)

    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(
        location=True,
        rotation=True,
        scale=True
    )

# Join all meshes
bpy.context.view_layer.objects.active = body_parts[0]
bpy.ops.object.join()

human = bpy.context.object
human.name = "Jungle Escape Human"

# Add armature modifier
modifier = human.modifiers.new(
    "Human Skeleton Deform",
    "ARMATURE"
)

modifier.object = armature

# ==========================================
# RUNNING ANIMATION
# ==========================================

armature.animation_data_create()

action = bpy.data.actions.new("Running Animation")
armature.animation_data.action = action

for pose_bone in armature.pose.bones:
    pose_bone.rotation_mode = 'XYZ'

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 25
scene.render.fps = 24

def animate_bone(name, frame, x_rotation):
    bone = armature.pose.bones[name]

    bone.rotation_euler[0] = x_rotation
    bone.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
        group=name
    )

# Four running poses
for frame, angle in [
    (1, 0.65),
    (7, -0.65),
    (13, 0.65),
    (19, -0.65),
    (25, 0.65)
]:
    # Legs alternate
    animate_bone("thigh.L", frame, angle)
    animate_bone("thigh.R", frame, -angle)

    # Arms move opposite to legs
    animate_bone("upper_arm.L", frame, -angle)
    animate_bone("upper_arm.R", frame, angle)

    # Forearms
    animate_bone("forearm.L", frame, angle * 0.4)
    animate_bone("forearm.R", frame, -angle * 0.4)

# Add a little body bounce
for frame, bounce in [
    (1, 0),
    (7, 0.05),
    (13, 0),
    (19, 0.05),
    (25, 0)
]:
    root_bone = armature.pose.bones["root"]
    root_bone.location.z = bounce

    root_bone.keyframe_insert(
        data_path="location",
        frame=frame,
        group="root"
    )

# Linear interpolation
if action:
    for fcurve in action.fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = 'LINEAR'

# ==========================================
# EXPORT GLB
# ==========================================

bpy.ops.object.select_all(action='DESELECT')

human.select_set(True)
armature.select_set(True)

bpy.context.view_layer.objects.active = armature

# Create assets folder
project_folder = bpy.path.abspath("//")
assets_folder = os.path.join(project_folder, "assets")

os.makedirs(assets_folder, exist_ok=True)

output_path = os.path.join(
    assets_folder,
    "player.glb"
)

bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    use_selection=True,
    export_animations=True,
    export_skins=True
)

print("================================")
print("JUNGLE ESCAPE PLAYER CREATED!")
print("PLAYER.GLB EXPORTED SUCCESSFULLY")
print(output_path)
print("================================")
