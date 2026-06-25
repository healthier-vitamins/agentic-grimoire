#!/usr/bin/env python3
"""Sync managed agent docs and skills into a user's home directory."""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
from pathlib import Path


MANAGED_BEGIN = "<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->"
MANAGED_END = "<!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->"
USER_CONTENT_MARKER = "<!-- AGENTIC-GRIMOIRE: USER CONTENT -->"
SHARED_BEGIN = "<!-- BEGIN AGENTIC-GRIMOIRE SHARED CONTENT -->"
SHARED_END = "<!-- END AGENTIC-GRIMOIRE SHARED CONTENT -->"


class SyncStatus:
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    SKIPPED = "skipped"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync this repo's Claude/Codex docs and skills into a home directory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="Target home directory. Defaults to the current user's home.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repo_root = arguments.repo_root.resolve()
    home_directory = arguments.home.expanduser().resolve()

    sync_document(
        source_path=repo_root / ".claude" / "CLAUDE.md",
        target_path=home_directory / ".claude" / "CLAUDE.md",
        shared_fragments=find_shared_fragments(repo_root, ("common", "claude")),
    )
    sync_document(
        source_path=repo_root / ".claude" / "CLAUDE.md",
        target_path=home_directory / ".claude-personal" / "CLAUDE.md",
        shared_fragments=find_shared_fragments(repo_root, ("common", "claude")),
    )
    sync_document(
        source_path=repo_root / ".codex" / "AGENTS.md",
        target_path=home_directory / ".codex" / "AGENTS.md",
        shared_fragments=find_shared_fragments(repo_root, ("common", "codex")),
    )
    sync_skills(
        source_root=repo_root / "skills",
        target_roots=(
            home_directory / ".claude" / "skills",
            home_directory / ".claude-personal" / "skills",
            home_directory / ".codex" / "skills",
        ),
    )

    return 0


def find_shared_fragments(repo_root: Path, scopes: tuple[str, ...]) -> list[Path]:
    shared_root = repo_root / ".shared-agents"
    if not shared_root.exists():
        return []

    fragments: list[Path] = []
    for scope in scopes:
        scope_root = shared_root / scope
        if not scope_root.exists():
            continue

        for candidate_path in sorted(scope_root.rglob("*")):
            if not candidate_path.is_file():
                continue
            relative_path = candidate_path.relative_to(shared_root)
            if "skills" in relative_path.parts:
                continue
            fragments.append(candidate_path)

    return fragments


def sync_document(
    source_path: Path, target_path: Path, shared_fragments: list[Path]
) -> None:
    if is_unmanaged_symlink(target_path):
        print_status(target_path, SyncStatus.SKIPPED, "symlink to unmanaged file")
        return

    generated_content = build_managed_document(source_path, shared_fragments)
    old_content = read_text_if_exists(target_path)
    new_content = merge_managed_content(old_content, generated_content)

    if old_content == new_content:
        print_status(target_path, SyncStatus.UNCHANGED)
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(new_content, encoding="utf-8")
    status = SyncStatus.CREATED if old_content is None else SyncStatus.UPDATED
    print_status(target_path, status)


def build_managed_document(source_path: Path, shared_fragments: list[Path]) -> str:
    source_content = source_path.read_text(encoding="utf-8").strip()
    shared_content = build_shared_content(source_path.parent.parent, shared_fragments)
    managed_parts = [MANAGED_BEGIN, "", source_content]

    if shared_content:
        managed_parts.extend(["", shared_content])

    managed_parts.extend(["", MANAGED_END, ""])
    return "\n".join(managed_parts)


def build_shared_content(repo_root: Path, shared_fragments: list[Path]) -> str:
    if not shared_fragments:
        return ""

    shared_root = repo_root / ".shared-agents"
    sections = [SHARED_BEGIN]
    for fragment_path in shared_fragments:
        relative_path = fragment_path.relative_to(shared_root)
        fragment_content = fragment_path.read_text(encoding="utf-8").strip()
        sections.extend(
            [
                "",
                f"## Shared Instructions: `{relative_path.as_posix()}`",
                "",
                fragment_content,
            ]
        )
    sections.extend(["", SHARED_END])
    return "\n".join(sections)


