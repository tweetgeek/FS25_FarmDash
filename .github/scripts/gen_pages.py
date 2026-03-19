#!/usr/bin/env python3
"""Generate gh-pages content: index.html + version.json + copy exe."""
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# ── Env ────────────────────────────────────────────────────────────────────
VERSION      = os.environ["APP_VERSION"]
RELEASE_BODY = os.environ.get("RELEASE_BODY", "")
RELEASE_NAME = os.environ.get("RELEASE_NAME", f"v{VERSION}")
GH_REPO      = os.environ["GH_REPO"]     # "owner/repo"
GH_OWNER     = os.environ["GH_OWNER"]
REPO_NAME    = GH_REPO.split("/")[1]
PAGES_URL    = f"https://{GH_OWNER}.github.io/{REPO_NAME}"
DIST_DIR     = Path("gh-pages-dist")
DIST_DIR.mkdir(exist_ok=True)

# ── Copy exe ───────────────────────────────────────────────────────────────
exe_src = next(Path("dist").glob("FarmDash-*.exe"), None)
if exe_src:
    shutil.copy(exe_src, DIST_DIR / f"FarmDash-{VERSION}.exe")
    print(f"Copied {exe_src} → gh-pages-dist/FarmDash-{VERSION}.exe")


# ── Helpers ────────────────────────────────────────────────────────────────
def parse_changelog(body) -> list:
    if not body:
        return []
    items = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith(("- ", "* ", "• ")):
            items.append(s[2:].strip())
        elif re.match(r"^\d+\. ", s):
            items.append(re.sub(r"^\d+\. ", "", s).strip())
    return [i for i in items if i]


def ver_key(v: str):
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


