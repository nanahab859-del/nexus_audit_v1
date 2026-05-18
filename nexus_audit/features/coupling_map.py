#!/usr/bin/env python3
"""
Coupling map helpers for cross-app violation analysis.
"""

from collections import defaultdict
from typing import Any, Dict, List


NEXUS_APPS = [
    "nexus_core",
    "nexus_gateway",
    "nexus_economy",
    "nexus_gaming",
    "nexus_social",
    "nexus_tournaments",
    "nexus_content",
]


def _get_value(item: Any, *keys: str, default: Any = "") -> Any:
    for key in keys:
        if hasattr(item, key):
            value = getattr(item, key)
            if value not in (None, ""):
                return value
        if isinstance(item, dict) and item.get(key) not in (None, ""):
            return item[key]
    return default


def _app_index(apps: List[str]) -> Dict[str, int]:
    return {app: idx for idx, app in enumerate(apps)}


def build_coupling_matrix(violations: list, allowed_comms: list, apps: list) -> dict:
    """Return coupling counts and drill-down details for app-to-app imports."""
    ordered_apps = [app for app in (apps or NEXUS_APPS) if app in NEXUS_APPS] or list(NEXUS_APPS)
    index = _app_index(ordered_apps)
    size = len(ordered_apps)
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    allowed = [[0 for _ in range(size)] for _ in range(size)]
    details: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for item in violations or []:
        source = _get_value(item, "source", default="")
        target = _get_value(item, "target", default="")
        src_app = (source or "").split(".")[0]
        tgt_app = (target or "").split(".")[0]
        if src_app not in index or tgt_app not in index:
            continue
        if src_app == tgt_app:
            continue
        i = index[src_app]
        j = index[tgt_app]
        matrix[i][j] += 1
        details[f"{src_app}|{tgt_app}"].append({
            "module_path": source or target or "unknown",
            "violation_type": _get_value(item, "type", default="Unknown"),
            "penalty_points": int(_get_value(item, "penalty_points", "penalty", default=5) or 5),
            "line_number": int(_get_value(item, "line_number", "line", default=0) or 0),
            "severity": _get_value(item, "severity", default=""),
        })

    for item in allowed_comms or []:
        src_app = _get_value(item, "source_app", default="")
        tgt_app = _get_value(item, "target_app", default="")
        if src_app not in index or tgt_app not in index or src_app == tgt_app:
            continue
        allowed[index[src_app]][index[tgt_app]] += 1

    violation_pairs = sum(1 for row in matrix for count in row if count > 0)

    return {
        "apps": ordered_apps,
        "matrix": matrix,
        "allowed": allowed,
        "details": details,
        "summary": {
            "violation_pairs": violation_pairs,
            "possible_pairs": size * (size - 1),
        },
    }
