"""Run: uv run --with pytest pytest <skill>/scripts/test_codemap.py"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import build
from scan import scan

JOBS = """from typing import Literal

from .store import save

Status = Literal["queued", "done"]


def run_next():
    save("queued")
    return "done"
"""


def project(tmp_path: Path) -> Path:
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "__init__.py").write_text("")
    (tmp_path / "app" / "jobs.py").write_text(JOBS)
    (tmp_path / "app" / "store.py").write_text("def save(state):\n    pass\n")
    (tmp_path / "web").mkdir()
    (tmp_path / "web" / "main.ts").write_text(
        "import { x } from './util.js';\nexport function start() {}\n"
    )
    (tmp_path / "web" / "util.ts").write_text("export const x = 1;\n")
    return tmp_path


def code_map(at: str = "app/jobs.py:10") -> dict:
    chart = {"name": "a job", "states_from": "app/jobs.py:5",
             "transitions": [{"from": "*", "to": "done", "at": at}]}  # fmt: skip
    return {"title": "t", "areas": [{"name": "Core", "sections": [
        {"slug": "jobs", "job": "Runs jobs.", "files": ["app/jobs.py"],
         "entry_points": ["app/jobs.py::run_next"], "statecharts": [chart]},
        {"slug": "store", "job": "Saves", "files": ["app/store.py", "app/__init__.py"],
         "entry_points": ["app/store.py::save"]},
    ]}]}  # fmt: skip


def test_scan_finds_imports_symbols_and_states(tmp_path):
    files = scan(project(tmp_path))["files"]
    assert files["app/jobs.py"]["imports"] == ["app/store.py"]
    assert files["app/jobs.py"]["symbols"]["run_next"] == 8
    assert files["app/jobs.py"]["states"] == [
        {"name": "Status", "line": 5, "values": ["queued", "done"]}
    ]
    assert files["web/main.ts"]["imports"] == ["web/util.ts"]


def test_build_resolves_lines_edges_prompt_and_walked_badge(tmp_path):
    root = project(tmp_path)
    page = build.resolve(code_map(), scan(root), root)
    jobs = page["sections"][0]
    assert jobs["uses"] == ["store"] and not jobs["walked"]
    assert build.prompt_for(jobs) == (
        "/codewalk jobs: Runs jobs. Entry points: app/jobs.py:8. Files: app/jobs.py. "
        "Walk only this section; stop where calls leave it."
    )
    (root / ".codewalk" / "jobs").mkdir(parents=True)
    (root / ".codewalk" / "jobs" / "page.html").write_text("")
    page = build.resolve(code_map(), scan(root), root)
    assert page["sections"][0]["walked"]
    assert 'href="../.codewalk/jobs/page.html"' in build.render(page)


def test_build_rejects_a_citation_that_does_not_spell_the_state(tmp_path):
    root = project(tmp_path)
    with pytest.raises(build.MapError, match="does not spell 'done'"):
        build.resolve(code_map(at="app/jobs.py:1"), scan(root), root)


def test_main_writes_the_page(tmp_path):
    root = project(tmp_path)
    (root / ".codemap").mkdir()
    (root / ".codemap" / "map.json").write_text(json.dumps(code_map()))
    assert build.main(["--root", str(root)]) == 0
    assert "<svg" in (root / ".codemap" / "map.html").read_text()
