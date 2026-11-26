#!/usr/bin/env python3
"""Generate an animated, self-hosted GitHub stats dashboard SVG.

Reads public stats through the GitHub GraphQL API using the default
GITHUB_TOKEN provided to Actions, then writes assets/stats/dashboard.svg.
Standard library only.
"""

import json
import math
import os
import urllib.request
import xml.sax.saxutils as sax

API = "https://api.github.com/graphql"
TOKEN = os.environ["GITHUB_TOKEN"]
LOGIN = os.environ.get("GH_LOGIN", "Mohmed-Dyaa-Al-Arja")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "stats", "dashboard.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "stats-dashboard-generator",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]["user"]


def fmt(n):
    return f"{n:,}"


def esc(s):
    return sax.escape(str(s))


def build_svg(data):
    followers = data["followers"]["totalCount"]
    repos = data["repositories"]["nodes"]
    repo_count = data["repositories"]["totalCount"]
    stars = sum(r["stargazerCount"] for r in repos)
    commits = data["contributionsCollection"]["totalCommitContributions"]

    lang_sizes = {}
    lang_colors = {}
    for r in repos:
        for edge in r["languages"]["edges"]:
            name = edge["node"]["name"]
            lang_sizes[name] = lang_sizes.get(name, 0) + edge["size"]
            if edge["node"]["color"]:
                lang_colors[name] = edge["node"]["color"]
    total_lang = sum(lang_sizes.values()) or 1
    top_langs = sorted(lang_sizes.items(), key=lambda kv: kv[1], reverse=True)[:5]

    weeks = data["contributionsCollection"]["contributionCalendar"]["weeks"]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks][-26:]

    W, H = 840, 532
    p = []
    a = p.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="\'Segoe UI\', Ubuntu, \'Helvetica Neue\', Arial, sans-serif">')
    a("<defs>")
    a('<linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
      '<stop offset="0%" stop-color="#7c3aed"/>'
      '<stop offset="50%" stop-color="#2563eb"/>'
      '<stop offset="100%" stop-color="#06b6d4"/>'
      '<animateTransform attributeName="gradientTransform" type="rotate" from="0 0.5 0.5" to="360 0.5 0.5" dur="12s" repeatCount="indefinite"/>'
      "</linearGradient>")
    a('<linearGradient id="titleGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
      '<stop offset="0%" stop-color="#a78bfa"/>'
      '<stop offset="100%" stop-color="#22d3ee"/>'
      '<animateTransform attributeName="gradientTransform" type="translate" from="-0.5 0" to="0.5 0" dur="6s" repeatCount="indefinite"/>'
      "</linearGradient>")
    a('<linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0%" stop-color="#22d3ee" stop-opacity="0.35"/>'
      '<stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>'
      "</linearGradient>")
    a('<radialGradient id="blob1" cx="50%" cy="50%" r="50%">'
      '<stop offset="0%" stop-color="#7c3aed" stop-opacity="0.28"/>'
      '<stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>'
      "</radialGradient>")
    a('<radialGradient id="blob2" cx="50%" cy="50%" r="50%">'
      '<stop offset="0%" stop-color="#0ea5e9" stop-opacity="0.22"/>'
      '<stop offset="100%" stop-color="#0ea5e9" stop-opacity="0"/>'
      "</radialGradient>")
    a('<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
      '<feGaussianBlur stdDeviation="3.2" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      "</filter>")
    a('<filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="1.6" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      "</filter>")
    a("</defs>")

    # Background
    a(f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="16" fill="#0d1117" stroke="url(#borderGrad)" stroke-width="2.5"/>')

    # Aurora blobs (animated)
    a('<ellipse cx="180" cy="90" rx="260" ry="140" fill="url(#blob1)">'
      '<animate attributeName="cx" values="180;640;180" dur="18s" repeatCount="indefinite"/>'
      '<animate attributeName="cy" values="90;140;90" dur="13s" repeatCount="indefinite"/>'
      "</ellipse>")
    a('<ellipse cx="660" cy="380" rx="280" ry="150" fill="url(#blob2)">'
      '<animate attributeName="cx" values="660;200;660" dur="22s" repeatCount="indefinite"/>'
      '<animate attributeName="cy" values="380;300;380" dur="15s" repeatCount="indefinite"/>'
      "</ellipse>")

    # Twinkling starfield
    star_positions = [
        (60, 130), (130, 60), (240, 30), (330, 75), (430, 40), (520, 80),
        (620, 35), (710, 70), (790, 120), (780, 30), (70, 300), (810, 250),
        (45, 420), (795, 430), (200, 445), (640, 450), (380, 440), (560, 210),
    ]
    for i, (sx, sy) in enumerate(star_positions):
        r = 1.1 + (i % 3) * 0.5
        dur = 2.4 + (i % 5) * 0.7
        begin = (i % 7) * 0.4
        a(f'<circle cx="{sx}" cy="{sy}" r="{r:.1f}" fill="#8b9dc3">'
          f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
          "</circle>")

    # Header
    a(f'<text x="44" y="58" font-size="26" font-weight="800" letter-spacing="4" fill="url(#titleGrad)" filter="url(#glow)">GITHUB DASHBOARD</text>')
    a('<text x="44" y="80" font-size="12.5" fill="#7d8590" letter-spacing="1.5">live stats, regenerated every 12 hours by GitHub Actions</text>')
    a(f'<rect x="{W-44-14}" y="46" width="14" height="22" rx="2" fill="#22d3ee">'
      '<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/>'
      "</rect>")
    a(f'<line x1="44" y1="96" x2="{W-44}" y2="96" stroke="#21262d" stroke-width="1.5"/>')

    # Stat tiles
    tiles = [
        ("TOTAL STARS", fmt(stars), "star", "#fbbf24"),
        ("COMMITS · 365D", fmt(commits), "commit", "#22d3ee"),
        ("PUBLIC REPOS", fmt(repo_count), "repo", "#a78bfa"),
        ("FOLLOWERS", fmt(followers), "person", "#34d399"),
    ]
    tile_w, tile_h, gap, x0, y0 = 180, 112, 12, 44, 116
    for i, (label, value, icon, color) in enumerate(tiles):
        x = x0 + i * (tile_w + gap)
        begin = 0.15 + i * 0.18
        a(f'<g opacity="0">')
        a(f'<animate attributeName="opacity" from="0" to="1" dur="0.7s" begin="{begin}s" fill="freeze"/>')
        a(f'<animateTransform attributeName="transform" type="translate" from="0 14" to="0 0" dur="0.7s" begin="{begin}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1" keyTimes="0;1"/>')
        a(f'<rect x="{x}" y="{y0}" width="{tile_w}" height="{tile_h}" rx="12" fill="#161b22" stroke="#21262d" stroke-width="1.2"/>')
        a(f'<rect x="{x}" y="{y0}" width="{tile_w}" height="4" rx="2" fill="{color}" opacity="0.85"/>')
        # icons
        ix, iy = x + 18, y0 + 30
        if icon == "star":
            pts = []
            for k in range(10):
                ang = -math.pi / 2 + k * math.pi / 5
                rr = 11 if k % 2 == 0 else 4.6
                pts.append(f"{ix + rr * math.cos(ang):.1f},{iy + rr * math.sin(ang):.1f}")
            a(f'<polygon points="{" ".join(pts)}" fill="{color}" filter="url(#softGlow)"/>')
        elif icon == "commit":
            a(f'<circle cx="{ix}" cy="{iy}" r="7" fill="none" stroke="{color}" stroke-width="2.6" filter="url(#softGlow)"/>')
            a(f'<line x1="{ix - 16}" y1="{iy}" x2="{ix - 7}" y2="{iy}" stroke="{color}" stroke-width="2.6"/>')
            a(f'<line x1="{ix + 7}" y1="{iy}" x2="{ix + 16}" y2="{iy}" stroke="{color}" stroke-width="2.6"/>')
        elif icon == "repo":
            a(f'<rect x="{ix - 11}" y="{iy - 12}" width="22" height="24" rx="3" fill="none" stroke="{color}" stroke-width="2.4" filter="url(#softGlow)"/>')
            a(f'<line x1="{ix - 4}" y1="{iy - 12}" x2="{ix - 4}" y2="{iy - 2}" stroke="{color}" stroke-width="2.4"/>')
        else:
            a(f'<circle cx="{ix}" cy="{iy - 5}" r="6" fill="{color}" filter="url(#softGlow)"/>')
            a(f'<path d="M {ix - 10} {iy + 12} a 10 9 0 0 1 20 0 z" fill="{color}"/>')
        a(f'<text x="{x + 18}" y="{y0 + 74}" font-size="30" font-weight="800" fill="#e6edf3" filter="url(#softGlow)">{esc(value)}'
          f'<animate attributeName="opacity" values="1;0.82;1" dur="3s" begin="{begin}s" repeatCount="indefinite"/>'
          "</text>")
        a(f'<text x="{x + 18}" y="{y0 + 97}" font-size="11" font-weight="600" letter-spacing="1.6" fill="#7d8590">{esc(label)}</text>')
        a("</g>")

    # Languages
    ly = 262
    a(f'<text x="44" y="{ly}" font-size="13" font-weight="700" letter-spacing="2.5" fill="#9da7b3">TOP LANGUAGES</text>')
    bar_x, bar_max_w = 190, 470
    row_h = 26
    for i, (name, size) in enumerate(top_langs):
        y = ly + 16 + i * row_h
        pct = size / total_lang * 100
        w = max(8, bar_max_w * size / (top_langs[0][1] or 1))
        color = lang_colors.get(name, "#58a6ff")
        begin = 0.9 + i * 0.15
        a(f'<text x="44" y="{y + 11}" font-size="12.5" fill="#c9d1d9">{esc(name)}</text>')
        a(f'<rect x="{bar_x}" y="{y}" width="{bar_max_w}" height="10" rx="5" fill="#161b22"/>')
        a(f'<rect x="{bar_x}" y="{y}" width="0" height="10" rx="5" fill="{color}" filter="url(#softGlow)">'
          f'<animate attributeName="width" from="0" to="{w:.1f}" dur="1s" begin="{begin}s" fill="freeze" calcMode="spline" keySplines="0.22 1 0.36 1" keyTimes="0;1"/>'
          "</rect>")
        a(f'<text x="{bar_x + bar_max_w + 12}" y="{y + 10}" font-size="12" font-weight="600" fill="{color}">{pct:.1f}%</text>')

    # Contribution sparkline
    sy = ly + 16 + 5 * row_h + 24
    a(f'<text x="44" y="{sy}" font-size="13" font-weight="700" letter-spacing="2.5" fill="#9da7b3">CONTRIBUTIONS · LAST 26 WEEKS</text>')
    chart_y, chart_h = sy + 14, 56
    chart_x0, chart_w = 44, W - 88
    peak = max(weekly) or 1
    n = len(weekly)
    step = chart_w / max(1, n - 1)
    pts = []
    for i, v in enumerate(weekly):
        px = chart_x0 + i * step
        py = chart_y + chart_h - (v / peak) * (chart_h - 6)
        pts.append((px, py))
    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    area = f"{chart_x0:.1f},{chart_y + chart_h} " + line + f" {chart_x0 + chart_w:.1f},{chart_y + chart_h}"
    a(f'<polygon points="{area}" fill="url(#sparkFill)"/>')
    approx_len = int(chart_w * 1.6)
    a(f'<polyline points="{line}" fill="none" stroke="#22d3ee" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" filter="url(#softGlow)" '
      f'stroke-dasharray="{approx_len}" stroke-dashoffset="{approx_len}">'
      f'<animate attributeName="stroke-dashoffset" from="{approx_len}" to="0" dur="2.2s" begin="1.4s" fill="freeze"/>'
      "</polyline>")
    if pts:
        lx, lyv = pts[-1]
        a(f'<circle cx="{lx:.1f}" cy="{lyv:.1f}" r="4.5" fill="#22d3ee" filter="url(#glow)">'
          '<animate attributeName="r" values="4.5;6.5;4.5" dur="2s" repeatCount="indefinite"/>'
          '<animate attributeName="opacity" values="1;0.55;1" dur="2s" repeatCount="indefinite"/>'
          "</circle>")
        a(f'<text x="{lx - 6:.1f}" y="{lyv - 12:.1f}" font-size="12" font-weight="700" fill="#22d3ee" text-anchor="end">{weekly[-1]}/wk</text>')
    a(f'<line x1="{chart_x0}" y1="{chart_y + chart_h}" x2="{chart_x0 + chart_w}" y2="{chart_y + chart_h}" stroke="#21262d" stroke-width="1.2"/>')

    # Footer pulse dot
    fy = H - 18
    a(f'<circle cx="46" cy="{fy}" r="4" fill="#34d399">'
      '<animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/>'
      "</circle>")
    a(f'<text x="58" y="{fy + 4}" font-size="11" fill="#7d8590" letter-spacing="1.2">auto-generated in this repo, no external services</text>')

    a("</svg>")
    return "\n".join(p)


def main():
    data = fetch()
    svg = build_svg(data)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {os.path.normpath(OUT)} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
