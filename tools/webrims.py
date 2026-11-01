"""Export car-mansion's forged rims (garage_kit) as bare web GLBs: one per style, axis +Z out of the face."""
import sys
from pathlib import Path
ROOT = Path('/home/user/car-mansion'); sys.path.insert(0, str(ROOT))
import bpy
from garage import garage_kit as GK
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for style in GK.STYLES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    src, d = GK.wheel_source(style, 20, 285, 'gloss_black', tyre=False)
    exp = bpy.data.collections.new('Export'); bpy.context.scene.collection.children.link(exp)
    objs = list(src.all_objects)
    for o in objs:
        exp.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in exp.objects:
        o.select_set(True)
    names = sorted({s.material.name for o in objs for s in getattr(o, 'material_slots', []) if s.material})
    f = out / f'rim_{style}.glb'
    bpy.ops.export_scene.gltf(filepath=str(f), export_format='GLB', use_selection=True, export_apply=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
        export_image_format='JPEG', export_cameras=False, export_lights=False, export_yup=True)
    print(f'[rim] {style}: {f.stat().st_size/1e3:.0f} kB, {len(objs)} objects, rb={d["rb"]:.3f} W={d["W"]:.3f}, mats={names}', flush=True)
