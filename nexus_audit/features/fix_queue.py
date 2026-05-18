#!/usr/bin/env python3
"""Persistent recommendation fix queue."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

TRACKED_STATUSES = {"open", "in_progress", "done", "snoozed"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_recommendation_id(recommendation: Dict[str, Any]) -> str:
    """Build a stable ID for a recommendation card."""
    payload = {
        "title": recommendation.get("title", ""),
        "priority": recommendation.get("priority", ""),
        "rec_type": recommendation.get("rec_type", ""),
        "description": recommendation.get("description", ""),
        "action": recommendation.get("action", ""),
        "why_harmful": recommendation.get("why_harmful", ""),
        "correct_location": recommendation.get("correct_location", ""),
        "migration_steps": recommendation.get("migration_steps", []) or [],
        "affected_modules": sorted(recommendation.get("affected_modules", []) or []),
        "before_code": recommendation.get("before_code", ""),
        "after_code": recommendation.get("after_code", ""),
    }
    digest = hashlib.sha1(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:12]
    return f"rec-{digest}"


class FixQueue:
    def __init__(self, queue_file: str = "fix_queue.json"):
        self.file = Path(queue_file)
        self.data = self._load()

    def _load(self) -> dict:
        """Load from JSON, return empty dict if not present."""
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")

    def get_status(self, rec_id: str) -> str | None:
        """Return current status or None if not tracked."""
        return self.data.get(rec_id, {}).get("status")

    def update_status(self, rec_id: str, status: str, notes: str = "") -> None:
        """Update a recommendation's status."""
        if status not in TRACKED_STATUSES:
            raise ValueError(f"Unsupported fix queue status: {status}")
        now = _utc_now()
        entry = self.data.get(rec_id)
        if entry is None:
            entry = {"created_at": now}
            self.data[rec_id] = entry
        entry.update({
            "status": status,
            "updated_at": now,
            "notes": notes,
        })
        self.save()

    def sync_recommendations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Attach fix-queue IDs/statuses to recommendations and persist any new entries.
        Returns a summary used by the report banner.
        """
        now = _utc_now()
        reappeared_done: List[str] = []
        status_counts = {status: 0 for status in sorted(TRACKED_STATUSES)}

        for recommendation in recommendations:
            rec_id = recommendation.get("rec_id") or build_recommendation_id(recommendation)
            recommendation["rec_id"] = rec_id

            entry = self.data.get(rec_id)
            if entry is None:
                entry = {
                    "status": "open",
                    "created_at": now,
                    "updated_at": now,
                    "notes": "",
                }
                self.data[rec_id] = entry
            else:
                entry.setdefault("created_at", now)
                entry.setdefault("notes", "")
                if entry.get("status") not in TRACKED_STATUSES:
                    entry["status"] = "open"
                entry["updated_at"] = now

            status = entry.get("status", "open")
            recommendation["fix_status"] = status
            recommendation["fix_notes"] = entry.get("notes", "")
            if status == "done":
                reappeared_done.append(rec_id)
            if status in status_counts:
                status_counts[status] += 1

        self.save()
        return {
            "tracked_recommendations": len(recommendations),
            "tracked_entries": len(self.data),
            "reappeared_done": reappeared_done,
            "reappeared_done_count": len(reappeared_done),
            "status_counts": status_counts,
        }
