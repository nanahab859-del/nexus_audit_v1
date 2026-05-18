#!/usr/bin/env python3
"""Score history loader for the Trends tab."""
from __future__ import annotations
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List
def _run_label(payload: Dict[str, Any], fallback_path: Path) -> str:
    ts = str(payload.get('metadata', {}).get('timestamp', '') or '')
    if ts:
        return ts[:10]
    return fallback_path.stem
def load_score_history(history_dir: str, max_runs: int = 30) -> Dict[str, Any]:
    """
    Load recent audit snapshots and return timeline data for the Trends tab.
    Returns:
        {
          'labels': ['2026-05-01', ...],
          'apps': {'nexus_core': [88, 90, ...], ...},
          'fleet_avg': [92.0, 91.3, ...]
        }
    """
    base = Path(history_dir)
    if not base.exists():
        return {'labels': [], 'apps': {}, 'fleet_avg': []}
    files = sorted(
        [p for p in base.glob('*.json') if p.is_file()],
        key=lambda p: p.stat().st_mtime,
    )[-max_runs:]
    runs: List[Dict[str, Any]] = []
    for fp in files:
        try:
            with fp.open('r', encoding='utf-8') as f:
                payload = json.load(f)
        except Exception:
            continue
        apps = payload.get('applications', {}) or {}
        scores: Dict[str, float] = {}
        for app_name, app_data in apps.items():
            try:
                scores[app_name] = round(float(app_data.get('score', 0)), 1)
            except Exception:
                scores[app_name] = 0.0
        fleet_avg = round(sum(scores.values()) / len(scores), 1) if scores else 0.0
        runs.append({
            'label': _run_label(payload, fp),
            'scores': scores,
            'fleet_avg': fleet_avg,
        })
    if not runs:
        return {'labels': [], 'apps': {}, 'fleet_avg': []}
    all_apps = sorted({app for run in runs for app in run['scores'].keys()})
    labels: List[str] = []
    fleet_avg: List[float] = []
    apps_series: Dict[str, List[Any]] = {app: [] for app in all_apps}
    for run in runs:
        labels.append(run['label'])
        fleet_avg.append(run['fleet_avg'])
        for app in all_apps:
            apps_series[app].append(run['scores'].get(app))
    return {
        'labels': labels,
        'apps': apps_series,
        'fleet_avg': fleet_avg,
        '_meta': {'runs': len(labels), 'apps': len(all_apps)},
    }


def _violation_key(item: Dict[str, Any]) -> str | None:
    if item.get('type') != 'Cross-App Import':
        return None
    source = str(item.get('source', '') or '').strip()
    target = str(item.get('target', '') or '').strip()
    if not source or not target:
        return None
    return f"{item.get('type', '')}|{source}|{target}"


def compute_violation_persistence(history_dir: str, max_runs: int = 5) -> Dict[str, Dict[str, Any]]:
    """
    Build per-violation persistence data from the last few audit snapshots.
    Returns a mapping keyed by the violation identity used in AI prompts.
    """
    base = Path(history_dir)
    if not base.exists():
        return {}

    files = sorted(
        [p for p in base.glob('*.json') if p.is_file()],
        key=lambda p: p.stat().st_mtime,
    )[-max_runs:]
    if not files:
        return {}

    runs: List[Dict[str, Any]] = []
    for fp in files:
        try:
            with fp.open('r', encoding='utf-8') as f:
                payload = json.load(f)
        except Exception:
            continue
        timestamp = str(payload.get('metadata', {}).get('timestamp', '') or '')
        if not timestamp:
            timestamp = fp.stem
        keys = []
        for violation in payload.get('violations', []) or []:
            key = _violation_key(violation)
            if key:
                keys.append(key)
        runs.append({
            'timestamp': timestamp[:10],
            'keys': set(keys),
        })

    if not runs:
        return {}

    occurrences: Dict[str, List[int]] = defaultdict(list)
    for idx, run in enumerate(runs):
        for key in run['keys']:
            occurrences[key].append(idx)

    latest_idx = len(runs) - 1
    memory: Dict[str, Dict[str, Any]] = {}
    for key, indexes in occurrences.items():
        first_idx = indexes[0]
        last_idx = indexes[-1]
        first_seen = runs[first_idx]['timestamp']
        last_seen = runs[last_idx]['timestamp']
        age_runs = len(indexes)
        consecutive = indexes == list(range(first_idx, last_idx + 1))
        present_now = latest_idx in indexes
        if present_now:
            if age_runs == 1:
                trend = 'new'
            elif consecutive:
                trend = 'persistent'
            else:
                trend = 'intermittent'
        else:
            trend = 'resolved'
        memory[key] = {
            'violation_id': key,
            'age_runs': age_runs,
            'trend': trend,
            'first_seen': first_seen,
            'last_seen': last_seen,
            'present': present_now,
            'runs_observed': indexes,
        }

    return memory
