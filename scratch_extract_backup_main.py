def build_audit_fortress_enhanced():
    print("\n" + "="*70)
    print("🛡️ NEXUS AUDIT COMMAND CENTER - STRICT MODULARITY EDITION")
    print("="*70 + "\n")

    # ── Tier detection ────────────────────────────────────────────────────
    print("🌐 Detecting tier capabilities...")
    online = _detect_internet()
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
        print("❌ Error: DNA not found! Run pulse.sh first.")
        return
    
    with open(DNA_PATH, 'r', encoding='utf-8') as f:
        dna = json.load(f)
    
    physical_files = []
    if os.path.exists(INVENTORY_PATH):
        with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
            physical_files = [line.strip() for line in f if line.strip()]
    
    dna_modules = set(dna.keys())
    first_party_physical = [f for f in physical_files if is_first_party(f)]
    first_party_dna = {k: v for k, v in dna.items() if is_first_party(k)}
    
    print(f"📊 First-party physical files: {len(first_party_physical)}, DNA modules: {len(first_party_dna)}\n")
    
    security_violations = run_bandit_enhanced(PROJECT_PATH)
    dead_code = run_dead_code_scan(PROJECT_PATH)
    complexity_metrics = run_lizard_analysis(PROJECT_PATH)

    # ── Tier 2: dependency scan (runs in parallel-ish — non-blocking) ─────
    dep_scan: Dict = {'packages': [], 'total_cves': 0, 'outdated_count': 0, 'critical_cves': []}
    if online:
        print("🔍 Tier 2: scanning dependencies for vulnerabilities and freshness...")
        dep_scan = run_tier2_dependency_scan(PROJECT_PATH)
        if dep_scan['total_cves']:
            print(f"   ⚠  {dep_scan['total_cves']} CVE(s) found across {len(TIER2_PACKAGES)} packages")
        if dep_scan['outdated_count']:
            print(f"   ⚠  {dep_scan['outdated_count']} package(s) are outdated")
        if not dep_scan['total_cves'] and not dep_scan['outdated_count']:
            print(f"   ✔ All {len(TIER2_PACKAGES)} packages are up-to-date and CVE-free")
        print()
    
    ghost_files = [f for f in first_party_physical if is_ghost_file(f, dna_modules)]
    print(f"👻 Found {len(ghost_files)} ghost files")
    
    violations = []
    allowed_comms = []
    app_stats = defaultdict(lambda: {'score': 100, 'violations': 0, 'security_issues': 0, 'modules': [], 'physical_files': 0})

    for module, data in first_party_dna.items():
        if module == "__main__":
            continue
        app = module.split('.')[0]
        app_stats[app]['modules'].append(module)

        # ── Bug 2 fix: deduplicated boundary counting ──────────────────────
        counted_violation_pairs: Set[str] = set()
        counted_allowed_pairs:   Set[str] = set()
        # Track which cross-app modules are imported from multiple apps
        # Used later to detect shared-utility candidates (Phase 5)

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
                if pair_key not in counted_violation_pairs:
                    counted_violation_pairs.add(pair_key)
                    app_stats[app]['violations'] += 1

            elif allowed_type == 'test_cross_app':
                # Test cross-app imports: log separately, never score
                comm_key = f"{module}|{imp}"
                if comm_key not in counted_allowed_pairs:
                    counted_allowed_pairs.add(comm_key)
                    allowed_comms.append(AllowedCommunication(
                        type="Test Cross-App Import",
                        source_app=app,
                        target_app=imp.split('.')[0],
                        details=f"{module} → {imp}"
                    ))

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
        # ── Assign security issues to app_stats (was a stub comment before) ──
        fp = getattr(v, 'file_path', '') or ''
        for app in FIRST_PARTY_APPS:
            if app in fp:
                app_stats[app]['security_issues'] = app_stats[app].get('security_issues', 0) + 1
                break

    # ── Dead code count per app ───────────────────────────────────────────
    for item in dead_code:
        fp = item.get('full_path', item.get('file', ''))
        for app in FIRST_PARTY_APPS:
            if app in fp:
                app_stats[app]['dead_code'] = app_stats[app].get('dead_code', 0) + 1
                break

    # ── Build deduplicated boundary-crossing counts per app ───────────────
    # Bug 2 fix tracked per-module boundaries; now aggregate to per-app
    # so calculate_app_score uses unique boundary crossings, not raw imports
    boundary_counts: Dict[str, int] = {}   # app → unique cross-app boundaries crossed
    seen_boundaries: Set[str] = set()
    for v in violations:
        if v.type == 'Cross-App Import':
            src_app = (v.source or '').split('.')[0]
            tgt_app = (v.target or '').split('.')[0]
            bkey = f"{src_app}|{tgt_app}"
            if bkey not in seen_boundaries:
                seen_boundaries.add(bkey)
                boundary_counts[src_app] = boundary_counts.get(src_app, 0) + 1

    for app in FIRST_PARTY_APPS:
        if app in app_stats:
            app_physical = [f for f in first_party_physical if f.startswith(app)]
            app_stats[app]['physical_files'] = len(app_physical)
            # Pass boundary_count (deduplicated) separately for accurate scoring
            app_stats[app]['boundary_violations'] = boundary_counts.get(app, 0)
            app_stats[app]['score'] = calculate_app_score(app, {
                # Use boundary count for the cross-app penalty (not raw import count)
                'violations': [v for v in violations
                               if v.source and v.source.startswith(app)
                               and v.type == 'Cross-App Import'][:boundary_counts.get(app, 0)]
                              + [v for v in violations
                                 if v.source and v.source.startswith(app)
                                 and v.type != 'Cross-App Import'],
                'security_findings': [s for s in security_violations
                                      if s.file_path and app in s.file_path],
                'avg_complexity': complexity_metrics['average_complexity'],
                'dead_code': [d for d in dead_code
                              if app in d.get('full_path', d.get('file', ''))],
                'ghost_files': len([g for g in ghost_files if g.startswith(app)])
            })

    cycles = find_circular_dependencies_accurate(dna)

    # ── Shared-utility candidate detection ───────────────────────────────
    # If a module is imported as a VIOLATION from 2+ different apps, it is
    # a shared concern that belongs in nexus_core (or a dedicated nexus_shared).
    shared_util_candidates: Dict[str, List[str]] = {}
    for v in violations:
        if v.type != 'Cross-App Import':
            continue
        tgt = v.target
        src_app = v.source.split('.')[0]
        if tgt not in shared_util_candidates:
            shared_util_candidates[tgt] = []
        if src_app not in shared_util_candidates[tgt]:
            shared_util_candidates[tgt].append(src_app)
    # Only flag if 2+ distinct apps import it
    real_candidates = {
        tgt: apps_importing
        for tgt, apps_importing in shared_util_candidates.items()
        if len(apps_importing) >= 2
    }
    if real_candidates:
        print(f"   ℹ  {len(real_candidates)} shared-utility candidate(s) detected:")
        for mod, importers in real_candidates.items():
            print(f"      {mod} ← imported by: {', '.join(importers)}")
            print(f"      → Consider moving to nexus_core or a nexus_shared package")

    recommendations = generate_recommendations(violations, complexity_metrics, cycles, ghost_files)

    # Add shared-utility recommendation if candidates found
    if real_candidates:
        cand_list = [
            f"`{tgt}` (used by {', '.join(apps)})"
            for tgt, apps in real_candidates.items()
        ]
        recommendations.append({
            'title':           'Move Shared Utilities to nexus_core',
            'priority':        'HIGH',
            'description':     (
                f"{len(real_candidates)} module(s) are imported by 2 or more apps as violations. "
                f"This means they are shared utilities living in the wrong app: "
                f"{'; '.join(cand_list)}."
            ),
            'action':          (
                "Move these modules to nexus_core (or create a nexus_shared package). "
                "Update all imports. The violation count will drop to zero for these "
                "once the module lives in the right place."
            ),
            'affected_modules': list(real_candidates.keys()),
        })

    # ── AI-powered recommendations: probe backend priority chain ─────────
    ai_backend, ai_key = _detect_ai_backend()
    if ai_backend:
        backend_label = {
            "ollama": "Ollama (local LLM)",
            "gemini": "Google Gemini",
            "claude": "Claude (Anthropic)",
        }.get(ai_backend, ai_backend)
        print(f"🤖 AI backend detected: {backend_label}")
        print("   Generating specific recommendations...")
        ai_recs, rec_label = run_ai_recommendations(
            violations             = violations,
            app_stats              = app_stats,
            ghost_files            = ghost_files,
            shared_util_candidates = real_candidates,
            backend                = ai_backend,
            api_key                = ai_key,
            dep_scan               = dep_scan,
        )
        if ai_recs:
            # AI recs first — they are specific and authoritative
            # Keep any T1 rec whose title doesn't overlap with an AI rec
            recommendations = ai_recs + [
                r for r in recommendations
                if not any(r.get('title','') == a.get('title','') for a in ai_recs)
            ]
            print(f"   ✔ {len(ai_recs)} AI recommendation(s) via {rec_label}")
            capabilities['ai_recommendations'] = True
            capabilities['ai_backend']         = rec_label
        else:
            print(f"   ℹ {backend_label} reachable but returned no recommendations — using smart templates")
            capabilities['ai_recommendations'] = False
    else:
        print("ℹ No AI backend available — smart template recommendations in use")
        print("  To enable AI recommendations, do ONE of:")
        print("  • Install Ollama: https://ollama.com  →  ollama run llama3")
        print("  • export GEMINI_API_KEY='...'  (free at aistudio.google.com)")
        print("  • export ANTHROPIC_API_KEY='...'  (paid at console.anthropic.com)")
        capabilities['ai_recommendations'] = False
        capabilities['ai_backend']         = None

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

    audit_data = {
        'metadata': {
            'timestamp':              datetime.now().isoformat(),
            'project_path':           PROJECT_PATH,
            'total_modules':          len(first_party_dna),
            'total_physical_files':   len(first_party_physical),
            'total_violations':       len([v for v in violations if v.type == 'Cross-App Import']),
            'total_raw_imports':      len([v for v in violations]),
            'total_cycles':           len(cycles),
            'ghost_files':            ghost_files,
            'trend':                  trend,
            'capabilities':           capabilities,
        },
        'applications':         {k: v for k, v in app_stats.items() if k in FIRST_PARTY_APPS},
        'modules':              first_party_dna,
        'violations':           [asdict(v) for v in violations],
        'security_findings':    [asdict(v) for v in security_violations],
        'allowed_communications':[asdict(c) for c in allowed_comms],
        'circular_dependencies': cycles,
        'metrics':              complexity_metrics,
        'dead_code':            dead_code,
        'recommendations':      recommendations,
        'dependency_scan':      dep_scan,
    }

    reporter = EnhancedAuditReport(audit_data)

    json_path = os.path.join(VISUALS_DIR, 'audit_data_complete.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(audit_data, f, indent=2, default=str)
    print(f"   ✔ JSON data  → {json_path}")

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