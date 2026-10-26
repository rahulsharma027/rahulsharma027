"""Render SVG widgets from public GitHub data using Python's standard library.

GITHUB_TOKEN is optional locally; Actions supplies its built-in repository token.
No private repositories or contribution estimates are queried. An API failure
leaves the last successfully generated widgets in place.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
INK = "#eef4e8"
MUTED = "#a6b4a0"
LIME = "#cef38a"
COLORS = ["#cef38a", "#8ad7c2", "#d7b987", "#9ab6ea", "#c5a1d4", "#ed9d8a", "#879485"]


def api(path: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "rahulsharma027-profile-widgets", "X-GitHub-Api-Version": "2026-03-10"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"GitHub API returned HTTP {error.code} for {path}; existing widgets were retained.") from None
        except (URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"GitHub API could not be reached for {path}; existing widgets were retained.") from None


def collect(username: str) -> dict:
    account = quote(username, safe="")
    repos, page = [], 1
    while True:
        batch = api(f"/users/{account}/repos?type=owner&sort=full_name&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected repository API response.")
        repos.extend(repo for repo in batch if not repo.get("private", True))
        if len(batch) < 100:
            break
        page += 1
    owned = [repo for repo in repos if not repo.get("fork", False)]
    language_bytes = Counter()
    for repo in owned:
        languages = api(f"/repos/{account}/{quote(repo['name'], safe='')}/languages")
        if not isinstance(languages, dict) or any(not isinstance(value, int) or value < 0 for value in languages.values()):
            raise RuntimeError(f"Unexpected language API response for {repo['name']}.")
        language_bytes.update(languages)
    recent = sorted(
        (repo for repo in owned if repo["name"].casefold() != username.casefold() and not repo.get("archived", False) and repo.get("pushed_at")),
        key=lambda repo: repo["pushed_at"], reverse=True,
    )[:4]
    return {
        "username": username,
        "date": datetime.now(timezone.utc).date().isoformat(),
        "public_repos": len(repos),
        "original_repos": len(owned),
        "language_bytes": dict(language_bytes),
        "recent": [{"name": repo["name"], "language": repo.get("language"), "pushed_at": repo["pushed_at"]} for repo in recent],
    }


def text(x, y, value, size=14, color=INK, weight=None, extra=""):
    weight_attribute = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"{weight_attribute} {extra}>{escape(str(value))}</text>'


def shell(title, description, height, content):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title description">'
        f'<title id="title">{escape(title)}</title><desc id="description">{escape(description)}</desc>'
        f'<rect x="1" y="1" width="998" height="{height - 2}" rx="12" fill="#121a15" stroke="#31402d"/>'
        f'<g font-family="Consolas, Liberation Mono, monospace">{content}</g></svg>\n'
    )


def snapshot(data):
    languages = len([value for value in data["language_bytes"].values() if value > 0])
    parts = [text(32, 38, "GITHUB / PUBLIC INVENTORY", 13, LIME, extra='letter-spacing="2"')]
    for x, value, label in [(32, data["public_repos"], "PUBLIC REPOS"), (350, data["original_repos"], "NON-FORK REPOS"), (668, languages, "CODE LANGUAGES")]:
        parts.extend([text(x, 102, value, 44, INK, "700"), text(x, 132, label, 12, MUTED, extra='letter-spacing="1"')])
    parts.append(text(32, 175, f"Public repositories only  /  Updated {data['date']} UTC", 12, MUTED))
    return shell("GitHub public inventory", f"{data['public_repos']} public repositories, {data['original_repos']} non-fork repositories, {languages} code languages. Updated {data['date']} UTC.", 202, "".join(parts))


def language_widget(data):
    pairs = sorted(((name, value) for name, value in data["language_bytes"].items() if value > 0), key=lambda item: (-item[1], item[0]))
    if len(pairs) > 6:
        pairs = pairs[:6] + [("Other", sum(value for _, value in pairs[6:]))]
    total, x = sum(value for _, value in pairs), 32.0
    parts = [text(32, 38, "LANGUAGE LOADOUT / PUBLIC CODE", 13, LIME, extra='letter-spacing="2"')]
    for index, (name, value) in enumerate(pairs):
        width = 936 * value / total
        parts.append(f'<rect x="{x:.4f}" y="61" width="{width:.4f}" height="13" fill="{COLORS[index]}"/>')
        x += width
        col, row = index % 4, index // 4
        tx, ty = 32 + col * 238, 113 + row * 42
        parts.extend([f'<rect x="{tx}" y="{ty - 10}" width="8" height="8" fill="{COLORS[index]}"/>', text(tx + 15, ty, name, 13), text(tx + 15, ty + 16, f"{100 * value / total:.1f}%", 11, MUTED)])
    if not pairs:
        parts.append(text(32, 112, "No public language data available yet.", 14, MUTED))
    parts.append(text(32, 199, "Code bytes in owned public repos; forks excluded. Not a skill rating.", 12, MUTED))
    parts.append(text(32, 220, f"Updated {data['date']} UTC", 11, MUTED))
    description = ", ".join(f"{name}: {100 * value / total:.1f}%" for name, value in pairs) or "No data"
    return shell("Language loadout", description + ". Code bytes only, not proficiency or professional experience.", 245, "".join(parts))


def recent_widget(data):
    parts = [text(32, 38, "RECENT BUILDS / LAST PUBLIC PUSH", 13, LIME, extra='letter-spacing="2"')]
    for index, repo in enumerate(data["recent"]):
        y, name = 80 + index * 42, repo["name"]
        display_name = name if len(name) <= 43 else name[:40] + "..."
        parts.extend([text(32, y, f"0{index + 1}", 12, LIME), text(77, y, display_name, 15), text(680, y, repo.get("language") or "No language", 12, MUTED), text(842, y, repo["pushed_at"][:10], 12, MUTED)])
    if not data["recent"]:
        parts.append(text(32, 85, "No public project pushes available yet.", 14, MUTED))
    parts.append(text(32, 264, f"Forks, archived repos and profile repo excluded. Updated {data['date']} UTC.", 11, MUTED))
    description = "; ".join(f"{repo['name']}, last pushed {repo['pushed_at'][:10]}" for repo in data["recent"])
    return shell("Recently pushed public projects", description or "No recent project data", 291, "".join(parts))


def mobile_shell(title, description, height, content):
    return shell(title, description, height, content).replace('width="1000"', 'width="600"').replace(f'viewBox="0 0 1000 {height}"', f'viewBox="0 0 600 {height}"').replace('width="998"', 'width="598"')


def mobile_widgets(data):
    languages = [(name, value) for name, value in sorted(data['language_bytes'].items(), key=lambda item: (-item[1], item[0])) if value > 0]
    inventory = [text(28, 40, "GITHUB / PUBLIC INVENTORY", 18, LIME)]
    for y, value, label in [(105, data['public_repos'], 'Public repositories'), (175, data['original_repos'], 'Non-fork repositories'), (245, len(languages), 'Code languages')]:
        inventory.extend([text(28, y, value, 39, INK, '700'), text(125, y - 5, label, 21, MUTED)])
    inventory.append(text(28, 295, f"Updated {data['date']} UTC", 17, MUTED))
    if len(languages) > 6:
        languages = languages[:6] + [('Other', sum(value for _, value in languages[6:]))]
    total = sum(value for _, value in languages)
    language_parts = [text(28, 40, "LANGUAGE LOADOUT / PUBLIC CODE", 17, LIME)]
    x = 28.0
    for index, (name, value) in enumerate(languages):
        width = 544 * value / total
        language_parts.append(f'<rect x="{x:.4f}" y="64" width="{width:.4f}" height="15" fill="{COLORS[index]}"/>')
        x += width
        tx, ty = 28 + index % 2 * 278, 123 + index // 2 * 61
        language_parts.extend([f'<rect x="{tx}" y="{ty - 13}" width="10" height="10" fill="{COLORS[index]}"/>', text(tx + 19, ty, name, 18), text(tx + 19, ty + 23, f'{100 * value / total:.1f}%', 17, MUTED)])
    if not languages:
        language_parts.append(text(28, 123, "No public language data yet.", 19, MUTED))
    language_parts.extend([text(28, 376, 'Code bytes; owned public repos; forks excluded.', 16, MUTED), text(28, 402, 'Not a skill rating or work experience measure.', 16, MUTED), text(28, 431, f"Updated {data['date']} UTC", 16, MUTED)])
    recent = [text(28, 40, 'RECENT BUILDS / LAST PUBLIC PUSH', 17, LIME)]
    for index, repo in enumerate(data['recent']):
        y = 90 + index * 75
        name = repo['name'] if len(repo['name']) <= 37 else repo['name'][:34] + '...'
        recent.extend([text(28, y, name, 20), text(28, y + 27, f"{repo.get('language') or 'No language'}  /  {repo['pushed_at'][:10]}", 17, MUTED)])
    if not data['recent']:
        recent.append(text(28, 95, 'No public project pushes yet.', 19, MUTED))
    recent.extend([text(28, 414, 'Forks, archived and profile repos excluded.', 16, MUTED), text(28, 441, f"Updated {data['date']} UTC", 16, MUTED)])
    return {
        'github-snapshot-mobile.svg': mobile_shell('GitHub public inventory', 'Public repository counts, excluding private work.', 328, ''.join(inventory)),
        'language-loadout-mobile.svg': mobile_shell('Public code languages', 'Language share by code bytes, not proficiency.', 462, ''.join(language_parts)),
        'recent-builds-mobile.svg': mobile_shell('Recently pushed public projects', 'Recent public project pushes, excluding forks and the profile repository.', 472, ''.join(recent)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="rahulsharma027")
    parser.add_argument("--from-json", type=Path, help="Render an existing public snapshot without network access.")
    parser.add_argument("--save-json", type=Path, help="Save a public snapshot for offline verification.")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.username):
        parser.error("Invalid GitHub username.")
    try:
        data = json.loads(args.from_json.read_text(encoding="utf-8")) if args.from_json else collect(args.username)
        if data["username"].casefold() != args.username.casefold():
            raise RuntimeError("Snapshot username does not match the requested profile.")
        output = {"github-snapshot.svg": snapshot(data), "language-loadout.svg": language_widget(data), "recent-builds.svg": recent_widget(data), **mobile_widgets(data)}
        for svg in output.values():
            ET.fromstring(svg)
        ASSETS.mkdir(parents=True, exist_ok=True)
        for name, svg in output.items():
            target = ASSETS / name
            if not target.exists() or target.read_text(encoding="utf-8") != svg:
                staging = target.with_suffix(".svg.tmp")
                staging.write_text(svg, encoding="utf-8", newline="\n")
                staging.replace(target)
        if args.save_json:
            args.save_json.parent.mkdir(parents=True, exist_ok=True)
            args.save_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated 3 profile widgets in desktop and mobile layouts for {data['username']} from public data dated {data['date']}.")
    except (RuntimeError, ValueError, KeyError, TypeError, OSError) as error:
        print(f"Widget generation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
