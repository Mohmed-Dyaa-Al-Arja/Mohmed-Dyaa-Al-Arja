#!/usr/bin/env python3
"""Animated 3D weekly activity skyline, self-hosted SVG.

One 3D bar = one week of GitHub contributions. Uses the GitHub GraphQL API
with the default GITHUB_TOKEN and writes assets/city/city.svg.
Standard library only. Set DEMO=1 for fake data.
"""

import datetime
import json
import os
import random
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "Mohmed-Dyaa-Al-Arja")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "city", "city.svg")
WEEKS = 26
FONT = "Segoe UI,Helvetica,Arial,sans-serif"

QUERY = """
query($login: String!) {
 user(login: $login) {
 contributionsCollection {
 contributionCalendar {
 totalContributions
 weeks { firstDay contributionDays { contributionCount date } }
 }
 }
 }
}
"""


def fetch():
    if os.environ.get("DEMO"):
        random.seed(5)
        start = datetime.date(2026, 5, 31)
        weeks = []
        for w in range(53):
            d0 = start + datetime.timedelta(days=7 * (w - 26))
            days = [{"contributionCount": random.choice([0, 0, 0, 1, 2, 4, 9]) if random.random() > 0.55 else 0,
                     "date": str(d0 + datetime.timedelta(days=d))} for d in range(7)]
            weeks.append({"firstDay": str(d0), "contributionDays": days})
        return {"total": sum(x["contributionCount"] for w in weeks for x in w["contributionDays"]), "weeks": weeks}
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "city-generator"},
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


