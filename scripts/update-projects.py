"""Refresh public-repository section of both profile README files."""
import json
import os
import re
import urllib.request
from html import escape
from pathlib import Path

USERNAME = "A-L-Z"
TOKEN = os.environ["GH_TOKEN"]
repos = []
page = 1
while True:
    request = urllib.request.Request(
        f"https://api.github.com/users/{USERNAME}/repos?type=owner&per_page=100&page={page}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ALZ-Profile",
            "Authorization": f"Bearer {TOKEN}",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        batch = json.load(response)
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1

repos = [
    r for r in repos
    if not r["private"] and not r["fork"] and not r["archived"]
    and r["name"].casefold() != USERNAME.casefold()
    and "profile-hide" not in r.get("topics", [])
]
repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
for filename, spanish in (("README.md", False), ("README.es.md", True)):
    rows = []
    for r in repos[:8]:
        title = escape(r["name"]).replace("|", "&#124;")
        desc = escape(" ".join((r.get("description") or "").split())).replace("|", "&#124;") or "—"
        language = escape(r.get("language") or "—").replace("|", "&#124;")
        rows.append(f"| [{title}]({r['html_url']}) | {desc} | {language} |")
    link = ("[Explorar todos los repositorios](https://github.com/A-L-Z?tab=repositories)"
            if spanish else "[Explore all repositories](https://github.com/A-L-Z?tab=repositories)")
    if rows:
        header = ("| Proyecto | Descripción original | Lenguaje |"
                  if spanish else "| Project | Original description | Language |")
        listing = header + "\n| --- | --- | --- |\n" + "\n".join(rows)
    else:
        listing = ("Próximamente nuevos proyectos públicos." if spanish
                   else "New public projects coming soon.")
    path = Path(filename)
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->",
        lambda _: "<!-- PROJECTS:START -->\n" + listing + "\n\n" + link
                  + "\n<!-- PROJECTS:END -->",
        content,
        flags=re.S,
    )
    if count != 1:
        raise ValueError(f"Invalid project markers in {filename}")
    path.write_text(updated, encoding="utf-8")
