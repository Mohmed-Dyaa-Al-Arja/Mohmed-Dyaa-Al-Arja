#!/usr/bin/env python3
"""Generate animated playing-card style project cards as self-hosted SVGs.

Writes assets/cards/*.svg. Star counts come from the GitHub REST API using the
default GITHUB_TOKEN (falls back to 0 on failure). Standard library only.
"""

import json
import os
import urllib.request

OWNER = os.environ.get("GH_LOGIN", "Mohmed-Dyaa-Al-Arja")
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "cards")
FONT = "Segoe UI,Helvetica,Arial,sans-serif"

# slug, repo, rank, title, description, stack tags, accent1, accent2
CARDS = [
    ("teryaq", "TERYaq", "A", "TERYaq",
     "Clinical RAG for breast cancer: retrieval, visual evidence, safety checks",
     ["Python", "RAG", "LLMs"], "#f472b6", "#a78bfa"),
    ("rag-assistant", "rag-document-assistant", "K", "RAG Document Assistant",
     "Document Q&A with source citations and conversation memory",
     ["FastAPI", "FAISS", "LangChain"], "#22d3ee", "#6366f1"),
    ("vehicle-identifier", "Smart-Vehicle-Identifier", "Q", "Smart Vehicle Identifier",
     "AI vehicle recognition built in the NTI Applied AI program",
     ["Python", "Computer Vision"], "#34d399", "#22d3ee"),
    ("sales-forecasting", "sales-forecasting-project", "J", "Sales Forecasting",
     "End-to-end forecasting with notebooks, slides and deployment files",
     ["Python", "ML"], "#fbbf24", "#f472b6"),
    ("rocket-league-ai", "RocketLeague_AI_Project", "10", "Rocket League AI",
     "Game bot mixing search algorithms with reinforcement learning",
     ["Python", "RL"], "#fb923c", "#ef4444"),
    ("image-effects", "Mohmed-Dyaa-Al-Arja-Image-Processing-Effects", "9", "Image Processing Effects",
     "OpenCV filters and effects with a Dash web app",
     ["OpenCV", "Dash"], "#a78bfa", "#38bdf8"),
    ("breast-cancer-app", "breast-cancer-diagnosis-app", "8", "Breast Cancer Diagnosis",
     "Streamlit diagnosis app using a Decision Tree classifier",
     ["Streamlit", "scikit-learn"], "#f472b6", "#fb7185"),
]


def stars(repo):
    if os.environ.get("DEMO"):
        return 3
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{OWNER}/{repo}",
            headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "card-generator",
                     "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(json.load(r).get("stargazers_count", 0))
    except Exception as e:  # keep going, card still renders
        print("stars failed for", repo, e)
        return 0