def lerp(c1, c2, t):
    a = [int(c1.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(c2.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def color_for(t):
    # low (blue) -> mid (violet) -> high (pink)
    return lerp("#38bdf8", "#a78bfa", t * 2) if t < 0.5 else lerp("#a78bfa", "#f472b6", (t - 0.5) * 2)


def nice_step(mx):
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500):
        if mx / s <= 4:
            return s
    return 1000


def build(data):
    weeks = data["weeks"][-WEEKS:]
    totals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    active = [sum(1 for d in w["contributionDays"] if d["contributionCount"] > 0) for w in weeks]
    shown_total = sum(totals)
    peak = max(totals) or 1
    best_i = totals.index(peak)
    step = nice_step(peak)
    top_val = ((peak + step - 1) // step) * step
    active_days = sum(active)
    cur = 0
    for t in reversed(totals):
        if t > 0:
            cur += 1
        else:
            break
    busy_weeks = sum(1 for t in totals if t > 0)

    W, H = 840, 560
    X0, X1 = 86, 796          # chart plot area
    BASE = 392                # baseline y (front edge of the floor)
    CH = 250                  # height for top_val
    n = len(weeks)
    slot = (X1 - X0) / n
    bw = slot * 0.62
    dx, dy = 7, -4            # 3D depth offset

    p, a = [], None
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Weekly contribution skyline: one 3D bar per week, taller means more contributions">')
    a('<defs>'
      '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#150d2e"/></linearGradient>'
      '<linearGradient id="bd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="0.5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>'
      '<linearGradient id="lg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="0.5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>'
      '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#a78bfa" stop-opacity="0.32"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>'
      '<radialGradient id="glow2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#22d3ee" stop-opacity="0.28"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>'
      '<clipPath id="clip"><rect x="2" y="2" width="836" height="556" rx="22"/></clipPath>'
      '</defs>')
    a(f'<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>')
    a('<g clip-path="url(#clip)">')
    a('<ellipse cx="260" cy="320" rx="280" ry="170" fill="url(#glow)"><animate attributeName="cx" values="240;340;240" dur="14s" repeatCount="indefinite"/></ellipse>')
    a('<ellipse cx="620" cy="380" rx="260" ry="150" fill="url(#glow2)"><animate attributeName="cx" values="660;540;660" dur="17s" repeatCount="indefinite"/></ellipse>')
    stars = [(60, 40), (150, 90), (380, 36), (480, 30), (700, 36), (790, 96), (820, 220), (40, 250), (810, 340), (30, 420)]
    for k, (sx, sy) in enumerate(stars):
        a(f'<circle cx="{sx}" cy="{sy}" r="{1 + (k % 3) * 0.5}" fill="#fff" opacity="0.3">'
          f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{2.5 + (k % 5) * 0.8}s" begin="{(k % 6) * 0.5}s" repeatCount="indefinite"/></circle>')
    a('</g>')
    a(f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="22" fill="none" stroke="url(#bd)" stroke-width="2" opacity="0.85"/>')
    # title + plain-language explanation
    a(f'<text x="44" y="54" font-family="{FONT}" font-size="26" font-weight="700" fill="#e6edf3">My activity, week by week</text>')
    a(f'<text x="44" y="80" font-family="{FONT}" font-size="14" fill="#9fb0c8">Each 3D bar is one week of GitHub work (commits, PRs, issues). The taller the bar, the more I did that week.</text>')
    a(f'<text x="44" y="100" font-family="{FONT}" font-size="12" fill="#6f7f99">Last {n} weeks, oldest on the left, this week on the right.</text>')

    # y axis grid
    a(f'<text x="30" y="{BASE - CH / 2:.0f}" font-family="{FONT}" font-size="11" fill="#6f7f99" text-anchor="middle" transform="rotate(-90 30 {BASE - CH / 2:.0f})">contributions per week</text>')
    v = 0
    while v <= top_val:
        y = BASE - CH * v / top_val
        a(f'<line x1="{X0 - 8}" y1="{y:.1f}" x2="{X1 + 10}" y2="{y:.1f}" stroke="#2a3a66" stroke-width="1" stroke-dasharray="{"0" if v == 0 else "3 5"}" opacity="{0.9 if v == 0 else 0.55}"/>')
        a(f'<text x="{X0 - 14}" y="{y + 4:.1f}" font-family="{FONT}" font-size="11" fill="#8b9bb4" text-anchor="end">{v}</text>')
        v += step

    # floor strip
    a(f'<polygon points="{X0 - 8},{BASE} {X1 + 10},{BASE} {X1 + 10 + dx},{BASE + dy} {X0 - 8 + dx},{BASE + dy}" fill="#101a33"/>')

    # bars (draw left to right; depth goes up-right so later bars overlap earlier only slightly)
    prev_month = None
    for i, (w, t) in enumerate(zip(weeks, totals)):
        x = X0 + i * slot + (slot - bw) / 2
        ratio = t / peak
        col = color_for(ratio) if t > 0 else "#243357"
        h = 0 if t == 0 else max(5, CH * t / top_val)
        delay = 0.25 + i * 0.07
        if t == 0:
            h = 2
        front = f"{x:.1f},{BASE - h:.1f} {x + bw:.1f},{BASE - h:.1f} {x + bw:.1f},{BASE} {x:.1f},{BASE}"
        side = f"{x + bw:.1f},{BASE - h:.1f} {x + bw + dx:.1f},{BASE - h + dy:.1f} {x + bw + dx:.1f},{BASE + dy} {x + bw:.1f},{BASE}"
        top = f"{x:.1f},{BASE - h:.1f} {x + dx:.1f},{BASE - h + dy:.1f} {x + bw + dx:.1f},{BASE - h + dy:.1f} {x + bw:.1f},{BASE - h:.1f}"
        a(f'<g transform="translate(0,{BASE})"><g>'
          f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1.05;1 1" keyTimes="0;0.7;1" dur="0.8s" begin="{delay:.2f}s" fill="freeze"/>'
          f'<g transform="translate(0,{-BASE})">'
          f'<polygon points="{front}" fill="{shade(col, 0.85)}"/>'
          f'<polygon points="{side}" fill="{shade(col, 0.55)}"/>'
          f'<polygon points="{top}" fill="{shade(col, 1.12) if t else col}"/>'
          f'</g></g></g>')
        if t > 0:
            is_best = i == best_i
            a(f'<text x="{x + bw / 2 + dx / 2:.1f}" y="{BASE - h + dy - 7:.1f}" font-family="{FONT}" font-size="{12 if is_best else 10}" font-weight="{700 if is_best else 400}" fill="{"#fbbf24" if is_best else "#cbd5e1"}" text-anchor="middle" opacity="0">'
              f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay + 0.7:.2f}s" fill="freeze"/>{t}</text>')
        # x labels: month name where a new month starts, otherwise a small tick
        try:
            d = datetime.date.fromisoformat(w["contributionDays"][0]["date"])
        except Exception:
            d = None
        cx = x + bw / 2
        if d and d.month != prev_month:
            prev_month = d.month
            a(f'<line x1="{cx:.1f}" y1="{BASE + 3}" x2="{cx:.1f}" y2="{BASE + 9}" stroke="#6f7f99"/>')
            a(f'<text x="{cx:.1f}" y="{BASE + 24}" font-family="{FONT}" font-size="12" font-weight="600" fill="#cbd5e1" text-anchor="middle">{d.strftime("%b")}</text>')
        else:
            a(f'<line x1="{cx:.1f}" y1="{BASE + 3}" x2="{cx:.1f}" y2="{BASE + 6}" stroke="#3a4a70"/>')
    # best-week callout
    bx = X0 + best_i * slot + slot / 2
    bh = BASE - max(5, CH * peak / top_val)
    a(f'<text x="{X0}" y="{BASE + 42}" font-family="{FONT}" font-size="11" fill="#6f7f99">each tick = one week</text>')

    # legend that teaches the reading
    ly = BASE + 62
    a(f'<rect x="44" y="{ly}" width="752" height="48" rx="12" fill="#0f1830" stroke="#2a3a66"/>')
    a(f'<text x="60" y="{ly + 20}" font-family="{FONT}" font-size="12" font-weight="700" fill="#e6edf3">How to read it</text>')
    a(f'<text x="60" y="{ly + 37}" font-family="{FONT}" font-size="12" fill="#9fb0c8">Short blue bar = a quiet week. Tall pink bar = a busy week. Number on top = contributions that week. Gold number = my best week.</text>')
    a(f'<rect x="640" y="{ly + 12}" width="140" height="8" rx="4" fill="url(#lg)"/>')
    a(f'<text x="640" y="{ly + 8}" font-family="{FONT}" font-size="10" fill="#6f7f99">quiet</text>')
    a(f'<text x="780" y="{ly + 8}" font-family="{FONT}" font-size="10" fill="#6f7f99" text-anchor="end">busy</text>')

    # stat chips
    chips = [(f"{shown_total:,}", f"contributions, last {n} wks", "#22d3ee"),
             (f"{busy_weeks} of {n}", "weeks with activity", "#a78bfa"),
             (f"{active_days}", "days with a commit", "#f472b6"),
             (f"{peak}", "best week", "#fbbf24")]
    cw, gap = 176, 16
    cy = H - 64
    # placed under legend only if room: legend ends at ly+48 = BASE+110 = 502; chips at 504 would collide, so shift
    cy = ly + 48 + 10
    for k, (val, lab, col) in enumerate(chips):
        cx = 44 + k * (cw + gap)
        a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="{1.0 + k * 0.15:.2f}s" fill="freeze"/>'
          f'<rect x="{cx}" y="{cy}" width="{cw}" height="0.1" fill="none"/>'
          f'<text x="{cx}" y="{cy + 14}" font-family="{FONT}" font-size="14" font-weight="700" fill="{col}">{val} <tspan font-size="11" font-weight="400" fill="#8b9bb4">{lab}</tspan></text></g>')
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
