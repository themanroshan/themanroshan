#!/usr/bin/env python3
"""Builds assets/stats.svg and assets/top-langs.svg from the GitHub API.
No third-party services: runs inside your own GitHub Action."""
import json, os, urllib.request
from html import escape

USER = os.environ.get("USERNAME", "themanroshan")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def all_repos():
    repos, page = [], 1
    while True:
        chunk = get(f"{API}/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += chunk
        if len(chunk) < 100:
            return repos
        page += 1

COLORS = {"Python": "#3572A5", "Jupyter Notebook": "#DA5B0B", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
          "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219", "SQL": "#e38c00", "Shell": "#89e051"}
FALLBACK = ["#38bdf8", "#a78bfa", "#34d399", "#fbbf24", "#f87171", "#94a3b8"]

STYLE = """<style>
.h{font:700 17px 'Segoe UI',Arial,sans-serif;fill:#7dd3fc}
.l{font:400 14px 'Segoe UI',Arial,sans-serif;fill:#cbd5e1}
.v{font:700 14px 'Segoe UI',Arial,sans-serif;fill:#f8fafc}
.fade{animation:f 1s ease-out both}@keyframes f{from{opacity:0}to{opacity:1}}
</style>"""

def stats_svg(u, repos):
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    forks = sum(r["forks_count"] for r in own)
    rows = [("Public repositories", u["public_repos"]), ("Total stars earned", stars),
            ("Total forks", forks), ("Followers", u["followers"])]
    body = "".join(f'<text x="24" y="{76+i*28}" class="l">{escape(k)}</text><text x="396" y="{76+i*28}" text-anchor="end" class="v">{v}</text>'
                   for i, (k, v) in enumerate(rows))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="190" viewBox="0 0 420 190" role="img" aria-label="GitHub stats">
{STYLE}<rect width="420" height="190" rx="14" fill="#1a1b27" stroke="#2f334d"/>
<g class="fade"><text x="24" y="38" class="h">{escape(USER)}'s GitHub Stats</text>{body}</g></svg>'''

def langs_svg(repos):
    totals = {}
    for r in repos:
        if r["fork"]:
            continue
        try:
            for lang, b in get(r["languages_url"]).items():
                totals[lang] = totals.get(lang, 0) + b
        except Exception:
            pass
    top = sorted(totals.items(), key=lambda x: -x[1])[:6]
    total = sum(b for _, b in top) or 1
    body, y = "", 72
    for i, (lang, b) in enumerate(top):
        pct = b / total * 100
        col = COLORS.get(lang, FALLBACK[i % len(FALLBACK)])
        body += (f'<text x="24" y="{y}" class="l">{escape(lang)}</text><text x="396" y="{y}" text-anchor="end" class="v">{pct:.1f}%</text>'
                 f'<rect x="24" y="{y+6}" width="372" height="7" rx="3.5" fill="#2f334d"/>'
                 f'<rect x="24" y="{y+6}" width="{max(372*pct/100,4):.1f}" height="7" rx="3.5" fill="{col}"/>')
        y += 30
    if not top:
        body = '<text x="24" y="80" class="l">No language data yet</text>'
    h = max(190, y + 14)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{h}" viewBox="0 0 420 {h}" role="img" aria-label="Top languages">
{STYLE}<rect width="420" height="{h}" rx="14" fill="#1a1b27" stroke="#2f334d"/>
<g class="fade"><text x="24" y="38" class="h">Top Languages</text>{body}</g></svg>'''

if __name__ == "__main__":
    user, repos = get(f"{API}/users/{USER}"), all_repos()
    os.makedirs("assets", exist_ok=True)
    open("assets/stats.svg", "w", encoding="utf-8").write(stats_svg(user, repos))
    open("assets/top-langs.svg", "w", encoding="utf-8").write(langs_svg(repos))
    print("Generated assets/stats.svg and assets/top-langs.svg")
