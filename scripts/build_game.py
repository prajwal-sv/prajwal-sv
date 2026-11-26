#!/usr/bin/env python3
"""Commit Harvester -> assets/harvest.svg  (replaces the snake).

A scanner drone sweeps your real contribution calendar column by column. Every active day
flashes white and settles into an energized cyan glow; a counter tallies what was harvested.
Standard library only. No token needed: it reads the public contributions page.

Usage:  python scripts/build_game.py
"""
import datetime as dt
import html
import math
import os
import pathlib
import re
import urllib.request

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
USER = os.environ.get("GH_USER", "prajwal-sv")

FONT = "'Fira Code','SF Mono',Consolas,'DejaVu Sans Mono',monospace"
BG, LINE, GRAY, TEXT = "#0d1117", "#30363d", "#8b949e", "#c9d1d9"
CYAN, ORANGE, GREEN = "#5fdcff", "#ff7a18", "#3fb950"
BASE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]       # GitHub greens
ENERGIZED = ["#161b22", "#0b4f66", "#0e86a8", "#38c8f0", "#b4f3ff"]  # after the drone passes

W, CELL, PITCH, X0, Y0 = 800, 11, 14, 29, 74
STEP_T = 0.075      # seconds the drone spends per cell


def fetch_calendar():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*for="contribution-day-component-(\d+)-(\d+)"[^>]*>\s*([^<]*)', page):
        txt = m.group(3).strip()
        n = re.match(r"(\d+) contribution", txt)
        counts[(int(m.group(1)), int(m.group(2)))] = int(n.group(1)) if n else 0
    cal = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", page):
        rid = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', tag)
        date = re.search(r'data-date="([\d-]+)"', tag)
        lvl = re.search(r'data-level="(\d)"', tag)
        if rid and date and lvl:
            row, col = int(rid.group(1)), int(rid.group(2))
            cal[(row, col)] = {"date": date.group(1), "level": int(lvl.group(1)), "count": counts.get((row, col), 0)}
    if len(cal) < 100:
        raise RuntimeError("could not parse contribution calendar")
    return cal


def tl(vals, T):
    return ";".join(f"{v / T:.4f}" for v in vals)


