#!/usr/bin/env python3
"""Fast changed-file-only checks for pre-commit use."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set

from ..config import FIRST_PARTY_APPS


def _tool_path(tool_name: str) -> str:
    path = shutil.which(tool_name)
    if path:
        return path
    fallback = Path.home() / "my_tools" / "miniconda3" / "envs" / "audit_env" / "bin" / tool_name
    return str(fallback) if fallback.exists() else tool_name


def get_changed_files(target_dir: str) -> Set[str]:
    """Return changed file paths from git diff HEAD."""
    result = subprocess.run(
        ["git", "-C", target_dir, "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def get_affected_apps(changed_files: Set[str]) -> Set[str]:
    """Map changed files to affected first-party Django apps."""
    apps: Set[str] = set()
    for file_path in changed_files:
        app = file_path.split("/", 1)[0]
        if app in FIRST_PARTY_APPS:
            apps.add(app)
    return apps


def _read_json(stdout: str):
    if not stdout.strip():
        return None
    return json.loads(stdout)


def _run_bandit(file_paths: List[str]) -> Dict[str, int]:
    if not file_paths:
        return {"count": 0}
    result = subprocess.run(
        [_tool_path("bandit"), "-f", "json", "-q", "--skip", "B101,B104", *file_paths],
        capture_output=True,
        text=True,
    )
    count = 0
    try:
        payload = _read_json(result.stdout) or {}
        count = len(payload.get("results", []))
    except Exception:
        count = 0
    return {"count": count}


def _run_vulture(file_paths: List[str]) -> Dict[str, int]:
    if not file_paths:
        return {"count": 0}
    result = subprocess.run(
        [_tool_path("vulture"), *file_paths, "--min-confidence=60", "--json"],
        capture_output=True,
        text=True,
    )
    count = 0
    try:
        payload = _read_json(result.stdout) or []
        count = len(payload)
    except Exception:
        count = 0
    return {"count": count}


def _run_radon(file_paths: List[str]) -> Dict[str, int]:
    if not file_paths:
        return {"count": 0}
    result = subprocess.run(
        [_tool_path("radon"), "cc", "-a", "-s", "-j", *file_paths],
        capture_output=True,
        text=True,
    )
    count = 0
    try:
        payload = _read_json(result.stdout) or {}
        for blocks in payload.values():
            for block in blocks:
                if int(block.get("complexity", 0)) > 10:
                    count += 1
    except Exception:
        count = 0
    return {"count": count}


def run_quick_check(target_dir: str, exclude_ai: bool = True) -> dict:
    """Fast static-only check for changed files."""
    changed_files = sorted(get_changed_files(target_dir))
    python_files = [
        str(Path(target_dir) / rel_path)
        for rel_path in changed_files
        if rel_path.endswith(".py") and (Path(target_dir) / rel_path).exists()
    ]
    affected_apps = sorted(get_affected_apps(set(changed_files)))

    print("FAST MODE — changed-file static analysis only")
    print(f"   Changed files: {len(changed_files)}")
    print(f"   Python files : {len(python_files)}")
    if affected_apps:
        print(f"   Affected apps: {', '.join(affected_apps)}")
    else:
        print("   Affected apps: none detected")

    if not python_files:
        print("   No Python files changed — 0 violations")
        return {
            "violations": 0,
            "pass": True,
            "changed_files": changed_files,
            "affected_apps": affected_apps,
            "counts": {"bandit": 0, "vulture": 0, "radon": 0},
        }

    counts = {
        "bandit": _run_bandit(python_files)["count"],
        "vulture": _run_vulture(python_files)["count"],
        "radon": _run_radon(python_files)["count"],
    }
    total = sum(counts.values())
    passed = total == 0

    print(f"   Bandit issues: {counts['bandit']}")
    print(f"   Dead code    : {counts['vulture']}")
    print(f"   Complexity   : {counts['radon']}")
    print(f"Fast check: {total} violation(s) — {'PASS' if passed else 'FAIL'}")

    return {
        "violations": total,
        "pass": passed,
        "changed_files": changed_files,
        "affected_apps": affected_apps,
        "counts": counts,
    }
