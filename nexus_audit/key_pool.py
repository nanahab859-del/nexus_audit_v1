#!/usr/bin/env python3
"""
Nexus Audit Tool - API Key Management
Manages a pool of API keys with round-robin and rate-limit detection
"""

import time
import threading
import os


class KeyPool:
    """Manages a pool of API keys (primarily Gemini) with rate-limit detection."""
    
    HEAVY = frozenset({
        "violation_analysis",
        "cve_advisor", 
        "extraction_plan",
        "complexity_advisor"
    })
    RPM_COOL = 65  # seconds to wait after RPM limit hit
    
    def __init__(self):
        self._slots = []
        self._rr = 0
        self._lock = threading.Lock()
        self._load()
    
    def _load(self):
        """Load all GEMINI_API_KEY_* from environment."""
        seen = set()
        for name in ["GEMINI_API_KEY"] + [f"GEMINI_API_KEY_{i}" for i in range(2, 21)]:
            k = os.environ.get(name, "").strip()
            if k and k not in seen:
                self._slots.append({
                    "key": k,
                    "ea": None,
                    "kind": "ok",
                    "calls": 0
                })
                seen.add(k)
        if self._slots:
            print(f"   Key pool: {len(self._slots)} key(s) loaded")
    
    def _available_unlocked(self, exclude=None):
        """Internal helper: return available keys WITHOUT acquiring lock (caller must hold lock)."""
        now = time.time()
        out = []
        for s in self._slots:
            if exclude and s["key"] in exclude:
                continue
            if s["ea"] is None:
                out.append(s)
            elif s["kind"] == "rpm" and now - s["ea"] >= self.RPM_COOL:
                s["ea"] = None
                s["kind"] = "ok"
                out.append(s)
        return out
    
    @property
    def has_keys(self) -> bool:
        """Check if any keys are available."""
        with self._lock:
            return bool(self._slots)
    
    def available(self, exclude=None):
        """Return list of available keys (not rate-limited or expired)."""
        with self._lock:
            return self._available_unlocked(exclude=exclude)
    
    def get_key(self, task="", exclude=None):
        """Get next available key, preferring heavy-task models."""
        with self._lock:
            av = self._available_unlocked(exclude=exclude)
            if not av:
                return None
            if task in self.HEAVY:
                return av[0]["key"]
            idx = self._rr % len(av)
            self._rr += 1
            return av[idx]["key"]
    
    def mark_rpm(self, key):
        """Mark key as rate-limited (per-minute)."""
        with self._lock:
            for s in self._slots:
                if s["key"] == key:
                    s["ea"] = time.time()
                    s["kind"] = "rpm"
                    print(f"   RPM-limited key {key[:10]}... rotating")
                    break
    
    def mark_daily(self, key):
        """Mark key as daily quota exhausted."""
        with self._lock:
            for s in self._slots:
                if s["key"] == key:
                    s["ea"] = time.time()
                    s["kind"] = "daily"
                    print(f"   Daily quota exhausted {key[:10]}... rotating")
                    break
    
    def mark_success(self, key):
        """Increment successful call count."""
        with self._lock:
            for s in self._slots:
                if s["key"] == key:
                    s["calls"] += 1
                    break
    
    def wait_rpm(self):
        """Wait for any RPM-limited keys to cool down."""
        with self._lock:
            rpm = [s for s in self._slots if s["kind"] == "rpm" and s["ea"]]
            if not rpm:
                return None
            rpm.sort(key=lambda s: s["ea"])
            t = rpm[0]
            wait = max(0, self.RPM_COOL - (time.time() - t["ea"]))
            if wait > 0:
                print(f"   All keys RPM-limited. Wait {int(wait)}s ", end="", flush=True)
                for _ in range(int(wait)):
                    time.sleep(1)
                    print(".", end="", flush=True)
                print(" ready", flush=True)
            t["ea"] = None
            t["kind"] = "ok"
            return t["key"]
    
    def status(self):
        """Return status string for all keys."""
        with self._lock:
            now = time.time()
            parts = []
            for i, s in enumerate(self._slots, 1):
                m = s["key"][:10] + "..."
                if s["kind"] == "rpm" and s["ea"]:
                    parts.append(f"K{i}:{m}:RPM({int(max(0, self.RPM_COOL - (now - s['ea'])))}s)")
                elif s["kind"] == "daily":
                    parts.append(f"K{i}:{m}:DAILY_DONE")
                else:
                    parts.append(f"K{i}:{m}:OK({s['calls']}calls)")
            return " | ".join(parts) or "no keys"


# Global key pool instance
key_pool = KeyPool()
