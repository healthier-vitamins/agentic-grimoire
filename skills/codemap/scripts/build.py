# /// script
# requires-python = ">=3.11"
# ///
"""Build `<project>/.codemap/map.html` from the agent's `map.json` and freshly scanned facts.

    uv run build.py --root <project>

The map holds what only reading can give (areas, sections, jobs, entry points by name,
statechart transitions with their `file:line`). The scan supplies every count, line number,
import edge and state list. The build checks each hand-written citation against the facts
and exits 1 with one line per problem, so a map that disagrees with the code never renders.

Example: a section `{"slug": "jobs", "files": ["src/jobs/"], "entry_points":
["src/jobs/run.py::run_next"]}` renders with its file count and lines, `run_next` at
`src/jobs/run.py:12`, the sections it imports, and a copy button holding
`/codewalk jobs: <job>. Entry points: src/jobs/run.py:12. Files: src/jobs/run.py, .... Walk
only this section; stop where calls leave it.`
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import deque
from pathlib import Path

from scan import prepare_out_dir, scan

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KEY_FILES = 5

# Statechart geometry, in SVG px. A mono 12px glyph is about 7.3px wide.
CHAR_W, BOX_H, BOX_PAD, GAP_X, ROW_GAP, TOP = 7.3, 26, 12, 14, 34, 30


class MapError(Exception):
    """The map disagrees with the code. Holds one line per problem."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write <root>/.codemap/map.html.")
    parser.add_argument(
        "--root", required=True, help="the project root holding .codemap/"
    )
    root = Path(parser.parse_args(argv).root).resolve()
    out = prepare_out_dir(root)
    facts = scan(root)
    (out / "facts.json").write_text(json.dumps(facts, indent=1))
    try:
        page = resolve(json.loads((out / "map.json").read_text()), facts, root)
    except MapError as error:
        print(error, file=sys.stderr)
        return 1
    (out / "map.html").write_text(render(page))
    unmapped = page["unmapped"]
    print(
        f"{out / 'map.html'}: {len(page['sections'])} sections, {page['lines']} lines mapped"
    )
    if unmapped:
        print(f"not in any section ({len(unmapped)} files): {', '.join(unmapped)}")
    return 0


# ---- resolving the map against the facts --------------------------------------------------


def resolve(code_map: dict, facts: dict, root: Path) -> dict:
    """The map with every computed fact filled in. Raises MapError listing each problem."""
    files = facts["files"]
    problems: list[str] = []
    owner_of: dict[str, str] = {}
    sections = []
    for area in code_map["areas"]:
        for section in area["sections"]:
            slug = section["slug"]
            if not SLUG.match(slug) or any(s["slug"] == slug for s in sections):
                problems.append(f"{slug}: slug must be unique kebab-case")
            members = _members(section["files"], files, slug, problems)
            for path in members:
                if path in owner_of:
                    problems.append(f"{path}: in both {owner_of[path]} and {slug}")
                owner_of[path] = slug
            entries = [
                _entry(spec, files, slug, problems) for spec in section["entry_points"]
            ]
            sections.append({
                "area": area["name"],
                "slug": slug,
                "job": section["job"].strip().rstrip("."),
                "files": members,
                "lines": sum(files[path]["lines"] for path in members),
                "entries": [entry for entry in entries if entry],
                "charts": [_chart(c, files, root, slug, problems) for c in section.get("statecharts", [])],
                "walked": (root / ".codewalk" / slug / "page.html").exists(),
            })  # fmt: skip
    if problems:
        raise MapError("\n".join(problems))
    for section in sections:
        section["uses"], section["used_by"] = _edges(section, sections, files, owner_of)
        entry_files = [entry["path"] for entry in section["entries"]]
        by_size = sorted(section["files"], key=lambda path: -files[path]["lines"])
        section["key_files"] = list(dict.fromkeys(entry_files + by_size))[:KEY_FILES]
        section["file_lines"] = {
            path: files[path]["lines"] for path in section["files"]
        }
    return {
        "title": code_map["title"],
        "areas": [area["name"] for area in code_map["areas"]],
        "sections": sections,
        "lines": sum(section["lines"] for section in sections),
        "files_mapped": len(owner_of),
        "files_total": len(files),
        "lines_total": sum(entry["lines"] for entry in files.values()),
        "unmapped": sorted(set(files) - set(owner_of)),
    }


