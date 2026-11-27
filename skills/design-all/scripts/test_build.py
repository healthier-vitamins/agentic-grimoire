"""Direct tests for build.py: the plan rules and what a build writes.

uv run --with pillow --with pytest python -I -m pytest test_build.py
"""

import json
from pathlib import Path

from build import build, check_plan, chosen_boards
from PIL import Image


def write_plan(plan_dir: Path, plan: dict, media: list[dict] | None = None) -> None:
    (plan_dir / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    if media is not None:
        (plan_dir / "media").mkdir()
        (plan_dir / "media" / "media.json").write_text(
            json.dumps(media), encoding="utf-8"
        )


def small_plan(**item_fields) -> dict:
    item = {
        "id": "venue",
        "title": "Book the venue",
        "group": "admin",
        "icon": "building",
        "state": "now",
        **item_fields,
    }
    return {
        "id": "test",
        "title": "Test plan",
        "when": "1 Jan 2030",
        "asOf": "2029-06-01",
        "event": {"start": "2030-01-01", "end": "2030-01-01"},
        "groups": [{"id": "admin", "name": "Admin", "icon": "wallet"}],
        "items": [item],
    }


def screenshot_entry(**fields) -> dict:
    return {
        "key": "venue-site",
        "file": "venue.png",
        "kind": "screenshot",
        "alt": "The venue's booking page",
        "source": {"label": "Venue site", "url": "https://example.com/venue"},
        **fields,
    }


def test_a_valid_plan_builds_both_pages_with_the_evidence_inlined(tmp_path):
    write_plan(tmp_path, small_plan(cover="venue-site"), [screenshot_entry()])
    Image.new("RGB", (40, 30), "white").save(tmp_path / "media" / "venue.png")

    assert build(tmp_path) == []
    board = (tmp_path / "board.html").read_text(encoding="utf-8")
    artifact = (tmp_path / "artifact.html").read_text(encoding="utf-8")
    assert board.startswith("<!doctype html>")
    assert not artifact.startswith("<!doctype")
    assert "data:image/jpeg;base64," in board


def test_a_picture_without_a_source_url_is_refused(tmp_path):
    entry = screenshot_entry(source={"label": "Venue site"})
    problems = check_plan(small_plan(cover="venue-site"), [entry], tmp_path)
    assert "media venue-site: a screenshot needs source.url" in problems


def test_a_commons_photo_needs_its_credit_and_license(tmp_path):
    entry = screenshot_entry(kind="commons")
    problems = check_plan(small_plan(), [entry], tmp_path)
    assert "media venue-site: a Commons picture needs credit and license" in problems


def test_a_cover_missing_from_the_media_list_is_refused(tmp_path):
    problems = check_plan(small_plan(cover="stock-photo"), [], tmp_path)
    assert "item venue: picture `stock-photo` is not in media/media.json" in problems


def test_links_to_unknown_items_groups_and_agenda_rows_are_refused(tmp_path):
    plan = small_plan(group="nowhere", dependsOn=["ghost"], onDay=["m1"])
    problems = check_plan(plan, [], tmp_path)
    assert "item venue: group `nowhere` is not in plan.groups" in problems
    assert "item venue: dependsOn `ghost` is not an item" in problems
    assert "item venue: onDay `m1` is not an agenda row" in problems


def test_a_failed_check_writes_nothing(tmp_path):
    write_plan(tmp_path, small_plan(state="someday"))
    assert build(tmp_path)
    assert not (tmp_path / "board.html").exists()


def items_like(n: int, **fields) -> list[dict]:
    return [
        {
            "id": f"i{k}",
            "title": f"Item {k}",
            "group": "admin",
            "icon": "list",
            "state": "now",
            **fields,
        }
        for k in range(n)
    ]


def test_a_mostly_undated_plan_is_not_offered_a_timeline():
    plan = small_plan()
    plan["items"] = items_like(3, due="2029-07-01") + items_like(20)[3:]
    assert "timeline" not in chosen_boards(plan)


def test_a_dated_plan_with_milestones_ranks_the_timeline_after_the_overview():
    plan = small_plan()
    plan["items"] = items_like(12, due="2029-07-01", milestone=True)
    assert chosen_boards(plan)[:2] == ["overview", "timeline"]


def test_debated_choices_earn_the_decisions_board():
    plan = small_plan()
    quote = {"who": "Jon", "date": "2029-06-01", "text": "Treasure, near the Bund"}
    decision = {"status": "open", "question": "Which hotel?"}
    plan["items"] = items_like(3, decision=decision, quotes=[quote])
    assert "decisions" in chosen_boards(plan)


def test_the_plan_can_name_its_own_boards():
    plan = {**small_plan(), "boards": ["moodboard", "kanban"]}
    assert chosen_boards(plan) == ["moodboard", "kanban"]


def test_unknown_boards_undated_milestones_and_stray_picks_are_refused(tmp_path):
    decision = {"status": "maybe", "chosen": "C", "options": [{"name": "A"}]}
    plan = {**small_plan(milestone=True, decision=decision), "boards": ["gantt"]}
    problems = check_plan(plan, [], tmp_path)
    assert any("board `gantt`" in p for p in problems)
    assert "item venue: a milestone needs `due` or `start`" in problems
    assert "item venue: decision.status must be `open` or `made`" in problems
    assert "item venue: decision.chosen is not one of its options" in problems


def test_a_dashboard_panel_width_is_pixels_not_columns(tmp_path):
    chart = {"type": "bars", "rows": [["Row 1", 175]]}
    plan = {**small_plan(), "dashboard": [{"title": "Price", "chart": chart, "w": 2}]}
    problems = check_plan(plan, [], tmp_path)
    assert "dashboard[0]: w is a width in pixels, at least 200" in problems
