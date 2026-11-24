#!/usr/bin/env python3
"""Builds the hand-made animated SVGs in assets/ (hero terminal, neural net, marquee, divider).

Edit the CONFIG block, then run:  python scripts/build_assets.py
"""
import pathlib
import random

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

# ---------------------------------------------------------------- CONFIG
HANDLE = "prajwal-sv"
HOST = "ai-lab"
TECH = ["Python", "C++", "TensorFlow", "PyTorch", "scikit-learn", "Keras", "NLP", "RAG",
        "Computer Vision", "Deep Learning", "FastAPI", "Streamlit", "Pandas", "NumPy",
        "Docker", "MongoDB", "MySQL", "Git"]
# (kind, text, color) - kind: cmd | out | train | prompt
SCRIPT = [
    ("cmd", "whoami", None),
    ("out", "prajwal-sv  //  AI/ML Engineer  |  Python Developer", "#79c0ff"),
    ("cmd", "cat mission.txt", None),
    ("out", "\"Create something that doesn't exist yet.\"", "#3fb950"),
    ("cmd", "ls skills/", None),
    ("out", "python/  ml/  deep-learning/  cv/  nlp/  rag/  full-stack/", "#d2a8ff"),
    ("cmd", "python train.py --epochs 100", None),
    ("train", "", None),
    ("prompt", "", None),
]
# -----------------------------------------------------------------------

FONT = "'Fira Code','SF Mono',Consolas,'DejaVu Sans Mono',monospace"
BG, PANEL, LINE = "#0d1117", "#161b22", "#30363d"
GREEN, CYAN, PURPLE, GRAY, TEXT = "#3fb950", "#58a6ff", "#d2a8ff", "#8b949e", "#c9d1d9"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anim(attr, a, d, on, off, T, hold):
    """Looping keyframes: sit at `off`, move to `on` between a and a+d, hold, then reset."""
    kt = f"0;{a / T:.4f};{(a + d) / T:.4f};{hold / T:.4f};1"
    vals = f"{off};{off};{on};{on};{off}"
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/>'