def _members(
    specs: list[str], files: dict, slug: str, problems: list[str]
) -> list[str]:
    """A spec ending in `/` takes every scanned file under that folder; else one file."""
    members = []
    for spec in specs:
        found = (
            [path for path in files if path.startswith(spec)]
            if spec.endswith("/")
            else [spec]
        )
        if not found or found[0] not in files:
            problems.append(f"{slug}: {spec} is not a scanned source file or folder")
            continue
        members += found
    return sorted(dict.fromkeys(members))


def _entry(spec: str, files: dict, slug: str, problems: list[str]) -> dict | None:
    """`path::Symbol` -> {path, symbol, line}, the line from the scan."""
    path, _, symbol = spec.partition("::")
    line = files.get(path, {}).get("symbols", {}).get(symbol)
    if line is None:
        problems.append(f"{slug}: entry point {spec} is not a symbol the scan found")
        return None
    return {"path": path, "symbol": symbol, "line": line}


def _chart(
    chart: dict, files: dict, root: Path, slug: str, problems: list[str]
) -> dict:
    """States come from the scanned enum or column at `states_from`; each transition's `at`
    must be a line (or one of the two after it) that spells its target state."""
    path, _, line = chart["states_from"].rpartition(":")
    found = [s for s in files.get(path, {}).get("states", []) if str(s["line"]) == line]
    if not found:
        problems.append(
            f"{slug}: {chart['states_from']} holds no state list the scan found"
        )
        return {"name": chart["name"], "states": [], "transitions": []}
    states = found[0]["values"]
    transitions = []
    for move in chart["transitions"]:
        label = f"{slug}/{chart['name']}: {move['from']} -> {move['to']}"
        if move["from"] not in [*states, "*"] or move["to"] not in states:
            problems.append(f"{label}: both ends must be in {states} (or from '*')")
            continue
        at_path, _, at_line = move["at"].rpartition(":")
        source = files.get(at_path)
        if source is None or not at_line.isdigit():
            problems.append(f"{label}: {move['at']} is not path:line in a scanned file")
            continue
        text = (root / at_path).read_text(errors="replace").splitlines()
        number = int(at_line)
        nearby = (
            " ".join(text[number - 1 : number + 2]) if 0 < number <= len(text) else ""
        )
        if not re.search(rf"\b{re.escape(move['to'])}\b", nearby):
            problems.append(f"{label}: {move['at']} does not spell '{move['to']}'")
            continue
        transitions.append({**move, "by": _enclosing(source["symbols"], number)})
    return {"name": chart["name"], "source": chart["states_from"], "states": states,
            "transitions": transitions}  # fmt: skip


def _enclosing(symbols: dict[str, int], line: int) -> str:
    """The symbol whose definition starts nearest above `line`: the function doing the move."""
    above = [(start, name) for name, start in symbols.items() if start <= line]
    return max(above)[1] if above else ""


def _edges(
    section: dict, sections: list, files: dict, owner_of: dict
) -> tuple[list, list]:
    """Sections this one imports from, and sections that import from it."""
    uses = {owner_of[target] for path in section["files"] for target in files[path]["imports"]
            if target in owner_of}  # fmt: skip
    used_by = {owner_of[path] for other in sections for path in other["files"]
               if any(owner_of.get(t) == section["slug"] for t in files[path]["imports"])}  # fmt: skip
    order = [s["slug"] for s in sections]

    def in_map_order(found: set[str]) -> list[str]:
        return sorted(found - {section["slug"]}, key=order.index)

    return in_map_order(uses), in_map_order(used_by)


# ---- the statechart: layered layout, done here so the page needs no script ----------------


