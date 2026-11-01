"""COACHWORK: one magazine system, one issue per car. Writes dist/<issue>/ (index.html, preview.html
for local checks, model.txt, draco/, any decal) from the issue configs below.

    python3 make_mag.py              # every issue
    python3 make_mag.py f812 agera   # some
"""
import base64, html, json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'src'
DRACO = HERE.parent / 'node_modules/three/examples/jsm/libs/draco/gltf'
CARS = Path('/home/user/webcars')
DECALS = Path('/home/user/car-mansion/garage/textures')
IMPORTMAP = '<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"}}</script>'

# rich colours only: no white, grey, silver or black paint
RIMS = [  # finishes, for the factory wheel's face or a forged rim's
    {'name': 'Factory', 'factory': True, 'sw': None},
    {'name': 'Gloss black', 'color': '#0a0a0c', 'metal': 0.25, 'rough': 0.12, 'coat': 1},
    {'name': 'Satin gold', 'color': '#b58f3e', 'metal': 1, 'rough': 0.3, 'coat': 0.4},
    {'name': 'Satin bronze', 'color': '#5b3d22', 'metal': 1, 'rough': 0.34},
    {'name': 'Copper', 'color': '#a8582f', 'metal': 1, 'rough': 0.2, 'coat': 0.5},
    {'name': 'Mirror chrome', 'color': '#e4e4e8', 'metal': 1, 'rough': 0.04},
    {'name': 'Candy', 'color': 'paint', 'metal': 0.7, 'rough': 0.2, 'coat': 1},
]
WHEELS = [  # car-mansion's forged rims (garage_kit), mounted on each car's own tyres
    {'id': 'factory', 'name': 'Factory'}, {'id': 'y5', 'name': 'Y-spoke'}, {'id': 's10', 'name': 'Ten-spoke'},
    {'id': 'aero', 'name': 'Aero turbine'}, {'id': 'mesh', 'name': 'Mesh'},
]
RIMDIR = CARS / 'rims'
BOLTS = [
    {'name': 'Gold', 'color': '#d4a23a', 'metal': 1, 'rough': 0.22},
    {'name': 'Black chrome', 'color': '#1a1a1e', 'metal': 1, 'rough': 0.12},
    {'name': 'Anodised red', 'color': '#a01522', 'metal': 0.8, 'rough': 0.25},
]

