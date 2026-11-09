#!/usr/bin/env python3
"""Synchronize a complete, self-contained Agent Skill into three agent folders."""
from __future__ import annotations
import argparse
import filecmp
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skill-src" / "finance-script-studio"
TARGETS = [
    ROOT / ".opencode" / "skills" / "finance-script-studio",
    ROOT / ".codex" / "skills" / "finance-script-studio",
    ROOT / ".pi" / "skills" / "finance-script-studio",
]

def sync(check: bool = False) -> None:
    # Catch a stale legacy deployment after migrating from the typo .py to .pi.
    legacy = ROOT / ".py" / "skills" / "finance-script-studio"
    if legacy.exists():
        raise SystemExit(f"Legacy deployment remains; remove it: {legacy}")
    if not (SOURCE / "SKILL.md").is_file():
        raise SystemExit("Missing canonical SKILL.md")
    source_paths = {p.relative_to(SOURCE) for p in SOURCE.rglob("*") if p.is_file()}
    if not any(str(p).startswith("references/") for p in source_paths):
        raise SystemExit("Skill references missing")
    for target in TARGETS:
        target_paths = {p.relative_to(target) for p in target.rglob("*") if p.is_file()} if target.exists() else set()
        if check:
            if target_paths != source_paths:
                raise SystemExit(f"Skill tree out of sync: {target}")
            for rel in source_paths:
                if not filecmp.cmp(SOURCE / rel, target / rel, shallow=False):
                    raise SystemExit(f"Skill mismatch: {target / rel}")
            continue
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SOURCE, target)
    print("Agent Skill deployments verified" if check else "Agent Skill deployments synchronized")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Verify instead of writing")
    sync(ap.parse_args().check)