def build(cal=None):
    cal = cal or fetch_calendar()
    cols = max(c for _, c in cal) + 1
    # zigzag sweep: down even columns, up odd columns (skipping days that do not exist yet)
    order = []
    for c in range(cols):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        order += [(r, c) for r in rows if (r, c) in cal]
    pos = [(X0 + c * PITCH + CELL / 2, Y0 + r * PITCH + CELL / 2) for r, c in order]
    dist = [0.0]
    for a, b in zip(pos, pos[1:]):
        dist.append(dist[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = dist[-1]
    start = 0.6
    sweep = L / PITCH * STEP_T
    t_end = start + sweep
    T = round(t_end + 4.0, 1)
    t_of = [start + d / L * sweep for d in dist]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pos)

    total = sum(v["count"] for v in cal.values())
    active = sum(1 for v in cal.values() if v["level"] > 0)

    # ---- cells
    cells, rings = [], []
    t_by_cell = {rc: t for rc, t in zip(order, t_of)}
    for (r, c), v in cal.items():
        x, y, lvl = X0 + c * PITCH, Y0 + r * PITCH, v["level"]
        tip = f'<title>{html.escape(v["date"])}: {v["count"]} contributions</title>'
        if lvl == 0:
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{BASE[0]}"/>')
            continue
        t = t_by_cell[(r, c)]
        kt = tl([0, t, t + 0.04, t + 0.5, T - 0.6, T], T)
        vals = f"{BASE[lvl]};{BASE[lvl]};#ffffff;{ENERGIZED[lvl]};{ENERGIZED[lvl]};{BASE[lvl]}"
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{BASE[lvl]}">{tip}'
                     f'<animate attributeName="fill" values="{vals}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></rect>')
        if lvl >= 3:
            cx, cy = x + CELL / 2, y + CELL / 2
            rings.append(
                f'<circle cx="{cx}" cy="{cy}" r="2" fill="none" stroke="{CYAN}" stroke-width="1.2" opacity="0">'
                f'<animate attributeName="r" values="2;2;14;14" keyTimes="{tl([0, t, t + 0.45, T], T)}" dur="{T}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="{tl([0, t, t + 0.03, t + 0.45, T], T)}" dur="{T}s" repeatCount="indefinite"/></circle>')

    # ---- month labels
    months, last_c = "", -9
    prev = None
    for c in range(cols):
        cell = cal.get((0, c)) or next((cal[(r, c)] for r in range(7) if (r, c) in cal), None)
        if not cell:
            continue
        mo = dt.date.fromisoformat(cell["date"]).strftime("%b")
        if mo != prev and c - last_c >= 3:
            months += f'<text x="{X0 + c * PITCH}" y="{Y0 - 9}" fill="{GRAY}" font-size="10">{mo}</text>'
            last_c = c
        prev = mo

    # ---- drone (+ short comet tail)
    def motion(delay):
        kt = tl([0, start + delay, t_end + delay, T], T)
        return (f'<animateMotion dur="{T}s" repeatCount="indefinite" path="{path}" calcMode="linear" '
                f'keyPoints="0;0;1;1" keyTimes="{kt}"/>')
    tail = "".join(f'<circle r="{5.2 - i * 0.7:.1f}" fill="{CYAN}" opacity="{0.34 - i * 0.055:.2f}">{motion(-0.07 * (i + 1) * 1.4)}</circle>'
                   for i in range(5))
    drone = f'''<g>{motion(0)}
<circle r="13" fill="{CYAN}" opacity="0.16"/>
<circle r="9" fill="none" stroke="{CYAN}" stroke-width="1"><animate attributeName="r" values="7;11;7" dur="0.8s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.9;0.2;0.9" dur="0.8s" repeatCount="indefinite"/></circle>
<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="0.45s" repeatCount="indefinite"/>
<line x1="-8" y1="-8" x2="8" y2="8" stroke="#8b949e" stroke-width="1.4"/><line x1="-8" y1="8" x2="8" y2="-8" stroke="#8b949e" stroke-width="1.4"/>
<circle cx="-8" cy="-8" r="2.6" fill="none" stroke="{CYAN}"/><circle cx="8" cy="-8" r="2.6" fill="none" stroke="{CYAN}"/>
<circle cx="-8" cy="8" r="2.6" fill="none" stroke="{CYAN}"/><circle cx="8" cy="8" r="2.6" fill="none" stroke="{CYAN}"/></g>
<circle r="4.2" fill="{BG}" stroke="#fff" stroke-width="1.2"/><circle r="1.9" fill="{ORANGE}"/></g>'''

    # ---- HUD: milestone counter + progress bar
    cum, run = [], 0
    for rc in order:
        run += cal[rc]["count"]
        cum.append(run)
    n = len(order)
    counter = ""
    marks = [(0, 0)] + [(round(n * m / 10) - 1, t_of[round(n * m / 10) - 1]) for m in range(1, 11)]
    for i, (idx, t0) in enumerate(marks):
        ts = 0.0005 if i == 0 else t0
        te = marks[i + 1][1] if i + 1 < len(marks) else T - 0.0005
        val = 0 if i == 0 else cum[idx]
        counter += (f'<text x="172" y="198" fill="{CYAN}" font-size="16" font-weight="700" opacity="{1 if i == 0 else 0}">{val}'
                    f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0;0" keyTimes="{tl([0, ts, te, T], T)}" dur="{T}s" repeatCount="indefinite"/></text>')
    bar_w = 300
    first = min(v["date"] for v in cal.values())
    last = max(v["date"] for v in cal.values())
    span = f'{dt.date.fromisoformat(first).strftime("%b %Y")} - {dt.date.fromisoformat(last).strftime("%b %Y")}'
    legend = "".join(f'<rect x="{648 + i * 14}" y="189" width="{CELL}" height="{CELL}" rx="2" fill="{BASE[i]}"/>' for i in range(5))
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="222" viewBox="0 0 {W} 222" font-family="{FONT}" role="img" aria-label="A drone sweeps {html.escape(USER)}'s contribution graph and energizes every active day: {total} contributions over {active} active days">
<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter></defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="221" rx="12" fill="{BG}" stroke="{LINE}"/>
<text x="24" y="36" fill="{GREEN}" font-size="14" font-weight="700">$</text><text x="42" y="36" fill="{TEXT}" font-size="14">./harvest --commits --user {html.escape(USER)}</text>
<text x="776" y="36" fill="{GRAY}" font-size="10" text-anchor="end">{span} | {total} contributions | {active} active days | synced {stamp}</text>
{months}
{''.join(cells)}
{''.join(rings)}
{tail}{drone}
<text x="29" y="198" fill="{GRAY}" font-size="12">commits harvested:</text>
{counter}
<rect x="250" y="190" width="{bar_w}" height="8" rx="4" fill="#161b22"/>
<rect x="250" y="190" width="{bar_w}" height="8" rx="4" fill="{CYAN}">
<animate attributeName="width" values="0;0;{bar_w};{bar_w};0" keyTimes="{tl([0, start, t_end, T - 0.6, T], T)}" dur="{T}s" repeatCount="indefinite"/></rect>
<text x="624" y="198" fill="{GRAY}" font-size="10" text-anchor="end">less</text>{legend}<text x="722" y="198" fill="{GRAY}" font-size="10">more</text>
</svg>'''
    (ASSETS / "harvest.svg").write_text(svg)
    return len(svg), n, total, T


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    size, n, total, T = build()
    print(f"harvest.svg: {size} bytes, {n} days swept, {total} contributions, loop {T}s")
