#!/usr/bin/env python3
"""Refreshes live profile data. Standard library only.

Writes:  assets/stats.svg, assets/leetcode.svg
Edits:   README.md between <!--RECENT_START-->/<!--RECENT_END--> and <!--SYNC_START-->/<!--SYNC_END-->

Usage:   python scripts/generate.py          (live data, run by the GitHub Action)
         python scripts/generate.py --seed   (offline placeholder data)
"""
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
USER = os.environ.get("GH_USER", "prajwal-sv")
LC_USER = os.environ.get("LEETCODE_USER", "prajwal__sv")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SEED = "--seed" in sys.argv

FONT = "'Fira Code','SF Mono',Consolas,'DejaVu Sans Mono',monospace"
BG, PANEL, LINE = "#0d1117", "#161b22", "#30363d"
GREEN, CYAN, PURPLE, AMBER, GRAY, TEXT = "#3fb950", "#58a6ff", "#d2a8ff", "#e3b341", "#8b949e", "#c9d1d9"
LANG_COLORS = {"Jupyter Notebook": "#DA5B0B", "Python": "#3572A5", "HTML": "#e34c26", "C++": "#f34b7d",
               "C": "#8a8a8a", "JavaScript": "#f1e05a", "CSS": "#8a63d2", "Shell": "#89e051",
               "TypeScript": "#3178c6", "Java": "#b07219", "Other": "#6e7681"}

