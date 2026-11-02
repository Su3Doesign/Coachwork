# Coachwork

A car magazine you read by scrolling. Five issues, one car each, in 3D: the car sits in front of the words and moves
from spread to spread (cover, build sheet, design & stance, signature details, after dark, final impression). A garage
library holds all five cars in one page, each in front of its name in layered metal type, with forged rims to fit on any of them.

Every page has an ignition: a start button inside a rev counter (on each issue's cover, in its top bar and in its After
Dark spread; centre stage in the garage). Press it and the needle sweeps, the
starter turns and the engine catches; hold it to rev (the body rocks on its springs, the exhaust crackles when you lift
off), tap it again to stop. The lights switch beside it wakes the headlamps. Changing rims opens a portal on the floor:
the car rises on its jacks with its wheels hanging, the rims change in a flash, and it drops back and settles.

Each car has its own engine note, built from its real layout (cylinders, redline, crank, turbos) and its own exhaust:

| Car | Exhaust | Sound |
| --- | --- | --- |
| Ferrari 812 Superfast | Canto | naturally aspirated V12, valved to sing to 8,900 rpm |
| Koenigsegg Agera | Ghost | twin-turbo flat-plane V8, wastegates that chatter on every lift |
| Bugatti Chiron | Molsheim | four turbos into one deep W16, a rush of air on every lift |
| Koenigsegg One:1 | Megawatt | titanium with a 3D-printed tip, the flat-plane V8 at its angriest to 8,250 rpm |
| Mercedes-AMG Project One | Brixworth | a Formula One V6 to 11,000 rpm under the electric whine |

In the garage, Drive puts the car on a rolling road inside the portal: tap the start button for gas (tap again to lift),
shift with the paddles either side of the rev counter (or the arrow keys, Q and E; the space bar is the throttle).
Seven gears from each car's redline and top speed; an upshift cuts the power for a moment and the car jerks and surges
as it bites again; a downshift blips and crackles, and is refused if it would over-rev. The wheels blur, the road
streaks past and leaves blow round the car and swirl in its wake.

| Page | Folder |
| --- | --- |
| Contents | `index.html` |
| 01 Ferrari 812 Superfast | `issues/01-ferrari-812-superfast/` |
| 02 Koenigsegg Agera | `issues/02-koenigsegg-agera/` |
| 03 Bugatti Chiron | `issues/03-bugatti-chiron/` |
| 04 Koenigsegg One:1 | `issues/04-koenigsegg-one1/` |
| 05 Mercedes-AMG Project One | `issues/05-mercedes-amg-project-one/` |
| Garage library | `garage/` |

## Run it

Serve the folder over HTTP (the pages load ES modules and fetch their models): `npx serve .` or
`python3 -m http.server`. three.js 0.169 loads from jsDelivr; everything else is here.

## The models

Each car is one file, `issues/<issue>/model.glb`; the garage loads the same files. They were restyled for this site
(paint, liveries, lamps, wheels) from third-party models:

- Bugatti Chiron: model by Bob Kimani (Kimz Auto).
- Ferrari 812 Superfast, Koenigsegg Agera, Koenigsegg One:1, Mercedes-AMG Project One: models by their original
  modellers.

To re-export a car: `tools/webcar.py <car> <car>.glb --lit` (Blender's Python module, `pip install bpy==4.5.14`,
Python 3.11), from the source models. The forged rims (`rim-*.glb`) are modelled in code; `tools/webrims.py`
re-exports them.

## How it works

- `engine/scrollstage.js`: one model on a fixed transparent canvas above the page; every `data-pose` element is a
  camera stop, and the camera glides between them as you scroll. A studio environment for the reflections, and
  bloom that keeps the canvas transparent.
- `engine/carkit.js`: flake paint and liveries, wheels that turn on their true axles, a body on springs over them,
  lamps with HDR light, the forged rim library and the portal that changes them, the engine (start, idle, rev,
  overrun) and the ignition control.
- `engine/make_mag.py` + `engine/issue.html`: the five issues from one config per car. `engine/make_garage.py` +
  `engine/garage.html`: the garage.

Car names and marks belong to their makers. A portfolio piece, not affiliated with them.