ISSUES = {
    'f812': dict(
        no='01', model='f812', make='Ferrari', name='812 Superfast', year='2018', short='812',
        tagline='V12 power, sculpted elegance, unmistakable presence.',
        pills=['6.5 L V12', '789 hp', 'RWD'],
        ink='#2b1145', accent='#8f5fd6', paper='#e8e5ea', paper2='#f6f4f7', dark='#141017', dark2='#2a1d36',
        intro='A technical overview of this 2018 Ferrari 812 Superfast, finished in a deep purple pearl that shifts with the light and follows every curve.',
        specs=[('Model', 'Ferrari 812 Superfast'), ('Year', '2018'), ('Engine', '6.5 L naturally aspirated V12'), ('Power', '789 hp at 8,500 rpm'),
               ('Transmission', '7-speed dual-clutch'), ('Drivetrain', 'Rear-wheel drive'), ('0–100 km/h', '2.9 s'), ('Top speed', '340 km/h')],
        note='Purple pearl over a black base, with a fine violet flake in the clear.',
        design=[('Sculpted to perfection.', 'A long bonnet over a front-mid V12, a low roofline and a cab-back stance that speaks to classic Ferrari grand tourers.'),
                ('Clean surfacing.', 'Flowing lines carve through the body and pull the light from the headlamps back over the haunches.'),
                ('Aggressive, yet refined.', 'A wide track, muscular rear wings and a poised stance: presence without shouting.')],
        details=[('Four round tail lamps', 'Two rings each side, a Ferrari signature, lit day or night.'),
                 ('Forged wheels, gold bolts', 'Twenty spokes in gloss black, forty gold bolts round the rim.'),
                 ('Quad exhaust', 'Four tips under an active diffuser whose flaps open at speed.'),
                 ('From above', 'Bonnet vents and a fastback roof that runs straight into the tail.')],
        night=('Three LED blades', 'and two projectors.', 'A stacked daytime-running blade sweeping up into the wing, twin full-LED projectors under it.'),
        final='An atmospheric V12 grand tourer with unmistakable style and presence.',
        paints=[{'name': 'Viola Notte', 'color': '#24093f', 'caliper': '#0b0b0c'}, {'name': 'Rosso Bordeaux', 'color': '#3c0710', 'caliper': '#0b0b0c'},
                {'name': 'Blu Notte', 'color': '#0b1a45', 'caliper': '#0b0b0c'}, {'name': 'Verde Abetone', 'color': '#0b2b1d', 'caliper': '#0b0b0c'}],
        rim_factory='Gloss black', bolts=True,
        engine={'idle': 42, 'range': 170},
    ),
    'agera': dict(
        no='02', model='agera', make='Koenigsegg', name='Agera', year='2011', short='Agera',
        tagline='Swedish carbon, a twin-turbo V8, and a roof that lives in the boot.',
        pills=['4.7 L twin-turbo V8', '947 hp', 'RWD'],
        ink='#3c0712', accent='#c0485a', paper='#ebe5e4', paper2='#f8f3f2', dark='#150f10', dark2='#33181d',
        intro='A technical overview of this 2011 Koenigsegg Agera, in deep burgundy over exposed carbon, with gold wheel lips and calipers.',
        specs=[('Model', 'Koenigsegg Agera'), ('Year', '2011'), ('Engine', '4.7 L twin-turbo V8'), ('Power', '947 hp (960 PS)'),
               ('Torque', '1,100 Nm'), ('Transmission', '7-speed dual-clutch'), ('0–100 km/h', '3.1 s'), ('Top speed', '390 km/h+ (claimed)')],
        note='Deep burgundy metallic, gold anodised wheel lips, gold calipers.',
        design=[('Built round a carbon tub.', 'A carbon-fibre and aluminium honeycomb chassis carries the engine as a stressed member.'),
                ('Doors that swing out and up.', 'Koenigsegg\'s dihedral synchro-helix doors rotate forward and up, clear of the kerb.'),
                ('A roof you take with you.', 'The targa top lifts off and stows under the front bonnet.')],
        details=[('Tail lamps', 'Round lamps set in the carbon, glowing red against the burgundy.'),
                 ('Gold lips, gold calipers', 'Gloss black faces with gold anodised lips, gold calipers behind.'),
                 ('Centre exhaust', 'One exit in the middle of the diffuser, framed in carbon.'),
                 ('From above', 'The roof panel, the vents and the long rear deck over the V8.')],
        night=('A line of light', 'with amber at the edges.', 'A dotted LED daytime line along the lamp, amber side markers, round tail lamps.'),
        final='A hypercar from a small Swedish workshop, built to take on the fastest cars in the world.',
        paints=[{'name': 'Rosso Borgogna', 'color': '#3c0712'}, {'name': 'Blu Notte', 'color': '#0b1a45'},
                {'name': 'Viola', 'color': '#2a0c46'}, {'name': 'Verde Inglese', 'color': '#0b2b1d'}],
        rim_factory='Black with gold lips', bolts=False,
        engine={'idle': 46, 'range': 190, 'mix': [[1, 'sawtooth', .5], [2, 'sawtooth', .25], [.5, 'square', .35]]},
    ),
    'chiron': dict(
        no='03', model='chiron', make='Bugatti', name='Chiron', year='2016', short='Chiron',
        tagline='Sixteen cylinders, four turbos, and not one bright colour.',
        pills=['8.0 L W16', '1,479 hp', 'AWD'],
        ink='#0d1a40', accent='#4d78e0', paper='#e4e7ee', paper2='#f4f6fa', dark='#0b0f1a', dark2='#18233f',
        intro='A technical overview of the Bugatti Chiron, in midnight-blue metallic over gloss black, with exposed carbon and black wheels.',
        specs=[('Model', 'Bugatti Chiron'), ('Year', '2016'), ('Engine', '8.0 L quad-turbo W16'), ('Power', '1,479 hp (1,500 PS)'),
               ('Torque', '1,600 Nm'), ('Drivetrain', 'All-wheel drive'), ('0–100 km/h', '2.4 s'), ('Top speed', '420 km/h (limited)')],
        note='Midnight blue metallic over gloss black. Nothing bright.',
        design=[('The C-line.', 'One curve sweeps from behind the front wheel over the door and back down, and splits the colours of the car.'),
                ('The horseshoe.', 'The grille every Bugatti has worn since the 1920s, larger here to feed ten radiators.'),
                ('A spine down the middle.', 'A fin runs from the windscreen to the tail along the car\'s centre line.')],
        details=[('A 1.6 metre tail lamp', 'One unbroken LED bar across the whole tail.'),
                 ('Black wheels', 'Gloss black faces with graphite lips, carbon-ceramic brakes behind.'),
                 ('Exhaust', 'A wide central exhaust under the tail, the air brake above it.'),
                 ('From above', 'The spine, the roof scoop and the long glass over the engine bay.')],
        night=('Four lamps a side', 'in a single line.', 'Four LED modules stacked in each headlamp, the Chiron\'s light signature.'),
        final='The most powerful car of its time, finished as quietly as it could be.',
        paints=[{'name': 'Midnight Blue', 'color': '#0a1838'}, {'name': 'Bordeaux', 'color': '#3c0712'},
                {'name': 'Violet', 'color': '#24093f'}, {'name': 'Racing Green', 'color': '#0b2b1d'}],
        rim_factory='Black, graphite lips', bolts=False,
        engine={'idle': 34, 'range': 130, 'mix': [[1, 'sawtooth', .5], [1.25, 'sawtooth', .4], [.5, 'square', .3], [2, 'sawtooth', .15]]},
    ),
    'one1': dict(
        no='04', model='one1', make='Koenigsegg', name='One:1', year='2014', short='One:1',
        tagline='One horsepower for every kilogram, in liquid copper.',
        pills=['5.0 L twin-turbo V8', '1,341 hp', 'RWD'],
        ink='#4a1d0a', accent='#d27a3e', paper='#ebe6e1', paper2='#f8f4ef', dark='#140f0c', dark2='#35221a',
        intro='A technical overview of the Koenigsegg One:1, in liquid copper over gloss carbon.',
        specs=[('Model', 'Koenigsegg One:1'), ('Year', '2014'), ('Engine', '5.0 L twin-turbo V8'), ('Power', '1,341 hp (1,360 PS) on E85'),
               ('Weight', '1,360 kg'), ('Power to weight', '1:1'), ('0–100 km/h', '2.8 s'), ('Top speed', '440 km/h (claimed)')],
        note='Liquid copper over gloss carbon fibre.',
        design=[('One to one.', 'The name is the ratio: 1,360 PS for 1,360 kg, the first production car to make a megawatt.'),
                ('Built for the track.', 'Wider wings, a roof scoop and a large active rear wing that moves with speed.'),
                ('Carbon everywhere.', 'Exposed carbon fibre on the lower body, the wing and the splitter.')],
        details=[('Tail lamps', 'Round lamps in the carbon rear, under the active wing.'),
                 ('Forged wheels', 'Fitted here with forged Y-spokes and a diamond-cut lip. The carbon originals are one tap away.'),
                 ('Exhaust', 'A single centre exit in the diffuser, like every Koenigsegg of the time.'),
                 ('From above', 'The roof scoop and the wing, in carbon against the copper.')],
        night=('A ring of light', 'round three projectors.', 'A light guide round each lamp with three projectors inside.'),
        final='Six were built for customers. This one is finished in liquid copper.',
        paints=[{'name': 'Liquid Copper', 'color': '#7a3214'}, {'name': 'Bordeaux', 'color': '#3c0712'},
                {'name': 'Midnight Blue', 'color': '#0b1a45'}, {'name': 'Violet', 'color': '#2a0c46'}],
        rim_factory='Gloss carbon black', bolts=False, wheel='y5', finish=1,
        engine={'idle': 48, 'range': 200, 'mix': [[1, 'sawtooth', .5], [2, 'sawtooth', .25], [.5, 'square', .35]]},
    ),
    'projectone': dict(
        no='05', model='projectone', make='Mercedes-AMG', name='Project One', year='2017', short='Project One',
        tagline='A Formula One power unit with number plates.',
        pills=['1.6 L V6 hybrid', '1,049 hp', 'AWD'],
        ink='#16300e', accent='#7cc11e', paper='#e5e9e2', paper2='#f4f7f1', dark='#0d120b', dark2='#1f3016',
        intro='A technical overview of the Mercedes-AMG Project One, in AMG Green Hell magno with a yellow line and pinstripe and yellow calipers.',
        specs=[('Model', 'Mercedes-AMG Project One'), ('Shown', '2017'), ('Engine', '1.6 L turbo V6 + 4 electric motors'), ('Power', '1,049 hp (1,063 PS)'),
               ('Redline', '11,000 rpm'), ('Drivetrain', 'All-wheel drive'), ('0–100 km/h', '2.9 s'), ('Top speed', '352 km/h')],
        note='AMG Green Hell magno, yellow line and pinstripe, yellow calipers.',
        design=[('A race car\'s heart.', 'The 1.6 litre turbo V6 comes from the Mercedes Formula One cars, with an electric motor on the turbo and one on the crank.'),
                ('Shaped by air.', 'A roof intake, a shark fin and an active rear wing with louvres over the front wheels.'),
                ('Green Hell.', 'The matte green is named after the Nürburgring Nordschleife, where AMG tests.')],
        details=[('Tail lamps', 'Thin LED lamps either side of the open rear mesh.'),
                 ('Yellow calipers', 'Carbon-ceramic brakes with yellow calipers behind black wheels.'),
                 ('Exhaust', 'Two central exits under the rear wing.'),
                 ('From above', 'The roof scoop and the fin running back to the wing.')],
        night=('A brow of light', 'over two projectors.', 'A light guide along the top of each slot, over two projectors.'),
        final='Hybrid Formula One technology, as close as it has come to the road.',
        paints=[{'name': 'AMG Green Hell', 'color': '#3b6a2c', 'flake': 0}],
        matte=True, rim_factory='Gloss black', bolts=False,
        livery={'color': '#f0c419', 'sweep': [0.92, -0.98, 0.42, 0.6, 0.024], 'pin': [0.14, 0.012], 'carbonBelow': 0.14,
                'decal': {'src': 'amg_side.png', 'at': [0.02, 0.3], 'size': [0.62, 0.08], 'color': '#0d0d0e'}},
        decal_file='livery_real/amg_side.png',
        engine={'idle': 60, 'range': 260, 'mix': [[1, 'sawtooth', .45], [2, 'square', .2], [3, 'sawtooth', .15]]},
    ),
}
ORDER = ['f812', 'agera', 'chiron', 'one1', 'projectone']