def statechart_svg(chart: dict, marker: str) -> str:
    """Rows by distance from the start; each edge a straight line between ports spread along
    the box edges, so opposite moves between two states stay apart.

    Example: queued -> running -> {paused, done} gives three rows; `running -> queued` leaves
    from running's top and lands on queued's bottom, beside `queued -> running`."""
    states, moves = (
        chart["states"],
        [m for m in chart["transitions"] if m["from"] != m["to"]],
    )
    depth = _depths(states, moves)
    rows: dict[int, list[str]] = {}
    for state in states:
        rows.setdefault(depth[state], []).append(state)
    width_of = {s: round(len(s) * CHAR_W + 2 * BOX_PAD) for s in states}
    row_widths = [
        sum(width_of[s] for s in row) + GAP_X * (len(row) - 1) for row in rows.values()
    ]
    width = max(row_widths) + 16
    box = {}
    for number, row in sorted(rows.items()):
        x = (width - row_widths[sorted(rows).index(number)]) / 2
        for state in row:
            box[state] = (
                x,
                TOP + sorted(rows).index(number) * (BOX_H + ROW_GAP),
                width_of[state],
            )
            x += width_of[state] + GAP_X
    height = max(y for _, y, _ in box.values()) + BOX_H + 4
    parts = [_edge_paths(moves, box, marker)]
    starts = sorted({m["to"] for m in chart["transitions"] if m["from"] == "*"})
    if starts:
        x, _, w = box[starts[0]]
        parts.append(f'<circle class="start" cx="{x + w / 2:.1f}" cy="8" r="4"/>')
    outgoing = {m["from"] for m in moves}
    for state, (x, y, w) in box.items():
        final = " final" if state not in outgoing else ""
        parts.append(
            f'<rect class="state{final}" x="{x:.1f}" y="{y}" width="{w}" height="{BOX_H}" rx="6"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + BOX_H / 2}">{html.escape(state)}</text>'
        )
    label = f"Statechart of {chart['name']}: states " + ", ".join(states)
    return (
        f'<svg class="chart" viewBox="0 0 {width:.0f} {height}" width="{width:.0f}" '
        f'role="img" aria-label="{html.escape(label)}"><defs><marker id="{marker}" '
        'viewBox="0 0 8 8" refX="7.5" refY="4" markerWidth="7" markerHeight="7" '
        'orient="auto"><path d="M0,0 L8,4 L0,8 z"/></marker></defs>'
        + "".join(parts)
        + "</svg>"
    )


def _depths(states: list[str], moves: list[dict]) -> dict[str, int]:
    """Breadth-first distance from the start; a state nothing reaches sits on a last row."""
    starts = [m["to"] for m in moves if m["from"] == "*"] or states[:1]
    depth = {state: 0 for state in starts}
    queue = deque(starts)
    while queue:
        state = queue.popleft()
        for move in moves:
            if move["from"] == state and move["to"] not in depth:
                depth[move["to"]] = depth[state] + 1
                queue.append(move["to"])
    last = max(depth.values()) + 1
    return {state: depth.get(state, last) for state in states}