def merge_managed_content(
    old_content: str | None, generated_content: str
) -> str:
    if old_content is None or not old_content.strip():
        return generated_content

    managed_start = old_content.find(MANAGED_BEGIN)
    managed_stop = old_content.find(MANAGED_END)
    if managed_start >= 0 and managed_stop >= managed_start:
        after_managed = managed_stop + len(MANAGED_END)
        preserved_tail = preserved_content_after_managed_block(old_content[after_managed:])
        return old_content[:managed_start] + generated_content.rstrip("\n") + preserved_tail

    if managed_start >= 0:
        preserved_tail = preserved_content_after_legacy_managed_file(old_content)
        return generated_content.rstrip("\n") + preserved_tail

    return "\n".join(
        [
            generated_content.rstrip("\n"),
            "",
            USER_CONTENT_MARKER,
            "",
            old_content.rstrip("\n"),
            "",
        ]
    )


def preserved_content_after_managed_block(content_after_managed: str) -> str:
    if not content_after_managed.lstrip().startswith(USER_CONTENT_MARKER):
        return content_after_managed

    marker_start = content_after_managed.find(USER_CONTENT_MARKER)
    after_marker = marker_start + len(USER_CONTENT_MARKER)
    possible_legacy_content = content_after_managed[after_marker:]
    if MANAGED_BEGIN not in possible_legacy_content:
        return content_after_managed

    return preserved_content_after_legacy_managed_file(possible_legacy_content)


def preserved_content_after_legacy_managed_file(legacy_content: str) -> str:
    shared_stop = legacy_content.find(SHARED_END)
    if shared_stop < 0:
        return ""

    after_shared = shared_stop + len(SHARED_END)
    preserved_content = legacy_content[after_shared:].strip()
    if not preserved_content:
        return ""

    return "\n\n" + USER_CONTENT_MARKER + "\n\n" + preserved_content + "\n"


def sync_skills(source_root: Path, target_roots: tuple[Path, ...]) -> None:
    if not source_root.exists():
        return

    for skill_directory in sorted(source_root.iterdir()):
        if not skill_directory.is_dir():
            continue

        skill_file = skill_directory / "SKILL.md"
        if not has_yaml_frontmatter(skill_file):
            for target_root in target_roots:
                target_path = target_root / skill_directory.name
                print_status(target_path, SyncStatus.SKIPPED, "SKILL.md missing frontmatter")
            continue

        for target_root in target_roots:
            sync_skill_directory(skill_directory, target_root / skill_directory.name)


def sync_skill_directory(source_path: Path, target_path: Path) -> None:
    if is_unmanaged_symlink(target_path):
        print_status(target_path, SyncStatus.SKIPPED, "symlink to unmanaged file")
        return

    if target_path.exists() and directories_match(source_path, target_path):
        print_status(target_path, SyncStatus.UNCHANGED)
        return

    status = SyncStatus.UPDATED if target_path.exists() else SyncStatus.CREATED
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        shutil.rmtree(target_path)
    shutil.copytree(source_path, target_path)
    print_status(target_path, status)


def has_yaml_frontmatter(skill_file: Path) -> bool:
    if not skill_file.exists():
        return False

    first_line = skill_file.read_text(encoding="utf-8").splitlines()[:1]
    return bool(first_line and first_line[0] == "---")


def directories_match(source_path: Path, target_path: Path) -> bool:
    if not target_path.is_dir():
        return False

    comparison = filecmp.dircmp(source_path, target_path)
    if comparison.left_only or comparison.right_only or comparison.diff_files:
        return False

    return all(
        directories_match(source_path / subdir_name, target_path / subdir_name)
        for subdir_name in comparison.common_dirs
    )


def is_unmanaged_symlink(target_path: Path) -> bool:
    return target_path.is_symlink()


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def print_status(path: Path, status: str, note: str | None = None) -> None:
    relative_path = path_for_display(path)
    if note:
        print(f"{relative_path}: {status} ({note})")
        return
    print(f"{relative_path}: {status}")


def path_for_display(path: Path) -> str:
    try:
        return os.path.relpath(path, Path.home())
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
