#!/usr/bin/env python3
"""Build the animated profile SVGs in assets/.

GitHub shows README images through its image proxy, which blocks external fonts,
so every font is subset to the glyphs the SVG uses and embedded as base64 woff2.
Fonts match kadirhanemrememis.xyz: Fraunces (display), Inter (text), JetBrains Mono.

Besides the two banners (hero, Git Hospital) it builds the data cards from data.json
(see DESIGN.md): every card is written twice, `<name>.svg` (1200 units wide) and
`<name>-phone.svg` (440 units wide), and README.md is written from the same data.

Usage (needs fonttools + brotli, e.g. in assets/src/.venv):
    python3 assets/src/build.py                        # writes assets/*.svg and README.md
    python3 assets/src/build.py --theme dark --out DIR   # preview build, nothing committed is touched
"""
import argparse
import base64
import json
import math
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(__file__).resolve().parent / ".fonts"
CDN = "https://cdn.jsdelivr.net/npm/@fontsource"

FONTS = {
    "F": f"{CDN}/fraunces@5.1.0/files/fraunces-latin-600-normal.woff2",
    "I4": f"{CDN}/inter@5.1.0/files/inter-latin-400-normal.woff2",
    "I5": f"{CDN}/inter@5.1.0/files/inter-latin-500-normal.woff2",
    "J": f"{CDN}/jetbrains-mono@5.1.0/files/jetbrains-mono-latin-500-normal.woff2",
    "Jx": f"{CDN}/jetbrains-mono@5.1.0/files/jetbrains-mono-latin-ext-500-normal.woff2",
}

# Palette of the portfolio ("workshop at night").
BG, SURFACE, BORDER = "#0c0a09", "#171310", "#3a2f28"
INK50, INK200, INK400, INK600 = "#f4ece2", "#d1c3b4", "#968779", "#695c51"
RED, AMBER = "#c7331e", "#d9a441"


_TT: dict = {}


def _font(key: str):
    """Cached fontTools handle: (cmap, hmtx, units per em)."""
    if key not in _TT:
        from fontTools.ttLib import TTFont
        src = CACHE / f"{key}.woff2"
        if not src.exists():
            CACHE.mkdir(exist_ok=True)
            urllib.request.urlretrieve(FONTS[key], src)
        f = TTFont(src)
        _TT[key] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _TT[key]


FAMILY_KEYS = {"display": ("F",), "sans": ("I4",), "mono": ("J", "Jx")}


def measure(family: str, s: str, size: float, spacing: float = 0.0) -> float:
    """Advance width of s in user units, from the real glyph advances (no kerning)."""
    total = 0.0
    for ch in s:
        for key in FAMILY_KEYS[family]:
            cmap, hmtx, upm = _font(key)
            if ord(ch) in cmap:
                total += hmtx[cmap[ord(ch)]][0] / upm * size + spacing
                break
        else:
            raise ValueError(f"no glyph for {ch!r} (U+{ord(ch):04X}) in {family}")
    return total


def wrap(family: str, s: str, size: float, width: float, spacing: float = 0.0) -> list:
    """Greedy word wrap by measured advance."""
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}" if cur else word
        if cur and measure(family, trial, size, spacing) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def ellipsize(family: str, s: str, size: float, width: float) -> str:
    if measure(family, s, size) <= width:
        return s
    while s and measure(family, s.rstrip() + "…", size) > width:
        s = s[:-1]
    return s.rstrip() + "…"


def font_face(key: str, family: str, text: str, weight: int = 400, latin_ext: bool = False) -> str:
    CACHE.mkdir(exist_ok=True)
    src = CACHE / f"{key}.woff2"
    if not src.exists():
        urllib.request.urlretrieve(FONTS[key], src)
    with tempfile.NamedTemporaryFile(suffix=".woff2") as out:
        subprocess.run(
            [sys.executable, "-m", "fontTools.subset", str(src), f"--text={text}", "--flavor=woff2",
             "--layout-features=kern,liga", f"--output-file={out.name}"],
            check=True,
        )
        data = base64.b64encode(Path(out.name).read_bytes()).decode()
    rng = "unicode-range: U+0100-024F; " if latin_ext else ""
    return (f"@font-face {{ font-family: '{family}'; font-weight: {weight}; {rng}"
            f"src: url(data:font/woff2;base64,{data}) format('woff2'); }}")


def text(x, y, cls, s, **attrs) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<text class="{cls}" x="{x}" y="{y}"{extra}>{escape(s)}</text>'


def svg(width, height, label, styles, body) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(label, {chr(34): "&quot;"})}">\n'
        f"<style>\n{styles}\n</style>\n{body}\n</svg>\n"
    )


def build_fonts(strings: dict) -> str:
    # strings: css family -> text used in that family
    faces = []
    if strings.get("display"):
        faces.append(font_face("F", "Display", strings["display"], 600))
    if strings.get("sans4"):
        faces.append(font_face("I4", "Sans", strings["sans4"], 400))
    if strings.get("sans5"):
        faces.append(font_face("I5", "Sans", strings["sans5"], 500))
    if strings.get("mono"):
        mono = strings["mono"]
        faces.append(font_face("J", "Mono", mono, 500))
        ext = "".join(sorted({c for c in mono if 0x100 <= ord(c) <= 0x24F}))
        if ext:
            faces.append(font_face("Jx", "Mono", ext, 500, latin_ext=True))
    return "\n".join(faces)


COMMON_CSS = f"""
.display {{ font: 600 76px 'Display', Georgia, serif; fill: {INK50}; letter-spacing: -1.5px; }}
.title   {{ font: 500 28px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK200}; }}
.body    {{ font: 400 20px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK400}; }}
.mono    {{ font: 500 15px 'Mono', 'SFMono-Regular', Menlo, Consolas, monospace; fill: {INK400}; letter-spacing: .3px; }}
.rise    {{ opacity: 0; animation: rise .9s ease-out forwards; }}
.grow    {{ transform-box: fill-box; transform-origin: left; animation: grow 1.1s ease-out .5s both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
"""

REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; opacity: 1 !important; } }"


def dot_grid(w, h, rx) -> str:
    return (
        f'<defs><pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1" fill="{INK50}" fill-opacity=".07"/></pattern>'
        f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
    )


# ---------------------------------------------------------------- hero

