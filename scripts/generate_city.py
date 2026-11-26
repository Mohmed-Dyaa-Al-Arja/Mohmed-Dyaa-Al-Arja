#!/usr/bin/env python3
"""Generate an animated isometric 3D contribution city as a self-hosted SVG.

Uses the GitHub GraphQL API with the default GITHUB_TOKEN and writes
assets/city/city.svg. Standard library only. Set DEMO=1 for fake data.
"""

import json
import os
import random
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "Mohmed-Dyaa-Al-Arja")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "city", "city.svg")

QUERY = """
query($login: String!) {
 user(login: $login) {
 contributionsCollection {
 contributionCalendar {
 totalContributions
 weeks { contributionDays { contributionCount date } }
 }
 }
 }
}
"""


def fetch():
    if os.environ.get("DEMO"):
        random.seed(3)
        weeks = []
        for w in range(53):
            days = []
            for d in range(7):
                c = random.choice([0, 0, 0, 1, 2, 3, 5, 8, 12]) if random.random() > 0.3 else 0
                days.append({"contributionCount": c, "date": "2026-01-01"})
            weeks.append({"contributionDays": days})
        return {"total": sum(x["contributionCount"] for w in weeks for x in w["contributionDays"]), "weeks": weeks}
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "city-generator"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return {"total": cal["totalContributions"], "weeks": cal["weeks"]}


def shade(hex_color, f):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)))


# level colours: low (teal) -> high (violet/pink)
LEVELS = ["#1e3a5f", "#0ea5e9", "#22d3ee", "#a78bfa", "#f472b6"]


