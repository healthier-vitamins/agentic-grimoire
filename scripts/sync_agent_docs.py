#!/usr/bin/env python3
"""Sync managed agent docs and skills into a user's home directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


# The conventional profile is owned by the `npx skills` CLI; the custom profiles are ones
# the CLI can't see, so the sync mirrors the store into them itself.
CONVENTIONAL_CLAUDE_DIRS = (".claude",)
CUSTOM_CLAUDE_DIRS = (".claude-sec", ".claude-personal")
CLAUDE_CONFIG_DIRS = CONVENTIONAL_CLAUDE_DIRS + CUSTOM_CLAUDE_DIRS

# Skill *content* is owned by the `npx skills` CLI, which populates the canonical store
# ~/.agents/skills and installs into ~/.claude (claude-code) directly. This dir is left
# to the CLI; the sync only mirrors the store into the profiles the CLI can't see.
NPX_MANAGED_CLAUDE_DIR = ".claude"
STORE_SKILLS_RELATIVE = (".agents", "skills")

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
    parser.add_argument(
        "--only",
        choices=[name.lstrip(".") for name in CLAUDE_CONFIG_DIRS],
        help=(
            "Restrict sync to a single Claude config dir (e.g. claude-sec). "
            "Skips Codex docs/agents."
        ),
    )
    parser.add_argument(
        "--custom",
        action="store_true",
        help=(
            "Sync the unconventional profiles (.claude-sec, .claude-personal). "
            "Skips .claude and Codex."
        ),
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repo_root = arguments.repo_root.resolve()
    home_directory = arguments.home.expanduser().resolve()

    claude_dirs, do_codex = select_claude_dirs(arguments.only, arguments.custom)
    claude_fragments = find_shared_fragments(repo_root, ("common", "claude"))

    for config_dir in claude_dirs:
        sync_document(
            repo_root=repo_root,
            source_path=repo_root / "CLAUDE.md",
            target_path=home_directory / config_dir / "CLAUDE.md",
            shared_fragments=claude_fragments,
        )

    # The `npx skills` CLI owns skill content in the store and in ~/.claude; it can't
    # reach the custom ~/.claude-sec / ~/.claude-personal profiles, so mirror the store
    # into those via symlinks only.
    store_skills_root = home_directory.joinpath(*STORE_SKILLS_RELATIVE)
    for config_dir in claude_dirs:
        if config_dir == NPX_MANAGED_CLAUDE_DIR:
            continue
        symlink_store_skills(store_skills_root, home_directory / config_dir / "skills")

    sync_agent_files(
        source_root=repo_root / "claude" / "agents",
        target_roots=tuple(
            home_directory / config_dir / "agents" for config_dir in claude_dirs
        ),
    )

    if do_codex:
        sync_document(
            repo_root=repo_root,
            source_path=repo_root / "AGENTS.md",
            target_path=home_directory / ".codex" / "AGENTS.md",
            shared_fragments=find_shared_fragments(repo_root, ("common", "codex")),
        )
        sync_agent_files(
            source_root=repo_root / "codex" / "agents",
            target_roots=(home_directory / ".codex" / "agents",),
        )

    return 0


def select_claude_dirs(only: str | None, custom: bool) -> tuple[tuple[str, ...], bool]:
    """Return the target Claude config dirs and whether to also sync Codex."""
    if only is not None:
        return (f".{only}",), False
    if custom:
        return CUSTOM_CLAUDE_DIRS, False
    return CONVENTIONAL_CLAUDE_DIRS, True


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
    repo_root: Path,
    source_path: Path,
    target_path: Path,
    shared_fragments: list[Path],
) -> None:
    if is_unmanaged_symlink(target_path):
        print_status(target_path, SyncStatus.SKIPPED, "symlink to unmanaged file")
        return

    generated_content = build_managed_document(repo_root, source_path, shared_fragments)
    old_content = read_text_if_exists(target_path)
    new_content = merge_managed_content(old_content, generated_content)

    if old_content == new_content:
        print_status(target_path, SyncStatus.UNCHANGED)
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(new_content, encoding="utf-8")
    status = SyncStatus.CREATED if old_content is None else SyncStatus.UPDATED
    print_status(target_path, status)


def build_managed_document(
    repo_root: Path, source_path: Path, shared_fragments: list[Path]
) -> str:
    source_content = source_path.read_text(encoding="utf-8").strip()
    shared_content = build_shared_content(repo_root, shared_fragments)
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


def symlink_store_skills(store_root: Path, target_root: Path) -> None:
    """Mirror the npx-managed skill store into a config dir the CLI can't reach.

    For every skill in the store, ensure target_root/<name> is a relative symlink into
    the store (create or repair). Prune managed symlinks (those pointing into the store)
    whose target no longer exists. Never touch real dirs or unrelated symlinks, so
    plugin/other skills already in the config dir are preserved.
    """
    if not store_root.exists():
        return

    target_root.mkdir(parents=True, exist_ok=True)

    for store_skill in sorted(store_root.iterdir()):
        if not store_skill.is_dir() or store_skill.name.startswith("."):
            continue

        link_path = target_root / store_skill.name
        desired_target = os.path.relpath(store_skill, target_root)

        if link_path.is_symlink():
            if os.readlink(link_path) == desired_target:
                print_status(link_path, SyncStatus.UNCHANGED)
                continue
            link_path.unlink()
            link_path.symlink_to(desired_target)
            print_status(link_path, SyncStatus.UPDATED)
        elif link_path.exists():
            print_status(link_path, SyncStatus.SKIPPED, "unmanaged (not a symlink)")
        else:
            link_path.symlink_to(desired_target)
            print_status(link_path, SyncStatus.CREATED)

    prune_dangling_store_links(target_root)


def prune_dangling_store_links(target_root: Path) -> None:
    """Remove symlinks into the shared store whose target no longer exists."""
    for link_path in sorted(target_root.iterdir()):
        if not link_path.is_symlink() or link_path.exists():
            continue
        target = os.readlink(link_path)
        if os.path.join(*STORE_SKILLS_RELATIVE) in target:
            link_path.unlink()
            print_status(link_path, SyncStatus.SKIPPED, "pruned dangling store link")


def sync_agent_files(source_root: Path, target_roots: tuple[Path, ...]) -> None:
    if not source_root.exists():
        return

    for source_file in sorted(source_root.iterdir()):
        if not source_file.is_file():
            continue
        for target_root in target_roots:
            sync_single_file(source_file, target_root / source_file.name)


def sync_single_file(source_path: Path, target_path: Path) -> None:
    if is_unmanaged_symlink(target_path):
        print_status(target_path, SyncStatus.SKIPPED, "symlink to unmanaged file")
        return

    new_content = source_path.read_text(encoding="utf-8")
    old_content = read_text_if_exists(target_path)
    if old_content == new_content:
        print_status(target_path, SyncStatus.UNCHANGED)
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(new_content, encoding="utf-8")
    status = SyncStatus.CREATED if old_content is None else SyncStatus.UPDATED
    print_status(target_path, status)


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
