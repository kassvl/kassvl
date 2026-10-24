#!/usr/bin/env python3
"""Build the animated profile SVGs in assets/.

GitHub shows README images through its image proxy, which blocks external fonts,
so every font is subset to the glyphs the SVG uses and embedded as base64 woff2.
Fonts match kadirhanemrememis.xyz: Fraunces (display), Inter (text), JetBrains Mono.

Usage: python3 assets/src/build.py   (needs fonttools + brotli: pip install fonttools brotli)
"""
import base64
import math
import subprocess
import tempfile
import urllib.request
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


def font_face(key: str, family: str, text: str, weight: int = 400, latin_ext: bool = False) -> str:
    CACHE.mkdir(exist_ok=True)
    src = CACHE / f"{key}.woff2"
    if not src.exists():
        urllib.request.urlretrieve(FONTS[key], src)
    with tempfile.NamedTemporaryFile(suffix=".woff2") as out:
        subprocess.run(
            ["pyftsubset", str(src), f"--text={text}", "--flavor=woff2",
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


def hero() -> str:
    W, H = 1200, 516
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
        "display": name, "sans5": role, "sans4": "".join(para), "mono": kicker + stack + "in" + "".join(c for _, c in contacts),
    })
    css = fonts + COMMON_CSS + f"""
.spin {{ transform-origin: {cx}px {cy}px; animation: spin linear infinite; }}
.contact {{ fill: {INK200}; }}
.beat {{ transform-origin: {cx}px {cy}px; animation: beat 1.6s ease-in-out infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes beat {{ 0%, 60%, 100% {{ transform: scale(1); }} 15% {{ transform: scale(1.22); }} 30% {{ transform: scale(.94); }} 42% {{ transform: scale(1.12); }} }}
""" + REDUCED
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
    label = (f"{name}, {role}. " + " ".join(para) + " Stack: " + stack.replace("  ", ", ") + ". "
             + " | ".join(c for _, c in contacts))
    return svg(W, H, label, css, "\n".join(body))


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


def git_hospital() -> str:
    W, H = 1200, 400
    road, park = 182, 700  # road line; where the ambulance stands when motion is off
    bay = 150              # left edge of the emergency bay
    tx = 292               # title x
    title = "Git Hospital"
    url = "github.com/Git-Hospital"
    lead = "Open-source tools that diagnose infrastructure and code, with the evidence for every diagnosis."
    tools = [
        ("helmbulance", "Helm chart day-2 tests"),
        ("meshmedic", "Istio alerts to fix PRs"),
        ("boards", "scores diagnosis tools"),
        ("githealthcheck", "code health, measured"),
    ]
    mono = url + "".join(a + b for a, b in tools) + "EMERGENCY"
    fonts = build_fonts({"display": title, "sans4": lead, "mono": mono})
    start, stop = bay - 210 - park, W + 120 - park
    css = fonts + COMMON_CSS + f"""
.gh-title {{ font: 600 68px 'Display', Georgia, serif; fill: {INK50}; letter-spacing: -1px;
            paint-order: stroke; stroke: {SURFACE}; stroke-width: 10px; stroke-linejoin: round; }}
.lead {{ font: 400 20px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK200}; }}
.tool {{ font: 500 17px 'Mono', 'SFMono-Regular', Menlo, Consolas, monospace; fill: {INK50}; }}
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
        f'<clipPath id="street"><rect x="{bay}" y="101" width="100" height="{road - 101 + 20}"/><rect x="250" y="0" width="{W}" height="{H}"/></clipPath>'
        f'<radialGradient id="glow-r"><stop offset="0" stop-color="{RED}" stop-opacity=".75"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glow-b"><stop offset="0" stop-color="{BLUE}" stop-opacity=".75"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="crossglow"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="bay" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".35"/><stop offset=".5" stop-color="#120f0d"/><stop offset="1" stop-color="#0c0a09"/></linearGradient>'
        f'<linearGradient id="lamp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".22"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AMBER}" stop-opacity=".45"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient></defs>'
    )
    body = [
        dot_grid(W, H, 18), defs,
        '<g clip-path="url(#frame)">',
        f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
        f'<circle cx="1062" cy="64" r="15" fill="{INK200}" fill-opacity=".85"/><circle cx="1069" cy="59" r="13" fill="{SURFACE}"/>',
        city(262, W, road, (tx - 10, 96, tx + 420, 172)),
        street_lamp(760, road), street_lamp(1070, road),
        hospital(road),
        f'<rect x="0" y="{road}" width="{W}" height="12" fill="#100d0b"/>',
        f'<line x1="0" y1="{road}" x2="{W}" y2="{road}" stroke="{INK600}" stroke-opacity=".8"/>',
        f'<line x1="250" y1="{road + 6}" x2="{W}" y2="{road + 6}" stroke="{INK600}" stroke-opacity=".6" stroke-dasharray="22 16"/>',
        text(W - 70, 40, "mono rise", url, text_anchor="end"),
        # the name is painted only where the ambulance has already been
        f'<g clip-path="url(#trail)"><g class="titlefade">{text(tx, 160, "gh-title", title)}</g></g>',
        f'<g clip-path="url(#street)"><g transform="translate({park} {road})"><g class="drive">{ambulance()}</g></g></g>',
        text(70, 238, "lead rise", lead, style="animation-delay:.3s"),
        f'<line x1="70" y1="276" x2="{W - 70}" y2="276" stroke="{BORDER}"/>',
    ]
    col = (W - 140) / 4
    for k, (name, desc) in enumerate(tools):
        x = 70 + k * col
        d = f"animation-delay:{.5 + .1 * k:.1f}s"
        body.append(text(x, 318, "tool rise", name, style=d))
        body.append(text(x, 346, "mono rise", desc, style=d))
    body.append("</g>")
    label = (f"{title}: {lead} An ambulance drives out of a hospital's emergency bay and the name appears behind it. "
             "Tools: " + "; ".join(f"{a}, {b}" for a, b in tools) + ".")
    return svg(W, H, label, css, "\n".join(body))


if __name__ == "__main__":
    for name, fn in (("hero.svg", hero), ("git-hospital.svg", git_hospital)):
        out = ROOT / name
        out.write_text(fn())
        print(f"{out.relative_to(ROOT.parent)}  {out.stat().st_size // 1024} KB")
