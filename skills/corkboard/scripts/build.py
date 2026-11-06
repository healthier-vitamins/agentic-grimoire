"""Build a corkboard from a plan folder.

    uv run --with pillow python -I build.py <plan-dir> [--artifact-url URL]

<plan-dir> holds plan.json and, when the plan has evidence, media/media.json plus the files it
lists. The build refuses to run while plan.json breaks a rule in `check_plan` (an unknown group,
a picture with no source, a dangling link), printing every break at once.

Writes into <plan-dir>:
    board.html     a full page for opening locally
    artifact.html  the same board in artifact form (no doctype), for publishing
Videos stay as files beside the pages (media/<file>); photos and screenshots are inlined.
"""

import argparse
import base64
import io
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

__all__ = ["build", "check_plan", "chosen_boards", "rank_boards"]

ASSETS = Path(__file__).resolve().parent.parent / "assets"
JS = [
    "core",
    "charts",
    "engine",
    "page",
    "overview",
    "timeline",
    "kanban",
    "decisions",
    "moodboard",
    "flow",
    "app",
]
STATES = {"late", "now", "waiting", "later", "idea", "done"}
KINDS = {"photo", "screenshot", "commons", "video"}
CHARTS = {"status", "bars", "stack", "votes", "swatches", "stat", "timeline", "days"}
MIN_PANEL_W = 200
BLOCKS = {
    "tiles",
    "callout",
    "iconlist",
    "chipset",
    "people",
    "checklist",
    "gallery",
    "chart",
    "window",
}
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600'
    '&family=Public+Sans:wght@400;500;600;700&family=Young+Serif&display=swap">'
)
BAR = (
    '<header class="bar"><b class="brand"></b>'
    '<nav class="seg" aria-label="Board"></nav></header>\n'
    '<main class="stage" id="stage"></main>\n'
)


@dataclass(frozen=True)
class Profile:
    """The counts a board's fit is judged on."""

    items: int
    groups: int
    dated: int
    milestones: int
    spans: int
    dated_deps: int
    decisions: int
    quotes: int
    pictures: int
    largest_state: int
    phased: bool

    @classmethod
    def of(cls, plan: dict) -> "Profile":
        items = plan["items"]
        dated = {i["id"] for i in items if i.get("due") or i.get("start")}
        states = [i["state"] for i in items]
        return cls(
            items=len(items),
            groups=len({i["group"] for i in items}),
            dated=len(dated),
            milestones=sum(1 for i in items if i.get("milestone")),
            spans=sum(1 for i in items if i.get("start") and i.get("end")),
            dated_deps=sum(
                1
                for i in items
                if i["id"] in dated
                for d in i.get("dependsOn", [])
                if d in dated
            ),
            decisions=sum(1 for i in items if i.get("decision")),
            quotes=sum(len(i.get("quotes", [])) for i in items),
            pictures=sum(1 for i in items if i.get("cover")),
            largest_state=max((states.count(s) for s in set(states)), default=0),
            phased="columns" in plan,
        )

    def share(self, n: int) -> float:
        """n as a fraction of all items: how much of the plan a board can place."""
        return n / self.items if self.items else 0.0


@dataclass(frozen=True)
class Board:
    """A board format: when the data earns it, how strongly (0 to 10), and the reason to print."""

    fits: Callable[[Profile], bool]
    score: Callable[[Profile], float]
    why: Callable[[Profile], str]


# The catalog in references/boards.md, as rules. A board is offered only when the plan holds the
# data it draws, and scores by the share of items it can place: a timeline over three dated items
# out of thirty would leave the other twenty-seven in its "No date" gutter.
BOARDS: dict[str, Board] = {
    "overview": Board(
        fits=lambda p: p.items >= 10 or p.groups >= 4,
        score=lambda p: 10,
        why=lambda p: f"{p.items} items in {p.groups} groups to see at once",
    ),
    "timeline": Board(
        fits=lambda p: p.dated >= 4,
        score=lambda p: 10 * p.share(p.dated) + min(p.milestones, 5),
        why=lambda p: f"{p.dated}/{p.items} items dated, {p.milestones} milestones",
    ),
    "decisions": Board(
        fits=lambda p: p.decisions >= 2,
        score=lambda p: (
            min(20 * p.share(p.decisions), 6) + min(p.quotes / p.decisions, 4)
        ),
        why=lambda p: f"{p.decisions} decisions, {p.quotes} quotes of back-and-forth",
    ),
    "kanban": Board(
        fits=lambda p: p.items >= 8 and p.largest_state < p.items,
        score=lambda p: 10 * (1 - p.share(p.largest_state)),
        why=lambda p: (
            f"items spread over states; the largest holds {p.largest_state}/{p.items}"
        ),
    ),
    # Timeline supersedes Flow on calendar dates; Flow stays for plans told in phases, not dates.
    "flow": Board(
        fits=lambda p: p.phased,
        score=lambda p: 8 + min(p.dated_deps, 2),
        why=lambda p: f"the plan runs in phases, with {p.dated_deps} waits-on links",
    ),
    "moodboard": Board(
        fits=lambda p: True,
        score=lambda p: 1 + 10 * p.share(p.pictures),
        why=lambda p: f"{p.pictures}/{p.items} items have evidence pictures",
    ),
}
MAX_BOARDS = 4


