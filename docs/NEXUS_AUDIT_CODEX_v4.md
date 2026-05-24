# NEXUS AUDIT CODEX v4

## 1. Package Structure
The tool is now a proper Python package (`nexus_audit/`) with a multi-module layout:
- `__main__.py` / `pulse.py` - Entry points for running the tool.
- `main.py` - Core CLI orchestration, arg parsing, and high-level execution flow.
- `config.py` - Configuration, environment variables, path resolutions, and constants.
- `audit_engine.py` - The core engine that walks the project, runs scanners, and aggregates results.
- `scanners.py` - Wrappers for Vulture, Radon, Bandit, and internal checks.
- `dependency.py` - Requirement parsing, vulnerability scanning, and outdated package checks.
- `models.py` - Data models (e.g., `Violation`, `AppStats`, `FeatureContext`).
- `key_pool.py` - Intelligent API key management (RPM and daily quota aware) across models.
- `ai/` - AI backend components:
  - `backend.py` - Core LLM caller handling Ollama, Gemini, Claude, and rate limit fallback logic.
  - `recommendations.py` - Multi-layered AI recommendation orchestrator.
  - `prompts.py` - Centralized prompt templates.
- `features/` - Advanced decoupled features:
  - `timeline.py` - Historical trend tracking (`master_nexus_dna.json`).
  - `coupling_map.py` - Generates dependency maps for cross-app relationships.
  - `fix_queue.py` - Persistent, user-manageable queue for fixes (`fix_queue.json`).
  - `quick_check.py` - Git-diff based fast static analysis mode.
  - `server.py` - Local dashboard server (`--serve`).
- `report/` - Dashboard generation:
  - `html_report.py` - Generates the interactive HTML dashboard.
  - `markdown_report.py` - Generates CLI markdown summaries.
  - `assets.py` - Static assets, templates, and script injections.

## 2. How to Run
```bash
pulse                  # full audit with AI
pulse --fast           # static analysis only, no AI, uses git diff
pulse --serve          # full audit then serve at http://localhost:8421
pulse --serve --watch  # same but re-runs on file changes
pulse --install-hook   # install pre-commit hook
```

## 3. The .env File
```
GEMINI_API_KEY=...          # primary key (required for AI)
GEMINI_API_KEY_2=...        # additional keys (optional, pooled smartly)
GEMINI_API_KEY_3=...        # add as many as you have up to _20
ANTHROPIC_API_KEY=...       # Claude fallback (paid)
```

## 4. Scoring System
- **Grade Thresholds:**
  - 90%+: Healthy (no AI health narrative needed)
  - 80-89%: Warning
  - <80%: Critical
- **Penalties:**
  - Cross-App Boundary Violations: 5 pts each (3 pts for core/gateway)
  - Security Issues: 3 pts each
  - High Complexity: 1 pt each
  - Max score is 100%. Score is per-app. The Fleet Average Score is the average across all apps.

## 5. BOOTSTRAP_LEAVES Sync Rule
The list of bootstrap/leaf apps must stay identical in both Python and JS to ensure accurate cycle detection and visualization.
- **Python:** Managed in `nexus_audit/config.py` (`BOOTSTRAP_LEAVES`).
- **JS:** Managed in the HTML template generation (`nexus_audit/report/assets.py` / `dashboard_template.html`).

## 6. KeyPool Routing
The `KeyPool` (`nexus_audit/key_pool.py`) manages a round-robin pool of API keys and routes tasks based on model quotas.
- Heavy tasks (like violation analysis) and light tasks (like health narratives) are distributed smartly.
- Handles HTTP 429 errors by marking keys as RPM-exhausted (initiates a 65s backoff) or Daily-exhausted (skips model until quota resets).

## 7. Dashboard Tabs
- **Overview:** Fleet average score, high-level stats, and recent trends.
- **App Details:** Per-app score, violations, complexity warnings, and health narrative.
- **Trends:** Historical score progression, violation counts, and complexity over time across audit runs.
- **Coupling Map:** Interactive `vis-network` graph showing cross-app dependencies and cycles.
- **Fix Queue:** Manageable to-do list for AI recommendations, persisting state across runs.
- **Inspect Edges:** Detailed view of specific import edges between apps.
- **Separate Apps:** Detailed view of individual app metrics and boundaries.

## 8. Patch History
- **Patch 1–4:** Early single-file structure fixes, logic corrections, and initial AI rate limiting.
- **Phase 1:** Massive refactor splitting `command_center_galaxy.py` into a proper multi-module package (`nexus_audit/`), extracting the AI backend, and introducing the `KeyPool`.
- **Phase 2:** Dashboard rewrite (HTML/JS template separation), Timeline, Fix Queue, and Coupling Map introductions.
- **Phase 3:** CLI enhancements, `--serve`, `--watch`, `--fast` mode via git diffs, and pre-commit hooks.
- **Phase 4:** Deep AI refinements, multi-layer AI recommendation orchestrator, and security/CVE advisors.
- **Phase 5:** Final cleanup, removing dead constants (`GEMINI_API_URL`), removing patch scripts, updating aliases, and establishing CODEX v4.

## 9. Quick Reference
- **Add Exempt Module:** Add to `EXEMPT_MODULES` in `nexus_audit/config.py`.
- **Add New Task Type:** Add to `TASK_MODELS` in `nexus_audit/ai/backend.py` and register it in `recommendations.py`.
- **Add New Rec Card Field:** Update `_parse_ai_json()` in `nexus_audit/ai/backend.py`, the prompts in `prompts.py`, and the JS template in `report/assets.py`.