def _edge_paths(moves: list[dict], box: dict, marker: str) -> str:
    """Each distinct (from, to) once. A move down leaves a box's bottom and lands on a top;
    a move up does the reverse; a move within a row arcs over it."""
    pairs = list(dict.fromkeys((m["from"], m["to"]) for m in moves))
    ports: dict[tuple[str, str], list] = {}

    def centre(state: str) -> float:
        x, _, w = box[state]
        return x + w / 2

    for source, target in pairs:
        if source == "*":
            ports.setdefault((target, "top"), []).append(
                (centre(target), (source, target))
            )
            continue
        down = box[target][1] > box[source][1]
        up = box[target][1] < box[source][1]
        if down or up:
            ports.setdefault((source, "bottom" if down else "top"), []).append(
                (centre(target), (source, target)))  # fmt: skip
            ports.setdefault((target, "top" if down else "bottom"), []).append(
                (centre(source), (source, target)))  # fmt: skip
    spot: dict[tuple, tuple[float, float]] = {}
    for (state, side), entries in ports.items():
        x, y, w = box[state]
        entries.sort(key=lambda entry: entry[0])
        for number, (_, pair) in enumerate(entries, start=1):
            spot[(pair, state)] = (
                x + w * number / (len(entries) + 1),
                y if side == "top" else y + BOX_H,
            )
    paths = []
    for source, target in pairs:
        if source == "*":
            x1, y1 = spot[((source, target), target)][0], 12
            x2, y2 = spot[((source, target), target)]
            paths.append(
                f'<path d="M{x1:.1f},{y1} L{x2:.1f},{y2}" marker-end="url(#{marker})"/>'
            )
        elif ((source, target), source) in spot:
            x1, y1 = spot[((source, target), source)]
            x2, y2 = spot[((source, target), target)]
            paths.append(
                f'<path d="M{x1:.1f},{y1} L{x2:.1f},{y2}" marker-end="url(#{marker})"/>'
            )
        elif _adjacent(source, target, box):
            (sx, y, sw), (tx, _, tw) = box[source], box[target]
            x1, x2 = (sx + sw, tx) if sx < tx else (sx, tx + tw)
            paths.append(f'<path d="M{x1:.1f},{y + BOX_H / 2} L{x2:.1f},{y + BOX_H / 2}" '
                         f'marker-end="url(#{marker})"/>')  # fmt: skip
        else:
            x1, y1, x2 = centre(source), box[source][1], centre(target)
            mid = (x1 + x2) / 2
            paths.append(
                f'<path d="M{x1:.1f},{y1} Q{mid:.1f},{y1 - 18} {x2:.1f},{y1}" '
                f'marker-end="url(#{marker})"/>'
            )
    return "".join(paths)


def _adjacent(source: str, target: str, box: dict) -> bool:
    """Two boxes on one row with no box between them."""
    (sx, y, _), (tx, _, _) = box[source], box[target]
    low, high = sorted((sx, tx))
    return not any(by == y and low < bx < high for bx, by, _ in box.values())


# ---- the page ------------------------------------------------------------------------------


def _count(number: int, noun: str) -> str:
    return f"{number:,} {noun}{'' if number == 1 else 's'}"


def prompt_for(section: dict) -> str:
    """The exact `/codewalk` prompt a section's button copies."""
    entries = ", ".join(f"{e['path']}:{e['line']}" for e in section["entries"])
    files = ", ".join(section["files"])
    return (
        f"/codewalk {section['slug']}: {section['job']}. Entry points: {entries}. "
        f"Files: {files}. Walk only this section; stop where calls leave it."
    )


def as_text(page: dict) -> str:
    """The whole map as plain text, for pasting into a chat."""
    lines = [
        (
            f"{page['title']} code map: {len(page['sections'])} sections, "
            f"{page['files_mapped']} files, {page['lines']:,} lines "
            f"(of {page['lines_total']:,} scanned)"
        )
    ]
    for area in page["areas"]:
        lines += ["", area]
        for s in (s for s in page["sections"] if s["area"] == area):
            walked = " [walked]" if s["walked"] else ""
            lines.append(
                f"- {s['slug']} ({_count(len(s['files']), 'file')}, {s['lines']:,} lines){walked}: {s['job']}"
            )
            lines.append(
                "  Entry points: "
                + ", ".join(
                    f"{e['symbol']} {e['path']}:{e['line']}" for e in s["entries"]
                )
            )
            if s["uses"]:
                lines.append("  Uses: " + ", ".join(s["uses"]))
            for chart in s["charts"]:
                moves = "; ".join(f"{'start' if m['from'] == '*' else m['from']} -> {m['to']} ({m['at']})"
                                  for m in chart["transitions"])  # fmt: skip
                lines.append(f"  States of {chart['name']}: {moves}")
    return "\n".join(lines) + "\n"