def orbit(cx, cy) -> str:
    """Three counter-rotating rings of nodes (a service mesh) with a radar sweep
    and a pulsing cross at the centre (the Git Hospital mark)."""
    rings = [  # radius, node count, seconds per turn (negative = counter-clockwise), phase
        (72, 3, 16, 10),
        (128, 5, -26, 40),
        (184, 7, 38, 5),
    ]
    out = [
        f'<radialGradient id="glow" cx="{cx}" cy="{cy}" r="230" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{RED}" stop-opacity=".22"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/>'
        f"</radialGradient>",
        f'<circle cx="{cx}" cy="{cy}" r="230" fill="url(#glow)"/>',
    ]
    # sweep: a 50 degree wedge that fades towards its trailing edge
    r = 196
    a0, a1 = math.radians(-50), 0.0
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    out.append(
        f'<linearGradient id="sweep" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset="1" stop-color="{RED}" stop-opacity=".32"/>'
        f"</linearGradient>"
        f'<g class="spin" style="animation-duration:6s">'
        f'<path d="M{cx} {cy} L{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f} Z" fill="url(#sweep)"/>'
        f'<line x1="{cx}" y1="{cy}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{RED}" stroke-width="2" stroke-linecap="round"/>'
        f"</g>"
    )
    for i, (radius, n, secs, phase) in enumerate(rings):
        dash = ' stroke-dasharray="2 7"' if i == 2 else ""
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{INK600}" stroke-opacity=".55"{dash}/>')
        pts = [
            (cx + radius * math.cos(math.radians(phase + k * 360 / n)),
             cy + radius * math.sin(math.radians(phase + k * 360 / n)))
            for k in range(n)
        ]
        g = [f'<g class="spin" style="animation-duration:{abs(secs)}s;animation-direction:{"reverse" if secs < 0 else "normal"}">']
        for k in range(n):  # chords to the next-but-one node: a mesh, not a polygon
            (ax, ay), (bx, by) = pts[k], pts[(k + 2) % n] if n > 3 else pts[(k + 1) % n]
            g.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{INK200}" stroke-opacity=".10"/>')
        for k, (px, py) in enumerate(pts):
            if i == 1 and k == 0:
                g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" fill="{RED}" fill-opacity=".18"/>')
                g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{RED}"/>')
            elif k % 3 == 1:
                g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{AMBER}"/>')
            else:
                g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{BG}" stroke="{INK50}" stroke-width="2"/>')
        g.append("</g>")
        out.extend(g)
    # the cross
    s, t = 15, 5.5
    out.append(
        f'<g class="beat"><rect x="{cx - t}" y="{cy - s}" width="{2 * t}" height="{2 * s}" rx="2" fill="{RED}"/>'
        f'<rect x="{cx - s}" y="{cy - t}" width="{2 * s}" height="{2 * t}" rx="2" fill="{RED}"/></g>'
    )
    return "\n".join(out)


def contact_icon(kind, x, cy) -> str:
    """16 px line icons, vertically centred on cy."""
    st = f'fill="none" stroke="{RED}" stroke-width="1.6"'
    if kind == "web":
        return (f'<circle cx="{x + 8}" cy="{cy}" r="7.5" {st}/><ellipse cx="{x + 8}" cy="{cy}" rx="3.2" ry="7.5" {st}/>'
                f'<line x1="{x + .5}" y1="{cy}" x2="{x + 15.5}" y2="{cy}" {st}/>')
    if kind == "in":
        return (f'<rect x="{x}" y="{cy - 8}" width="16" height="16" rx="3" fill="{RED}"/>'
                f'<text x="{x + 8}" y="{cy + 4.5}" text-anchor="middle" '
                f'style="font: 500 11px \'Mono\', monospace; fill: {BG}">in</text>')
    return (f'<rect x="{x}" y="{cy - 6}" width="16" height="12" rx="2" {st}/>'
            f'<path d="M{x + 1} {cy - 5} L{x + 8} {cy + 1} L{x + 15} {cy - 5}" {st}/>')


def hero(phone=False) -> str:
    W, H = (440, 0) if phone else (1200, 516)
    cx, cy = 958, 235
    kicker = "kassvl  /  Wrocław, PL"
    name = "Kadirhan Emre"
    role = "Software Engineer"
    para = [
        "I build web products end to end: React and Next.js",
        "front ends, APIs in Python, TypeScript and Go,",
        "PostgreSQL, and the Docker, CI and cloud setup",
        "that ships them. Maintainer of Git Hospital and Nordstjernen.",
    ]
    stack = "TypeScript  React  Next.js  Python  FastAPI  Go  PostgreSQL  Docker  Kubernetes  AWS"
    contacts = [("web", "kadirhanemrememis.xyz"), ("in", "linkedin.com/in/kadirhan-emre"),
                ("mail", "kadirhanemre@proton.me")]
    fonts = build_fonts({
        "display": name, "sans5": role, "sans4": "".join(para), "mono": kicker + stack + "in" + "".join(c for _, c in contacts) + "·",
    })
    css = fonts + COMMON_CSS + f"""
.spin {{ transform-origin: {cx}px {cy}px; animation: spin linear infinite; }}
.contact {{ fill: {INK200}; }}
.beat {{ transform-origin: {cx}px {cy}px; animation: beat 1.6s ease-in-out infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes beat {{ 0%, 60%, 100% {{ transform: scale(1); }} 15% {{ transform: scale(1.22); }} 30% {{ transform: scale(.94); }} 42% {{ transform: scale(1.12); }} }}
""" + REDUCED
    if phone:
        body, H = _hero_phone_body(W, cx, cy, kicker, name, role, para, stack, contacts)
    else:
        body = _hero_body(W, H, cx, cy, kicker, name, role, para, stack, contacts)
    label = (f"{name}, {role}. " + " ".join(para) + " Stack: " + stack.replace("  ", ", ") + ". "
             + " | ".join(c for _, c in contacts))
    return svg(W, H, label, css, "\n".join(body))


def _hero_body(W, H, cx, cy, kicker, name, role, para, stack, contacts):
    body = [
        dot_grid(W, H, 18),
        '<g clip-path="url(#frame)">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        orbit(cx, cy),
        f'<rect x="70" y="78" width="9" height="9" fill="{RED}"/>',
        text(90, 88, "mono rise", kicker, style="animation-delay:.1s"),
        text(66, 172, "display rise", name, style="animation-delay:.2s"),
        f'<rect class="grow" x="70" y="198" width="88" height="4" rx="2" fill="{RED}"/>',
        text(70, 248, "title rise", role, style="animation-delay:.6s"),
    ]
    for k, line in enumerate(para):
        body.append(text(70, 298 + 30 * k, "body rise", line, style=f"animation-delay:{.8 + .08 * k:.2f}s"))
    body.append(f'<line x1="70" y1="418" x2="{W - 70}" y2="418" stroke="{BORDER}"/>')
    body.append(text(70, 446, "mono rise", stack.replace("  ", "  ·  "), style="animation-delay:1.3s"))
    x = 70
    for k, (icon, value) in enumerate(contacts):
        body.append(f'<g class="rise" style="animation-delay:{1.4 + .1 * k:.1f}s">{contact_icon(icon, x, 478)}'
                    + text(x + 26, 484, "mono contact", value) + "</g>")
        x += 26 + 9.3 * len(value) + 44
    body.append("</g>")
    return body


