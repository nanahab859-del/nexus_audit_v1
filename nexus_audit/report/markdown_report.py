#!/usr/bin/env python3
"""
Markdown Report Generator
=========================
Generates the comprehensive standalone Markdown audit report.
"""

from typing import Dict, Any, List

def generate_comprehensive_markdown(audit_data: Dict) -> str:
    """
    Generates a fully self-contained Markdown report.
    Every section is complete — a reader can understand the full project
    state from this file alone, without opening the HTML or JSON.
    """
    meta      = audit_data.get('metadata', {})
    apps      = audit_data.get('applications', {})
    modules   = audit_data.get('modules', {})
    violations= audit_data.get('violations', [])
    security  = audit_data.get('security_findings', [])
    metrics   = audit_data.get('metrics', {})
    cycles    = audit_data.get('circular_dependencies', [])
    recs      = audit_data.get('recommendations', [])
    ghost     = meta.get('ghost_files', [])
    allowed   = audit_data.get('allowed_communications', [])
    dead_code = audit_data.get('dead_code', [])

    ts = meta.get('timestamp', '')[:19].replace('T', ' ')

    def grade(s: float) -> str:
        return 'A' if s >= 90 else 'B' if s >= 80 else 'C' if s >= 70 else 'D' if s >= 60 else 'F'

    def emoji_score(s: float) -> str:
        return '💚' if s >= 80 else '💛' if s >= 60 else '❤️'

    lines: list = []
    a = lines.append

    # ── Title & metadata ─────────────────────────────────────────────────
    a("# 🛡️ NEXUS MASTER AUDIT REPORT")
    a("")
    capabilities = meta.get('capabilities', {})
    tier  = capabilities.get('tier', 1)
    online= capabilities.get('online', False)
    a(f"**Generated:** {ts}  ")
    a(f"**Project:** `{meta.get('project_path', 'N/A')}`  ")
    a(f"**Tier:** {'🌐 Tier 2 — ONLINE (Enhanced Mode)' if online else '📴 Tier 1 — OFFLINE (Standard Mode)'}  ")
    a(f"**Total modules:** {meta.get('total_modules', 0)}  ")
    a(f"**Physical files:** {meta.get('total_physical_files', 0)}  ")
    a(f"**Policy:** Strict modularity — cross-app imports are violations. "
      f"Signals, tasks, and receivers are allowed communications.")
    a("")

    # Capability manifest
    a("## ⚙️ CAPABILITY MANIFEST")
    a("")
    a("| Capability | Status |")
    a("| :--- | :--- |")
    cap_icons = {True: '✅ Active', False: '⭕ Offline only'}
    for cap, active in capabilities.items():
        if cap in ('tier', 'online'): continue
        label = cap.replace('_', ' ').title()
        a(f"| {label} | {cap_icons.get(active, str(active))} |")
    a("")

    # ── Executive summary ─────────────────────────────────────────────────
    overall = sum(a_.get('score', 0) for a_ in apps.values()) / max(len(apps), 1)
    cross_v = [v for v in violations if v.get('type') == 'Cross-App Import']
    trend   = meta.get('trend', {})
    trend_meta = trend.get('_meta', {})

    a("## 📊 Executive Summary")
    a("")
    a(f"| Metric | Value |")
    a(f"| :--- | :--- |")
    a(f"| Overall fleet health | {emoji_score(overall)} **{overall:.1f}%** (Grade {grade(overall)}) |")
    a(f"| Apps audited | {len(apps)} |")
    a(f"| Cross-app violations | {len(cross_v)} |")
    if trend_meta:
        prev_ts    = trend_meta.get('previous_timestamp', '')
        cross_prev = trend_meta.get('cross_violations_prev', '?')
        cross_delt = trend_meta.get('cross_violations_delta', 0)
        ddir       = '↑ worse' if cross_delt > 0 else '↓ improved' if cross_delt < 0 else '→ unchanged'
        a(f"| Violations vs last run | {ddir} ({cross_delt:+d}) — prev: {cross_prev} on {prev_ts[:10]} |")
    a(f"| Allowed communications | {len(allowed)} |")
    a(f"| Security findings | {len(security)} |")
    a(f"| Ghost files | {len(ghost)} |")
    a(f"| Circular dependency cycles | {len(cycles)} |")
    a(f"| Avg cyclomatic complexity | {metrics.get('average_complexity', 0):.2f} |")
    a(f"| Max cyclomatic complexity | {metrics.get('max_complexity', 0)} |")
    a(f"| Maintainability index | {(metrics.get('maintainability_index') or 0):.1f} |")
    a("")

    # ── Cycles (critical — show first) ───────────────────────────────────
    if cycles:
        a("## 🔄 CRITICAL: CIRCULAR DEPENDENCIES")
        a("")
        a("Circular dependencies prevent clean testing and deployment isolation.")
        a("")
        for c in cycles:
            nodes_str = " → ".join(c.get('nodes', []))
            sev       = c.get('severity', '?').upper()
            scope     = "CROSS-APP" if c.get('cross_app') else "INTRA-APP"
            apps_inv  = ", ".join(c.get('apps', []))
            a(f"- **[{sev} / {scope}]** `{nodes_str}`  ")
            a(f"  Apps involved: {apps_inv}")
        a("")

    # ── Ghost files ───────────────────────────────────────────────────────
    if ghost:
        a("## 👻 CRITICAL: GHOST FILES")
        a("")
        a("These files exist on disk but were not scanned by pydeps. "
          "They may be dead code or unreachable entry points.")
        a("")
        for g in sorted(ghost):
            a(f"- `{g}`")
        a("")

    # ── Fleet health table ────────────────────────────────────────────────
    a("## 🖤 APPLICATION FLEET HEALTH")
    a("")
    has_trend = bool(trend and any(k != '_meta' for k in trend))
    if has_trend:
        a("| App | Score | Grade | Trend | Physical | Audited | Boundary Violations | Security | Ghosts |")
        a("| :--- | ---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: |")
    else:
        a("| App | Score | Grade | Physical | Audited | Boundary Violations | Security | Ghosts |")
        a("| :--- | ---: | :---: | ---: | ---: | ---: | ---: | ---: |")
    for app_name, s in sorted(apps.items()):
        sc    = round(s.get('score', 0))
        phys  = s.get('physical_files', len(s.get('physical', [])))
        mods  = len(s.get('modules', []))
        bviol = s.get('boundary_violations', s.get('violations', 0))
        sec   = s.get('security_issues', 0)
        ghosts= sum(1 for g in ghost if g.startswith(app_name))
        tr    = trend.get(app_name, {})
        if has_trend:
            delt = tr.get('delta', None)
            dstr = f"{tr.get('direction','')}{abs(delt):.1f}%" if delt is not None and delt != 0 else "→"
            a(f"| **{app_name.upper()}** | {emoji_score(sc)} {sc}% | {grade(sc)} "
              f"| {dstr} "
              f"| {phys} | {mods} | {bviol} | {sec} | {ghosts} |")
        else:
            a(f"| **{app_name.upper()}** | {emoji_score(sc)} {sc}% | {grade(sc)} "
              f"| {phys} | {mods} | {bviol} | {sec} | {ghosts} |")
    a("")

    # ── Test coverage debt ────────────────────────────────────────────────
    test_cross = [v for v in violations if v.get('type') == 'Test Cross-App Import']
    if test_cross:
        a("## 🧪 TEST COVERAGE DEBT")
        a("")
        a(f"These {len(test_cross)} cross-app import(s) appear in test files only. "
          "They do not affect health scores but indicate tests are coupling to "
          "live app internals. Use mocks or factories instead.")
        a("")
        a("| Test File | Imports From |")
        a("| :--- | :--- |")
        for v in test_cross:
            a(f"| `{v.get('source','')}` | `{v.get('target','')}` |")
        a("")

    # ── Violations ────────────────────────────────────────────────────────
    a("## 🚨 VIOLATIONS")
    a("")
    if not cross_v:
        a("✅ No cross-app import violations detected.")
    else:
        a(f"### Cross-App Imports ({len(cross_v)} violations)")
        a("")
        a("Direct imports between first-party apps violate strict modularity. "
          "Replace with Django signals, Celery tasks, or REST API calls.")
        a("")
        a("| Source Module | Target Module | Recommendation |")
        a("| :--- | :--- | :--- |")
        for v in cross_v:
            a(f"| `{v.get('source','')}` | `{v.get('target','')}` "
              f"| {v.get('recommendation', 'Replace with signal/task/API')} |")
        a("")
    other_v = [v for v in violations if v.get('type') != 'Cross-App Import']
    if other_v:
        a(f"### Other Violations ({len(other_v)})")
        a("")
        a("| Type | Source | Severity |")
        a("| :--- | :--- | :--- |")
        for v in other_v:
            a(f"| {v.get('type','')} | `{v.get('source','')}` | {v.get('severity','')} |")
        a("")

    # ── Allowed communications ────────────────────────────────────────────
    a("## 🔗 ALLOWED CROSS-APP COMMUNICATIONS")
    a("")
    if not allowed:
        a("No allowed communications recorded. "
          "Re-run the audit with the fixed signal-detection tool to see signals and tasks here.")
    else:
        a("These cross-app interactions use decoupled communication patterns and are permitted.")
        a("")
        a("| Type | Source App | Target App | Details |")
        a("| :--- | :--- | :--- | :--- |")
        for c in allowed:
            a(f"| {c.get('type','')} | {c.get('source_app','')} "
              f"| {c.get('target_app','')} | `{c.get('details','')}` |")
    a("")

    # ── Dependency health (Tier 2 only) ──────────────────────────────────
    dep_scan = audit_data.get('dependency_scan', {})
    dep_pkgs = dep_scan.get('packages', [])
    if dep_pkgs:
        a("## 📦 DEPENDENCY HEALTH (Tier 2 — Online Scan)")
        a("")
        a(f"Scanned {len(dep_pkgs)} packages for CVEs (OSV database) and version freshness (PyPI).  ")
        a(f"Total CVEs found: **{dep_scan.get('total_cves', 0)}** | "
          f"Outdated packages: **{dep_scan.get('outdated_count', 0)}**")
        a("")
        crit = dep_scan.get('critical_cves', [])
        if crit:
            a("### ⚠️ Critical CVEs")
            a("")
            a("| Package | CVE ID | Summary |")
            a("| :--- | :--- | :--- |")
            for c in crit:
                a(f"| `{c.get('package','')}` | `{c.get('id','')}` | {c.get('summary','')[:100]} |")
            a("")
        a("### Package Summary")
        a("")
        a("| Package | Installed | Latest | Status | CVEs |")
        a("| :--- | :--- | :--- | :--- | :--- |")
        for p in dep_pkgs:
            status = '⚠️ Outdated' if p.get('outdated') else '✅ Current'
            inst   = p.get('installed', 'unknown')
            if inst == 'unknown': status = '— Not installed'
            a(f"| `{p['name']}` | {inst} | {p.get('latest','?')} | {status} | {p.get('cve_count',0)} |")
        a("")
    elif capabilities.get('online') is False:
        a("## 📦 DEPENDENCY HEALTH (Tier 2 — Not Available)")
        a("")
        a("This was a Tier 1 offline run. Re-run with internet access to enable "
          "the OSV vulnerability scan and PyPI freshness check.")
        a("")

    # ── Security ──────────────────────────────────────────────────────────
    a("## 🔒 SECURITY FINDINGS")
    a("")
    if not security:
        a("✅ No security issues detected.")
    else:
        a(f"Bandit scan found {len(security)} issue(s). "
          f"Test-file findings are excluded from health scoring.")
        a("")
        a("| Severity | File | Line | Issue |")
        a("| :---: | :--- | ---: | :--- |")
        for s in security:
            sev  = s.get('severity', 'LOW').upper()
            file = (s.get('file_path') or s.get('source') or '').split('/')[-1]
            desc = (s.get('description') or '')[:100]
            a(f"| **{sev}** | `{file}` | {s.get('line','')} | {desc} |")
    a("")

    # ── Complexity ────────────────────────────────────────────────────────
    a("## 📊 COMPLEXITY METRICS")
    a("")
    a(f"| Metric | Value |")
    a(f"| :--- | ---: |")
    a(f"| Average cyclomatic complexity | {metrics.get('average_complexity',0):.2f} |")
    a(f"| Maximum cyclomatic complexity | {metrics.get('max_complexity',0)} |")
    a(f"| Maintainability index | {(metrics.get('maintainability_index') or 0):.1f} |")
    a(f"| Functions analysed | {metrics.get('functions_analyzed',0)} |")
    a("")
    hcf = sorted(metrics.get('high_complexity_functions', []),
                 key=lambda x: x.get('complexity', 0), reverse=True)
    if hcf:
        a(f"### High Complexity Functions (>{10})")
        a("")
        a("| Function | File | Complexity | Lines |")
        a("| :--- | :--- | ---: | ---: |")
        for f in hcf:
            a(f"| `{f.get('function','')}` | `{f.get('file','')}` "
              f"| {f.get('complexity',0)} | {f.get('lines','')} |")
        a("")
    else:
        a("✅ No functions exceed the complexity threshold of 10.")
        a("")

    # ── Dead code ─────────────────────────────────────────────────────────
    if dead_code:
        a("## 💀 DEAD CODE")
        a("")
        a(f"Vulture identified {len(dead_code)} potentially unused code item(s).")
        a("")
        a("| Type | Name | File | Line | Confidence |")
        a("| :--- | :--- | :--- | ---: | ---: |")
        for d in dead_code[:50]:
            a(f"| {d.get('type','')} | `{d.get('name','')}` "
              f"| `{d.get('file','')}` | {d.get('line','')} | {d.get('confidence','')}% |")
        if len(dead_code) > 50:
            a(f"\n*…and {len(dead_code)-50} more. See `audit_data_complete.json` for full list.*")
        a("")

    # ── Recommendations ───────────────────────────────────────────────────
    a("## 💡 RECOMMENDATIONS")
    a("")
    if not recs:
        a("✅ No recommendations generated.")
    else:
        for r in recs:
            pri = r.get('priority', 'LOW')
            a(f"### [{pri}] {r.get('title','')}")
            a("")
            a(r.get('description', ''))
            a("")
            a(f"**Action:** {r.get('action', '')}")
            affected = r.get('affected_modules', [])
            if affected:
                a("")
                a(f"**Affected modules:** {', '.join(f'`{m}`' for m in affected)}")
            a("")

    # ── Full module manifest ──────────────────────────────────────────────
    a("## 📋 FULL MODULE MANIFEST")
    a("")
    # Group by app
    by_app: dict = {}
    for mod_name, mod_data in sorted(modules.items()):
        app = mod_name.split('.')[0]
        by_app.setdefault(app, []).append((mod_name, mod_data))

    for app_name, mods in sorted(by_app.items()):
        a(f"### {app_name.upper()} ({len(mods)} modules)")
        a("")
        a("| Module | Depth | Imports | Imported By |")
        a("| :--- | ---: | ---: | ---: |")
        for mod_name, mod_data in sorted(mods):
            depth = mod_data.get('bacon', mod_data.get('bacon_depth', 0))
            imp_c = len(mod_data.get('imports', []))
            iby_c = len(mod_data.get('imported_by', []))
            a(f"| `{mod_name}` | {depth} | {imp_c} | {iby_c} |")
        a("")

    a("---")
    a(f"*Report generated by Nexus Audit Command Center — {ts}*")

    return "\n".join(lines)