SEED_DATA = {
    "repos": 24, "stars": 7, "followers": 6, "following": 6, "contributions": None,
    "languages": {"Jupyter Notebook": 4, "Python": 1, "HTML": 1},
    "recent": [
        ("hotel-booking-analysis", "End-to-end analysis of 119K hotel bookings with hypothesis tests", "Jupyter Notebook", 1, None),
        ("mumbai-heat-aq-risk", "Streamlit dashboard for 23 Mumbai monitoring stations", "HTML", 5, None),
        ("AI-Learning-Career-Assistant", "AI-powered smart learning and career assistant", "Jupyter Notebook", 1, None),
        ("Algerian-Forest-Fires-Dataset---Project-", "ML on Algerian forest-fire records", "Jupyter Notebook", 0, None),
        ("Machine-Learning", "End-to-end ML curriculum from Python to deployment", "Jupyter Notebook", 0, None),
    ],
}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def http(url, body=None, headers=None):
    h = {"User-Agent": "profile-readme-bot", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        h["Authorization"] = f"Bearer {TOKEN}"
    if headers:
        h.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_github():
    user = http(f"https://api.github.com/users/{USER}")
    repos, page = [], 1
    while True:
        chunk = http(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&sort=pushed")
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    langs = {}
    for r in own:
        try:
            for k, v in http(r["languages_url"]).items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            pass
    contrib = None
    if TOKEN:
        try:
            q = {"query": "query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{totalContributions}}}}",
                 "variables": {"l": USER}}
            contrib = http("https://api.github.com/graphql", q)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        except Exception:
            pass
    recent = [(r["name"], r["description"] or "", r["language"] or "", r["stargazers_count"], r["pushed_at"])
              for r in sorted(own, key=lambda r: r["pushed_at"], reverse=True) if r["name"].lower() != USER.lower()][:5]
    return {"repos": user["public_repos"], "stars": sum(r["stargazers_count"] for r in own),
            "followers": user["followers"], "following": user["following"],
            "contributions": contrib, "languages": langs, "recent": recent}


def fade(delay, dur=1.4):
    """Fade-in that still renders fully where SMIL is unsupported."""
    return f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{delay / dur:.3f};1" dur="{dur}s" begin="0s" fill="freeze"/>'


def render_stats(s):
    langs = dict(s["languages"])
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)
    if len(top) > 6:
        top = top[:5] + [("Other", sum(v for _, v in top[5:]))]
    tiles = [("public repos", s["repos"], GREEN), ("stars earned", s["stars"], CYAN), ("followers", s["followers"], PURPLE),
             (("contributions / yr", s["contributions"], AMBER) if s["contributions"] is not None
              else ("following", s["following"], AMBER))]
    out = []
    for i, (label, val, col) in enumerate(tiles):
        x, y = 24 + (i % 2) * 190, 64 + (i // 2) * 92
        out.append(f'<g>{fade(0.1 * i)}<rect x="{x}" y="{y}" width="176" height="78" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
                   f'<text x="{x + 16}" y="{y + 26}" fill="{GRAY}" font-size="12">{esc(label)}</text>'
                   f'<text x="{x + 16}" y="{y + 62}" fill="{col}" font-size="30" font-weight="700">{esc(val)}</text></g>')
    bx, bw, by = 420, 356, 92
    seg, acc = [], 0.0
    for i, (name, v) in enumerate(top):
        w = bw * v / total
        c = LANG_COLORS.get(name, "#6e7681")
        kt = f"0;{min(0.1 * i + 0.1, 0.9):.2f};1"
        seg.append(f'<rect x="{bx + acc:.1f}" y="{by}" width="{w:.1f}" height="14" fill="{c}">'
                   f'<animate attributeName="width" values="0;0;{w:.1f}" keyTimes="{kt}" dur="1.6s" begin="0s" fill="freeze"/></rect>')
        acc += w
    legend = []
    for i, (name, v) in enumerate(top):
        lx, ly = bx, 140 + i * 21
        c = LANG_COLORS.get(name, "#6e7681")
        legend.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{c}"/>'
                      f'<text x="{lx + 18}" y="{ly}" fill="{TEXT}" font-size="12">{esc(name)}</text>'
                      f'<text x="{bx + bw}" y="{ly}" fill="{GRAY}" font-size="12" text-anchor="end">{100 * v / total:.1f}%</text>')
    stamp = "seed data - run the workflow" if SEED else "synced " + dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="260" viewBox="0 0 800 260" font-family="{FONT}" role="img" aria-label="GitHub statistics for {esc(USER)}">
<rect x="0.5" y="0.5" width="799" height="259" rx="12" fill="{BG}" stroke="{LINE}"/>
<text x="24" y="36" fill="{GREEN}" font-size="14" font-weight="700">$</text><text x="42" y="36" fill="{TEXT}" font-size="14">gh stats --user {esc(USER)}</text>
{''.join(out)}
<text x="{bx}" y="78" fill="{GRAY}" font-size="12">top languages (by code size)</text>
<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="14" rx="7"/></clipPath>
<g clip-path="url(#bar)"><rect x="{bx}" y="{by}" width="{bw}" height="14" fill="#21262d"/>{''.join(seg)}</g>
{''.join(legend)}
<text x="776" y="246" fill="{GRAY}" font-size="10" text-anchor="end">{stamp}</text>
</svg>'''


def fetch_leetcode():
    q = {"query": "query($u:String!){allQuestionsCount{difficulty count} matchedUser(username:$u){profile{ranking} "
                  "submitStatsGlobal{acSubmissionNum{difficulty count}}}}", "variables": {"u": LC_USER}}
    d = http("https://leetcode.com/graphql", q, {"Referer": "https://leetcode.com", "Accept": "application/json"})["data"]
    solved = {x["difficulty"]: x["count"] for x in d["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]}
    avail = {x["difficulty"]: x["count"] for x in d["allQuestionsCount"]}
    return {"solved": solved, "avail": avail, "rank": d["matchedUser"]["profile"]["ranking"]}


def render_leetcode(lc):
    solved = lc["solved"] if lc else {}
    avail = lc["avail"] if lc else {}
    total = solved.get("All", "-")
    rank = f"global rank #{lc['rank']:,}" if lc else "syncing - run the workflow"
    rows = []
    for i, (name, col) in enumerate([("Easy", GREEN), ("Medium", AMBER), ("Hard", "#f85149")]):
        y = 66 + i * 28
        s, a = solved.get(name, 0), avail.get(name, 1) or 1
        w = 300 * min(s / a, 1)
        label = f"{s} / {a}" if lc else "-"
        rows.append(f'<text x="300" y="{y + 9}" fill="{GRAY}" font-size="12">{name}</text>'
                    f'<rect x="372" y="{y}" width="300" height="10" rx="5" fill="#21262d"/>'
                    f'<rect x="372" y="{y}" width="{w:.1f}" height="10" rx="5" fill="{col}">'
                    f'<animate attributeName="width" values="0;0;{w:.1f}" keyTimes="0;0.2;1" dur="1.6s" begin="0s" fill="freeze"/></rect>'
                    f'<text x="776" y="{y + 9}" fill="{TEXT}" font-size="12" text-anchor="end">{label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="160" viewBox="0 0 800 160" font-family="{FONT}" role="img" aria-label="LeetCode progress for {esc(LC_USER)}">
<rect x="0.5" y="0.5" width="799" height="159" rx="12" fill="{BG}" stroke="{LINE}"/>
<text x="24" y="36" fill="{GREEN}" font-size="14" font-weight="700">$</text><text x="42" y="36" fill="{TEXT}" font-size="14">leetcode --user {esc(LC_USER)}</text>
<text x="40" y="104" fill="{AMBER}" font-size="46" font-weight="700">{esc(total)}</text>
<text x="40" y="126" fill="{GRAY}" font-size="12">problems solved</text>
<text x="40" y="146" fill="{GRAY}" font-size="11">{esc(rank)}</text>
{''.join(rows)}
</svg>'''


def ago(iso):
    if not iso:
        return "-"
    d = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    return "today" if d < 1 else f"{d}d ago" if d < 30 else f"{d // 30}mo ago"


def recent_table(recent):
    rows = ["| Repo | What it is | Lang | Stars | Updated |", "| :-- | :-- | :-- | :-: | :-: |"]
    for name, desc, lang, stars, pushed in recent:
        desc = (desc[:90] + "...") if len(desc) > 90 else desc
        rows.append(f"| [**{name}**](https://github.com/{USER}/{name}) | {desc.replace('|', '/')} | `{lang or '-'}` | {stars} | {ago(pushed)} |")
    return "\n".join(rows)


def replace_block(text, tag, content):
    pat = re.compile(rf"(<!--{tag}_START-->).*?(<!--{tag}_END-->)", re.S)
    return pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", text)


def main():
    ASSETS.mkdir(exist_ok=True)
    data = SEED_DATA if SEED else fetch_github()
    (ASSETS / "stats.svg").write_text(render_stats(data))

    lc = None
    if not SEED:
        try:
            lc = fetch_leetcode()
        except Exception as e:
            print("leetcode fetch failed:", e)
    if lc or not (ASSETS / "leetcode.svg").exists():
        (ASSETS / "leetcode.svg").write_text(render_leetcode(lc))

    text = README.read_text()
    text = replace_block(text, "RECENT", recent_table(data["recent"]))
    stamp = "seed data" if SEED else dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    text = replace_block(text, "SYNC", f"<sub>last synced: {stamp}</sub>")
    README.write_text(text)
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import build_game
        build_game.build()
    except Exception as e:
        print("harvest build failed:", e)
    print("done:", "seed" if SEED else "live")


if __name__ == "__main__":
    main()