def _hero_phone_body(W, cx, cy, kicker, name, role, para, stack, contacts):
    """Stacked layout: the orbit on top, then name, role, sentence, stack and contacts."""
    px, width = 40, W - 80
    k, ocx, ocy = .62, W / 2, 140
    body = [
        f'<g transform="translate({ocx} {ocy}) scale({k}) translate({-cx} {-cy})">{orbit(cx, cy)}</g>',
        f'<rect x="{px}" y="302" width="9" height="9" fill="{RED}"/>',
        text(px + 20, 312, "mono rise", kicker, style="animation-delay:.1s"),
    ]
    size = min(76, 76 * width / measure("display", name, 76, -1.5))  # fit the name to the column
    body.append(text(px - 3, 312 + 30 + size * .78, "display rise", name,
                     style=f"animation-delay:.2s;font-size:{size:.1f}px"))
    y = 312 + 30 + size * .78 + 26
    body.append(f'<rect class="grow" x="{px}" y="{y:.0f}" width="88" height="4" rx="2" fill="{RED}"/>')
    y += 52
    body.append(text(px, y, "title rise", role, style="animation-delay:.6s"))
    y += 52
    for i, line in enumerate(wrap("sans", " ".join(para), 20, width)):
        body.append(text(px, y, "body rise", line, style=f"animation-delay:{.8 + .08 * i:.2f}s"))
        y += 30
    y += 14
    body.append(f'<line x1="{px}" y1="{y:.0f}" x2="{W - px}" y2="{y:.0f}" stroke="{BORDER}"/>')
    y += 34
    sep, cur, rows = "  ·  ", "", []
    for item in stack.split("  "):          # break between items, never next to a separator
        trial = cur + sep + item if cur else item
        if cur and measure("mono", trial, 15, .3) > width:
            rows.append(cur)
            cur = item
        else:
            cur = trial
    for line in rows + [cur]:
        body.append(text(px, y, "mono rise", line, style="animation-delay:1.3s"))
        y += 26
    y += 12
    for i, (icon, value) in enumerate(contacts):
        body.append(f'<g class="rise" style="animation-delay:{1.4 + .1 * i:.1f}s">{contact_icon(icon, px, y - 6)}'
                    + text(px + 26, y, "mono contact", value) + "</g>")
        y += 34
    H = int(y + 6)
    return [dot_grid(W, H, 18), '<g clip-path="url(#frame)">',
            f'<rect width="{W}" height="{H}" fill="{BG}"/>', f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
            *body, "</g>"], H


# ---------------------------------------------------------------- Git Hospital card

BLUE = "#3b82f6"


def ambulance() -> str:
    """An ambulance facing right, drawn around its rear bottom corner (0, 0)."""
    glass, tyre = "#2b3138", "#1b1714"
    lights = "".join(
        f'<circle class="flash {cls}" cx="{x}" cy="-82" r="22" fill="url(#glow-{c})"/>'
        f'<rect class="flash {cls}" x="{x - 6}" y="-87" width="12" height="9" rx="2" fill="{col}"/>'
        for x, c, col, cls in ((156, "r", RED, "fa"), (170, "b", BLUE, "fb"))
    )
    waves = "".join(
        f'<circle class="wave" cx="163" cy="-83" r="16" fill="none" stroke="{RED if k % 2 == 0 else BLUE}" '
        f'stroke-width="2" style="animation-delay:{k * .45:.2f}s"/>'
        for k in range(3)
    )
    def wheel(x):
        spokes = "".join(
            f'<line x1="{x}" y1="-12" x2="{x + 7 * math.cos(a):.1f}" y2="{-12 + 7 * math.sin(a):.1f}" '
            f'stroke="{INK400}" stroke-width="2"/>'
            for a in (0, 2.094, 4.189)
        )
        return (f'<circle cx="{x}" cy="-12" r="13" fill="{tyre}" stroke="{INK600}" stroke-width="3"/>'
                f'<g class="wheel">{spokes}<circle cx="{x}" cy="-12" r="2.5" fill="{INK200}"/></g>')
    return "".join([
        # speed lines
        *(f'<line class="speed" x1="{-70 + d}" y1="{y}" x2="{-18}" y2="{y}" stroke="{INK400}" stroke-width="2" '
          f'stroke-linecap="round" style="animation-delay:{d / 100:.2f}s"/>'
          for y, d in ((-62, 0), (-44, 22), (-26, 10))),
        # headlight beam
        f'<path d="M204 -27 L300 -52 L300 -2 Z" fill="url(#beam)"/>',
        f'<ellipse cx="103" cy="0" rx="112" ry="5" fill="#000" fill-opacity=".45"/>',
        waves,
        # body and cab
        f'<rect x="0" y="-80" width="146" height="66" rx="6" fill="{INK50}"/>',
        f'<path d="M140 -80 L170 -80 L196 -52 L207 -47 L207 -20 Q207 -14 201 -14 L140 -14 Z" fill="{INK50}"/>',
        f'<path d="M150 -72 L167 -72 L187 -52 L150 -52 Z" fill="{glass}"/>',
        f'<rect x="0" y="-38" width="207" height="7" fill="{RED}"/>',
        f'<rect x="60" y="-68" width="8" height="24" rx="1.5" fill="{RED}"/><rect x="52" y="-60" width="24" height="8" rx="1.5" fill="{RED}"/>',
        f'<line x1="140" y1="-50" x2="140" y2="-16" stroke="{INK400}" stroke-opacity=".6"/>',
        f'<rect x="200" y="-30" width="7" height="6" rx="1.5" fill="{AMBER}"/>',
        f'<rect x="-3" y="-22" width="8" height="6" rx="1.5" fill="{RED}"/>',
        f'<rect x="146" y="-82" width="34" height="4" rx="2" fill="{INK400}"/>',
        lights,
        wheel(42), wheel(168),
    ])


def city(x0, x1, road, avoid) -> str:
    """Night skyline with lit windows; deterministic so rebuilds give the same city."""
    import random
    rnd = random.Random(7)
    out, x = [], x0
    while x < x1:
        w = rnd.choice((54, 66, 78, 90))
        h = rnd.randint(58, 96)
        top = road - h
        out.append(f'<rect x="{x}" y="{top}" width="{w - 6}" height="{h}" fill="#211b17"/>')
        for wy in range(top + 10, road - 12, 14):
            for wx in range(x + 8, x + w - 14, 12):
                if avoid[0] < wx < avoid[2] and avoid[1] < wy < avoid[3]:
                    continue
                r = rnd.random()
                if r < .26:
                    col = AMBER if r < .2 else "#cfe3ff"
                    cls = ' class="flicker"' if rnd.random() < .08 else ""
                    out.append(f'<rect{cls} x="{wx}" y="{wy}" width="5" height="7" fill="{col}" fill-opacity="{.25 + rnd.random() * .3:.2f}"/>')
        x += w
    return "".join(out)


def street_lamp(x, road) -> str:
    return (f'<path d="M{x - 70} {road} L{x - 8} 98 L{x + 8} 98 L{x + 70} {road} Z" fill="url(#lamp)"/>'
            f'<line x1="{x + 22}" y1="{road}" x2="{x + 22}" y2="92" stroke="#3a2f28" stroke-width="3"/>'
            f'<path d="M{x + 22} 92 Q{x + 22} 84 {x + 12} 86 L{x} 90" fill="none" stroke="#3a2f28" stroke-width="3"/>'
            f'<rect x="{x - 9}" y="89" width="16" height="6" rx="2" fill="{AMBER}"/>')


