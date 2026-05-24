#!/usr/bin/env python3
"""
Nexus Audit AI Recommendations
================================
Orchestrates all AI-powered recommendation layers:
  1. Per-violation deep refactoring analysis
  2. Per-app health narratives (below 90%)
  3. Shared-utility extraction plans
  4. Outdated package upgrade advisor
  5. CVE security advisor

Also provides the Tier-1 template-based fallback: generate_recommendations().
"""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .backend import (
    _detect_ai_backend, _ai_complete, _ai_complete_best_of,
    _parse_ai_json, _probe_available_models,
    TASK_MODELS, GEMINI_MODELS, _GEMINI_RATE_LIMITED,
)
from .prompts import (
    AI_SYSTEM,
    build_violation_prompt,
    build_health_prompt,
    build_extraction_prompt,
    build_upgrade_prompt,
    build_cve_prompt,
)
from ..config import HISTORY_DIR
from ..models import Violation
from ..features.timeline import compute_violation_persistence



def _show_ai_progress(progress: Dict[str, str]) -> None:
    if not progress:
        return
    done = sum(1 for status in progress.values() if status == "done")
    total = len(progress)
    line = "  ".join(
        f"{app} {'✅' if state == 'done' else '⏳'}"
        for app, state in progress.items()
    )
    print(f"\r[AI] {line}   {done}/{total}", end="", flush=True)


def _first_nonempty(*values):
    for value in values:
        if value not in (None, "", [], {}, ()):
            return value
    return None


def _security_guidance(issue_type: str) -> tuple[str, str]:
    guidance = {
        "Hardcoded Password": (
            "Move the password into an environment variable or secret manager.",
            "Replace hardcoded credentials with settings-backed secrets and rotate the exposed value.",
        ),
        "Hardcoded Secret": (
            "Move the secret into an environment variable or secret manager.",
            "Replace hardcoded secrets with settings-backed secrets and rotate the exposed value.",
        ),
        "Insecure Random": (
            "Use secrets.SystemRandom or secrets.token_hex for cryptographic values.",
            "Replace random-based security logic with the secrets module and verify callers still work.",
        ),
        "Bare Except": (
            "Replace broad exception handling with specific exception types.",
            "Narrow each catch block to the real failure mode and preserve the stack trace where needed.",
        ),
        "Security Issue": (
            "Review the Bandit finding and apply the safest targeted fix.",
            "Follow Bandit guidance for the exact line and verify the issue is gone after the change.",
        ),
    }
    return guidance.get(issue_type, (
        "Apply the safest targeted fix for this security finding.",
        "Review the exact line and remove the pattern that triggered the alert.",
    ))


def _rec_key(rec: Dict) -> tuple:
    return (
        rec.get("title", ""),
        rec.get("priority", ""),
        rec.get("rec_type", ""),
        tuple(rec.get("affected_modules", []) or []),
        rec.get("action", ""),
    )


def _make_template_recommendation(
    title: str,
    priority: str,
    description: str,
    action: str,
    affected_modules: List[str],
    rec_type: str,
    effort: str = "",
    confidence: int = 7,
    line_number: int = 0,
) -> Dict:
    return {
        "title": title,
        "priority": priority,
        "description": description,
        "action": action,
        "affected_modules": affected_modules[:8],
        "rec_type": rec_type,
        "ai_generated": False,
        "confidence": confidence,
        **({"line_number": line_number} if line_number else {}),
        **({"effort": effort} if effort else {}),
    }


