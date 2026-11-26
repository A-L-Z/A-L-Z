"""Refresh the automated parts of both profile READMEs.

* Public repositories: queried from the official GitHub REST API and rendered as
  cards between the <!-- PROJECTS:START --> / <!-- PROJECTS:END --> markers.
  Private, archived and forked repositories, the profile repository itself and
  repositories tagged with the `profile-hide` topic are excluded. Original
  descriptions are kept verbatim.
* Development activity: the real contribution calendar of the last year from the
  GitHub GraphQL API, rendered to assets/statistics/.

Only files inside those markers, assets/cards/repos/ and assets/statistics/ are
touched; the static professional sections are never modified.

Usage:
    GH_TOKEN=... python3 scripts/update-projects.py
    python3 scripts/update-projects.py --fixture tests/fixture.json --root /tmp/copy
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design  # noqa: E402
from design import THEMES, WIDTH, esc, frame, icon, pill, svg, text, text_width, tile, wrap  # noqa: E402

USERNAME = "A-L-Z"
MAX_REPOS = 6
HIDE_TOPIC = "profile-hide"
API = "https://api.github.com"

LABELS = {
    "en": {
        "heading": "PUBLIC REPOSITORIES",
        "public": "Public",
        "no_description": "No description provided.",
        "contributions": ("contribution", "contributions"),
        "period": "in the last year",
        "activity": "Development activity",
        "syncing": "Contribution data syncs automatically from GitHub.",
        "motto": "Consistency. Learning. Building.",
        "less": "Less",
        "more": "More",
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    },
    "es": {
        "heading": "REPOSITORIOS PÚBLICOS",
        "public": "Público",
        "no_description": "Sin descripción.",
        "contributions": ("contribución", "contribuciones"),
        "period": "en el último año",
        "activity": "Actividad de desarrollo",
        "syncing": "Los datos de contribuciones se sincronizan automáticamente desde GitHub.",
        "motto": "Constancia. Aprendizaje. Construcción.",
        "less": "Menos",
        "more": "Más",
        "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    },
}
READMES = {"en": "README.md", "es": "README.es.md"}
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
LANGUAGE_COLORS = {
    "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Python": "#3572A5", "HTML": "#E34C26",
    "CSS": "#663399", "Shell": "#89E051", "Go": "#00ADD8", "Rust": "#DEA584", "Java": "#B07219",
    "PHP": "#4F5D95", "Vue": "#41B883", "Svelte": "#FF3E00", "C": "#555555", "C++": "#F34B7D",
    "C#": "#178600", "Dart": "#00B4AB", "Kotlin": "#A97BFF", "Swift": "#F05138", "Lua": "#000080",
}


# ---------------------------------------------------------------- GitHub API
def request(url, token=None, payload=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "A-L-Z-profile",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def fetch_repos(token):
    repos, page = [], 1
    while True:
        batch = request(f"{API}/users/{USERNAME}/repos?type=owner&sort=pushed&per_page=100&page={page}", token)
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def fetch_calendar(token):
    query = """query($login: String!) { user(login: $login) { contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays {
        date contributionCount contributionLevel } } } } } }"""
    result = request(f"{API}/graphql", token, {"query": query, "variables": {"login": USERNAME}})
    if result.get("errors"):
        raise RuntimeError(result["errors"])
    return result["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def select_repos(repos):
    chosen = [
        r for r in repos
        if not r.get("private") and not r.get("fork") and not r.get("archived")
        and r["name"].casefold() != USERNAME.casefold()
        and HIDE_TOPIC not in (r.get("topics") or [])
    ]
    chosen.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    return chosen[:MAX_REPOS]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-") or "repo"


# ---------------------------------------------------------------- repository card
def repo_card(repo, lang, theme):
    t, l = THEMES[theme], LABELS[lang]
    w, pad = WIDTH, 28
    description = " ".join((repo.get("description") or "").split())
    lines = wrap(description or l["no_description"], 15, 400, w - pad * 2)
    desc_color = t["text"] if description else t["muted"]
    first = pad + 40 + 32
    has_meta = bool(repo.get("language") or repo.get("stargazers_count"))
    footer = first + (len(lines) - 1) * 22 + 34
    h = (footer if has_meta else first + (len(lines) - 1) * 22) + pad - 2
    body = [frame(0, 0, w, h, t, "card", 12), tile(pad, pad, 40, t, "folder-git", 20)]
    name = repo["name"]
    body.append(text(pad + 56, pad + 26, name, 18, t["text"], 600, spacing=-0.2))
    badge, _ = pill(0, 0, l["public"], t, 12, 500, None, 24, pad=10)
    bx = pad + 56 + text_width(name, 18, 600) + 12
    body.append(f'<g transform="translate({bx:g} {pad + 8})">{badge}</g>')
    body.append(icon("arrow-up-right", w - pad - 18, pad + 11, 18, t["icon"], 2))
    for i, line in enumerate(lines):
        body.append(text(pad, first + i * 22, line, 15, desc_color, 400))
    x = pad
    language = repo.get("language")
    if language:
        body.append(f'<circle cx="{x + 6}" cy="{footer - 4.5}" r="5.5" fill="{LANGUAGE_COLORS.get(language, t["icon"])}"/>')
        body.append(text(x + 18, footer, language, 13, t["muted"], 500))
        x += 18 + text_width(language, 13, 500) + 20
    stars = repo.get("stargazers_count") or 0
    if stars:
        body.append(icon("star", x, footer - 12, 15, t["muted"], 2))
        body.append(text(x + 21, footer, f"{stars:,}", 13, t["muted"], 500))
    return svg(w, h, "".join(body), f"{name} — {l['public']}", description or l["no_description"])


def projects_block(repos, lang):
    if not repos:
        return ""
    l = LABELS[lang]
    parts = [f"###### {l['heading']}", ""]
    for repo in repos:
        slug = slugify(repo["name"])
        alt = esc(f"{repo['name']}: {' '.join((repo.get('description') or l['no_description']).split())}")
        parts.append(
            f'<a href="{esc(repo["html_url"])}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/cards/repos/{slug}-{lang}-dark.svg">'
            f'<img src="assets/cards/repos/{slug}-{lang}-light.svg" alt="{alt}" width="100%">'
            f"</picture></a>"
        )
        parts.append("")
    return "\n".join(parts).rstrip()


def update_projects(root, repos):
    pattern = re.compile(r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->", re.S)
    readmes = {}
    for lang, filename in READMES.items():  # validate before touching anything
        content = (root / filename).read_text(encoding="utf-8")
        if len(pattern.findall(content)) != 1:
            raise ValueError(f"Expected exactly one PROJECTS marker pair in {filename}")
        readmes[lang] = content
    repo_dir = root / "assets" / "cards" / "repos"
    repo_dir.mkdir(parents=True, exist_ok=True)
    expected = set()
    for repo in repos:
        slug = slugify(repo["name"])
        for lang in LABELS:
            for theme in THEMES:
                path = repo_dir / f"{slug}-{lang}-{theme}.svg"
                expected.add(path.name)
                write_if_changed(path, repo_card(repo, lang, theme))
    for stale in repo_dir.glob("*.svg"):
        if stale.name not in expected:
            stale.unlink()
            print(f"removed {stale.name}")
    for lang, content in readmes.items():
        block = projects_block(repos, lang)
        inner = f"\n{block}\n" if block else "\n"
        updated = pattern.sub(lambda _: f"<!-- PROJECTS:START -->{inner}<!-- PROJECTS:END -->", content)
        write_if_changed(root / READMES[lang], updated)


# ---------------------------------------------------------------- activity card
def activity_card(calendar, lang, theme):
    t, l = THEMES[theme], LABELS[lang]
    w, pad = WIDTH, 32
    body = []
    if calendar is None:
        h = 168
        body.append(frame(0, 0, w, h, t, "card", 14))
        body.append(tile(pad, pad, 44, t, "activity", 22))
        body.append(text(pad + 62, pad + 20, l["activity"], 18, t["text"], 600))
        body.append(text(pad + 62, pad + 42, l["syncing"], 14, t["muted"], 400))
        body.append(f'<line x1="{pad}" y1="{h - 56.5}" x2="{w - pad}" y2="{h - 56.5}" stroke="{t["border"]}"/>')
        body.append(text(pad, h - 26, l["motto"], 14, t["text"], 500))
        return svg(w, h, "".join(body), l["activity"], l["syncing"])

    total = calendar["totalContributions"]
    weeks = calendar["weeks"][-53:]
    noun = l["contributions"][0 if total == 1 else 1]
    step, cell = 15, 11.5
    grid_w = len(weeks) * step - (step - cell)
    x0 = (w - grid_w) / 2
    grid_y = 122
    h = 304
    body.append(frame(0, 0, w, h, t, "card", 14))
    body.append(tile(pad, pad, 44, t, "activity", 22))
    number = f"{total:,}"
    body.append(text(pad + 62, pad + 31, number, 26, t["text"], 700, spacing=-0.5))
    nx = pad + 62 + text_width(number, 26, 700, -0.5) + 10
    body.append(text(nx, pad + 30, f"{noun} {l['period']}", 15, t["muted"], 400))
    last_label_x = -100
    previous_month = None
    for i, week in enumerate(weeks):
        days = week["contributionDays"]
        month = int(days[0]["date"][5:7])
        x = x0 + i * step
        if month != previous_month and i < len(weeks) - 2 and x - last_label_x > 34:
            body.append(text(x, grid_y - 10, l["months"][month - 1], 11, t["muted"], 500))
            last_label_x = x
        previous_month = month
        for day in days:
            weekday = (dt.date.fromisoformat(day["date"]).weekday() + 1) % 7  # Sunday = 0
            level = LEVELS.get(day.get("contributionLevel"), 0)
            body.append(f'<rect x="{x:g}" y="{grid_y + weekday * step:g}" width="{cell}" height="{cell}" rx="2.5" fill="{t["heat"][level]}"/>')
    divider = grid_y + 6 * step + cell + 26
    body.append(f'<line x1="{pad}" y1="{divider + .5}" x2="{w - pad}" y2="{divider + .5}" stroke="{t["border"]}"/>')
    body.append(text(pad, h - 27, l["motto"], 14, t["text"], 500))
    lx = w - pad - text_width(l["more"], 11, 500)
    body.append(text(lx, h - 28, l["more"], 11, t["muted"], 500))
    lx -= 6 + 5 * 15 - 3.5
    for level in range(5):
        body.append(f'<rect x="{lx + level * 15:g}" y="{h - 38:g}" width="{cell}" height="{cell}" rx="2.5" fill="{t["heat"][level]}"/>')
    body.append(text(lx - 6, h - 28, l["less"], 11, t["muted"], 500, anchor="end"))
    summary = f"{number} {noun} {l['period']}. {l['motto']}"
    return svg(w, h, "".join(body), l["activity"], summary)


def update_activity(root, calendar):
    out = root / "assets" / "statistics"
    out.mkdir(parents=True, exist_ok=True)
    for lang in LABELS:
        for theme in THEMES:
            write_if_changed(out / f"activity-{lang}-{theme}.svg", activity_card(calendar, lang, theme))


# ---------------------------------------------------------------- helpers
def write_if_changed(path, content):
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        print(f"updated {path.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=design.ROOT, help="profile repository root")
    parser.add_argument("--fixture", type=Path, help="JSON file with 'repos' and 'calendar' test data")
    args = parser.parse_args()
    root = args.root.resolve()
    design.ASSETS = root / "assets"
    design._BRAND_CACHE.clear()

    if args.fixture:
        data = json.loads(args.fixture.read_text(encoding="utf-8"))
        repos, calendar = data.get("repos", []), data.get("calendar")
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        repos = fetch_repos(token)  # fails loudly: never wipe the section on API errors
        calendar = None
        if token:
            try:
                calendar = fetch_calendar(token)
            except (urllib.error.URLError, RuntimeError, KeyError, TypeError) as error:
                print(f"warning: contribution calendar unavailable ({error})", file=sys.stderr)
        else:
            print("warning: no token, contribution calendar skipped", file=sys.stderr)

    update_projects(root, select_repos(repos))
    stats = root / "assets" / "statistics" / "activity-en-light.svg"
    if calendar is not None or not stats.exists():
        update_activity(root, calendar)  # keep the last real data if the API fails


if __name__ == "__main__":
    main()
