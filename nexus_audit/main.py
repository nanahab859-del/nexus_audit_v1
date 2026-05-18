#!/usr/bin/env python3
"""
Nexus Audit Tool - Main Orchestrator
====================================
Builds the complete audit report by orchestrating all modules:
DNA discovery, violation detection, security scanning, complexity analysis,
circular dependency detection, and AI-powered recommendations.
"""

import json
import os
import glob
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Set
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from .config import (
    _load_dotenv, VAULT_PATH, DNA_PATH, INVENTORY_PATH, VISUALS_DIR, HISTORY_DIR,
    PROJECT_PATH, NEXUS_ROOT, FIRST_PARTY_APPS, SCORING_EXCLUDE_TESTS, _detect_internet
)
from .key_pool import key_pool
from .models import Violation, AllowedCommunication
from .scanners import run_bandit_enhanced, run_dead_code_scan, run_lizard_analysis
from .audit_engine import is_ghost_file, classify_connection, find_circular_dependencies_accurate
from .dependency import run_tier2_dependency_scan
from .report.html_report import EnhancedAuditReport
from .report.markdown_report import generate_comprehensive_markdown

from .ai.backend import _detect_ai_backend
from .features.fix_queue import FixQueue
from .features.timeline import load_score_history

from .ai.recommendations import run_ai_recommendations, generate_recommendations


def calculate_app_score(app_name: str, metrics_data: Dict[str, Any]) -> float:
    """Calculate overall health score for an app (0-100)."""
    base_score = 100.0
    is_core_app = app_name in ['nexus_core', 'nexus_gateway']

    violations = metrics_data.get('violations', [])
    if SCORING_EXCLUDE_TESTS:
        violations = [
            v for v in violations
            if '/tests/' not in ((v.file_path if hasattr(v, 'file_path') else v.get('file_path', '')) or '')
        ]
    base_score -= len(violations) * (3 if is_core_app else 5)

    security_findings = metrics_data.get('security_findings', [])
    if SCORING_EXCLUDE_TESTS:
        security_findings = [
            s for s in security_findings
            if '/tests/' not in ((s.file_path if hasattr(s, 'file_path') else s.get('file_path', '')) or '')
        ]
    security_penalties = {'HIGH': 12, 'MEDIUM': 6, 'LOW': 3}
    for issue in security_findings:
        severity = (getattr(issue, 'severity', None) or issue.get('severity', 'LOW')).upper()
        base_score -= security_penalties.get(severity, 3)

    avg_complexity = metrics_data.get('avg_complexity', 0)
    if avg_complexity > 10:
        base_score -= min(20, (avg_complexity - 10) * 2)

    dead_code = len(metrics_data.get('dead_code', []))
    base_score -= min(15, dead_code * 3)

    ghost_files = metrics_data.get('ghost_files', 0)
    base_score -= min(10, ghost_files * 2)

    if is_core_app:
        base_score += 10

    return max(0, min(100, base_score))