def hospital(road) -> str:
    """Hospital with an emergency bay; the bay opening is x 150-240."""
    wins = "".join(
        f'<rect x="{wx}" y="{wy}" width="9" height="7" fill="#cfe3ff" fill-opacity="{.22 + ((wx * 7 + wy) % 5) * .07:.2f}"/>'
        for wy in (56, 70) for wx in range(116, 236, 16)
    )
    return "".join([
        f'<rect x="40" y="44" width="210" height="{road - 44}" fill="#2a221d"/>',
        f'<rect x="40" y="44" width="210" height="4" fill="#3a2f28"/>',
        wins,
        # lit cross on the facade
        f'<circle cx="78" cy="74" r="30" fill="url(#crossglow)" class="buzz"/>',
        f'<rect x="72" y="58" width="12" height="32" rx="2" fill="{RED}"/><rect x="62" y="68" width="32" height="12" rx="2" fill="{RED}"/>',
        # emergency sign and bay
        f'<rect x="146" y="80" width="98" height="14" rx="2" fill="{RED}" class="buzz"/>',
        f'<text x="195" y="91" text-anchor="middle" style="font: 500 10px \'Mono\', monospace; fill: {INK50}; letter-spacing: 1.5px">EMERGENCY</text>',
        f'<rect x="150" y="97" width="90" height="{road - 97}" fill="url(#bay)"/>',
        f'<rect x="150" y="97" width="90" height="4" fill="#3a2f28"/>',
        f'<rect x="58" y="128" width="70" height="{road - 128}" fill="#1b1714"/>',
        f'<line x1="93" y1="128" x2="93" y2="{road}" stroke="#3a2f28"/>',
    ])


def git_hospital(phone=False) -> str:
    W = 1200        # width of the scene (the phone version scales it by .5)
    if phone:
        W = 880
    road, park = 182, 700  # road line; where the ambulance stands when motion is off
    bay = 150              # left edge of the emergency bay
    tx = 292               # title x
    title = "Git Hospital"
    url = "github.com/Git-Hospital"
    lead = "Open-source tools that diagnose infrastructure and code, with the evidence for every diagnosis."
    moon = 820 if phone else 1062
    mono = url + "EMERGENCY"
    fonts = build_fonts({"display": title, "sans4": lead, "mono": mono})
    start, stop = bay - 210 - park, W + 120 - park
    css = fonts + COMMON_CSS + f"""
.gh-title {{ font: 600 68px 'Display', Georgia, serif; fill: {INK50}; letter-spacing: -1px;
            paint-order: stroke; stroke: {SURFACE}; stroke-width: 10px; stroke-linejoin: round; }}
.lead {{ font: 400 20px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK200}; }}
.drive {{ animation: drive 9s cubic-bezier(.4,0,.7,1) infinite; }}
.titlefade {{ animation: titlefade 9s linear infinite; }}
.wheel {{ transform-box: fill-box; transform-origin: center; animation: spin .45s linear infinite; }}
.flash {{ animation: flash .5s steps(1) infinite; }}
.fb {{ animation-delay: .25s; }}
.wave {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: wave 1.35s ease-out infinite; }}
.speed {{ animation: speed .5s ease-in-out infinite alternate; }}
.flicker {{ animation: flicker 3.7s steps(1) infinite; }}
.buzz {{ animation: buzz 4.3s steps(1) infinite; }}
@keyframes drive {{ 0%, 10% {{ transform: translateX({start}px); }} 56%, 100% {{ transform: translateX({stop}px); }} }}
@keyframes titlefade {{ 0%, 88% {{ opacity: 1; }} 96%, 100% {{ opacity: 0; }} }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes flash {{ 0% {{ opacity: 1; }} 50% {{ opacity: .12; }} }}
@keyframes wave {{ 0% {{ opacity: .9; transform: scale(.5); }} 100% {{ opacity: 0; transform: scale(2.6); }} }}
@keyframes speed {{ from {{ opacity: .15; }} to {{ opacity: .7; }} }}
@keyframes flicker {{ 0%, 70% {{ opacity: 1; }} 72% {{ opacity: .2; }} 76%, 100% {{ opacity: 1; }} }}
@keyframes buzz {{ 0%, 90% {{ opacity: 1; }} 91% {{ opacity: .55; }} 93% {{ opacity: 1; }} 95% {{ opacity: .7; }} 96%, 100% {{ opacity: 1; }} }}
@media (prefers-reduced-motion: reduce) {{ .wave, .speed {{ opacity: 0 !important; }} }}
""" + REDUCED
    defs = (
        f'<defs><clipPath id="trail"><rect class="drive" x="{park - 2400}" y="0" width="2400" height="{road + 10}"/></clipPath>'
        # the ambulance is visible inside the bay opening and anywhere right of the building
        f'<clipPath id="street"><rect x="{bay}" y="101" width="100" height="{road - 101 + 20}"/><rect x="250" y="0" width="{W}" height="{road + 60}"/></clipPath>'
        f'<radialGradient id="glow-r"><stop offset="0" stop-color="{RED}" stop-opacity=".75"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glow-b"><stop offset="0" stop-color="{BLUE}" stop-opacity=".75"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="crossglow"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="bay" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".35"/><stop offset=".5" stop-color="#120f0d"/><stop offset="1" stop-color="#0c0a09"/></linearGradient>'
        f'<linearGradient id="lamp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".22"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AMBER}" stop-opacity=".45"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient></defs>'
    )
    scene = [
        (f'<circle cx="{moon}" cy="64" r="15" fill="{INK200}" fill-opacity=".85"/>'
         f'<circle cx="{moon + 7}" cy="59" r="13" fill="{SURFACE}"/>'),
        city(262, W, road, (tx - 10, 96, tx + 420, 172)),
        *(street_lamp(x, road) for x in (760, 1070) if x < W),
        hospital(road),
        f'<rect x="0" y="{road}" width="{W}" height="12" fill="#100d0b"/>',
        f'<line x1="0" y1="{road}" x2="{W}" y2="{road}" stroke="{INK600}" stroke-opacity=".8"/>',
        f'<line x1="250" y1="{road + 6}" x2="{W}" y2="{road + 6}" stroke="{INK600}" stroke-opacity=".6" stroke-dasharray="22 16"/>',
        # the name is painted only where the ambulance has already been
        f'<g clip-path="url(#trail)"><g class="titlefade">{text(tx, 160, "gh-title", title)}</g></g>',
        f'<g clip-path="url(#street)"><g transform="translate({park} {road})"><g class="drive">{ambulance()}</g></g></g>',
    ]
    if phone:
        OW, k = 440, .5
        scene_h = (road + 12) * k
        lines = wrap("sans", lead, 20, OW - 80)
        y = scene_h + 40
        texts = [text(40, y + 30 * i, "lead rise", ln, style="animation-delay:.3s") for i, ln in enumerate(lines)]
        y += 30 * (len(lines) - 1) + 38
        texts.append(text(40, y, "mono rise", url, style="animation-delay:.4s"))
        H = int(y + 30)
        body = [dot_grid(OW, H, 18), defs, '<g clip-path="url(#frame)">',
                f'<rect width="{OW}" height="{H}" fill="{SURFACE}"/>',
                f'<rect width="{OW}" height="{H}" fill="url(#dots)"/>',
                f'<g transform="scale({k})">{"".join(scene)}</g>', *texts, "</g>"]
        W = OW
    else:
        H = 272
        body = [dot_grid(W, H, 18), defs, '<g clip-path="url(#frame)">',
                f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
                f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
                *scene,
                text(W - 70, 40, "mono rise", url, text_anchor="end"),
                text(70, 238, "lead rise", lead, style="animation-delay:.3s"), "</g>"]
    label = f"{title}: {lead} An ambulance drives out of a hospital's emergency bay and the name appears behind it."
    return svg(W, H, label, css, "\n".join(body))


