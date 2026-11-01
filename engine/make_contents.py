"""Coachwork's contents page: the five issues and the garage library, as a magazine contents spread.
    python3 make_contents.py   -> dist/contents/index.html (links from links.json)
"""
import html, json, sys
from pathlib import Path
import make_mag

HERE = Path(__file__).resolve().parent


def build(links):
    e = lambda s: html.escape(s, quote=True)
    issues = ''
    for k in make_mag.ORDER:
        c = make_mag.ISSUES[k]
        issues += (f'<a class="item" href="{e(links.get(k, "#"))}" target="_blank" rel="noopener" style="--c:{c["accent"]}">'
                   f'<span class="no">{c["no"]}</span><span class="t"><b>{e(c["make"])} {e(c["name"])}</b>'
                   f'<i>{e(c["tagline"])}</i></span><span class="y">{c["year"]}</span></a>')
    issues += (f'<a class="item" href="{e(links.get("garage", "#"))}" target="_blank" rel="noopener" style="--c:#c9a24c">'
               f'<span class="no">+</span><span class="t"><b>Garage library</b><i>All five cars in one page, and a wall of forged rims to fit them.</i></span><span class="y">Supplement</span></a>')
    return f'''<title>Coachwork Contents</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@300..700&family=Jost:wght@300;400;500&family=Cormorant+Garamond:ital,wght@1,500&display=swap">
<style>
/* Layout: the magazine's contents spread: five issues and the garage library, each a row you open. */
:root {{ --paper: #e9e7ea; --ink: #19161c; --dim: #67626d; --line: rgba(25,22,28,.18); --accent: #5b2a86;
  --head: "Oswald", "Arial Narrow", Impact, sans-serif; --thin: "Jost", "Futura", sans-serif; --serif: "Cormorant Garamond", Georgia, serif; color-scheme: light }}
* {{ box-sizing: border-box }}
html, body {{ background: var(--paper) }}
body {{ color: var(--ink); font-family: var(--thin); -webkit-font-smoothing: antialiased; padding-left: max(28px, env(safe-area-inset-left, 0px)); padding-right: max(28px, env(safe-area-inset-right, 0px)); padding-block: 40px 60px }}
.mast {{ display: flex; justify-content: space-between; align-items: baseline; gap: 16px; border-bottom: 1.5px solid var(--ink); padding-bottom: 10px; font-size: 11px; letter-spacing: .28em; text-transform: uppercase }}
.mast b {{ font-family: var(--head); font-size: 20px; letter-spacing: .06em }}
h1 {{ margin: 48px 0 8px; font-family: var(--head); font-weight: 600; font-size: clamp(72px, 14vw, 220px); line-height: .82; text-transform: uppercase }}
.lede {{ margin: 0 0 54px; font-family: var(--serif); font-style: italic; font-size: clamp(20px, 2vw, 28px); max-width: 34ch }}
h2 {{ margin: 40px 0 0; font-size: 11px; font-weight: 500; letter-spacing: .28em; text-transform: uppercase; color: var(--dim) }}
.item {{ display: grid; grid-template-columns: 80px 1fr auto; gap: 24px; align-items: baseline; padding: 22px 0; border-bottom: 1px solid var(--line); color: inherit; text-decoration: none }}
.item .no {{ font-family: var(--head); font-weight: 300; font-size: 34px; color: var(--c) }}
.item .t {{ display: grid; gap: 4px; min-width: 0 }}
.item b {{ font-family: var(--head); font-weight: 600; font-size: clamp(28px, 4vw, 54px); line-height: .95; text-transform: uppercase; transition: color .3s }}
.item i {{ font-family: var(--serif); font-size: 19px; color: var(--dim) }}
.item .y {{ font-size: 13px; letter-spacing: .2em; color: var(--dim) }}
.item:hover b, .item:focus-visible b {{ color: var(--c) }}
.item:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 4px }}
.foot {{ margin-top: 60px; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 16px; font-size: 11px; letter-spacing: .2em; text-transform: uppercase; color: var(--dim) }}
@media (max-width: 600px) {{ .item {{ grid-template-columns: 44px 1fr; gap: 14px }} .item .y {{ display: none }} .item .no {{ font-size: 24px }} }}
</style>
<header class="mast"><b>COACHWORK</b><span>Issues 01–05 · 2026</span></header>
<h1>Contents</h1>
<p class="lede">Five cars in 3D that move with the scroll, in front of the words, and a garage to fit them with new wheels.</p>
<h2>The magazine · five issues</h2>
{issues}
<div class="foot"><span>Each page opens in a new tab</span><span>Car models are third-party; names and marks belong to their makers</span></div>
'''


if __name__ == '__main__':
    links = json.loads((HERE / 'links.json').read_text())
    d = HERE / 'dist' / 'contents'; d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(build(links))
    print('contents')