def load_previous_audit(history_dir: str) -> dict | None:
    """Load most recent audit JSON from history_dir. Returns None if none exists."""
    files = sorted(glob.glob(os.path.join(history_dir, '*.json')))
    if not files:
        return None
    try:
        with open(files[-1], 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None
def compute_change_summary(current: dict, previous: dict | None) -> dict:
    """Compare current audit with previous run. Return change summary."""
    if not previous:
        return {'first_run': True}
    cur_viols = {
        f"{v.get('type', '')}|{v.get('source', '')}|{v.get('target', '')}"
        for v in current.get('violations', [])
    }
    prev_viols = {
        f"{v.get('type', '')}|{v.get('source', '')}|{v.get('target', '')}"
        for v in previous.get('violations', [])
    }
    cur_apps = current.get('applications', {}) or current.get('app_stats', {})
    prev_apps = previous.get('applications', {}) or previous.get('app_stats', {})
    cur_scores = {a: s.get('score', 0) for a, s in cur_apps.items()}
    prev_scores = {a: s.get('score', 0) for a, s in prev_apps.items()}
    return {
        'first_run': False,
        'new_violations': len(cur_viols - prev_viols),
        'resolved': len(prev_viols - cur_viols),
        'score_deltas': {a: cur_scores.get(a, 0) - prev_scores.get(a, 0)
                        for a in cur_scores},
        'previous_timestamp': (previous.get('metadata', {}) or {}).get('timestamp', ''),
    }

def main():
    """Main orchestrator for the Nexus Audit Tool."""
    import sys
    parser = argparse.ArgumentParser(description="Nexus Audit Tool")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode: static analysis only, no AI",
    )
    args = parser.parse_args()
    if args.fast:
        from .features.quick_check import run_quick_check

        result = run_quick_check(str(NEXUS_ROOT))
        sys.exit(0 if result.get("pass") else 1)

    print("MAIN STARTED", flush=True)
    sys.stdout.flush()
    print("\n" + "="*70, flush=True)
    print("🛡️ NEXUS AUDIT COMMAND CENTER - STRICT MODULARITY EDITION", flush=True)
    print("="*70 + "\n", flush=True)

    # ── Tier detection ────────────────────────────────────────────────────
    import sys
    print("🌐 Detecting tier capabilities...", flush=True)
    sys.stdout.flush()
    try:
        online = _detect_internet()
    except Exception as e:
        print("INTERNET CHECK CRASHED:", e, flush=True)
        online = False
    print("Tier detection done", flush=True)
    tier   = 2 if online else 1
    if online:
        print("   ✔ Internet available — Tier 2 ONLINE mode activated")
        print("     + Package vulnerability scan (OSV)")
        print("     + Dependency freshness check (PyPI)")
    else:
        print("   ℹ No internet — Tier 1 OFFLINE mode (full audit, no dependency scan)")
    print()

    capabilities: Dict = {
        'tier':                  tier,
        'online':                online,
        'dna_audit':             True,
        'violation_detection':   True,
        'security_scan':         True,
        'complexity_analysis':   True,
        'ghost_file_detection':  True,
        'cycle_detection':       True,
        'trend_tracking':        True,
        'shared_util_detection': True,
        'package_vuln_scan':     online,
        'dependency_freshness':  online,
        'cve_enrichment':        online,
    }

    if not os.path.exists(DNA_PATH):
        print("❌ Error: DNA not found! Run the DNA discovery first.")
        return

    with open(DNA_PATH, 'r', encoding='utf-8') as f:
        dna = json.load(f)

    physical_files = []
    if os.path.exists(INVENTORY_PATH):
        with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
            physical_files = [line.strip() for line in f if line.strip()]

    dna_modules = set(dna.keys())
    first_party_physical = [f for f in physical_files if f.split('.')[0] in FIRST_PARTY_APPS]
    first_party_dna = {k: v for k, v in dna.items() if k.split('.')[0] in FIRST_PARTY_APPS}

    print(f"📊 First-party physical files: {len(first_party_physical)}, DNA modules: {len(first_party_dna)}\n")

    # ── Run scanners ──────────────────────────────────────────────────────
    print("   Running scanners in parallel (bandit + dead code + complexity)...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_security   = executor.submit(run_bandit_enhanced, PROJECT_PATH)
        f_dead_code  = executor.submit(run_dead_code_scan,  PROJECT_PATH)
        f_complexity = executor.submit(run_lizard_analysis, PROJECT_PATH)
    security_violations = f_security.result()
    dead_code           = f_dead_code.result()
    complexity_metrics  = f_complexity.result()
    print(f"   Scanners complete — {len(security_violations)} security findings, "
          f"{len(dead_code)} dead code items")

    # ── Tier 2: dependency scan ───────────────────────────────────────────
    dep_scan: Dict = {'packages': [], 'total_cves': 0, 'outdated_count': 0, 'critical_cves': []}
    if online:
        print("🔍 Tier 2: scanning dependencies for vulnerabilities and freshness...")
        dep_scan = run_tier2_dependency_scan(PROJECT_PATH)
        if dep_scan['total_cves']:
            print(f"   ⚠  {dep_scan['total_cves']} CVE(s) found across packages")
        if dep_scan['outdated_count']:
            print(f"   ⚠  {dep_scan['outdated_count']} package(s) are outdated")
        print()

    # ── Ghost files ───────────────────────────────────────────────────────
    ghost_files = [f for f in first_party_physical if is_ghost_file(f, dna_modules)]
    print(f"👻 Found {len(ghost_files)} ghost files\n")

    # ── Violations & allowed communications ────────────────────────────────
    violations = []
    allowed_comms = []
    app_stats = defaultdict(lambda: {
        'score': 100, 'violations': 0, 'security_issues': 0,
        'modules': [], 'physical_files': 0
    })

    counted_violation_pairs_by_app: Dict[str, Set[str]] = defaultdict(set)
    counted_allowed_pairs: Set[str] = set()

    for module, data in first_party_dna.items():
        if module == "__main__":
            continue
        app = module.split('.')[0]
        app_stats[app]['modules'].append(module)

        for imp in data.get('imports', []):
            if imp not in dna or imp == module:
                continue

            conn_type, severity, is_violation, allowed_type = classify_connection(module, imp)

            if is_violation:
                tgt_app  = imp.split('.')[0]
                pair_key = f"{app}|{tgt_app}"
                violations.append(Violation(
                    type=conn_type,
                    severity='HIGH',
                    source=module,
                    target=imp,
                    description=f"{conn_type}: {module} → {imp}",
                    recommendation="Replace with Django signal, Celery task, or REST API call."
                ))
                if pair_key not in counted_violation_pairs_by_app[app]:
                    counted_violation_pairs_by_app[app].add(pair_key)
                    app_stats[app]['violations'] += 1

            elif allowed_type:
                comm_key = f"{module}|{imp}"
                if comm_key not in counted_allowed_pairs:
                    counted_allowed_pairs.add(comm_key)
                    allowed_comms.append(AllowedCommunication(
                        type=conn_type,
                        source_app=app,
                        target_app=imp.split('.')[0],
                        details=f"{module} → {imp}"
                    ))

    for v in security_violations:
        violations.append(v)
        fp = getattr(v, 'file_path', '') or ''
        for app in FIRST_PARTY_APPS:
            if app in fp:
                app_stats[app]['security_issues'] = app_stats[app].get('security_issues', 0) + 1
                break

    for item in dead_code:
        fp = item.get('full_path', item.get('file', ''))
        for app in FIRST_PARTY_APPS:
            if app in fp:
                app_stats[app]['dead_code'] = app_stats[app].get('dead_code', 0) + 1
                break

    # ── Circular dependencies ─────────────────────────────────────────────
    cycles = find_circular_dependencies_accurate(dna)

    # ── Shared utility candidates (modules imported by 2+ apps as violations) ──
    _shared_targets: Dict[str, List] = {}
    for v in violations:
        if v.type == 'Cross-App Import':
            tgt = v.target
            src_app = v.source.split('.')[0]
            _shared_targets.setdefault(tgt, []).append(src_app)
    shared_util_candidates = {
        tgt: list(set(apps))
        for tgt, apps in _shared_targets.items()
        if len(set(apps)) >= 2
    }

    # ── Build deduplicated boundary-crossing counts per app ───────────────
    # Bug 2 fix tracked per-module boundaries; now aggregate to per-app
    # so calculate_app_score uses unique boundary crossings, not raw imports
    boundary_pair_counts: Dict[str, int] = {}  # app → unique cross-app boundaries crossed
    boundary_raw_counts: Dict[str, int] = {}   # app → raw cross-app import violations
    seen_boundaries: Set[str] = set()
    for v in violations:
        if v.type == 'Cross-App Import':
            src_app = (v.source or '').split('.')[0]
            tgt_app = (v.target or '').split('.')[0]
            boundary_raw_counts[src_app] = boundary_raw_counts.get(src_app, 0) + 1
            bkey = f"{src_app}|{tgt_app}"
            if bkey not in seen_boundaries:
                seen_boundaries.add(bkey)
                boundary_pair_counts[src_app] = boundary_pair_counts.get(src_app, 0) + 1

    # ── Build app scores ──────────────────────────────────────────────────
    for app in FIRST_PARTY_APPS:
        if app in app_stats:
            app_physical = [f for f in first_party_physical if f.startswith(app)]
            app_stats[app]['physical_files'] = len(app_physical)
            # Report raw per-app boundary violations in output (matches table/card counts)
            app_stats[app]['boundary_violations'] = boundary_raw_counts.get(app, 0)
            app_stats[app]['score'] = calculate_app_score(app, {
                # Use deduplicated app-pair boundary count for scoring penalty
                'violations': [v for v in violations
                               if v.source and v.source.startswith(app)
                              and v.type == 'Cross-App Import'][:boundary_pair_counts.get(app, 0)]
                              + [v for v in violations
                                 if v.source and v.source.startswith(app)
                                 and v.type != 'Cross-App Import'],
                'security_findings': [s for s in security_violations
                                      if s.file_path and app in s.file_path],
                'avg_complexity': complexity_metrics['average_complexity'],
                'dead_code': [d for d in dead_code if app in d.get('full_path', d.get('file', ''))],
                'ghost_files': len([g for g in ghost_files if g.startswith(app)])
            })

    # ── Trend: compare with previous run if it exists ─────────────────────
    trend: Dict[str, Any] = {}
    prev_json_path = os.path.join(VISUALS_DIR, 'audit_data_complete.json')
    if os.path.exists(prev_json_path):
        try:
            with open(prev_json_path, 'r', encoding='utf-8') as f:
                prev = json.load(f)
            prev_apps = prev.get('applications', {})
            prev_ts   = prev.get('metadata', {}).get('timestamp', '')[:19]
            for app, s in app_stats.items():
                if app in prev_apps:
                    prev_score = prev_apps[app].get('score', 0)
                    curr_score = s.get('score', 0)
                    delta      = round(curr_score - prev_score, 1)
                    trend[app] = {
                        'previous_score': prev_score,
                        'delta':          delta,
                        'direction':      '↑' if delta > 0 else '↓' if delta < 0 else '→',
                    }
            prev_cross = len([v for v in prev.get('violations', [])
                              if v.get('type') == 'Cross-App Import'])
            curr_cross = len([v for v in violations if v.type == 'Cross-App Import'])
            trend['_meta'] = {
                'previous_timestamp':    prev_ts,
                'cross_violations_prev': prev_cross,
                'cross_violations_curr': curr_cross,
                'cross_violations_delta': curr_cross - prev_cross,
            }
            print(f"   ✔ Trend data loaded from previous run ({prev_ts})")
        except Exception as exc:
            print(f"   ℹ Could not load trend data: {exc}")

    # ── Build audit data ──────────────────────────────────────────────────
    audit_data = {
        'metadata': {
            'timestamp':              datetime.now().isoformat(),
            'project_path':           PROJECT_PATH,
            'total_modules':          len(first_party_dna),
            'total_physical_files':   len(first_party_physical),
            'total_violations':       len([v for v in violations if v.type == 'Cross-App Import']),
            'total_raw_imports':      len(violations),
            'total_cycles':           len(cycles),
            'ghost_files':            ghost_files,
            'trend':                  trend,
            'capabilities':           capabilities,
        },
        'applications':              {k: v for k, v in app_stats.items() if k in FIRST_PARTY_APPS},
        'modules':                   first_party_dna,
        'violations':                [asdict(v) for v in violations],
        'security_findings':         [asdict(v) for v in security_violations],
        'allowed_communications':    [asdict(c) for c in allowed_comms],
        'circular_dependencies':     cycles,
        'metrics':                   complexity_metrics,
        'dead_code':                 dead_code,
        'recommendations':           [],   # filled below after AI run
        'dependency_scan':           dep_scan,
    }

    # ── AI recommendations (or Tier-1 template fallback) ─────────────────
    print()
    print("\U0001f916 Detecting AI backend...")
    ai_backend, ai_key = _detect_ai_backend()

    if ai_backend:
        print(f"   \u2714 Backend: {ai_backend}")
        print("\U0001f4a1 Running AI-powered recommendations...")
        cross_violations = [v for v in violations if v.type == 'Cross-App Import']
        ai_recs, ai_label = run_ai_recommendations(
            violations=cross_violations,
            app_stats=dict(app_stats),
            ghost_files=ghost_files,
            shared_util_candidates=shared_util_candidates,
            backend=ai_backend,
            api_key=ai_key,
            dep_scan=dep_scan,
        )
        if ai_recs:
            audit_data['recommendations'] = ai_recs
            audit_data['metadata']['ai_backend'] = ai_label
            print(f"   \u2714 {len(ai_recs)} AI recommendation(s) generated")
        else:
            print("   \u26a0 AI returned no recommendations (likely rate-limit/quota).")
            print("   \u2139 Falling back to smart template recommendations.")
            template_recs = generate_recommendations(
                violations=violations,
                metrics=complexity_metrics,
                cycles=cycles,
                ghost_files=ghost_files,
            )
            audit_data['recommendations'] = template_recs
            audit_data['metadata']['ai_backend'] = f"{ai_label} + templates"
            audit_data['metadata']['ai_fallback_reason'] = 'no_ai_output'
            print(f"   \u2714 {len(template_recs)} template recommendation(s) generated (fallback)")
    else:
        print("   \u2139 No AI backend — using Tier-1 template recommendations")
        all_violations = violations  # includes security violations too
        template_recs = generate_recommendations(
            violations=all_violations,
            metrics=complexity_metrics,
            cycles=cycles,
            ghost_files=ghost_files,
        )
        audit_data['recommendations'] = template_recs
        audit_data['metadata']['ai_backend'] = 'template'
        print(f"   \u2714 {len(template_recs)} template recommendation(s) generated")
    print()

    # ── Fix queue tracking ────────────────────────────────────────────────
    fix_queue_path = Path(__file__).resolve().parents[1] / 'fix_queue.json'
    queue = FixQueue(str(fix_queue_path))
    fix_queue_summary = queue.sync_recommendations(audit_data.get('recommendations', []))
    audit_data['fix_queue'] = queue.data
    audit_data['metadata']['fix_queue'] = fix_queue_summary
    if fix_queue_summary['reappeared_done_count']:
        print(
            f"   ⚠ {fix_queue_summary['reappeared_done_count']} done recommendation(s) "
            f"reappeared (regression)"
        )

    # ── Generate reports ──────────────────────────────────────────────────
    # ── Load previous audit and compute change summary ───────────────────
    prev = load_previous_audit(HISTORY_DIR)
    audit_data['change_summary'] = compute_change_summary(audit_data, prev)
    audit_data['timeline'] = load_score_history(HISTORY_DIR)
    reporter = EnhancedAuditReport(audit_data)

    json_path = os.path.join(VISUALS_DIR, 'audit_data_complete.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=2, default=str)
    print(f"   ✔ JSON data  → {json_path}")

    os.makedirs(HISTORY_DIR, exist_ok=True)
    history_path = os.path.join(
        HISTORY_DIR,
        f"audit_{audit_data['metadata']['timestamp'][:19].replace(':', '-')}.json",
    )
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=2, default=str)
    print(f"   ✔ History     → {history_path}")


    html_path = os.path.join(VISUALS_DIR, 'NEXUS_AUDIT_DASHBOARD.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(reporter.generate_html_dashboard())
    print(f"   ✔ HTML dash  → {html_path}")

    md_path = os.path.join(VISUALS_DIR, 'AUDIT_REPORT_COMPREHENSIVE.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(generate_comprehensive_markdown(audit_data))
    print(f"   ✔ Markdown   → {md_path}")

    # ── Console summary ───────────────────────────────────────────────────
    cross_count = len([v for v in violations if v.type == 'Cross-App Import'])
    avg_score   = sum(s['score'] for s in app_stats.values() if s['score']) // max(len(app_stats), 1)
    tier_label  = f"Tier {capabilities['tier']} — {'ONLINE' if capabilities['online'] else 'OFFLINE'}"

    BOX_WIDTH   = 60
    LABEL_WIDTH = 25
    VALUE_WIDTH = BOX_WIDTH - LABEL_WIDTH - 2

    def box_line(label: str, value: str) -> str:
        label_part = f"{label:<{LABEL_WIDTH}}"
        value_part = f"{value:<{VALUE_WIDTH}}"
        content = f"{label_part}: {value_part}"
        return f" ║{content}║"

    print()
    print(" ╔════════════════════════════════════════════════════════════╗")
    print(f" ║     NEXUS AUDIT COMPLETE — {tier_label:<32}║")
    print(" ╠════════════════════════════════════════════════════════════╣")
    print(box_line("Apps audited",         str(len(app_stats))))
    print(box_line("Modules scanned",      str(len(first_party_dna))))
    print(box_line("Cross-app violations", str(cross_count)))
    print(box_line("Allowed comms",        str(len(allowed_comms))))
    print(box_line("Security findings",    str(len(security_violations))))
    print(box_line("Ghost files",          str(len(ghost_files))))
    print(box_line("Cycles detected",      str(len(cycles))))
    print(box_line("Fleet avg score",      f"{avg_score}%"))
    if capabilities.get('online'):
        print(" ╠════════════════════════════════════════════════════════════╣")
        print(box_line("[T2] CVEs found",      str(dep_scan.get('total_cves', 0))))
        print(box_line("[T2] Outdated pkgs",   str(dep_scan.get('outdated_count', 0))))
    print(" ╠════════════════════════════════════════════════════════════╣")

    for app, s in sorted(app_stats.items()):
        sc    = int(s.get('score', 0))
        tr    = trend.get(app, {})
        arrow = tr.get('direction', ' ')
        delt  = tr.get('delta', None)
        dstr  = f"{arrow}{abs(delt):.1f}" if delt is not None and delt != 0 else ""
        APP_COL = 22; BAR_COL = 12; SCORE_COL = 4; TREND_COL = 19
        line_content = f"{app:<{APP_COL}} {'█'*(sc//10)+'░'*(10-sc//10)} {sc:>{SCORE_COL-1}}% {dstr:<{TREND_COL}}"
        print(f" ║{line_content}  ║")

    print(" ╚════════════════════════════════════════════════════════════╝")

    if cross_count:
        print(f"\n⚠️  {cross_count} cross-app violation(s) — see Violations tab.")
    if cycles:
        print(f"⚠️  {len(cycles)} circular dependency cycle(s) — see Cycles tab.")
    if ghost_files:
        print(f"⚠️  {len(ghost_files)} ghost file(s) — see Ghost Files tab.")

    print()


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