def wrap(text, width):
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(idx, slug, rank, title, desc, tags, c1, c2, star_text, more=False):
    W, H = 260, 360
    uid = f"c{idx}"
    initials = "".join(ch for ch in title if ch.isupper())[:2] or title[:2].upper()
    if slug == "teryaq":
        initials = "TQ"
    if more:
        initials = "+"
    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)} project card">')
    a('<defs>'
      f'<linearGradient id="{uid}bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1326"/><stop offset="1" stop-color="#1a1236"/></linearGradient>'
      f'<linearGradient id="{uid}bd" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">'
      f'<stop offset="0" stop-color="{c1}"/><stop offset="0.5" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/>'
      f'<animateTransform attributeName="gradientTransform" type="rotate" from="0 {W / 2} {H / 2}" to="360 {W / 2} {H / 2}" dur="6s" repeatCount="indefinite"/></linearGradient>'
      f'<radialGradient id="{uid}orb" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{c1}" stop-opacity="0.55"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></radialGradient>'
      f'<linearGradient id="{uid}sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
      f'<clipPath id="{uid}cl"><rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="18"/></clipPath>'
      '</defs>')
    a(f'<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="18" fill="url(#{uid}bg)"/>')
    a(f'<g clip-path="url(#{uid}cl)">')
    a(f'<ellipse cx="130" cy="98" rx="120" ry="80" fill="url(#{uid}orb)"><animate attributeName="ry" values="70;90;70" dur="5s" repeatCount="indefinite"/></ellipse>')
    # twinkles
    for k, (sx, sy) in enumerate([(40, 60), (215, 48), (225, 130), (30, 140), (150, 40)]):
        a(f'<circle cx="{sx}" cy="{sy}" r="1.4" fill="#fff" opacity="0.2"><animate attributeName="opacity" values="0.1;0.9;0.1" dur="{2.4 + k * 0.7}s" begin="{k * 0.4}s" repeatCount="indefinite"/></circle>')
    # emblem: hex frame with monogram
    cx, cy, r = 130, 98, 42
    hexpts = " ".join(f"{cx + r * __import__('math').cos(__import__('math').radians(60 * k - 90)):.1f},{cy + r * __import__('math').sin(__import__('math').radians(60 * k - 90)):.1f}" for k in range(6))
    a(f'<polygon points="{hexpts}" fill="#0a0f20" stroke="url(#{uid}bd)" stroke-width="2.5"/>')
    hexpts2 = " ".join(f"{cx + (r + 12) * __import__('math').cos(__import__('math').radians(60 * k - 90)):.1f},{cy + (r + 12) * __import__('math').sin(__import__('math').radians(60 * k - 90)):.1f}" for k in range(6))
    a(f'<polygon points="{hexpts2}" fill="none" stroke="{c2}" stroke-width="1" opacity="0.5"><animate attributeName="opacity" values="0.15;0.7;0.15" dur="3s" repeatCount="indefinite"/>'
      f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/></polygon>')
    a(f'<text x="{cx}" y="{cy + 11}" font-family="{FONT}" font-size="32" font-weight="800" fill="{c1}" text-anchor="middle">{esc(initials)}'
      f'<animate attributeName="fill" values="{c1};{c2};{c1}" dur="5s" repeatCount="indefinite"/></text>')
    # corner rank
    a(f'<text x="22" y="40" font-family="{FONT}" font-size="22" font-weight="800" fill="{c1}">{esc(rank)}</text>')
    a(f'<polygon points="28,48 34,56 28,64 22,56" fill="{c2}"/>')
    a(f'<g transform="rotate(180 {W - 28} {H - 48})"><text x="{W - 28}" y="{H - 40}" font-family="{FONT}" font-size="22" font-weight="800" fill="{c1}" text-anchor="middle" opacity="0.0">{esc(rank)}</text></g>')
    # title
    ty = 178
    tl = wrap(title, 19)
    for k, line in enumerate(tl[:2]):
        a(f'<text x="{W / 2}" y="{ty + k * 21}" font-family="{FONT}" font-size="17" font-weight="700" fill="#f1f5f9" text-anchor="middle">{esc(line)}</text>')
    dy0 = ty + (len(tl[:2]) - 1) * 21 + 24
    a(f'<line x1="70" y1="{dy0 - 12}" x2="190" y2="{dy0 - 12}" stroke="url(#{uid}bd)" stroke-width="1.5" opacity="0.8"/>')
    for k, line in enumerate(wrap(desc, 28)[:4]):
        a(f'<text x="{W / 2}" y="{dy0 + 6 + k * 16}" font-family="{FONT}" font-size="12.5" fill="#a9b6cc" text-anchor="middle">{esc(line)}</text>')
    # stack chips
    chip_y = 292
    widths = [len(t) * 7 + 18 for t in tags]
    total = sum(widths) + 6 * (len(tags) - 1)
    x = (W - total) / 2
    for t, w in zip(tags, widths):
        a(f'<rect x="{x:.1f}" y="{chip_y}" width="{w}" height="22" rx="11" fill="{c1}" fill-opacity="0.14" stroke="{c1}" stroke-opacity="0.6"/>')
        a(f'<text x="{x + w / 2:.1f}" y="{chip_y + 15}" font-family="{FONT}" font-size="11.5" font-weight="600" fill="#e2e8f0" text-anchor="middle">{esc(t)}</text>')
        x += w + 6
    # footer
    a(f'<line x1="24" y1="326" x2="{W - 24}" y2="326" stroke="#2a3a66"/>')
    if not more:
        a(f'<polygon points="30,336 33,343 40,343 34.5,347.5 36.5,355 30,350.5 23.5,355 25.5,347.5 20,343 27,343" fill="#fbbf24"/>')
        a(f'<text x="46" y="352" font-family="{FONT}" font-size="13" font-weight="700" fill="#e2e8f0">{star_text}</text>')
    a(f'<text x="{W - 26}" y="352" font-family="{FONT}" font-size="12" font-weight="700" fill="{c1}" text-anchor="end">VIEW REPO  →'
      f'<animate attributeName="opacity" values="1;0.55;1" dur="2.6s" repeatCount="indefinite"/></text>')
    # shine sweep
    a(f'<g opacity="1"><rect x="-120" y="-20" width="70" height="{H + 40}" fill="url(#{uid}sh)" transform="rotate(18 0 0)">'
      f'<animate attributeName="x" values="-120;340;340" keyTimes="0;0.35;1" dur="{6 + idx % 3}s" begin="{idx * 0.6:.1f}s" repeatCount="indefinite"/></rect></g>')
    a('</g>')
    a(f'<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="18" fill="none" stroke="url(#{uid}bd)" stroke-width="3"/>')
    a('</svg>')
    return "\n".join(p)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    for i, (slug, repo, rank, title, desc, tags, c1, c2) in enumerate(CARDS):
        n = stars(repo)
        svg = card(i, slug, rank, title, desc, tags, c1, c2, f"{n} star" + ("" if n == 1 else "s"))
        with open(os.path.join(OUTDIR, f"{slug}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    svg = card(len(CARDS), "more", "+", "More projects",
               "Heart disease, loan approval, forest cover, music genres and more",
               ["ML", "Data Science"], "#22d3ee", "#a78bfa", "", more=True)
    with open(os.path.join(OUTDIR, "more.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", len(CARDS) + 1, "cards")


if __name__ == "__main__":
    main()