def hero():
    W, H, CW, FS = 800, 340, 9.0, 15
    T, hold = 22.0, 20.4
    x0, y, step = 28, 82, 30
    t = 0.7
    parts, clips = [], []
    for i, (kind, text, color) in enumerate(SCRIPT):
        if kind == "cmd":
            n = len(text)
            d = max(0.6, n * 0.09)
            w = n * CW
            parts.append(f'<text x="{x0}" y="{y}" fill="{GREEN}" font-size="{FS}" font-weight="700">$'
                         f'{anim("opacity", t, 0.1, 1, 0, T, hold)}</text>')
            clips.append(f'<clipPath id="c{i}"><rect x="{x0 + 2 * CW}" y="{y - 16}" width="{w}" height="22">'
                         f'{anim("width", t + 0.15, d, w, 0, T, hold)}</rect></clipPath>')
            parts.append(f'<text x="{x0 + 2 * CW}" y="{y}" fill="{TEXT}" font-size="{FS}" textLength="{w}" '
                         f'lengthAdjust="spacingAndGlyphs" clip-path="url(#c{i})" xml:space="preserve">{esc(text)}</text>')
            t += d + 0.5
        elif kind == "out":
            w = len(text) * CW
            parts.append(f'<text x="{x0}" y="{y}" fill="{color}" font-size="{FS}" textLength="{w}" '
                         f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(text)}'
                         f'{anim("opacity", t, 0.35, 1, 0, T, hold)}</text>')
            t += 0.9
        elif kind == "train":
            bw = 320
            parts.append(f'<text x="{x0}" y="{y}" fill="{GRAY}" font-size="{FS}">epoch</text>')
            parts.append(f'<rect x="{x0 + 60}" y="{y - 12}" width="{bw}" height="12" rx="6" fill="#21262d"/>')
            parts.append(f'<rect x="{x0 + 60}" y="{y - 12}" width="{bw}" height="12" rx="6" fill="{GREEN}">'
                         f'{anim("width", t, 3.2, bw, 0, T, hold)}</rect>')
            parts.append(f'<text x="{x0 + 60 + bw + 16}" y="{y}" fill="{GREEN}" font-size="{FS}" font-weight="700">100%  [ OK ]'
                         f'{anim("opacity", t + 3.3, 0.3, 1, 0, T, hold)}</text>')
            t += 4.2
        elif kind == "prompt":
            parts.append(f'<text x="{x0}" y="{y}" fill="{GREEN}" font-size="{FS}" font-weight="700">$'
                         f'{anim("opacity", t, 0.1, 1, 0, T, hold)}</text>')
            parts.append(f'<g>{anim("opacity", t, 0.1, 1, 0, T, hold)}'
                         f'<rect x="{x0 + 2 * CW}" y="{y - 14}" width="9" height="18" fill="{GREEN}">'
                         f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" calcMode="discrete" dur="1s" repeatCount="indefinite"/></rect></g>')
        y += step
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Animated terminal introducing {HANDLE}">
<defs>{''.join(clips)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>
<path d="M1,12 a11,11 0 0 1 11,-11 h{W - 24} a11,11 0 0 1 11,11 v24 h-{W - 2} z" fill="{PANEL}"/>
<line x1="1" y1="36" x2="{W - 1}" y2="36" stroke="{LINE}"/>
<circle cx="22" cy="18" r="6" fill="#ff5f56"/><circle cx="42" cy="18" r="6" fill="#ffbd2e"/><circle cx="62" cy="18" r="6" fill="#27c93f"/>
<text x="{W / 2}" y="23" text-anchor="middle" fill="{GRAY}" font-size="12">{HANDLE}@{HOST}: ~/profile</text>
{''.join(parts)}
</svg>'''
    (ASSETS / "hero.svg").write_text(svg)


def neural():
    random.seed(7)
    W, H = 800, 180
    layers = [4, 6, 6, 3]
    xs = [130, 310, 490, 670]
    cols = [GREEN, CYAN, CYAN, PURPLE]
    pos = []
    for x, n in zip(xs, layers):
        top, bottom = 28, 134
        gap = (bottom - top) / (n - 1)
        pos.append([(x, top + gap * i) for i in range(n)])
    edges = [(a, b) for li in range(len(layers) - 1) for a in pos[li] for b in pos[li + 1]]
    lines = "".join(f'<line x1="{a[0]}" y1="{a[1]:.1f}" x2="{b[0]}" y2="{b[1]:.1f}" stroke="{LINE}" stroke-width="1"/>'
                    for a, b in edges)
    pulses = ""
    for a, b in random.sample(edges, 26):
        dur = random.uniform(1.6, 2.8)
        begin = -random.uniform(0, 3)
        c = random.choice([GREEN, CYAN, PURPLE])
        pulses += (f'<circle r="2.8" fill="{c}"><animateMotion dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" '
                   f'path="M{a[0]},{a[1]:.1f} L{b[0]},{b[1]:.1f}"/>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="{dur:.2f}s" '
                   f'begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    nodes = ""
    for li, layer in enumerate(pos):
        for (x, y) in layer:
            nodes += (f'<circle cx="{x}" cy="{y:.1f}" r="7" fill="{BG}" stroke="{cols[li]}" stroke-width="1.6">'
                      f'<animate attributeName="r" values="7;8.6;7" dur="{random.uniform(2.4, 4):.2f}s" '
                      f'begin="{-random.uniform(0, 3):.2f}s" repeatCount="indefinite"/></circle>')
    labels = "".join(f'<text x="{x}" y="164" text-anchor="middle" fill="{GRAY}" font-size="11">{n}</text>'
                     for x, n in zip(xs, ["input", "hidden", "hidden", "output"]))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Animated neural network">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>
<text x="20" y="24" fill="{GRAY}" font-size="11">model.forward(x)</text>
{lines}{pulses}{nodes}{labels}
</svg>'''
    (ASSETS / "neural.svg").write_text(svg)


def marquee():
    W, H, CW = 800, 52, 7.8
    chips, x = [], 0
    for name in TECH:
        w = len(name) * CW + 40
        chips.append((x, w, name))
        x += w + 12
    total = x

    def row(offset):
        out = ""
        for cx, w, name in chips:
            out += (f'<g transform="translate({cx + offset:.1f},12)"><rect width="{w:.1f}" height="28" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
                    f'<circle cx="16" cy="14" r="3.5" fill="{GREEN}"/><text x="28" y="19" fill="{TEXT}" font-size="13">{esc(name)}</text></g>')
        return out

    dur = total / 55
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Scrolling list of technologies">
<defs><linearGradient id="f" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.08" stop-color="#fff"/><stop offset="0.92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>
<g mask="url(#m)"><g>{row(0)}{row(total)}{row(total * 2)}
<animateTransform attributeName="transform" type="translate" from="0 0" to="-{total:.1f} 0" dur="{dur:.1f}s" repeatCount="indefinite"/></g></g>
</svg>'''
    (ASSETS / "marquee.svg").write_text(svg)


def divider():
    W, H = 800, 18
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="divider">
<line x1="40" y1="9" x2="{W - 40}" y2="9" stroke="#238636" stroke-width="2" stroke-dasharray="3 9" stroke-linecap="round" opacity="0.7">
<animate attributeName="stroke-dashoffset" from="0" to="-48" dur="2s" repeatCount="indefinite"/></line>
<circle r="4" fill="{GREEN}"><animateMotion dur="5s" repeatCount="indefinite" path="M40,9 L{W - 40},9"/>
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="5s" repeatCount="indefinite"/></circle>
</svg>'''
    (ASSETS / "divider.svg").write_text(svg)


def loss_curve():
    """Animated, illustrative training curves (not real metrics)."""
    import math
    random.seed(11)
    W, H = 800, 270
    x0, x1, y0, y1 = 70, 770, 60, 215
    def X(e): return x0 + (x1 - x0) * e / 100
    def Y(v): return y1 - (y1 - y0) * v / 1.8
    tr, va = [], []
    for e in range(0, 101, 2):
        base = 1.6 * math.exp(-e / 20) + 0.10
        tr.append((X(e), Y(base + random.uniform(-0.015, 0.015))))
        va.append((X(e), Y(base * 1.08 + 0.05 + 0.04 * math.sin(e / 9) * math.exp(-e / 60) + random.uniform(-0.02, 0.02))))
    d_tr = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in tr)
    d_va = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in va)
    grid = ""
    for v in (0, 0.5, 1.0, 1.5):
        grid += (f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{LINE}" stroke-dasharray="2 5"/>'
                 f'<text x="{x0 - 10}" y="{Y(v) + 4:.1f}" text-anchor="end" fill="{GRAY}" font-size="11">{v:.1f}</text>')
    for e in (0, 25, 50, 75, 100):
        grid += f'<text x="{X(e):.1f}" y="{y1 + 20}" text-anchor="middle" fill="{GRAY}" font-size="11">{e}</text>'
    T = 12
    kt = "0;0.35;0.9;1"
    def line(d, col, width):
        return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" '
                f'pathLength="1" stroke-dasharray="1" stroke-dashoffset="0">'
                f'<animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></path>')
    def dot(d, col):
        return (f'<circle r="5" fill="{col}"><animateMotion dur="{T}s" repeatCount="indefinite" path="{d}" '
                f'keyPoints="0;1;1;1" keyTimes="{kt}" calcMode="linear"/>'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.35;0.4;1" dur="{T}s" repeatCount="indefinite"/></circle>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Animated training and validation loss curves">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>
<text x="24" y="34" fill="{GREEN}" font-size="14" font-weight="700">$</text><text x="42" y="34" fill="{TEXT}" font-size="14">tensorboard --logdir runs/</text>
<circle cx="590" cy="30" r="5" fill="{GREEN}"/><text x="602" y="34" fill="{GRAY}" font-size="12">train loss</text>
<circle cx="684" cy="30" r="5" fill="{CYAN}"/><text x="696" y="34" fill="{GRAY}" font-size="12">val loss</text>
{grid}
<text x="{(x0 + x1) / 2}" y="{H - 14}" text-anchor="middle" fill="{GRAY}" font-size="11">epoch  (illustrative curve)</text>
{line(d_va, CYAN, 2)}{line(d_tr, GREEN, 2.5)}{dot(d_va, CYAN)}{dot(d_tr, GREEN)}
</svg>'''
    (ASSETS / "loss-curve.svg").write_text(svg)


if __name__ == "__main__":
    hero()
    neural()
    marquee()
    divider()
    loss_curve()
    print("built:", ", ".join(sorted(p.name for p in ASSETS.glob("*.svg"))))