def render(page: dict) -> str:
    esc = html.escape
    areas = []
    for area in page["areas"]:
        members = [s for s in page["sections"] if s["area"] == area]
        lines = sum(s["lines"] for s in members)
        nodes = "".join(_node(s) for s in members)
        areas.append(
            f'<li class="area"><h2>{esc(area)}<span class="size">{_count(len(members), "section")} · '
            f'{lines:,} lines</span></h2><ul class="branch">{nodes}</ul></li>'
        )
    meta = (
        f"{len(page['sections'])} sections in {len(page['areas'])} areas · "
        f"{page['files_mapped']} files · {page['lines']:,} of {page['lines_total']:,} lines mapped"
    )
    text_json = json.dumps(as_text(page)).replace("</", "<\\/")
    return (
        TEMPLATE.read_text()
        .replace("{{TITLE}}", esc(page["title"]))
        .replace("{{META}}", esc(meta))
        .replace("{{AREAS}}", "".join(areas))
        .replace("{{TEXT_JSON}}", text_json)
    )


def _node(section: dict) -> str:
    esc = html.escape
    slug = esc(section["slug"])
    walked_link = f"../.codewalk/{slug}/page.html"
    badges = ""
    if section["walked"]:
        badges += f'<a class="badge walked" href="{walked_link}">walked</a>'
    if section["charts"]:
        count = len(section["charts"])
        badges += (
            f'<span class="badge">{count} statechart{"s" if count > 1 else ""}</span>'
        )
    entries = "".join(
        f'<li><code>{esc(e["symbol"])}</code><span class="where">{esc(e["path"])}:{e["line"]}</span></li>'
        for e in section["entries"]
    )
    more = len(section["files"]) - len(section["key_files"])
    key_files = "".join(
        f'<li><span class="where">{esc(path)}</span><span class="n">{section["file_lines"][path]:,}</span></li>'
        for path in section["key_files"]
    ) + (f'<li class="more">and {more} more in the prompt</li>' if more > 0 else "")
    links = ""
    for title, slugs in (("Uses", section["uses"]), ("Used by", section["used_by"])):
        if slugs:
            chips = "".join(f'<a href="#{esc(s)}">{esc(s)}</a>' for s in slugs)
            links += f'<div class="links"><h3>{title}</h3><p>{chips}</p></div>'
    charts = ""
    for number, chart in enumerate(section["charts"]):
        moves = "".join(
            f'<li><span class="move">{esc("start" if m["from"] == "*" else m["from"])} → {esc(m["to"])}</span>'
            f'<span class="when">{esc(m.get("when", ""))}</span>'
            f'<span class="where">{esc(m["by"])} · {esc(m["at"])}</span></li>'
            for m in chart["transitions"]
        )
        charts += (
            f'<figure class="statechart"><figcaption><h3>States of {esc(chart["name"])}</h3>'
            f'<span class="where">from {esc(chart["source"])}</span></figcaption>'
            f'{statechart_svg(chart, f"arrow-{slug}-{number}")}<ul class="moves">{moves}</ul></figure>'
        )
    walked_line = (
        f'<p class="walked-line">Walked: <a href="{walked_link}">open the codewalk</a></p>'
        if section["walked"] else ""
    )  # fmt: skip
    return (
        f'<li class="node" id="{slug}"><details><summary>'
        f'<span class="head"><span class="slug">{slug}</span>'
        f'<span class="size">{_count(len(section["files"]), "file")} · {section["lines"]:,} lines</span></span>'
        f'<span class="job">{esc(section["job"])}</span>'
        f"{f'<span class=badges>{badges}</span>' if badges else ''}</summary>"
        f'<div class="body"><div><h3>Entry points</h3><ul class="refs">{entries}</ul></div>'
        f'<div><h3>Key files</h3><ul class="refs files">{key_files}</ul></div>{links}{charts}'
        f'{walked_line}<button class="copy" type="button" data-prompt="{esc(prompt_for(section))}">'
        "Copy /codewalk prompt</button></div></details></li>"
    )


if __name__ == "__main__":
    raise SystemExit(main())
