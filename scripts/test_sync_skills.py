#!/usr/bin/env python3
"""Self-check for symlink_store_skills: run `python3 scripts/test_sync_skills.py`."""

import os
import tempfile
from pathlib import Path

from sync_agent_docs import symlink_store_skills


def test_symlink_store_skills() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        store = home / ".agents" / "skills"
        (store / "keystone").mkdir(parents=True)
        (store / "compass").mkdir(parents=True)

        target = home / ".claude-sec" / "skills"
        target.mkdir(parents=True)
        # Pre-existing real dir (e.g. a plugin skill) must be preserved.
        (target / "gstack").mkdir()
        # Dangling symlink into the store must be pruned.
        (target / "gone").symlink_to("../../.agents/skills/gone")

        symlink_store_skills(store, target)

        # Store skills become relative symlinks that resolve.
        for name in ("keystone", "compass"):
            link = target / name
            assert link.is_symlink(), f"{name} should be a symlink"
            assert os.readlink(link) == f"../../.agents/skills/{name}"
            assert link.resolve() == (store / name).resolve()

        # Unmanaged real dir left untouched; dangling store link pruned.
        assert (target / "gstack").is_dir() and not (target / "gstack").is_symlink()
        assert not (target / "gone").is_symlink(), "dangling store link should be pruned"

        # Idempotent: a second run changes nothing.
        symlink_store_skills(store, target)
        assert os.readlink(target / "keystone") == "../../.agents/skills/keystone"

    print("test_symlink_store_skills: OK")


if __name__ == "__main__":
    test_symlink_store_skills()