# ---------------------------------------------------------------- data cards (DESIGN.md)

DATA = Path(__file__).resolve().parent / "data.json"

# name: (dark, light). The two halves of every card's theme come from this table.
THEME_VARS = {
    "bg": ("#0c0a09", "#ffffff"), "raised": ("#171310", "#f6f9fc"), "border": ("#3a2f28", "#d6e0e9"),
    "strong": ("#f4ece2", "#0f1c2a"), "body": ("#d1c3b4", "#2d3d4e"), "muted": ("#968779", "#5e7082"),
    "vital": ("#c7331e", "#dc383e"), "review": ("#d9a441", "#a8720f"), "merged": ("#7fb069", "#16803f"),
    "trace": ("#c7331e", "#0f1c2a"),            # the trace itself: vital red on the monitor, ink on ECG paper
    "glow": (".3", "0"), "dots": (".1", "0"), "paper": ("0", "1"),
}


def theme_css(theme=None) -> str:
    def block(i):
        return "; ".join(f"--{k}: {v[i]}" for k, v in THEME_VARS.items())
    if theme == "dark":
        return f"svg {{ {block(0)} }}"
    if theme == "light":
        return f"svg {{ {block(1)} }}"
    return f"svg {{ {block(0)} }}\n@media (prefers-color-scheme: light) {{ svg {{ {block(1)} }} }}"


SERIF = "'Display', Georgia, serif"
SANS = "'Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Mono', 'SFMono-Regular', Menlo, Consolas, monospace"
CARD_CSS = f"""
.shell {{ fill: var(--bg); stroke: var(--border); }}
.n    {{ font: 600 28px {SERIF}; fill: var(--strong); }}
.num  {{ font: 600 56px {SERIF}; fill: var(--strong); }}
.s    {{ font: 400 20px {SANS}; fill: var(--body); }}
.st   {{ font: 400 20px {SANS}; fill: var(--strong); }}
.d    {{ font: 500 16px {MONO}; fill: var(--muted); }}
.db   {{ font: 500 16px {MONO}; fill: var(--body); }}
.hair {{ stroke: var(--border); }}
.pill {{ fill: none; stroke: var(--muted); }}
.dm   {{ fill: var(--merged); }}
.dr   {{ fill: var(--review); }}
"""
CLASS_FAMILY = {"n": "display", "num": "display", "s": "sans", "st": "sans", "d": "mono", "db": "mono"}
PAD, PT = 40, 30          # side padding, top and bottom padding of a row
DW, PW = 1200, 440        # desktop and phone viewBox widths


class Canvas:
    """Collects the elements of one card and the glyphs each font family has to carry."""

    def __init__(self, width):
        self.W, self.el = width, []
        self.chars = {"display": set(), "sans": set(), "mono": set()}

    def t(self, x, y, cls, s, anchor=None, style=None):
        self.chars[CLASS_FAMILY[cls]].update(s)
        extra = {}
        if anchor:
            extra["text_anchor"] = anchor
        if style:
            extra["style"] = style
        self.el.append(text(round(x, 1), round(y, 1), cls, s, **extra))

    def add(self, markup):
        self.el.append(markup)

    def render(self, H, label, theme, css=""):
        join = lambda k: "".join(sorted(self.chars[k]))
        fonts = build_fonts({"display": join("display"), "sans4": join("sans"), "mono": join("mono")})
        body = (f'<rect class="shell" x=".5" y=".5" width="{self.W - 1}" height="{H - 1}" rx="18"/>\n'
                + "\n".join(self.el))
        return svg(self.W, H, label, fonts + "\n" + theme_css(theme) + CARD_CSS + css, body)


def fmt(n) -> str:
    return f"{n:,}"


def plural(n, word) -> str:
    return f"{fmt(n)} {word}" + ("" if n == 1 else "s")


def pill(c, x, base, s):
    """Outlined status pill whose first text baseline is `base`; x is its left edge (None: right-aligned)."""
    w = measure("mono", s, 16) + 28
    if x is None:
        x = c.W - PAD - w
    c.add(f'<rect class="pill" x="{x:.1f}" y="{base - 21:.1f}" width="{w:.1f}" height="30" rx="15"/>')
    c.t(x + w / 2, base - 1, "db", s, anchor="middle")
    return w


def lines_at(c, x, y, cls, lines, step=30):
    """Draw lines from baseline y; returns the last baseline."""
    for i, ln in enumerate(lines):
        c.t(x, y + step * i, cls, ln)
    return y + step * (len(lines) - 1)


# ---- rows: each draws at y (top of the row, padding included) and returns its height

def row_tool(c, y, r, phone):
    base = y + PT + 24
    c.t(PAD, base, "n", r["name"])
    if phone:
        last = lines_at(c, PAD, base + 38, "s", wrap("sans", r["desc"], 20, c.W - 2 * PAD))
        top = last + 22
        pill(c, PAD, top + 21, r["status"])
        return top + 30 + PT - y
    pw = measure("mono", r["status"], 16) + 28
    right = c.W - PAD - pw - 40
    last = lines_at(c, 350, base, "s", wrap("sans", r["desc"], 20, right - 350))
    pill(c, None, base, r["status"])
    return last + 10 + PT - y


OS_NAME_W = 290   # name column, x 40 to 330


def _repo_name(c, x, base, name):
    size = 28.0
    w = measure("display", name, size)
    if w > OS_NAME_W:
        size = max(22.0, size * OS_NAME_W / w)
    c.t(x, base, "n", name, style=f"font-size:{size:.1f}px" if size != 28 else None)


def _counts(r):
    out = [("dm", f"{fmt(r['merged'])} merged")]
    if r["open"]:
        out.append(("dr", f"{fmt(r['open'])} in review"))
    return out


