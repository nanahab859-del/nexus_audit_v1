# NEXUS AUDIT TOOL — HANDOVER v3
**Date:** 2026-05-25
**Status:** Production-ready. Phases 1–5 complete. Config Health tab added.

---

## What This Tool Is

A self-contained Django modularity auditor for the Nexus gaming platform (7 apps).
Runs as `pulse` in the terminal. Produces a standalone HTML dashboard, JSON data file, and Markdown report.

---

## Key Paths

| Item | Path |
|------|------|
| Tool root | ~/my_tools/nexus_audit/ |
| Package | ~/my_tools/nexus_audit/nexus_audit/ |
| Entry point | ~/my_tools/nexus_audit/pulse.py |
| Shell alias target | ~/my_tools/nexus_audit/pulse.sh |
| .env (API keys) | ~/my_tools/nexus_audit/.env |
| HTML output | ~/my_tools/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html |
| JSON output | ~/my_tools/nexus_audit/visuals/audit_data_complete.json |
| Audit history | ~/my_tools/nexus_audit/visuals/audit_history/ |
| Fix queue state | ~/my_tools/nexus_audit/fix_queue.json |
| Graph library | ~/my_tools/nexus_audit/vis-network.min.js |
| Docs | ~/my_tools/nexus_audit/docs/ |
| Backup | ~/my_tools/nexus_audit_backup_phase3/ |
| Live Nexus source | ~/nexus-gaming/ |
| Synced audit copy | ~/my_tools/nexus_project_copy/ |
| Python env | ~/my_tools/miniconda3/envs/audit_env/ |

---

## How to Run

```
pulse                  - full audit with AI recommendations
pulse --serve          - full audit then serve at http://localhost:8421
pulse --serve --watch  - same but re-runs on file changes
pulse --fast           - static analysis only, no AI
pulse --install-hook   - install as git pre-commit hook
```

pulse alias in ~/.bashrc points to pulse.sh which ends with:
  python3 "$AUDIT_DIR/pulse.py" "$@"
The $@ is critical — without it --serve and --fast are silently ignored.

---

## Package Structure

```
nexus_audit/nexus_audit/
  config.py              - constants, _load_dotenv(), VISUALS_DIR, HISTORY_DIR
  key_pool.py            - KeyPool class, multi-key Gemini management
  models.py              - dataclasses: Violation, AppHealth, ModuleMetrics
  audit_engine.py        - classify_connection(), calculate_app_score(), BOOTSTRAP_LEAVES
  scanners.py            - bandit, dead code, lizard, vulture
  dependency.py          - PyPI freshness + OSV CVE scan (parallel ThreadPoolExecutor x10)
  config_health.py       - scans nexus-gaming config folder (settings.py, urls.py etc.)
  main.py                - orchestrator, CLI args, --serve/--fast routing
  ai/
    backend.py           - _ai_complete(), _detect_ai_backend(), KeyPool 429 handling
    prompts.py           - all AI prompt functions returning (system, user) tuples
    recommendations.py   - run_ai_recommendations(), parallel ThreadPoolExecutor x4
  report/
    html_report.py       - EnhancedAuditReport using string.Template
    dashboard_template.html  - HTML template with ${VAR} substitution
    markdown_report.py
    assets.py            - get_vis_js() loads vis-network.min.js from disk
  features/
    fix_queue.py         - mark recs Done/Snoozed/In Progress
    timeline.py          - load_score_history() for Trends tab
    quick_check.py       - --fast mode using git diff
    server.py            - --serve mode ThreadingHTTPServer on port 8421
    coupling_map.py      - 7x7 cross-app coupling heatmap
```

---

## Dashboard Tabs (all working)

- App score cards (7 apps) + Config Health banner above them
- Violations, Security, Dependencies, Recommendations
- Graph (lazy-loaded, three modes: Normal / Separate Apps / Inspect Edges)
- Trends (score history), Coupling Map, Manifest, Ghost Files, Cycles

---

## Critical Rules

### dashboard_template.html
- Plain HTML with ${VAR} substitution — NO f-string escaping needed
- html_report.py uses string.Template to inject data
- _safe_json() escapes <, >, &, and backticks (\u0060)
  Backticks in AI text break JS template literals without this escape

### BOOTSTRAP_LEAVES — two copies, always in sync
- Python: audit_engine.py module-level frozenset (includes 'admin')
- JS: APP_SCHEME block in dashboard_template.html

### KeyPool singleton
- Only key_pool.py instantiates KeyPool()
- All others: from nexus_audit.key_pool import key_pool
- .env: GEMINI_API_KEY=... plus GEMINI_API_KEY_2=... up to _20

### visNodes / visEdges / network scope — CRITICAL
- Declared as `let` at module level in dashboard_template.html
- Assigned inside initGraph() WITHOUT const
- If const is added back they shadow the module-level vars
- Legend, sidebar, SVG overlay all break because they read the null module-level vars

### Graph overlay (SVG bundle lines in Inspect mode)
- Inter-island edges hidden from vis-network (intraIslandEdges filter)
- Drawn as SVG by buildBundleOverlay()
- _destroyOverlay removes event listeners on mode change (prevents stacking)
- injectConfigNode() placed AFTER APP_SCHEME definition — putting it before crashed the graph

### pycache
- Clear before testing: find ~/my_tools/nexus_audit -name "*.pyc" -delete
- Stale bytecode caused many silent failures where fixes appeared to not work

---

## Scoring System

Score = clamp(0, 100, 100 - V - S - C - D - G + B)

V = violations penalty  (-5 per violation, -3 for nexus_core/nexus_gateway)
S = security penalty    (-12 HIGH, -6 MEDIUM, -3 LOW) — test files excluded
C = per-app complexity penalty (max -20)
D = dead code penalty (max -15)
G = ghost file penalty (max -10)
B = core app bonus (+10 for nexus_core, nexus_gateway)

Current scores (2026-05-23):
  nexus_content 92%, nexus_core 63%, nexus_economy 92%, nexus_gaming 94%
  nexus_gateway 95%, nexus_social 57%, nexus_tournaments 66%
  Fleet average: 80%

---

## Open Items

1. Config Health Phase 2: make findings clickable, add AI explanations, add config node edges to graph
2. Dependency upgrades without AI: derive pip install commands from PyPI data directly in dependency.py
3. my_tools/ root has loose markdown notes — can move to my_tools/doc/ if desired
4. check_js.js in nexus_audit root is a debug artifact — safe to delete

---

## Agent Skills

~/my_tools/.github/
  agents/nexus-audit-agent.agent.md     - agent rules and environment facts
  skills/nexus-audit-graph-modes/       - graph mode implementation
  skills/nexus-audit-graph-node-spacing/- node spacing fix
  skills/nexus-audit-graph-mode-fixes/  - overlay and scope fixes
  skills/nexus-audit-html-rewrite/      - string.Template rewrite

---

## Quick Health Check

```bash
cd ~/my_tools/nexus_audit
find . -name "*.pyc" -delete 2>/dev/null
python3 -c "
import sys; sys.path.insert(0, '.')
from nexus_audit.main import main
from nexus_audit.report.html_report import EnhancedAuditReport
from nexus_audit.features.server import serve
from nexus_audit.config_health import run_config_health_scan
print('All imports OK')
"
```

---

*Handover generated: 2026-05-25*