def _violation_template(v: Violation) -> Optional[Dict]:
    v_type = getattr(v, "type", "") or ""
    source = getattr(v, "source", "") or ""
    target = getattr(v, "target", "") or ""
    severity = (getattr(v, "severity", "") or "LOW").upper()
    source_module = source or getattr(v, "file_path", "") or "unknown"

    if v_type in {"Cross-App Import", "Direct Cross-App Import"}:
        src_app = source.split(".")[0] if source else "unknown"
        tgt_app = target.split(".")[0] if target else "shared"
        line_number = int(getattr(v, "line_number", 0) or getattr(v, "line", 0) or 0)
        title = f"Refactor {src_app} -> {tgt_app} import"
        description = (
            f"Direct import from {source} to {target} crosses app boundaries and "
            f"should be replaced with a decoupled integration path."
        )
        action = (
            "Move the shared behavior into a signal, Celery task, REST call, or "
            "a shared interface in nexus_core so the apps stop importing each other directly."
        )
        return _make_template_recommendation(
            title=title,
            priority="CRITICAL",
            description=description,
            action=action,
            affected_modules=[m for m in [source, target] if m],
            rec_type="violation",
            effort="M",
            confidence=8,
            line_number=line_number,
        )

    if v_type == "Test Cross-App Import":
        title = f"Decouple test import in {source_module}"
        line_number = int(getattr(v, "line_number", 0) or getattr(v, "line", 0) or 0)
        description = (
            f"Test code in {source_module} crosses app boundaries by importing {target} directly."
        )
        action = (
            "Replace the live app import with factories, fixtures, or mocks so the test stays isolated."
        )
        return _make_template_recommendation(
            title=title,
            priority="LOW",
            description=description,
            action=action,
            affected_modules=[m for m in [source, target] if m],
            rec_type="test-violation",
            effort="S",
            confidence=7,
            line_number=line_number,
        )

    if v_type in {"Hardcoded Password", "Hardcoded Secret", "Insecure Random", "Bare Except", "Security Issue"}:
        fix, follow_up = _security_guidance(v_type)
        affected = [p for p in [getattr(v, "file_path", ""), source] if p]
        line_number = int(getattr(v, "line_number", 0) or getattr(v, "line", 0) or 0)
        title = f"Fix {v_type}"
        if affected and affected[0]:
            title = f"Fix {v_type} in {Path(affected[0]).name}"
        return _make_template_recommendation(
            title=title,
            priority="HIGH" if severity in {"HIGH", "CRITICAL"} else "MEDIUM",
            description=getattr(v, "description", "") or f"{v_type} detected by Bandit.",
            action=f"{fix} {follow_up}",
            affected_modules=affected[:3],
            rec_type="security",
            effort="S",
            confidence=8,
            line_number=line_number,
        )

    return _make_template_recommendation(
        title=f"Review {v_type or 'Unknown'}",
        priority="MEDIUM" if severity != "LOW" else "LOW",
        description=getattr(v, "description", "") or "Unhandled variation detected by the audit.",
        action=(
            "Inspect the source and convert this pattern into the project's preferred "
            "decoupled or framework-approved approach."
        ),
        affected_modules=[p for p in [source, target, getattr(v, "file_path", "")] if p],
        rec_type="generic",
        effort="S",
        confidence=6,
        line_number=int(getattr(v, "line_number", 0) or getattr(v, "line", 0) or 0),
    )


def _complexity_template(item: Dict) -> Dict:
    file_path = item.get("full_path") or item.get("file") or "unknown"
    function = item.get("function", "unknown")
    complexity = item.get("complexity", 0)
    priority = "HIGH" if complexity > 20 else "MEDIUM"
    return _make_template_recommendation(
        title=f"Refactor {function}",
        priority=priority,
        description=(
            f"{function} in {Path(file_path).name} has cyclomatic complexity {complexity}."
        ),
        action=(
            "Split the function into smaller helpers, flatten branches, and move repeated "
            "logic into a shared utility so the code becomes easier to test."
        ),
        affected_modules=[file_path],
        rec_type="performance",
        effort="M" if complexity <= 20 else "L",
        confidence=7,
    )


def _ghost_template(group_app: str, files: List[str]) -> Dict:
    return _make_template_recommendation(
        title=f"Review ghost files in {group_app}",
        priority="LOW",
        description=f"{len(files)} ghost file(s) were discovered for {group_app}.",
        action=(
            "Remove dead files that are no longer imported, or register the missing modules "
            "properly if they are still required."
        ),
        affected_modules=files[:8],
        rec_type="health",
        effort="S",
        confidence=6,
    )