def row_os(c, y, r, phone):
    """Open source row. Desktop grid: L1 owner, L2 name / PR title / merged, L3 stars / date / in review."""
    y0 = y + PT
    L1, L2, L3 = y0 + 12, y0 + 46, y0 + 74
    static = "sentence" in r
    c.t(PAD, L1, "d", r["owner"])
    _repo_name(c, PAD, L2, r["repo"])
    if not static:
        c.t(PAD, L3, "d", plural(r["stars"], "star"))
    if phone:
        base = (L2 if static else L3) + 38
        if static:
            last = lines_at(c, PAD, base, "st", wrap("sans", r["sentence"], 20, c.W - 2 * PAD))
            pill(c, PAD, last + 43, r["state"])
            return last + 43 + 9 + PT - y
        last = base - 30
        if r.get("title"):
            ls = wrap("sans", r["title"], 20, c.W - 2 * PAD)
            if len(ls) > 2:   # at most two lines, the ellipsis ends the second
                ls = [ls[0], ellipsize("sans", " ".join(ls[1:]), 20, c.W - 2 * PAD)]
            last = lines_at(c, PAD, base, "st", ls)
            c.t(PAD, last + 28, "d", f"merged {r['date']}")
            last += 28
        x = PAD
        for dot, label in _counts(r):
            c.add(f'<circle class="{dot}" cx="{x + 5}" cy="{last + 36.5}" r="5"/>')
            c.t(x + 18, last + 42, "db", label)
            x += 18 + measure("mono", label, 16) + 26
        return last + 42 + 8 + PT - y
    if static:
        c.t(350, L2, "st", r["sentence"])
        pill(c, None, L2, r["state"])
    else:
        right = c.W - PAD
        counts = _counts(r)
        left = right - max(measure("mono", lb, 16) for _, lb in counts) - 18 - 40
        if r.get("title"):
            c.t(350, L2, "st", ellipsize("sans", r["title"], 20, left - 350))
            c.t(350, L3, "d", f"merged {r['date']}")
        for (dot, label), by in zip(counts, (L2, L3)):
            c.t(right, by, "db", label, anchor="end")
            c.add(f'<circle class="{dot}" cx="{right - measure("mono", label, 16) - 14:.1f}" cy="{by - 5.5}" r="5"/>')
    return (y0 + 84) + PT - y


def row_work(c, y, r, phone):
    """Work and team row: name (+ place) left, sentence (+ Built with) right; stacked on phones."""
    base = y + PT + 24
    c.t(PAD, base, "n", r["name"])
    built = f"Built with {r['built']}" if r.get("built") else None
    if phone:
        yy = base
        if r.get("place"):
            c.t(PAD, base + 28, "d", r["place"])
            yy = base + 28
        last = lines_at(c, PAD, yy + 38, "s", wrap("sans", r["sentence"], 20, c.W - 2 * PAD))
        if built:
            last = lines_at(c, PAD, last + 32, "d", wrap("mono", built, 16, c.W - 2 * PAD), step=24)
        return last + 10 + PT - y
    left_bottom = base
    if r.get("place"):
        c.t(PAD, base + 30, "d", r["place"])
        left_bottom = base + 30
    last = lines_at(c, 350, base, "s", wrap("sans", r["sentence"], 20, c.W - PAD - 350))
    if built:
        last = lines_at(c, 350, last + 32, "d", wrap("mono", built, 16, c.W - PAD - 350), step=24)
    return max(last, left_bottom) + 10 + PT - y


ROW_FN = {"tool": row_tool, "os": row_os, "work": row_work}


def rows_card(rows, phone, theme, label):
    c = Canvas(PW if phone else DW)
    y = 0
    for i, r in enumerate(rows):
        if i:
            c.add(f'<line class="hair" x1="{PAD}" y1="{y}" x2="{c.W - PAD}" y2="{y}"/>')
        y += ROW_FN[r["kind"]](c, y, r, phone)
    return c.render(int(y), label, theme)


# ---- the vitals card

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def scale_for(weeks):
    """Ceiling = second-highest week rounded up to the next 50 (at least 50) and the reference-line step."""
    counts = sorted((w["count"] for w in weeks), reverse=True)
    second = counts[1] if len(counts) > 1 else counts[0]
    ceiling = max(50, math.ceil(second / 50) * 50)
    step = next(s for s in (10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000) if ceiling / s <= 3.5)
    return ceiling, step


def week_points(weeks, x0, step, base, top, ceiling):
    """One heartbeat per week; apex height is linear in the count from zero up to the ceiling,
    a week above it is drawn to the top edge."""
    span = base - top
    pts, apexes = [(x0, base)], {}
    for i, w in enumerate(weeks):
        a = x0 + i * step
        h = min(w["count"], ceiling) / ceiling * span
        if h > 0:
            dip, und = min(.12 * h, 9), min(.16 * h, 14)
            pts += [(a + .2 * step, base), (a + .32 * step, base + dip), (a + .46 * step, base - h),
                    (a + .6 * step, base + und), (a + .72 * step, base)]
            apexes[i] = (a + .46 * step, base - h)
        pts.append((a + step, base))
    return pts, apexes


def draw_plot(c, x, y, w, h, weeks, phone):
    """Grid region, reference lines, trace, clipped-spike label and month names. Returns (ceiling, clipped indexes)."""
    gutter = 44
    base, top = y + h - 18, y + 8
    step = (w - gutter - 10) / len(weeks)
    ceiling, ref = scale_for(weeks)
    pts, apexes = week_points(weeks, x + gutter, step, base, top, ceiling)
    path = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    length = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))
    c.trace_len = math.ceil(length) + 2
    clipped = [i for i, wk in enumerate(weeks) if wk["count"] > ceiling]
    refs = "".join(
        f'<line class="ref" x1="{x}" y1="{base - v / ceiling * (base - top):.1f}" x2="{x + w}" y2="{base - v / ceiling * (base - top):.1f}"/>'
        for v in range(ref, ceiling, ref))
    c.add(
        f'<defs><clipPath id="plot"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
        f'<pattern id="pd" x="{x}" y="{y}" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" class="gd"/></pattern>'
        f'<pattern id="pp" x="{x}" y="{y}" width="40" height="40" patternUnits="userSpaceOnUse">'
        + "".join(f'<path d="M{k} 0V40M0 {k}H40" class="g1"/>' for k in (8, 16, 24, 32))
        + '<path d="M0 0V40M0 0H40" class="g2"/></pattern></defs>'
        f'<g clip-path="url(#plot)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#pd)" class="dg"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#pp)" class="pg"/>{refs}'
        f'<line class="hair" x1="{x}" y1="{base}" x2="{x + w}" y2="{base}"/>'
        f'<path class="glowp" d="{path}"/><path class="trace" d="{path}"/>'
        f'<circle class="endr" cx="{pts[-1][0]:.1f}" cy="{base}" r="5"/><circle class="end" cx="{pts[-1][0]:.1f}" cy="{base}" r="5"/></g>'
    )
    for v in range(ref, ceiling, ref):
        c.t(x + 2, base - v / ceiling * (base - top) - 6, "d", str(v), style="font-size:14px")
    for i in clipped:   # break mark (two short slashes across the spike) and the real value
        ax, ay = apexes[i]
        for dy in (22, 28):
            c.add(f'<line class="brk" x1="{ax - 5:.1f}" y1="{ay + dy + 3:.1f}" x2="{ax + 5:.1f}" y2="{ay + dy - 3:.1f}"/>')
        c.t(ax + 9, ay + 12, "db", fmt(weeks[i]["count"]))
    marks, prev = [], None
    for i, wk in enumerate(weeks):
        m = int(wk["start"][5:7]) - 1
        if prev is not None and m != prev and i >= 2:
            marks.append((i, MONTHS[m]))
        prev = m
    for k, (i, name) in enumerate(marks):
        if phone and k % 2:
            continue
        if x + gutter + i * step + 30 < x + w:
            c.t(x + gutter + i * step, y + h + 26, "d", name)
    return ceiling, clipped