def h(text: str) -> str:
    """HTML-escape."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


# ── Current release ────────────────────────────────────────────────────────
cur_changelog = parse_changelog(RELEASE_BODY)
if not cur_changelog and RELEASE_BODY.strip():
    cur_changelog = [RELEASE_BODY.strip()]

cur_download = f"{PAGES_URL}/FarmDash-{VERSION}.exe"

# ── version.json ───────────────────────────────────────────────────────────
(DIST_DIR / "version.json").write_text(
    json.dumps({"version": VERSION, "download_url": cur_download,
                "changelog": cur_changelog}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Written version.json")

# ── All releases (from gh api output) ─────────────────────────────────────
releases = []
raw_file = Path("all_releases.json")
if raw_file.exists():
    for r in json.loads(raw_file.read_text(encoding="utf-8")):
        tag  = r.get("tag_name", "")
        ver  = tag.lstrip("v")
        body = r.get("body", "")
        cl   = parse_changelog(body) or ([body.strip()] if body.strip() else [])
        releases.append({
            "version":    ver,
            "tag":        tag,
            "name":       r.get("name", tag) or tag,
            "date":       (r.get("published_at") or "")[:10],
            "changelog":  cl,
            "download":   f"{PAGES_URL}/FarmDash-{ver}.exe",
            "prerelease": r.get("prerelease", False),
        })

# Ensure current version present
if not any(r["version"] == VERSION for r in releases):
    releases.insert(0, {
        "version":   VERSION,
        "tag":       f"v{VERSION}",
        "name":      RELEASE_NAME,
        "date":      datetime.utcnow().strftime("%Y-%m-%d"),
        "changelog": cur_changelog,
        "download":  cur_download,
        "prerelease": False,
    })

releases.sort(key=lambda r: ver_key(r["version"]), reverse=True)
latest = releases[0]

# ── HTML ───────────────────────────────────────────────────────────────────
def changelog_html(items: list, show_empty=True) -> str:
    if not items:
        return '<p class="no-changes">Brak informacji o zmianach.</p>' if show_empty else ""
    return "<ul>" + "".join(f"<li>{h(i)}</li>" for i in items) + "</ul>"


def release_card(r: dict, is_latest: bool) -> str:
    badge  = '<span class="badge-latest">najnowsza</span>' if is_latest else ""
    pre    = '<span class="badge-pre">pre-release</span>' if r["prerelease"] else ""
    date   = f'<span class="rel-date">{h(r["date"])}</span>' if r["date"] else ""
    dl_btn = (
        f'<a href="{h(r["download"])}" class="dl-btn" download>'
        f'⬇ Pobierz FarmDash v{h(r["version"])}</a>'
    ) if is_latest else (
        f'<a href="{h(r["download"])}" class="dl-btn dl-btn-sm" download>'
        f'⬇ .exe</a>'
    )
    cl = changelog_html(r["changelog"], show_empty=is_latest)
    details = (
        f'<details><summary>Co nowego w {h(r["name"])}?</summary>{cl}</details>'
        if not is_latest else
        f'<div class="changelog-block"><h3>Co nowego:</h3>{cl}</div>'
    )
    card_class = "release-card latest-card" if is_latest else "release-card"
    return f"""
    <div class="{card_class}">
      <div class="rel-header">
        <span class="rel-ver">v{h(r["version"])}</span>
        {badge}{pre}{date}
        {dl_btn}
      </div>
      {details}
    </div>"""


cards_html = "".join(
    release_card(r, i == 0) for i, r in enumerate(releases)
)

total = len(releases)
history_label = f"{total} wydani{'e' if total==1 else 'a' if 2<=total<=4 else 'ń'}"

html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FarmDash — FS25 Live Dashboard</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:      #0d1117;
      --surface: #161b22;
      --border:  #30363d;
      --text:    #e6edf3;
      --dim:     #8b949e;
      --accent:  #3fb950;
      --accent2: #58a6ff;
      --latest-glow: rgba(63,185,80,.12);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 15px; line-height: 1.6;
    }}
    body {{ background: var(--bg); color: var(--text); min-height: 100vh; }}

    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 28px 20px;
      text-align: center;
    }}
    header h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 6px; }}
    header p  {{ color: var(--dim); font-size: .95rem; }}

    .container {{ max-width: 760px; margin: 0 auto; padding: 32px 20px; }}

    .section-title {{
      font-size: .75rem; font-weight: 600; letter-spacing: .08em;
      text-transform: uppercase; color: var(--dim);
      margin: 32px 0 14px;
      padding-bottom: 8px; border-bottom: 1px solid var(--border);
    }}

    /* ── Release cards ── */
    .release-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      margin-bottom: 12px;
    }}
    .latest-card {{
      border-color: var(--accent);
      background: linear-gradient(135deg, var(--surface) 0%, var(--latest-glow) 100%);
      margin-bottom: 24px;
    }}
    .rel-header {{
      display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
      margin-bottom: 12px;
    }}
    .rel-ver {{
      font-size: 1.15rem; font-weight: 700; font-family: monospace;
      color: var(--accent);
    }}
    .latest-card .rel-ver {{ font-size: 1.5rem; }}
    .rel-date  {{ font-size: .8rem; color: var(--dim); margin-left: auto; }}

    .badge-latest, .badge-pre {{
      font-size: .7rem; font-weight: 600; padding: 2px 8px;
      border-radius: 20px; letter-spacing: .04em;
    }}
    .badge-latest {{ background: var(--accent); color: #000; }}
    .badge-pre    {{ background: #6e40c9; color: #fff; }}

    .dl-btn {{
      display: inline-block; padding: 8px 20px; border-radius: 6px;
      background: var(--accent); color: #000; font-weight: 600; font-size: .9rem;
      text-decoration: none; white-space: nowrap;
      transition: opacity .15s;
    }}
    .dl-btn:hover {{ opacity: .85; }}
    .dl-btn-sm {{
      padding: 4px 12px; font-size: .8rem; margin-left: auto;
      background: var(--surface); color: var(--accent2);
      border: 1px solid var(--border);
    }}
    .dl-btn-sm:hover {{ border-color: var(--accent2); }}

    .changelog-block h3 {{
      font-size: .85rem; font-weight: 600; color: var(--dim);
      margin-bottom: 8px; text-transform: uppercase; letter-spacing: .05em;
    }}
    .changelog-block ul, details ul {{
      padding-left: 18px; display: flex; flex-direction: column; gap: 4px;
    }}
    .changelog-block li, details li {{ color: var(--text); font-size: .9rem; }}
    .no-changes {{ color: var(--dim); font-size: .85rem; }}

    details {{ cursor: pointer; }}
    details summary {{
      font-size: .85rem; color: var(--dim); list-style: none;
      display: flex; align-items: center; gap: 6px;
    }}
    details summary::before {{ content: "▶"; font-size: .65rem; }}
    details[open] summary::before {{ content: "▼"; }}
    details[open] ul {{ margin-top: 10px; }}

    .platform {{ font-size: .8rem; color: var(--dim); margin-top: 4px; }}

    footer {{
      text-align: center; padding: 32px 20px;
      color: var(--dim); font-size: .8rem;
      border-top: 1px solid var(--border);
    }}
    footer a {{ color: var(--accent2); text-decoration: none; }}
    footer a:hover {{ text-decoration: underline; }}

    @media (max-width: 500px) {{
      .rel-header {{ flex-direction: column; align-items: flex-start; }}
      .rel-date {{ margin-left: 0; }}
      .dl-btn-sm {{ margin-left: 0; }}
    }}
  </style>
</head>
<body>

<header>
  <div>
    <h1>🚜 FarmDash</h1>
    <p>Farming Simulator 25 &mdash; Panel monitorowania w czasie rzeczywistym</p>
  </div>
</header>

<div class="container">

  <p class="section-title">Najnowsza wersja</p>

  {release_card(latest, True)}

  <p class="platform" style="margin-top:-16px; margin-bottom:24px; font-size:.8rem; color:var(--dim);">
    Windows 64-bit &nbsp;·&nbsp; wymaga systemu Windows 10/11
  </p>

  <p class="section-title">{history_label}</p>

  {"".join(release_card(r, False) for r in releases[1:]) if len(releases) > 1 else
   '<p style="color:var(--dim); font-size:.9rem;">To pierwsze wydanie.</p>'}

</div>

<footer>
  Wygenerowano automatycznie przez GitHub Actions &nbsp;·&nbsp;
  <a href="https://github.com/{h(GH_REPO)}/releases" target="_blank">Wszystkie wydania na GitHub →</a>
</footer>

</body>
</html>
"""

(DIST_DIR / "index.html").write_text(html, encoding="utf-8")
print("Written index.html")
print(f"Done. Pages URL: {PAGES_URL}")