def _cycle_template(cycle: Dict) -> Dict:
    nodes = cycle.get("nodes", [])
    apps = cycle.get("apps", [])
    cross = bool(cycle.get("cross_app"))
    title = "Break cross-app cycle" if cross else "Resolve intra-app cycle"
    priority = "CRITICAL" if cross else "HIGH"
    return _make_template_recommendation(
        title=title,
        priority=priority,
        description=" -> ".join(nodes) if nodes else "Circular dependency detected.",
        action=(
            "Move the shared dependency into a lower-level module, then replace the direct "
            "edge with a signal, task, or helper import that does not re-enter the cycle."
        ),
        affected_modules=nodes[:8] or apps[:8],
        rec_type="architecture",
        effort="L" if cross else "M",
        confidence=7,
    )

def _analyze_single_app(
    app: str,
    s: Dict,
    backend: str,
    label: str,
    throttled_complete,
    rate_limited,
) -> List[Dict]:
    score = s.get("score", 100)
    if score >= 90:
        return []
    bv      = s.get("boundary_violations", s.get("violations", 0))
    sec     = s.get("security_issues", 0)
    is_core = app in ("nexus_core", "nexus_gateway")
    vpts    = bv * (3 if is_core else 5)
    spts    = sec * 3

    prompt = build_health_prompt(app, score, bv, sec, is_core)
    if rate_limited():
        print(f"   \u26a0 Rate-limited \u2014 skipping health narrative for {app}")
        return []
    narrative = throttled_complete(
        prompt, AI_SYSTEM, backend, max_tokens=300,
        desc=f"Health narrative: {app} ({score}%)",
        task_type="health_narrative",
    )
    if not narrative:
        return []
    return [{
        "title":            f"{app.upper()} \u2014 Health Analysis",
        "priority":         "HIGH" if score < 80 else "MEDIUM",
        "description":      narrative,
        "action":           (
            f"Fix {bv} boundary violation(s) first (+{vpts} pts), "+
            f"then {sec} security finding(s) (+{spts} pts). "+
            f"Projected score: {min(100, score + vpts + spts)}%."
        ),
        "affected_modules": list(s.get("modules", []))[:5],
        "ai_generated":     True,
        "ai_backend":       label,
        "effort":           "M" if bv <= 2 else "L",
    }]