VITALS_CSS = """
.gd { fill: var(--strong); } .dg { opacity: var(--dots); }
.g1 { stroke: var(--vital); stroke-opacity: .08; fill: none; } .g2 { stroke: var(--vital); stroke-opacity: .16; fill: none; }
.pg { opacity: var(--paper); }
.ref { stroke: var(--muted); stroke-opacity: .45; stroke-dasharray: 2 5; }
.brk { stroke: var(--strong); stroke-width: 2; stroke-linecap: round; }
.trace, .glowp { fill: none; stroke-linejoin: round; stroke-linecap: round; stroke-dasharray: var(--len); stroke-dashoffset: 0;
                 animation: draw 2.4s linear .3s both; }
.trace { stroke: var(--trace); stroke-width: 2; }
.glowp { stroke: var(--vital); stroke-width: 7; opacity: var(--glow); }
.end { fill: var(--vital); animation: appear .3s linear 2.7s both; }
.endr { fill: none; stroke: var(--vital); stroke-width: 2; transform-box: fill-box; transform-origin: center;
        opacity: 0; animation: pulse 1.8s ease-out 2.8s infinite; }
@keyframes draw { from { stroke-dashoffset: var(--len); } to { stroke-dashoffset: 0; } }
@keyframes appear { from { opacity: 0; } to { opacity: 1; } }
@keyframes pulse { 0% { opacity: .7; transform: scale(1); } 100% { opacity: 0; transform: scale(3.4); } }
@media (prefers-reduced-motion: reduce) { .trace, .glowp, .end, .endr { animation: none; } }
"""


def vitals(data, phone, theme):
    cal, weeks = data["calendar"], data["calendar"]["weeks"]
    c = Canvas(PW if phone else DW)
    reads = [(fmt(cal["total"]), "contributions, last 12 months"),
             (fmt(data["merged_outside"]), "pull requests merged in public repos"),
             (fmt(data["reviewed_public"]), "public pull requests reviewed")]
    facts = [plural(cal["active_days"], "active day"), f"longest streak {plural(cal['longest_streak'], 'day')}"]
    updated = f"updated {data['updated']} from the GitHub API"

    def meta(x, y, s, width):
        size = 16
        while measure("mono", s, size) > width:   # meta lines never wrap
            size -= .5
        c.t(x, y, "d", s, style=f"font-size:{size:g}px" if size != 16 else None)

    summary = f"{facts[0]}, {facts[1]}"
    if phone:
        plot_h = 170
        ceiling, clipped = draw_plot(c, PAD, PT, PW - 2 * PAD, plot_h, weeks, True)
        y = PT + plot_h + 36 + 10
        for num, label in reads:                 # equal rows: numeral column 170, label right of it
            c.t(PAD, y + 40, "num", num, style="font-size:48px")
            ls = wrap("sans", label, 20, PW - 24 - PAD - 170)
            assert len(ls) <= 2, label
            lines_at(c, PAD + 170, y + 20, "s", ls)
            y += 72
        y += 6
        meta(PAD, y + 18, summary, PW - 2 * PAD)
        meta(PAD, y + 18 + 28, updated, PW - 2 * PAD)
        H = y + 18 + 28 + 12 + PT
    else:
        plot_h = 284
        ceiling, clipped = draw_plot(c, PAD, PT, 760, plot_h, weeks, False)
        rx = 812
        last_base = PT + plot_h - 18            # the plot baseline
        n1 = PT + 37                            # top of the first numeral on the plot top
        n3 = last_base - 28
        for k, (num, label) in enumerate(reads):
            n = n1 + (n3 - n1) * k / 2          # blocks spread evenly over the plot's height
            c.t(rx, n, "num", num, style="font-size:52px")
            assert measure("sans", label, 20) <= DW - PAD - rx, label
            c.t(rx, n + 28, "s", label)
        by = PT + plot_h + 26 + 30
        meta(PAD, by, updated, 760)
        c.t(DW - PAD, by, "d", summary, anchor="end")
        H = by + 12 + PT - 6
    clip = ""
    if clipped:
        i = clipped[0]
        clip = (f" The week starting {weeks[i]['start']} has {fmt(weeks[i]['count'])}, above the ceiling, "
                "and is drawn to the top edge with a break mark.")
    alt = (f"Contributions per week over the last 53 weeks, one heartbeat per week, on a linear scale from zero to a "
           f"ceiling of {ceiling} per week, with reference lines.{clip} {fmt(cal['total'])} contributions in the last 12 months, "
           f"{fmt(data['merged_outside'])} pull requests merged in public repositories outside my own account, "
           f"{fmt(data['reviewed_public'])} pull requests by others reviewed in public repositories. {facts[0]}, {facts[1]}, {updated}.")
    return c.render(int(H), alt, theme, f"svg {{ --len: {c.trace_len}; }}" + VITALS_CSS), alt


# ---- content (DESIGN.md "Content")

TOOLS = [
    ("Helmbulance", "Git-Hospital/helmbulance", "Installs a Helm chart on a throwaway kind cluster and runs day-2 scenarios: upgrades, reinstalls, Secret rotation, network isolation", "pre-release"),
    ("MeshMedic", "Git-Hospital/meshmedic", "Matches Istio's Prometheus telemetry against reviewed failure scenarios and opens a GitOps pull request with the diagnosis, evidence and rollback plan", "v1.0.0"),
    ("boards", "Git-Hospital/boards", "Benchmark for diagnosis tools: known defects, clean twins and hand-verified values, scored by applying the fix", "in development"),
    ("GitHealthCheck", "Git-Hospital/githealthcheck", "Code health analyzer: tests, history, complexity. Every number is a measurement, or null with a reason", "Go rewrite in progress"),
]
HARFBUZZ = {"owner": "harfbuzz", "repo": "harfbuzz", "kind": "os",
            "sentence": "Reported a text-shaping bug that was fixed the same day", "state": "issue #6320",
            "url": "https://github.com/harfbuzz/harfbuzz/issues/6320"}
