"""Build one car of the collection with car-mansion's own loaders and save it as a web GLB (Draco).
    bvenv/bin/python webcar.py <car_key> <out.glb> [--lit]
"""
import sys, json, time
from pathlib import Path
ROOT = Path('/home/user/car-mansion')
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts'))
import bpy
import studio, export_cars as EC, export_world as EW
from garage import carlights

key, out = sys.argv[1], Path(sys.argv[2])
lit = '--lit' in sys.argv and key in carlights.SIGNATURES
t0 = time.time()
sc = studio.build(carlights.lit_variant(key) if lit else key, 'CPU')
if lit:
    carlights.lights_on(key, sc)
EC.alone(sc)
EW.curves_to_meshes()
rec = EW.usd_surfaces()
# hide anything hidden for render (logos for invented brands etc.)
for ob in bpy.data.objects:
    if ob.hide_render:
        ob.hide_set(True); ob.hide_viewport = True
bpy.context.view_layer.update()
out.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out), export_format='GLB', use_visible=True, export_apply=True,
    export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12,
    export_image_format='JPEG', export_jpeg_quality=85, export_cameras=False, export_lights=False, export_yup=True)
out.with_suffix('.json').write_text(json.dumps(rec, indent=1))
print(f'[web] {key} -> {out} {out.stat().st_size/1e6:.1f} MB in {time.time()-t0:.0f}s', flush=True)