# camera stops (orbit round an anchor; car length = 1; positive yaw = the car's left side, 180 = behind)
P = {
    'cover':   ({'at': 'center', 'yaw': 32, 'pitch': 5, 'dist': 1.55, 'fov': 30, 'sx': 0.1, 'sy': -0.11, 'lights': 0, 'spin': 0, 'env': 1, 'drift': 1, 'shadow': 1, 'tx': 0, 'ty': 0, 'tz': 0, 'roll': 0},
                {'dist': 3.1, 'sx': 0, 'sy': -0.1}),
    'side':    ({'at': 'center', 'yaw': 90, 'pitch': 1, 'dist': 1.55, 'sx': 0.14, 'sy': -0.25}, {'dist': 3.2, 'sx': 0, 'sy': 0.16}),
    'frontv':  ({'yaw': 0, 'pitch': 4, 'dist': 1.75, 'sx': -0.25, 'sy': -0.04}, {'dist': 1.9, 'sx': 0, 'sy': 0.2}),
    'top':     ({'yaw': 0, 'pitch': 86, 'dist': 1.95, 'sx': -0.24, 'sy': 0.0, 'roll': 90}, {'dist': 1.9, 'sx': 0, 'sy': 0.2, 'roll': 0}),
    'stance':  ({'yaw': -90, 'pitch': 0.5, 'dist': 1.5, 'sx': 0.12, 'sy': -0.29, 'roll': 0}, {'dist': 3.2, 'sx': 0, 'sy': 0.15}),
    'finish':  ({'yaw': -40, 'pitch': 7, 'dist': 1.6, 'sx': -0.18, 'sy': -0.02}, {'dist': 2.6, 'sx': 0, 'sy': 0.17}),
    'rear34':  ({'at': 'center', 'yaw': 150, 'pitch': 9, 'dist': 1.4, 'sx': 0.16, 'sy': -0.04, 'lights': 0.7}, {'dist': 2.4, 'sx': 0, 'sy': 0.17}),
    'tail':    ({'at': 'tailm', 'yaw': 158, 'pitch': 5, 'dist': 0.42, 'fov': 28, 'sx': 0.18, 'sy': 0.02, 'lights': 1}, {'dist': 0.6, 'sx': 0, 'sy': 0.2}),
    'wheel':   ({'at': 'wheelFm', 'yaw': 92, 'pitch': 2, 'dist': 0.42, 'fov': 32, 'sx': 0.2, 'sy': 0.0, 'lights': 0, 'spin': 0.8, 'shadow': 0.6}, {'dist': 0.55, 'sx': 0, 'sy': 0.2}),
    'exhaust': ({'at': 'exhaust', 'yaw': 186, 'pitch': 3, 'dist': 0.5, 'fov': 30, 'sx': -0.2, 'sy': 0.04, 'spin': 0, 'shadow': 1}, {'dist': 0.7, 'sx': 0, 'sy': 0.2}),
    'topr':    ({'at': 'center', 'yaw': 180, 'pitch': 86, 'dist': 1.95, 'fov': 30, 'sx': 0.22, 'sy': 0, 'roll': -90}, {'dist': 1.9, 'sx': 0, 'sy': 0.2, 'roll': 0}),
    'night':   ({'at': 'center', 'yaw': 14, 'pitch': 1.5, 'dist': 1.3, 'fov': 30, 'sx': 0.14, 'sy': -0.05, 'roll': 0, 'lights': 1, 'env': 0.12, 'shadow': 0.5}, {'dist': 2.2, 'sx': 0, 'sy': 0.12}),
    'final':   ({'yaw': 148, 'pitch': 6, 'dist': 1.55, 'sx': 0.0, 'sy': -0.14, 'lights': 0.6, 'env': 1, 'shadow': 1}, {'dist': 2.5, 'sy': -0.02}),
    'away':    ({'yaw': 215, 'pitch': 14, 'dist': 2.4, 'sy': 0.06, 'lights': 0.3}, {'dist': 3.2, 'sy': 0.14}),
}