def build(data):
    weeks = data["weeks"]
    grid = [[d["contributionCount"] for d in w["contributionDays"]] for w in weeks]
    n_w = len(grid)
    flat = [c for col in grid for c in col]
    peak = max(flat) or 1
    nz = sorted(c for c in flat if c > 0)

    def level(c):
        if c == 0:
            return 0
        if not nz:
            return 1
        rank = nz.index(c) / len(nz)
        return 1 + min(3, int(rank * 4))

    # streaks
    longest = cur = 0
    for c in flat:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    cur = 0
    for c in reversed(flat):
        if c > 0:
            cur += 1
        else:
            break
    active_days = len(nz)

    TW, TH, MAXH = 24, 12, 90
    W, H = 840, 540
    ox = 0
    oy = 0

    def proj(i, j):
        return ox + (i - j) * TW / 2 + 6 * TW / 2, oy + (i + j) * TH / 2

    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="3D contribution city">')
    a('<defs>'
      '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#150d2e"/></linearGradient>'
      '<linearGradient id="bd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>'
      '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#a78bfa" stop-opacity="0.35"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>'
      '<radialGradient id="glow2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#22d3ee" stop-opacity="0.3"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>'
      '<clipPath id="clip"><rect x="2" y="2" width="836" height="536" rx="22"/></clipPath>'
      '</defs>')
    a(f'<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>')
    a('<g clip-path="url(#clip)">')
    a('<ellipse cx="260" cy="300" rx="280" ry="170" fill="url(#glow)"><animate attributeName="cx" values="240;340;240" dur="14s" repeatCount="indefinite"/></ellipse>')
    a('<ellipse cx="620" cy="360" rx="260" ry="150" fill="url(#glow2)"><animate attributeName="cx" values="660;540;660" dur="17s" repeatCount="indefinite"/></ellipse>')
    stars = [(60, 40), (150, 90), (260, 30), (380, 70), (480, 36), (600, 80), (700, 40), (790, 100), (820, 200), (40, 220), (810, 330), (30, 380), (790, 470), (120, 500), (700, 500)]
    for k, (sx, sy) in enumerate(stars):
        a(f'<circle cx="{sx}" cy="{sy}" r="{1 + (k % 3) * 0.5}" fill="#fff" opacity="0.3">'
          f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{2.5 + (k % 5) * 0.8}s" begin="{(k % 6) * 0.5}s" repeatCount="indefinite"/></circle>')
    a('</g>')
    a(f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="22" fill="none" stroke="url(#bd)" stroke-width="2" opacity="0.85"/>')
    a('<text x="44" y="56" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="24" font-weight="700" fill="#e6edf3" letter-spacing="2">CONTRIBUTION CITY</text>')
    a('<text x="44" y="80" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="13" fill="#8b9bb4">every building is one day. taller means more contributions. last 12 months.</text>')

    minx, _ = proj(-0.5, 6.5)
    maxx, _ = proj(n_w - 0.5, -0.5)
    miny = proj(-0.5, -0.5)[1] - MAXH - 12
    maxy = proj(n_w - 0.5, 6.5)[1] + 4
    sc = min(752 / (maxx - minx), 360 / (maxy - miny))
    tx = 44 + (752 - sc * (maxx - minx)) / 2 - sc * minx
    ty = 112 + (360 - sc * (maxy - miny)) / 2 - sc * miny
    a(f'<g transform="translate({tx:.1f},{ty:.1f}) scale({sc:.3f})">')
    # ground plate
    c1 = proj(-0.5, -0.5)
    c2 = proj(n_w - 0.5, -0.5)
    c3 = proj(n_w - 0.5, 6.5)
    c4 = proj(-0.5, 6.5)
    a('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#101a33" stroke="#2a3a66" stroke-width="1.2"/>'
      % (c1 + c2 + c3 + c4))
    a('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#0a1226" opacity="0.9" transform="translate(0,10)"/>'
      % (c4 + c3 + (c3[0], c3[1] + 0) + (c4[0], c4[1] + 0)))

    cells = [(i, j) for i in range(n_w) for j in range(len(grid[i]))]
    cells.sort(key=lambda t: (t[0] + t[1], t[0]))
    for i, j in cells:
        c = grid[i][j]
        x, y = proj(i, j)
        hw, hh = TW / 2 - 1.2, TH / 2 - 0.6
        lv = level(c)
        base = LEVELS[lv]
        delay = 0.2 + (i * 0.035) + j * 0.02
        if c == 0:
            a(f'<polygon points="{x:.1f},{y - hh:.1f} {x + hw:.1f},{y:.1f} {x:.1f},{y + hh:.1f} {x - hw:.1f},{y:.1f}" fill="#16213f" opacity="0.9"/>')
            continue
        h = 6 + (c / peak) * MAXH
        top = f"{x:.1f},{y - hh - h:.1f} {x + hw:.1f},{y - h:.1f} {x:.1f},{y + hh - h:.1f} {x - hw:.1f},{y - h:.1f}"
        left = f"{x - hw:.1f},{y - h:.1f} {x:.1f},{y + hh - h:.1f} {x:.1f},{y + hh:.1f} {x - hw:.1f},{y:.1f}"
        right = f"{x:.1f},{y + hh - h:.1f} {x + hw:.1f},{y - h:.1f} {x + hw:.1f},{y:.1f} {x:.1f},{y + hh:.1f}"
        a(f'<g transform="translate({x:.1f},{y:.1f})"><g>'
          f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1.06;1 1" keyTimes="0;0.7;1" dur="0.9s" begin="{delay:.2f}s" fill="freeze"/>'
          f'<g transform="translate({-x:.1f},{-y:.1f})">'
          f'<polygon points="{left}" fill="{shade(base, 0.62)}"/>'
          f'<polygon points="{right}" fill="{shade(base, 0.82)}"/>'
          f'<polygon points="{top}" fill="{base}"/>'
          f'</g></g></g>')

    a('</g>')
    # stat chips
    chips = [("TOTAL", f"{data['total']:,}", "#22d3ee"), ("ACTIVE DAYS", str(active_days), "#a78bfa"),
             ("LONGEST STREAK", f"{longest} d", "#f472b6"), ("CURRENT STREAK", f"{cur} d", "#34d399"), ("BEST DAY", str(peak), "#fbbf24")]
    cw, gap, cy = 148, 10, H - 72
    for k, (lab, val, col) in enumerate(chips):
        cx = 44 + k * (cw + gap)
        a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="{1.2 + k * 0.15:.2f}s" fill="freeze"/>'
          f'<rect x="{cx}" y="{cy}" width="{cw}" height="52" rx="12" fill="#0f1830" stroke="{col}" stroke-opacity="0.55"/>'
          f'<text x="{cx + 14}" y="{cy + 24}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="20" font-weight="700" fill="{col}">{val}</text>'
          f'<text x="{cx + 14}" y="{cy + 41}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="10" letter-spacing="1" fill="#8b9bb4">{lab}</text></g>')
    # legend
    lx = W - 44 - 5 * 16 - 60
    a(f'<text x="{lx - 34}" y="106" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="#8b9bb4">less</text>')
    for k, col in enumerate(LEVELS):
        a(f'<rect x="{lx + k * 16}" y="96" width="12" height="12" rx="3" fill="{col}"/>')
    a(f'<text x="{lx + 5 * 16 + 4}" y="106" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="#8b9bb4">more</text>')
    a('</svg>')
    return "\n".join(p)


def main():
    svg = build(fetch())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.normpath(OUT), len(svg))


if __name__ == "__main__":
    main()
