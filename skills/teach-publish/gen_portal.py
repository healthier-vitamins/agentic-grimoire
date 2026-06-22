#!/usr/bin/env python3
"""Generate index pages for the teach-publish staging site.

Two modes, both called by publish.sh:

    gen_portal.py portal <site_dir>    -> <site_dir>/index.html listing every course
    gen_portal.py course <course_dir>  -> <course_dir>/index.html, a TOC of its lessons

No third-party deps — stdlib only, so it runs anywhere Python 3 does.
Personal data never touches this file; it only reads folder names and <title> tags.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)

# A small self-contained stylesheet so portal/course indexes look like the
# lessons (Tufte-ish palette) without depending on any one course's assets.
STYLE = """
  :root { --ink:#1a1a1a; --paper:#fffff8; --muted:#6b6b63; --rule:#d8d8cf; --accent:#8a3324; }
  * { box-sizing:border-box; }
  body { margin:0 auto; max-width:42rem; padding:4rem 2rem 8rem; background:var(--paper);
         color:var(--ink); line-height:1.5; -webkit-font-smoothing:antialiased;
         font-family:Palatino,"Palatino Linotype","Book Antiqua",Georgia,serif; }
  .eyebrow { font-variant:small-caps; letter-spacing:.08em; color:var(--muted);
             font-size:.85rem; margin:0 0 .25rem; }
  h1 { font-weight:400; font-size:2.1rem; line-height:1.1; margin:0 0 .5rem; }
  .subtitle { color:var(--muted); font-style:italic; margin:0 0 2.5rem; }
  ul { list-style:none; padding:0; }
  li { margin:0; border-bottom:1px solid var(--rule); }
  a.row { display:flex; justify-content:space-between; gap:1rem; align-items:baseline;
          padding:.8rem .2rem; text-decoration:none; color:var(--ink); }
  a.row:hover { background:#fdfbf0; }
  a.row .name { color:var(--accent); }
  a.row .meta { color:var(--muted); font-size:.85rem; font-style:italic; }
  .empty { color:var(--muted); font-style:italic; }
  footer { margin-top:3rem; padding-top:1rem; border-top:1px solid var(--rule);
           color:var(--muted); font-size:.85rem; }
"""


def read_title(path: Path, fallback: str) -> str:
    """Pull the <title> text from an HTML file, else use the fallback."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return fallback
    m = TITLE_RE.search(text)
    return " ".join(m.group(1).split()) if m else fallback


def page(title: str, eyebrow: str, subtitle: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<p class="eyebrow">{html.escape(eyebrow)}</p>
<h1>{html.escape(title)}</h1>
<p class="subtitle">{html.escape(subtitle)}</p>
{body}
<footer>Private · Cloudflare Pages + Access · built by teach-publish</footer>
</body>
</html>
"""


def row(href: str, name: str, meta: str) -> str:
    return (
        f'<li><a class="row" href="{html.escape(href)}">'
        f'<span class="name">{html.escape(name)}</span>'
        f'<span class="meta">{html.escape(meta)}</span></a></li>'
    )


def build_portal(site_dir: Path) -> None:
    """Top-level index: one row per course subfolder."""
    courses = sorted(
        p for p in site_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )
    rows = []
    for c in courses:
        index = c / "index.html"
        title = read_title(index, c.name) if index.exists() else c.name
        lessons = list((c / "lessons").glob("*.html")) if (c / "lessons").is_dir() else []
        meta = f"{len(lessons)} lesson{'s' if len(lessons) != 1 else ''}" if lessons else "—"
        rows.append(row(f"{c.name}/", title, meta))

    body = (
        f"<ul>{''.join(rows)}</ul>"
        if rows
        else '<p class="empty">No courses published yet.</p>'
    )
    out = page(
        title="Your Courses",
        eyebrow="teach · private library",
        subtitle="Everything you're learning, in one private place.",
        body=body,
    )
    (site_dir / "index.html").write_text(out, encoding="utf-8")


def build_course(course_dir: Path) -> None:
    """Fallback per-course TOC when the course shipped no index.html."""
    lessons_dir = course_dir / "lessons"
    lessons = sorted(lessons_dir.glob("*.html")) if lessons_dir.is_dir() else []
    rows = [
        row(f"lessons/{p.name}", read_title(p, p.stem), p.stem.split("-")[0])
        for p in lessons
    ]

    ref_dir = course_dir / "reference"
    refs = sorted(ref_dir.glob("*.html")) if ref_dir.is_dir() else []
    ref_rows = [row(f"reference/{p.name}", read_title(p, p.stem), "reference") for p in refs]

    body_parts = []
    if rows:
        body_parts.append(f"<h2 style='font-weight:400'>Lessons</h2><ul>{''.join(rows)}</ul>")
    if ref_rows:
        body_parts.append(f"<h2 style='font-weight:400'>Reference</h2><ul>{''.join(ref_rows)}</ul>")
    body = "".join(body_parts) or '<p class="empty">No lessons yet.</p>'

    out = page(
        title=course_dir.name,
        eyebrow="course",
        subtitle="Lessons in this course.",
        body=body,
    )
    (course_dir / "index.html").write_text(out, encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in {"portal", "course"}:
        print("usage: gen_portal.py {portal|course} <dir>", file=sys.stderr)
        return 2
    mode, target = argv[1], Path(argv[2])
    if not target.is_dir():
        print(f"gen_portal.py: not a directory: {target}", file=sys.stderr)
        return 1
    (build_portal if mode == "portal" else build_course)(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
