#!/usr/bin/env python3
"""
Nexus Audit AI Backend
======================
Handles AI backend detection and completion calls.

Priority chain:
  1. Ollama  (local, free, offline)   — if running on localhost:11434
  2. Gemini  (Google AI Studio, free) — if GEMINI_API_KEY env var set
  3. Claude  (Anthropic, paid)        — if ANTHROPIC_API_KEY env var set
  4. None    → fall back to smart template engine only
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Tuple

from ..config import _GEMINI_BASE
from ..key_pool import key_pool

# ── Model / URL constants ─────────────────────────────────────────────────────

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL      = "claude-sonnet-4-20250514"

# Every model here has an independent daily quota bucket.
# Expanded to ~20 models for better redundancy and quota distribution.
GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
    "gemini-pro-latest",
    "gemini-flash-latest",
    "gemini-pro-1.5",
    "gemini-flash-lite-latest",
    "gemma-4-26b-a4b-it",
    "gemma-2-27b-it",
    "gemma-2-9b-it",
]

GEMINI_API_URL          = f"{_GEMINI_BASE}/gemini-2.0-flash:generateContent"
GEMINI_API_URL_FALLBACK = f"{_GEMINI_BASE}/gemini-2.0-flash-lite:generateContent"

# ── Task-to-model routing ──────────────────────────────────────────────────────
TASK_MODELS: dict = {
    "violation_analysis": [
        "gemini-2.5-pro",
        "gemini-3.1-pro-preview",
        "gemini-3-pro-preview",
        "gemini-2.5-flash",
        "gemini-pro-latest",
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
    ],
    "health_narrative": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-3-flash-preview",
        "gemini-3.1-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-flash-lite-latest",
    ],
    "extraction_plan": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-3.1-pro-preview",
        "gemini-pro-latest",
        "gemini-2.0-flash",
        "gemini-flash-latest",
    ],
    "upgrade_advisor": [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-lite-001",
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemma-4-26b-a4b-it",
    ],
    "cve_advisor": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-3.1-pro-preview",
        "gemini-pro-latest",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
    ],
    "complexity_advisor": [
        "gemini-2.5-pro",
        "gemma-4-26b-a4b-it",
        "gemini-3.1-pro-preview",
        "gemini-2.5-flash",
        "gemini-3-pro-preview",
        "gemini-2.0-flash",
    ],
}

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

# Rate-limit sentinel: set True when Gemini returns 429.
_GEMINI_RATE_LIMITED: bool = False


def _detect_ai_backend() -> Tuple[Optional[str], Optional[str]]:
    """
    Probe available AI backends in priority order.
    Returns (backend_name, api_key_or_none).
    """
    # 1. Ollama (local — fastest, free, works offline)
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                f"{OLLAMA_URL.rsplit('/api', 1)[0]}/api/tags",
                headers={"User-Agent": "nexus-audit/1.0"}
            ),
            timeout=2
        )
        return ("ollama", None)
    except Exception:
        pass

    # 2. Gemini — key_pool manages all GEMINI_API_KEY, GEMINI_API_KEY_2...N
    if key_pool.has_keys:
        _first = key_pool.get_key()
        if _first:
            return ("gemini", _first)
    else:
        import os
        _single = os.environ.get("GEMINI_API_KEY", "").strip()
        if _single:
            return ("gemini", _single)

    # 3. Claude (Anthropic — paid, internet required)
    import os
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if claude_key:
        return ("claude", claude_key)

    return (None, None)


def _ai_complete(
    prompt: str,
    system: str,
    backend: str,
    api_key: Optional[str],
    max_tokens: int = 1000,
    timeout: int = 30,
    preferred_models: Optional[List[str]] = None,
    silent: bool = False,
) -> Optional[str]:
    """
    Send a completion request to the detected AI backend.
    preferred_models overrides GEMINI_MODELS for the gemini branch.
    Returns the text response or None on any error.
    """
    global _GEMINI_RATE_LIMITED

    try:
        if backend == "ollama":
            payload = json.dumps({
                "model":  OLLAMA_MODEL,
                "prompt": f"{system}\n\n{prompt}",
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0.3},
            }).encode()
            req = urllib.request.Request(
                OLLAMA_URL, data=payload,
                headers={"Content-Type": "application/json"}
            )
            resp = urllib.request.urlopen(req, timeout=timeout)
            data = json.loads(resp.read())
            return data.get("response", "").strip()

        elif backend == "gemini":
            _model_list = preferred_models if preferred_models else GEMINI_MODELS
            for _model in _model_list:
                try:
                    url = f"{_GEMINI_BASE}/{_model}:generateContent?key={api_key}"
                    payload = json.dumps({
                        "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
                        "generationConfig": {
                            "maxOutputTokens": max_tokens,
                            "temperature": 0.3,
                        },
                    }).encode()
                    req = urllib.request.Request(
                        url, data=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    resp = urllib.request.urlopen(req, timeout=timeout)
                    data = json.loads(resp.read())
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join(
                            p.get("text", "") for p in parts
                            if "text" in p and "thoughtSignature" not in p
                        ).strip()
                        if text:
                            key_pool.mark_success(api_key)
                            return text

                except urllib.error.HTTPError as _gemini_http_err:
                    _body = b""
                    try:
                        _body = _gemini_http_err.read()
                    except Exception:
                        pass
                    _body_str = _body.decode("utf-8", errors="ignore")

                    if (_gemini_http_err.code == 403
                            or "allowlist" in _body_str.lower()
                            or "API_KEY_HTTP_REFERRER_BLOCKED" in _body_str):
                        print()
                        print("   \u2716 Gemini 403 \u2014 API key has HTTP referrer restrictions.")
                        print("     Fix: console.cloud.google.com \u2192 Credentials \u2192 Application restrictions \u2192 None")
                        print()
                        return None

                    elif (_gemini_http_err.code == 401
                            or "API_KEY_INVALID" in _body_str
                            or "INVALID_ARGUMENT" in _body_str):
                        print()
                        print("   \u2716 Gemini 401 \u2014 API key invalid or revoked.")
                        print("     Check GEMINI_API_KEY in .env  |  New key: aistudio.google.com")
                        print()
                        return None

                    elif _gemini_http_err.code == 429:
                        _is_daily = (
                            "RESOURCE_EXHAUSTED" in _body_str
                            or "quota" in _body_str.lower()
                            or "daily" in _body_str.lower()
                        )
                        if _is_daily:
                            key_pool.mark_daily(api_key)
                            print(f"       \u21b3 {_model}: daily quota exhausted \u2014 trying next model", flush=True)
                            continue
                        else:
                            key_pool.mark_rpm(api_key)
                            _backoff = 65
                            print(f"\n   \u26a0 [{_model}] RPM limit. Cooling down {_backoff}s ", end="", flush=True)
                            for _tick in range(_backoff):
                                time.sleep(1)
                                print("|" if (_tick + 1) % 5 == 0 else ".", end="", flush=True)
                            print(" ready", flush=True)
                            continue

                    else:
                        print(f"   \u26a0 Gemini HTTP {_gemini_http_err.code} [{_model}]: "
                              f"{_body_str[:120].strip()}")
                        continue

                except Exception:
                    continue

            if not silent:
                print("       \u2716 all models exhausted \u2014 using smart templates")
            return None

        elif backend == "claude":
            payload = json.dumps({
                "model":      CLAUDE_MODEL,
                "max_tokens": max_tokens,
                "system":     system,
                "messages":   [{"role": "user", "content": prompt}],
            }).encode()
            req = urllib.request.Request(
                ANTHROPIC_API_URL, data=payload,
                headers={
                    "Content-Type":      "application/json",
                    "anthropic-version": "2023-06-01",
                    "x-api-key":         api_key or "",
                }
            )
            resp = urllib.request.urlopen(req, timeout=timeout)
            data = json.loads(resp.read())
            blocks = data.get("content", [])
            return " ".join(b.get("text", "") for b in blocks
                            if b.get("type") == "text").strip()

    except Exception:
        return None


def _parse_ai_json(raw: str) -> Optional[dict]:
    """Robustly parse JSON from LLM output.
    Handles: markdown fences, prose before/after JSON, partial truncation.
    """
    import re
    def _normalize(parsed):
        if not isinstance(parsed, dict):
            return parsed
        confidence = parsed.get("confidence", 5)
        try:
            confidence = int(confidence)
        except Exception:
            confidence = 5
        parsed["confidence"] = max(1, min(10, confidence))
        parsed["fix_effort"] = parsed.get("fix_effort", "unknown") or "unknown"
        parsed["fix_effort_rationale"] = parsed.get("fix_effort_rationale", "") or ""
        return parsed
    if not raw:
        return None
    clean = raw.strip()
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean).strip()
    if clean.lower().startswith("json"):
        clean = clean[4:].strip()
    try:
        return _normalize(json.loads(clean))
    except json.JSONDecodeError:
        pass
    start = clean.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(clean[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return _normalize(json.loads(clean[start: i + 1]))
                    except json.JSONDecodeError:
                        break
    return None


def _ai_complete_best_of(
    prompt:     str,
    system:     str,
    backend:    str,
    api_key:    Optional[str],
    task_type:  str,
    max_tokens: int = 1400,
    n_models:   int = 2,
) -> Optional[str]:
    """
    Send the same prompt to up to n_models different models, parse each as JSON,
    score it by completeness, and return the best one.
    """
    REQUIRED = {"title", "why_harmful", "correct_location", "migration_steps",
                "before_code", "after_code", "effort", "priority", "confidence",
                "fix_effort", "fix_effort_rationale"}
    OPTIONAL = {"what_breaks_today", "description", "action"}

    models = TASK_MODELS.get(task_type, GEMINI_MODELS)

    def _score(parsed: Optional[dict]) -> int:
        if not parsed or not isinstance(parsed, dict):
            return -1
        score = 0
        for f in REQUIRED:
            if parsed.get(f):
                score += 2
        for f in OPTIONAL:
            if parsed.get(f):
                score += 1
        steps = parsed.get("migration_steps", [])
        if isinstance(steps, list) and len(steps) >= 3:
            score += 3
        if parsed.get("before_code") and parsed.get("after_code"):
            score += 2
        return score

    candidates = []
    tried = 0
    for _model in models:
        if tried >= n_models:
            break
        raw = _ai_complete(prompt, system, backend, api_key,
                           max_tokens=max_tokens,
                           preferred_models=[_model],
                           silent=True)
        if raw is None:
            continue
        parsed = _parse_ai_json(raw)
        s = _score(parsed)
        candidates.append((s, raw, parsed))
        tried += 1
        if tried < n_models and backend == "gemini":
            time.sleep(4)

    if not candidates:
        print("       \u2716 all models exhausted \u2014 using smart templates")
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    winner_score, winner_raw, winner_parsed = candidates[0]
    if len(candidates) > 1:
        loser_score = candidates[1][0]
        if winner_score > loser_score:
            print(f"       \u2605 best-of-{tried}: picked score {winner_score} over {loser_score}", flush=True)
        else:
            print(f"       \u2605 best-of-{tried}: tied at score {winner_score}", flush=True)
    return winner_raw


def _probe_available_models(api_key: str, timeout: int = 10) -> dict:
    """
    Send a 1-token probe to every model in GEMINI_MODELS.
    Returns {model_name: True/False} — True means quota available right now.
    """
    BASE    = f"{_GEMINI_BASE}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": "1"}]}],
        "generationConfig": {"maxOutputTokens": 1, "temperature": 0}
    }).encode()

    availability: dict = {}
    avail_names:  list = []
    exhausted:    list = []
    errored:      list = []

    print("   Probing model availability...", end="", flush=True)
    for model in GEMINI_MODELS:
        url = f"{BASE}/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            urllib.request.urlopen(req, timeout=timeout)
            availability[model] = True
            avail_names.append(model)
            print(".", end="", flush=True)
        except urllib.error.HTTPError as e:
            body = b""
            try:
                body = e.read()
            except Exception:
                pass
            body_str = body.decode("utf-8", errors="ignore")
            is_quota = (
                e.code == 429
                or "RESOURCE_EXHAUSTED" in body_str
                or "quota" in body_str.lower()
            )
            availability[model] = False
            if is_quota:
                exhausted.append(model)
            else:
                errored.append(f"{model}({e.code})")
            print("x", end="", flush=True)
        except Exception:
            availability[model] = False
            errored.append(model)
            print("?", end="", flush=True)
        time.sleep(0.3)
    print(flush=True)

    if avail_names:
        print(f"     \u2705 Available  : {chr(10).join(f'       {m}' for m in avail_names)}", flush=True)
    if exhausted:
        short = ", ".join(exhausted[:4])
        more  = f" +{len(exhausted)-4} more" if len(exhausted) > 4 else ""
        print(f"     \u231b Exhausted  : {short}{more}", flush=True)
        print("     \u2139  24h rolling window \u2014 quota resets as yesterday's requests age out.", flush=True)
    if errored:
        print(f"     \u26a0 Errors     : {','.join(errored)}", flush=True)
    if not avail_names:
        print("     \u2716 No models available \u2014 smart templates will be used.", flush=True)
    print(flush=True)
    return availability