def rank_boards(plan: dict) -> list[tuple[float, str, str]]:
    """Every board the plan's data earns, best first, as (score, board id, why). Scores cap at 10
    and ties keep catalog order, so a fully dated plan still opens on its overview."""
    profile = Profile.of(plan)
    ranked = [
        (round(min(b.score(profile), 10), 1), board_id, b.why(profile))
        for board_id, b in BOARDS.items()
        if b.fits(profile)
    ]
    return sorted(ranked, key=lambda r: -r[0])


def chosen_boards(plan: dict) -> list[str]:
    """The plan's own `boards` list, or the top of the ranking."""
    return plan.get("boards") or [b for _, b, _ in rank_boards(plan)[:MAX_BOARDS]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0]
    )
    parser.add_argument("plan_dir", type=Path)
    parser.add_argument(
        "--artifact-url",
        default="",
        help="published artifact URL, so New tab links resolve",
    )
    args = parser.parse_args()
    problems = build(args.plan_dir, args.artifact_url)
    if problems:
        print(
            "plan.json breaks these rules; nothing was built:",
            *problems,
            sep="\n  ",
            file=sys.stderr,
        )
        sys.exit(1)
    plan = json.loads((args.plan_dir / "plan.json").read_text(encoding="utf-8"))
    print("Board ranking (score, board, why):")
    for score, board_id, why in rank_boards(plan):
        print(f"  {score:5.1f}  {board_id:<10} {why}")
    print("Built with:", ", ".join(chosen_boards(plan)))
    for name in ("board.html", "artifact.html"):
        print(f"{(args.plan_dir / name).stat().st_size:>9}  {args.plan_dir / name}")


def build(plan_dir: Path, artifact_url: str = "") -> list[str]:
    """Write board.html and artifact.html into plan_dir; return the rule breaks instead if any."""
    plan = json.loads((plan_dir / "plan.json").read_text(encoding="utf-8"))
    media = _read_media(plan_dir)
    problems = check_plan(plan, media, plan_dir)
    if problems:
        return problems
    head = f"<title>{_escape(plan['title'])}</title>\n{FONTS}\n<style>\n{_css(plan)}\n</style>\n"
    body = (
        BAR + f"<script>\n{_scripts(plan, media, plan_dir, artifact_url)}\n</script>\n"
    )
    (plan_dir / "board.html").write_text(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f"{head}</head><body>\n{body}</body></html>\n",
        encoding="utf-8",
    )
    (plan_dir / "artifact.html").write_text(
        head.replace(
            "</title>\n",
            '</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n',
            1,
        )
        + body,
        encoding="utf-8",
    )
    return []


def check_plan(plan: dict, media: list[dict], plan_dir: Path) -> list[str]:
    """Every rule break in the plan and its media list. An empty list means the plan builds."""
    problems: list[str] = []
    for key in ("id", "title", "when", "asOf", "event", "groups", "items"):
        if key not in plan:
            problems.append(f"plan: missing `{key}`")
    if problems:
        return problems
    problems += _check_media(media, plan_dir)
    media_keys = {m["key"] for m in media}
    groups = {g["id"] for g in plan["groups"]}
    item_ids = [i["id"] for i in plan["items"]]
    agenda_ids = {r["id"] for phase in plan.get("agenda", []) for r in phase["rows"]}
    problems += [
        f"plan: board `{b}` is not one of {sorted(BOARDS)}"
        for b in plan.get("boards", [])
        if b not in BOARDS
    ]
    if len(item_ids) != len(set(item_ids)):
        problems.append("items: ids repeat")
    for it in plan["items"]:
        problems += _check_item(it, groups, set(item_ids), agenda_ids, media_keys)
    for k, p in enumerate(plan.get("dashboard", [])):
        if p.get("chart", {}).get("type") not in CHARTS:
            problems.append(
                f"dashboard[{k}]: chart type must be one of {sorted(CHARTS)}"
            )
        if "w" in p and not (isinstance(p["w"], int) and p["w"] >= MIN_PANEL_W):
            problems.append(
                f"dashboard[{k}]: w is a width in pixels, at least {MIN_PANEL_W}"
            )
    return problems


