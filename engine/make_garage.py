"""The garage library: one page, five cars loaded on demand, four forged rims. Writes dist/garage/."""
import base64, json, shutil
from pathlib import Path
import make_mag as MM
HERE = Path(__file__).resolve().parent
d = HERE / 'dist' / 'garage'
if d.exists(): shutil.rmtree(d)
(d / 'draco').mkdir(parents=True)
cars = []
for k in MM.ORDER:
    c = MM.ISSUES[k]
    cars.append({'key': k, 'no': c['no'], 'make': c['make'], 'name': c['name'], 'accent': c['accent'], 'paint': c['paints'][0]['name'], 'exhaust': c['engine']['name'],
                 'cfg': {'paints': c['paints'], 'matte': c.get('matte', False), 'livery': c.get('livery'), 'engine': c.get('engine'), 'accent': c['accent']}})
    (d / f'model-{k}.txt').write_text(base64.b64encode((MM.CARS / f"{c['model']}.glb").read_bytes()).decode())
    if c.get('decal_file'): shutil.copy(MM.DECALS / c['decal_file'], d / Path(c['decal_file']).name)
for style in ('y5', 's10', 'aero', 'mesh'):
    (d / f'rim-{style}.txt').write_text(base64.b64encode((MM.CARS / 'rims' / f'rim_{style}.glb').read_bytes()).decode())
for f in ('draco_decoder.wasm', 'draco_wasm_wrapper.js', 'draco_decoder.js'):
    shutil.copy(MM.DRACO / f, d / 'draco' / f)
html = (HERE / 'src' / 'garage.html').read_text()
for k, v in {'IMPORTMAP': MM.IMPORTMAP, 'STAGE': (HERE / 'src' / 'scrollstage.js').read_text(), 'CARKIT': (HERE / 'src' / 'carkit.js').read_text(), 'CARS': json.dumps(cars)}.items():
    html = html.replace('%%' + k + '%%', v)
(d / 'index.html').write_text(html)
(d / 'preview.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body style="margin:0">' + html + '</body></html>')
print('garage', sum(f.stat().st_size for f in d.rglob('*') if f.is_file()) / 1e6, 'MB')