def run_ai_recommendations(
    violations: List,
    app_stats:  Dict,
    ghost_files: List,
    shared_util_candidates: Dict,
    backend: str,
    api_key: Optional[str],
    dep_scan: Optional[Dict] = None,
) -> Tuple[List[Dict], str]:
    """
    Generate AI-powered recommendations using the detected backend.
    Returns (recommendations_list, backend_label).

    Five layers:
      1. Per-violation refactoring plans (concrete code + migration steps) — parallel
      2. Per-app health narratives for apps below 90% — parallel
      3. Shared-utility extraction plans — sequential
      4. Outdated package upgrade advisor — parallel
      5. CVE security advisor — parallel
    """
    from . import backend as _backend_mod
    import threading

    ai_recs:  List[Dict] = []
    label = {
        "ollama": "Ollama (local)",
        "gemini": "Google Gemini",
        "claude": "Claude (Anthropic)",
    }.get(backend, backend)

    # ── Rate-limit controls ───────────────────────────────────────────────
    INTER_CALL_DELAY    = 4      # seconds between every AI call
    MAX_VIOLATION_CALLS = 5      # cap Layer 1 to top-5 violations by impact
    MAX_CONSEC_429      = 2      # abort after this many consecutive failures

    _consec_429  = 0
    _total_calls = 0
    _counter_lock = threading.Lock()  # Protect counter increments in parallel threads

    # ── Pre-flight quota probe ────────────────────────────────────────────
    _model_avail:          dict = {}
    _filtered_task_models: dict = {}
    if backend == "gemini" and api_key:
        _model_avail = _probe_available_models(api_key)
        _globally_available = [m for m, ok in _model_avail.items() if ok]
        for _task, _mlist in TASK_MODELS.items():
            _filtered = [m for m in _mlist if _model_avail.get(m, False)]
            for m in _globally_available:
                if m not in _filtered:
                    _filtered.append(m)
            _filtered_task_models[_task] = _filtered

    violation_memory = compute_violation_persistence(HISTORY_DIR)

    def _throttled_complete(prompt, system, backend, max_tokens=800,
                            desc="", task_type=None, best_of=1):
        """Wrapper: log progress, pace calls, track consecutive failures (thread-safe)."""
        nonlocal _consec_429, _total_calls
        with _counter_lock:
            call_n = _total_calls + 1
            _total_calls += 1
        if task_type and _filtered_task_models.get(task_type):
            pref = _filtered_task_models[task_type]
        elif task_type:
            pref = TASK_MODELS.get(task_type)
        else:
            pref = None
        model_tag = f"[{task_type or 'default'}]"
        if desc:
            print(f"\n   [{call_n}] {model_tag} {desc}", flush=True)
        if _total_calls > 1:  # Check without lock (minor race, acceptable)
            print("       pacing ", end="", flush=True)
            for _w in range(INTER_CALL_DELAY):
                time.sleep(1)
                print(".", end="", flush=True)
            print(flush=True)
        if best_of > 1 and backend == "gemini" and task_type:
            result = _ai_complete_best_of(
                prompt, system, backend,
                task_type=task_type, max_tokens=max_tokens, n_models=best_of
            )
        else:
            result = _ai_complete(prompt, system, backend,
                                  max_tokens=max_tokens,
                                  preferred_models=pref)
        if result is None:
            with _counter_lock:
                _consec_429 += 1
            if desc:
                print("       \u2717 failed", flush=True)
        else:
            with _counter_lock:
                _consec_429 = 0
            if desc:
                print("       \u2713 done", flush=True)
        return result

    def _rate_limited():
        with _counter_lock:
            return _consec_429 >= MAX_CONSEC_429

    def _analyze_single_violation(tgt, info, src_mods_list):
        """Analyze a single violation independently (for parallel execution)."""
        if _rate_limited():
            return None
        src_apps = sorted(info["src_apps"])
        src_mods = info["sources"][:5]
        tgt_app  = tgt.split(".")[0]
        tgt_leaf = tgt.split(".")[-1]

        memory_context = [
            violation_memory[key]
            for key in (f"Cross-App Import|{src_mod}|{tgt}" for src_mod in src_mods)
            if key in violation_memory
        ]
        prompt = build_violation_prompt(
            tgt, tgt_app, tgt_leaf, src_mods, src_apps,
            memory=memory_context or None
        )
        _is_top = src_mods_list.index(tgt) < 2
        raw = _throttled_complete(
            prompt, AI_SYSTEM, backend, max_tokens=1400,
            desc=f"Violation: {tgt_leaf} ← {len(src_apps)} app(s)",
            task_type="violation_analysis",
            best_of=2 if _is_top else 1,
        )
        rec = _parse_ai_json(raw)
        if rec and isinstance(rec, dict):
            rec["ai_generated"]     = True
            rec["ai_backend"]       = label
            rec["affected_modules"] = src_mods
            return rec
        elif raw:
            return {
                "title":            f"Refactor: move {tgt_leaf} to correct app",
                "priority":         "HIGH",
                "description":      raw[:500],
                "action":           f"Move {tgt} to nexus_core or appropriate shared module.",
                "affected_modules": src_mods,
                "ai_generated":     True,
                "ai_backend":       label,
                "effort":           "M",
            }
        return None

    # ── Layer 1: per-violation deep analysis (parallel) ──────────────────────────────
    by_target: Dict[str, Dict] = {}
    for v in violations:
        if getattr(v, "type", "") != "Cross-App Import":
            continue
        tgt = getattr(v, "target", "")
        src_mod = getattr(v, "source", "")
        if tgt not in by_target:
            by_target[tgt] = {"sources": [], "src_apps": set()}
        by_target[tgt]["sources"].append(src_mod)
        by_target[tgt]["src_apps"].add(src_mod.split(".")[0])

    sorted_targets = sorted(
        by_target.items(),
        key=lambda kv: len(kv[1]["src_apps"]),
        reverse=True
    )[:MAX_VIOLATION_CALLS]

    if len(by_target) > MAX_VIOLATION_CALLS:
        print(f"   ℹ {len(by_target)} unique violation targets — analysing top "
              f"{MAX_VIOLATION_CALLS} by impact to respect rate limits")

    # Run violation analyses in parallel (max 3 workers to respect rate limits)
    if sorted_targets:
        violation_results: List[Dict] = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(_analyze_single_violation, tgt, info, [t for t, _ in sorted_targets]): tgt
                for tgt, info in sorted_targets
            }
            for future in as_completed(futures):
                tgt = futures[future]
                try:
                    rec = future.result()
                    if rec:
                        violation_results.append(rec)
                        print(f"   ✓ [{label}] {str(rec.get('title', ''))[:60]}")
                except Exception as exc:
                    print(f"\n   ✗ [{label}] violation analysis error for {tgt}: {exc}")
        ai_recs.extend(violation_results)

    # ── Layer 2: per-app health narratives (below 90%) ───────────────────
    health_apps = [(app, s) for app, s in sorted(app_stats.items()) if s.get("score", 100) < 90]
    health_results: List[tuple[str, List[Dict]]] = []
    if health_apps:
        progress = {app: "pending" for app, _ in health_apps}
        _show_ai_progress(progress)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    _analyze_single_app, app, s, backend, label, _throttled_complete, _rate_limited
                ): app for app, s in health_apps
            }
            for future in as_completed(futures):
                app = futures[future]
                try:
                    recs = future.result()
                except Exception as exc:
                    print(f"\n   ✗ [{label}] health narrative error for {app}: {exc}")
                    recs = []
                health_results.append((app, recs))
                progress[app] = "done"
                _show_ai_progress(progress)
            print()
        for _, recs in sorted(health_results, key=lambda item: item[0]):
            ai_recs.extend(recs)
    
    def _analyze_upgrade(pkg_info):
        """Analyze a single package upgrade independently (for parallel execution)."""
        if _rate_limited():
            return None
        pkg_name  = pkg_info["name"]
        installed = pkg_info["installed"]
        latest    = pkg_info["latest"]
        cve_count = pkg_info.get("cve_count", 0)
        
        prompt = build_upgrade_prompt(pkg_name, installed, latest, cve_count)
        raw = _throttled_complete(
            prompt, AI_SYSTEM, backend, max_tokens=400,
            desc=f"Upgrade: {pkg_name} {installed} → {latest}",
            task_type="upgrade_advisor",
        )
        rec = _parse_ai_json(raw)
        if rec and isinstance(rec, dict):
            rec["ai_generated"]     = True
            rec["ai_backend"]       = label
            rec["title"]            = rec.get("title", f"Upgrade {pkg_name}: {installed} → {latest}")
            rec["priority"]         = "HIGH" if cve_count > 0 else "MEDIUM"
            rec["affected_modules"] = [pkg_name]
            rec["rec_type"]         = "upgrade"
            rec["action"] = (
                f"{rec.get('upgrade_command', f'pip install {pkg_name}=={latest}')}"
                + (f"\n\nBreaking changes: {rec['breaking_changes']}" if rec.get("breaking_changes") else "")
                + (f"\n\nVerify: {rec['test_after']}" if rec.get("test_after") else "")
            )
            return rec
        elif raw:
            return {
                "title":            f"Upgrade {pkg_name}: {installed} → {latest}",
                "priority":         "HIGH" if cve_count > 0 else "MEDIUM",
                "action":           f"pip install {pkg_name}=={latest}\n\n{raw[:300]}",
                "affected_modules": [pkg_name],
                "ai_generated":     True,
                "ai_backend":       label,
                "rec_type":         "upgrade",
            }
        return None

    def _analyze_cve(cve):
        """Analyze a single CVE independently (for parallel execution)."""
        if _rate_limited():
            return None
        cve_id   = cve.get("id", "CVE-unknown")
        pkg_name = cve.get("package", "unknown")
        summary  = cve.get("summary", "No summary available")
        severity = cve.get("severity", "UNKNOWN")
        
        prompt = build_cve_prompt(cve_id, pkg_name, severity, summary)
        raw = _throttled_complete(
            prompt, AI_SYSTEM, backend, max_tokens=450,
            desc=f"CVE: {cve_id} in {pkg_name}",
            task_type="cve_advisor",
        )
        rec = _parse_ai_json(raw)
        if rec and isinstance(rec, dict):
            rec["ai_generated"]     = True
            rec["ai_backend"]       = label
            rec["title"]            = rec.get("title", f"Fix {cve_id} in {pkg_name}")
            rec["priority"]         = rec.get("nexus_risk_level", "HIGH").split()[0]
            rec["affected_modules"] = [pkg_name]
            rec["rec_type"]         = "cve"
            rec["action"] = (
                f"{rec.get('fix_command', f'pip install --upgrade {pkg_name}')}"
                + (f"\n\nConfig: {rec['config_changes']}"
                   if rec.get("config_changes") and rec["config_changes"] != "None required" else "")
                + (f"\n\nVerify: {rec['verify_fixed']}" if rec.get("verify_fixed") else "")
            )
            return rec
        elif raw:
            return {
                "title":            f"Fix {cve_id} in {pkg_name} ({severity})",
                "priority":         "CRITICAL" if severity.upper() == "CRITICAL" else "HIGH",
                "action":           f"pip install --upgrade {pkg_name}\n\n{raw[:300]}",
                "affected_modules": [pkg_name],
                "ai_generated":     True,
                "ai_backend":       label,
                "rec_type":         "cve",
            }
        return None

    # ── Layer 3: shared-utility extraction plans ──────────────────────────
    for tgt, importers in list(shared_util_candidates.items())[:3]:
        prompt = build_extraction_prompt(tgt, importers)

        if _rate_limited():
            print(f"   \u26a0 Rate-limited \u2014 skipping extraction plan for {tgt}")
            continue
        plan = _throttled_complete(
            prompt, AI_SYSTEM, backend, max_tokens=400,
            desc=f"Extract plan: {tgt.split('.')[-1]}",
            task_type="extraction_plan",
        )
        if plan:
            ai_recs.append({
                "title":            f"Extract Shared Utility: {'.'.join(tgt.split('.')[-2:])}",
                "priority":         "HIGH",
                "description":      (
                    f"`{tgt}` is imported by {len(importers)} app(s) "
                    f"({', '.join(importers)}) as a cross-app violation. "
                    f"One refactor eliminates all {len(importers)} violations."
                ),
                "action":           plan,
                "affected_modules": [tgt] + importers,
                "ai_generated":     True,
                "ai_backend":       label,
                "effort":           "M",
            })
            print(f"   \u2714 [{label}] extraction plan: {tgt}")

    # ── Layer 4: outdated package upgrade advisor (parallel) ──────────────────────────
    if dep_scan and dep_scan.get("outdated_count", 0) > 0:
        outdated_pkgs = [
            p for p in dep_scan.get("packages", [])
            if p.get("outdated") and p.get("installed") != "unknown"
        ]
        if outdated_pkgs:
            upgrade_results: List[Dict] = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(_analyze_upgrade, pkg): pkg["name"] for pkg in outdated_pkgs}
                for future in as_completed(futures):
                    pkg_name = futures[future]
                    try:
                        rec = future.result()
                        if rec:
                            upgrade_results.append(rec)
                            print(f"   ✓ [{label}] upgrade plan: {pkg_name}")
                    except Exception as exc:
                        print(f"\n   ✗ [{label}] upgrade analysis error for {pkg_name}: {exc}")
            ai_recs.extend(upgrade_results)

    # ── Layer 5: CVE security advisor (parallel) ─────────────────────────────────────
    if dep_scan and dep_scan.get("critical_cves"):
        top_cves = dep_scan["critical_cves"][:3]
        if top_cves:
            cve_results: List[Dict] = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(_analyze_cve, cve): cve.get("id", "unknown") for cve in top_cves}
                for future in as_completed(futures):
                    cve_id = futures[future]
                    try:
                        rec = future.result()
                        if rec:
                            cve_results.append(rec)
                            print(f"   ✓ [{label}] CVE analysis: {cve_id}")
                    except Exception as exc:
                        print(f"\n   ✗ [{label}] CVE analysis error for {cve_id}: {exc}")
            ai_recs.extend(cve_results)

    # ── Rate-limit summary ────────────────────────────────────────────────
    if _backend_mod._GEMINI_RATE_LIMITED and backend == "gemini":
        total_planned = len(by_target) + sum(
            1 for s in app_stats.values() if s.get("score", 100) < 90
        ) + min(3, len(shared_util_candidates))
        skipped = max(0, total_planned - len(ai_recs))
        print()
        print("   \u26a0  Gemini free-tier 429: rate window exhausted.")
        if ai_recs:
            print(f"     \u2713  {len(ai_recs)} recommendation(s) generated before limit.")
        if skipped > 0:
            print(f"     \u25a1  {skipped} call(s) skipped \u2014 re-run in ~60 s for the rest.")
        print("     Tip: `ollama run llama3` = local AI with zero rate limits.")
        print()
        _backend_mod._GEMINI_RATE_LIMITED = False

    return ai_recs, label


