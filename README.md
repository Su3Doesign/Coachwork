# Coachwork

A car magazine you read by scrolling. Five issues, one car each, in 3D: the car sits in front of the words and moves
from spread to spread (cover, build sheet, design & stance, signature details, after dark, final impression). A garage
library holds all five cars in one page, under their names in neon, with forged rims to fit on any of them.

Every page has an ignition: a start button inside a rev counter (on each issue's cover, in its top bar and in its After
Dark spread; centre stage in the garage). Press it and the needle sweeps, the
starter turns and the engine catches; hold it to rev (the body rocks on its springs, the exhaust crackles when you lift
off), tap it again to stop. The lights switch beside it wakes the headlamps. Changing rims opens a portal on the floor:
the car rises on its jacks with its wheels hanging, the rims change in a flash, and it drops back and settles.

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

## What is not in git

The five car models are third-party downloads whose licences allow your own renders, not redistribution, so
`.gitignore` keeps them out: `issues/*/model.glb` and `garage/model-*.glb`, and the AMG side lettering. They are in
the release zip. To rebuild them: fetch the cars with car-mansion's `scripts/fetch_cars.py`, then export each one with
`tools/webcar.py <car> <car>.glb --lit` (Blender's Python module, `pip install bpy==4.5.14`, Python 3.11) and copy it
into place. The forged rims (`rim-*.glb`) are car-mansion's own, modelled in code, and are committed;
`tools/webrims.py` re-exports them.

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