WORK = [
    {"kind": "work", "name": "Bluesense", "place": "Boston, remote", "sentence": "iOS app in Swift and SwiftUI: session, checkout and cart fixes, release tooling, and GitHub automation for a team of about 30"},
    {"kind": "work", "name": "Nordstjernen", "place": "open source", "sentence": "Maintainer of an open-source browser engine in C: 200+ commits, made Google Search and Gmail sign-in work"},
    {"kind": "work", "name": "BirthdayMessaging", "place": "UK, remote", "sentence": "Security scanning of a production messaging platform with OWASP ZAP, Burp Suite and nmap"},
]
TEAM = [
    {"kind": "work", "name": "EmlakPlus", "sentence": "Largest contributor (team of 4) to a CRM for real-estate agencies: listings, clients, map search, scheduled social posts", "built": "FastAPI, Next.js, PostgreSQL, Redis, Celery, Terraform"},
    {"kind": "work", "name": "data-stock", "sentence": "REST API and admin web of an inventory SaaS that logs stock by barcode and syncs Amazon, Allegro and eBay listings", "built": "FastAPI, Alembic, React, Vite, Playwright"},
    {"kind": "work", "name": "Vantage", "sentence": "TypeScript API of an Instagram analytics app: Graph API login, ad-supported free tier, Fly.io deploys", "built": "Node.js, TypeScript, Docker, Fly.io"},
]
SITE = "https://kadirhanemrememis.xyz"
HERO_ALT = ("Kadirhan Emre, Software Engineer. I build web products end to end: React and Next.js front ends, APIs in "
            "Python, TypeScript and Go, PostgreSQL, and the Docker, CI and cloud setup that ships them. Maintainer of "
            "Git Hospital and Nordstjernen. Wrocław, Poland. Contact: kadirhanemrememis.xyz, "
            "linkedin.com/in/kadirhan-emre, kadirhanemre@proton.me.")
GH_ALT = ("Git Hospital: open-source tools that diagnose infrastructure and code, with the evidence for every diagnosis. "
          "An ambulance drives across and the name appears behind it.")


def os_rows(data):
    """Open source rows in the order of the allowlist, then the static harfbuzz row."""
    rows = []
    for repo, v in data["repos"].items():
        owner, name = repo.split("/")
        rows.append({"kind": "os", "owner": owner, "repo": name, "stars": v["stars"], "merged": v["merged"],
                     "open": v["open"], "title": v.get("latest_title"), "date": v.get("latest_merged"),
                     "url": f"https://github.com/{repo}/pulls?q=is%3Apr+author%3Akassvl"})
    return rows + [HARFBUZZ]


def os_alt(r):
    if "sentence" in r:
        return f"harfbuzz/harfbuzz: {r['sentence']}, issue #6320."
    s = f"{r['owner']}/{r['repo']}, {plural(r['stars'], 'star')}. "
    if r.get("title"):
        s += f"Latest merged pull request, {r['date']}: {r['title']}. "
    return s + f"{fmt(r['merged'])} merged" + (f", {fmt(r['open'])} in review." if r["open"] else ".")


def work_alt(rows):
    return " ".join(f"{r['name']}" + (f" ({r['place']})" if r.get("place") else "") + f": {r['sentence']}."
                    + (f" Built with {r['built']}." if r.get("built") else "") for r in rows)


def card_specs(data):
    """(file name, builder(phone, theme) -> (svg, alt), link) for every data card, in page order."""
    specs = [("vitals", lambda ph, th: vitals(data, ph, th),
              "https://github.com/search?q=author%3Akassvl+is%3Apr+is%3Amerged&type=pullrequests")]
    for name, repo, desc, status in TOOLS:
        alt = f"{name}: {desc}. Status: {status}."
        row = {"kind": "tool", "name": name, "desc": desc, "status": status}
        specs.append((f"tool-{name.lower()}", lambda ph, th, row=row, alt=alt: (rows_card([row], ph, th, alt), alt),
                      f"https://github.com/{repo}"))
    for r in os_rows(data):
        alt = os_alt(r)
        specs.append((f"os-{r['owner']}-{r['repo']}".lower().replace(".", "-"),
                      lambda ph, th, r=r, alt=alt: (rows_card([r], ph, th, alt), alt), r["url"]))
    for name, rows in (("work", WORK), ("team", TEAM)):
        alt = work_alt(rows)
        specs.append((name, lambda ph, th, rows=rows, alt=alt: (rows_card(rows, ph, th, alt), alt), SITE))
    return specs


# ---------------------------------------------------------------- README

def picture(prefix, name, alt, href):
    alt = escape(alt, {'"': "&quot;"})
    return (f'<a href="{href}"><picture><source media="(max-width: 600px)" srcset="{prefix}{name}-phone.svg">'
            f'<img src="{prefix}{name}.svg" width="100%" alt="{alt}"></picture></a>')


STACK = """## Stack

```text
frontend   React, Next.js, TypeScript, Tailwind CSS, Framer Motion, Vite, React Native
backend    Python (FastAPI, Celery), Node.js (NestJS, Express), Go, REST, JWT/OAuth
data       PostgreSQL, Redis, SQLAlchemy + Alembic
testing    pytest, Vitest, Playwright, Jest, go test
platform   Docker, Kubernetes, Helm, Istio, GitHub Actions, Terraform, AWS, Vercel, Fly.io, Linux
```

<sub>B.Eng. Information Technology, WSB Merito Wrocław · Oracle Cloud Infrastructure 2025 Foundations Associate · Turkish, English (C1+), Polish (A2-B1)</sub>
"""


def readme(alts, specs, prefix) -> str:
    link = {n: h for n, _, h in specs}
    pic = lambda n: picture(prefix, n, alts[n], link[n])
    tools = [f"tool-{t[0].lower()}" for t in TOOLS]
    oss = [n for n, _, _ in specs if n.startswith("os-")]
    parts = [
        picture(prefix, "hero", HERO_ALT, SITE),
        pic("vitals"),
        picture(prefix, "git-hospital", GH_ALT, "https://github.com/Git-Hospital"),
        "\n".join(pic(n) for n in tools),
        "## Open source\n\n" + "\n".join(pic(n) for n in oss),
        "## Work\n\n" + pic("work"),
        "### Team products (private repos, happy to walk through the code)\n\n" + pic("team"),
    ]
    return "\n\n".join(parts) + "\n\n" + STACK


# ---------------------------------------------------------------- driver

def validate(path: Path):
    """Parses as XML and loads nothing from outside the file."""
    txt = path.read_text()
    root = ET.fromstring(txt)
    assert root.tag.endswith("svg"), path
    assert "http" not in txt.replace("http://www.w3.org/2000/svg", ""), f"{path.name}: http in file"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", choices=("light", "dark"), help="hard-set the card theme (previews only)")
    ap.add_argument("--out", type=Path, help="write here instead of assets/ (previews only)")
    a = ap.parse_args()
    data = json.loads(DATA.read_text())
    out = a.out or ROOT
    out.mkdir(parents=True, exist_ok=True)
    prefix = "" if a.out else "assets/"
    specs = card_specs(data)
    alts = {}
    for name, fn in (("hero", hero), ("git-hospital", git_hospital)):   # illustrations: always dark
        for phone in (False, True):
            f = out / f"{name}{'-phone' if phone else ''}.svg"
            f.write_text(fn(phone))
            validate(f)
    for name, fn, _ in specs:
        for phone in (False, True):
            markup, alt = fn(phone, a.theme)
            alts[name] = alt
            f = out / f"{name}{'-phone' if phone else ''}.svg"
            f.write_text(markup)
            validate(f)
    target = (out / "README.md") if a.out else (ROOT.parent / "README.md")
    target.write_text(readme(alts, specs, prefix))
    print(f"wrote {len(list(out.glob('*.svg')))} svg files to {out} and {target}")


if __name__ == "__main__":
    main()