def _check_item(
    it: dict, groups: set, item_ids: set, agenda_ids: set, media_keys: set
) -> list[str]:
    where = f"item {it.get('id')}"
    problems = [
        f"{where}: missing `{k}`"
        for k in ("id", "title", "group", "icon", "state")
        if k not in it
    ]
    if it.get("group") not in groups:
        problems.append(f"{where}: group `{it.get('group')}` is not in plan.groups")
    if it.get("state") not in STATES:
        problems.append(f"{where}: state must be one of {sorted(STATES)}")
    problems += [
        f"{where}: dependsOn `{d}` is not an item"
        for d in it.get("dependsOn", [])
        if d not in item_ids
    ]
    problems += [
        f"{where}: onDay `{d}` is not an agenda row"
        for d in it.get("onDay", [])
        if d not in agenda_ids
    ]
    pictures = [it["cover"]] if "cover" in it else []
    pictures += it.get("media", []) + [
        k for b in it.get("blocks", []) for k in b.get("media", [])
    ]
    problems += [
        f"{where}: picture `{k}` is not in media/media.json"
        for k in pictures
        if k not in media_keys
    ]
    for b in it.get("blocks", []):
        if b.get("type") not in BLOCKS:
            problems.append(f"{where}: block type must be one of {sorted(BLOCKS)}")
        if b.get("type") == "chart" and b.get("chart", {}).get("type") not in CHARTS:
            problems.append(f"{where}: chart type must be one of {sorted(CHARTS)}")
    if it.get("milestone") and not (it.get("due") or it.get("start")):
        problems.append(f"{where}: a milestone needs `due` or `start`")
    problems += _check_decision(it.get("decision"), where)
    for q in it.get("quotes", []):
        if not all(q.get(k) for k in ("who", "date", "text")):
            problems.append(f"{where}: every quote needs who, date and text")
    return problems


def _check_decision(decision: dict | None, where: str) -> list[str]:
    if decision is None:
        return []
    problems = []
    if decision.get("status") not in {"open", "made"}:
        problems.append(f"{where}: decision.status must be `open` or `made`")
    names = {o.get("name") for o in decision.get("options", [])}
    if decision.get("chosen") and names and decision["chosen"] not in names:
        problems.append(f"{where}: decision.chosen is not one of its options")
    return problems


# Provenance: every picture names where it came from, so a reader can open the source.
def _check_media(media: list[dict], plan_dir: Path) -> list[str]:
    problems = []
    for m in media:
        where = f"media {m.get('key')}"
        if m.get("kind") not in KINDS:
            problems.append(f"{where}: kind must be one of {sorted(KINDS)}")
        if not m.get("alt"):
            problems.append(f"{where}: needs `alt` text saying what the picture shows")
        if not (m.get("source") or {}).get("label"):
            problems.append(
                f"{where}: needs source.label (the page, chat or file it came from)"
            )
        if m.get("kind") in {"screenshot", "commons"} and not (
            m.get("source") or {}
        ).get("url"):
            problems.append(f"{where}: a {m['kind']} needs source.url")
        if m.get("kind") == "commons" and not (m.get("credit") and m.get("license")):
            problems.append(f"{where}: a Commons picture needs credit and license")
        if not (plan_dir / "media" / str(m.get("file"))).is_file():
            problems.append(f"{where}: file media/{m.get('file')} is missing")
    return problems


def _read_media(plan_dir: Path) -> list[dict]:
    path = plan_dir / "media" / "media.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []


def _css(plan: dict) -> str:
    accent = plan.get("accent", {})
    light, dark = accent.get("light", "#0d7465"), accent.get("dark", "#47c1aa")
    tokens = (
        f":root {{ --accent-l: {light}; --accent-soft-l: color-mix(in srgb, {light} 14%, #ffffff);"
        f" --accent-d: {dark}; --accent-soft-d: color-mix(in srgb, {dark} 18%, #181d1a); }}\n"
    )
    return tokens + (ASSETS / "board.css").read_text(encoding="utf-8")


def _scripts(plan: dict, media: list[dict], plan_dir: Path, artifact_url: str) -> str:
    inlined = {m["key"]: _media_entry(m, plan_dir) for m in media}
    data = (
        f"const PLAN = {json.dumps(plan, ensure_ascii=False)};\n"
        f"const MEDIA = {json.dumps(inlined, ensure_ascii=False)};\n"
        f"const BOARDS = {json.dumps(chosen_boards(plan))};\n"
    )
    code = "\n".join((ASSETS / f"{name}.js").read_text(encoding="utf-8") for name in JS)
    return data + code.replace(
        "artifactUrl: ''", f"artifactUrl: {json.dumps(artifact_url)}", 1
    )


def _media_entry(m: dict, plan_dir: Path) -> dict:
    entry = {k: v for k, v in m.items() if k not in {"key", "file", "poster"}}
    if m["kind"] == "video":
        entry["src"] = f"media/{m['file']}"
        if m.get("poster"):
            entry["poster"] = _data_uri(plan_dir / "media" / m["poster"], 900)
    else:
        entry["src"] = _data_uri(
            plan_dir / "media" / m["file"], 1400 if m["kind"] == "screenshot" else 900
        )
    return entry


def _data_uri(path: Path, longest_side: int) -> str:
    image = Image.open(path).convert("RGB")
    image.thumbnail((longest_side, longest_side))
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=78, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