def pose(k, **over):
    d, m = P[k]
    d = {**d, **over}
    return f"data-pose='{json.dumps(d)}' data-pose-m='{json.dumps(m)}'"


def e(s):
    return html.escape(s, quote=True)


def chips_json(c):
    return json.dumps({'paints': c['paints'], 'rims': RIMS, 'bolts': BOLTS if c.get('bolts') else []})


def page(key, links):
    c = ISSUES[key]
    nxt = ORDER[(ORDER.index(key) + 1) % len(ORDER)]
    nc = ISSUES[nxt]
    title = f"{c['make']} {c['name']}"
    spec_rows = ''.join(f'<div class="row"><span>{e(a)}</span><b>{e(b)}</b></div>' for a, b in c['specs'])
    design = ''.join(f'<p class="rv"><b>{e(t)}</b> {e(x)}</p>' for t, x in c['design'])
    keys = ['tail', 'wheel', 'exhaust', 'topr']
    sides = {'tail': 'left', 'wheel': 'left', 'exhaust': 'right', 'topr': 'left'}
    details = ''
    for i, ((t, x), k) in enumerate(zip(c['details'], keys)):
        side = sides[k]
        extra = ''
        if k == 'wheel':
            extra = ('<div class="group"><span class="lab">Wheel</span><div class="chips" id="wheels"></div></div>'
                     '<div class="group"><span class="lab">Finish</span><div class="chips" id="rims"></div></div>')
            if c.get('bolts'):
                extra += '<div class="group"><span class="lab">Bolts</span><div class="chips" id="bolts"></div></div>'
        details += f'''
    <article class="detail {side}" {pose(k)}>
      <div class="card rv"><h4><span class="chev">›</span>{e(t)}</h4><p>{e(x)}</p>{extra}</div>
    </article>'''
    paints_block = ''
    if len(c['paints']) > 1:
        paints_block = '<div class="group rv"><span class="lab">Finish</span><div class="chips" id="paints"></div></div>'
    else:
        paints_block = f'<div class="group rv"><span class="lab">Finish</span><p class="finish-one">{e(c["paints"][0]["name"])} · the livery as specified</p></div>'
    next_href = links.get(nxt, '#')
    cfg = {'paints': c['paints'], 'rims': [dict(r, name=(c['rim_factory'] if r.get('factory') else r['name'])) for r in RIMS],
           'bolts': BOLTS if c.get('bolts') else [], 'matte': c.get('matte', False), 'livery': c.get('livery'), 'engine': c.get('engine'), 'accent': c['accent'],
           'wheels': WHEELS, 'wheel': c.get('wheel', 'factory'), 'finish': c.get('finish', 0)}
    n1, n2, n3 = c['night']
    tpl = (SRC / 'issue.html').read_text()
    rep = {
        'TITLE': f"Coachwork {c['no']}: {c['short']}", 'ISSUE': c['no'], 'MAKE': e(c['make']), 'NAME': e(c['name']), 'YEAR': c['year'],
        'FULL': e(title), 'TAGLINE': e(c['tagline']), 'PILLS': ''.join(f'<span>{e(p)}</span>' for p in c['pills']),
        'INK': c['ink'], 'ACCENT': c['accent'], 'PAPER': c['paper'], 'PAPER2': c['paper2'], 'DARK': c['dark'], 'DARK2': c['dark2'],
        'INTRO': e(c['intro']), 'SPECS': spec_rows, 'NOTE': e(c['note']), 'DESIGN': design, 'PAINTS': paints_block, 'DETAILS': details,
        'NIGHT1': e(n1), 'NIGHT2': e(n2), 'NIGHT3': e(n3), 'FINAL': e(c['final']), 'NEXTNO': nc['no'], 'NEXTNAME': e(f"{nc['make']} {nc['name']}"),
        'NEXTHREF': next_href, 'CFG': json.dumps(cfg),
        'P_COVER': pose('cover'), 'P_SIDE': pose('side'), 'P_FRONT': pose('frontv'), 'P_TOP': pose('top'), 'P_STANCE': pose('stance'),
        'P_FINISH': pose('finish'), 'P_REAR': pose('rear34'), 'P_NIGHT': pose('night'), 'P_FINAL': pose('final'), 'P_AWAY': pose('away'),
        'ALT': e(f"{title} ({c['year']}), shown in 3D"),
        'IMPORTMAP': IMPORTMAP, 'STAGE': (SRC / 'scrollstage.js').read_text(), 'CARKIT': (SRC / 'carkit.js').read_text(),
    }
    out = tpl
    for k, v in rep.items():
        out = out.replace('%%' + k + '%%', v)
    assert '%%' not in out, [l for l in out.splitlines() if '%%' in l][:3]
    return out


def build(keys, links):
    for key in keys:
        c = ISSUES[key]
        d = HERE / 'dist' / f'issue-{key}'
        if d.exists():
            shutil.rmtree(d)
        (d / 'draco').mkdir(parents=True)
        html_ = page(key, links)
        (d / 'index.html').write_text(html_)
        (d / 'preview.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body style="margin:0">' + html_ + '</body></html>')
        (d / 'model.txt').write_text(base64.b64encode((CARS / f"{c['model']}.glb").read_bytes()).decode())
        for f in ('draco_decoder.wasm', 'draco_wasm_wrapper.js', 'draco_decoder.js'):
            shutil.copy(DRACO / f, d / 'draco' / f)
        for st in ('y5', 's10', 'aero', 'mesh'):
            (d / f'rim-{st}.txt').write_text(base64.b64encode((RIMDIR / f'rim_{st}.glb').read_bytes()).decode())
        if c.get('decal_file'):
            shutil.copy(DECALS / c['decal_file'], d / Path(c['decal_file']).name)
        print('built', d.name)


if __name__ == '__main__':
    links = json.loads((HERE / 'links.json').read_text()) if (HERE / 'links.json').exists() else {}
    build(sys.argv[1:] or ORDER, links)