def generate_recommendations(
    violations: List,
    metrics: Dict,
    cycles: List,
    ghost_files: List,
) -> List[Dict]:
    """
    Tier-1 (offline) template-based recommendations.
    Called when no AI backend is available, or to supplement AI results.

    Covers every variation emitted by the audit, with targeted fallbacks for
    unknown future violation types.
    """
    recommendations: List[Dict] = []
    seen = set()

    def _append(rec: Dict) -> None:
        key = _rec_key(rec)
        if key in seen:
            return
        seen.add(key)
        recommendations.append(rec)

    cross_app = [v for v in violations if getattr(v, "type", "") == "Cross-App Import"]
    by_target = defaultdict(list)
    for v in cross_app:
        by_target[getattr(v, "target", "") or "unknown"].append(v)
    for target, items in sorted(by_target.items()):
        src_modules = sorted({getattr(v, "source", "") for v in items if getattr(v, "source", "")})
        src_apps = sorted({s.split(".")[0] for s in src_modules if s})
        title = f"Refactor {target.split('.')[-1] or 'cross-app'} boundary"
        _append(_make_template_recommendation(
            title=title,
            priority="CRITICAL",
            description=(
                f"{len(items)} cross-app violation(s) point at {target}. "
                f"Apps involved: {', '.join(src_apps) if src_apps else 'unknown'}."
            ),
            action=(
                "Replace the direct import with a signal, Celery task, REST call, or "
                "shared service boundary so each app owns its own implementation."
            ),
            affected_modules=src_modules[:8] + ([target] if target else []),
            rec_type="violation",
            effort="M",
            confidence=8,
        ))

    test_cross = [v for v in violations if getattr(v, "type", "") == "Test Cross-App Import"]
    by_test_source = defaultdict(list)
    for v in test_cross:
        by_test_source[getattr(v, "source", "") or "unknown"].append(v)
    for source, items in sorted(by_test_source.items()):
        targets = sorted({getattr(v, "target", "") for v in items if getattr(v, "target", "")})
        _append(_make_template_recommendation(
            title=f"Decouple test import in {Path(source).name if source else 'tests'}",
            priority="LOW",
            description=(
                f"{len(items)} test cross-app import(s) were found in {source}. "
                "Tests should isolate external modules instead of importing them directly."
            ),
            action=(
                "Use factories, fixtures, or mocks so the test stays focused on one app "
                "and does not depend on live behavior from another app."
            ),
            affected_modules=[source] + targets[:4],
            rec_type="test-violation",
            effort="S",
            confidence=7,
        ))

    security_viols = [
        v for v in violations
        if hasattr(v, "type") and getattr(v, "type", "") in {
            "Hardcoded Password", "Bare Except", "Security Issue",
            "Insecure Random", "Hardcoded Secret"
        }
    ]
    by_security_type = defaultdict(list)
    for v in security_viols:
        by_security_type[getattr(v, "type", "Security Issue")].append(v)
    for sec_type, items in sorted(by_security_type.items()):
        fix, follow_up = _security_guidance(sec_type)
        affected = sorted({
            _first_nonempty(getattr(v, "file_path", ""), getattr(v, "source", ""))
            for v in items
        })
        affected = [a for a in affected if a]
        priority = "HIGH" if any((getattr(v, "severity", "") or "").upper() == "HIGH" for v in items) else "MEDIUM"
        _append(_make_template_recommendation(
            title=f"Fix {sec_type}",
            priority=priority,
            description=(
                f"{len(items)} {sec_type.lower()} finding(s) were detected by Bandit."
            ),
            action=f"{fix} {follow_up}",
            affected_modules=affected[:8],
            rec_type="security",
            effort="S",
            confidence=8,
        ))

    avg_cx = metrics.get("average_complexity", 0)
    max_cx = metrics.get("max_complexity", 0)
    hcf = metrics.get("high_complexity_functions", [])
    if hcf:
        for item in sorted(hcf, key=lambda i: (i.get("file", ""), i.get("function", ""))):
            _append(_complexity_template(item))
    elif avg_cx > 10 or max_cx > 20:
        _append(_make_template_recommendation(
            title="Reduce cyclomatic complexity",
            priority="HIGH" if max_cx > 20 else "MEDIUM",
            description=(
                f"Average complexity is {avg_cx:.2f} and max complexity is {max_cx}."
            ),
            action=(
                "Split the largest functions into helpers and replace long branching chains "
                "with smaller composable pieces."
            ),
            affected_modules=[],
            rec_type="performance",
            effort="M",
            confidence=7,
        ))

    if ghost_files:
        by_app_ghost = defaultdict(list)
        for gf in ghost_files:
            by_app_ghost[gf.split(".")[0]].append(gf)
        for app, files in sorted(by_app_ghost.items()):
            _append(_ghost_template(app, files))

    if cycles:
        for cycle in cycles[:8]:
            _append(_cycle_template(cycle))

    known_types = {
        "Cross-App Import",
        "Test Cross-App Import",
        "Hardcoded Password",
        "Bare Except",
        "Security Issue",
        "Insecure Random",
        "Hardcoded Secret",
        "Circular Dependency",
        "Ghost File",
        "Excessive Complexity",
    }
    for v in violations:
        v_type = getattr(v, "type", "") or "Unknown"
        if v_type in known_types:
            continue
        _append(_violation_template(v))

    if not recommendations:
        recommendations.append(_make_template_recommendation(
            title="Review audit findings",
            priority="MEDIUM",
            description="No specific template matched the current audit output.",
            action="Inspect the findings and apply the project’s decoupling and safety rules.",
            affected_modules=[],
            rec_type="generic",
            confidence=6,
        ))

    return recommendations
