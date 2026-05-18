#!/usr/bin/env python3
"""
Nexus Audit AI Prompts
======================
Architecture context strings and system prompts used by the AI recommendation engine.
"""

# ── Architecture context injected into every AI prompt ───────────────────────

ARCH_CONTEXT = """
NEXUS PROJECT ARCHITECTURE:
  nexus_core        — user auth, core models, tokens, middleware, serializers
  nexus_economy     — wallet, finance views, Celery payment tasks, mgmt commands
  nexus_gaming      — feature flags, tier permissions, decorators, settings, logging
  nexus_gateway     — WebSocket consumers, middleware, routing, gateway views
  nexus_tournaments — services layer, signals, tasks, split model package, REST API
  nexus_social      — social models, notification preferences
  nexus_content     — content models and views
STRICT POLICY: No direct cross-app imports. Use Django signals, Celery tasks,
or REST calls via nexus_gateway for all cross-app communication.
""".strip()

# ── System prompt for all AI calls ────────────────────────────────────────────

AI_SYSTEM = (
    "You are a senior Django architect specialising in modular monolith design "
    "and strict app-boundary enforcement. Give precise, actionable guidance — "
    "specific module names, concrete code changes, effort estimates (S/M/L/XL), "
    "and migration steps. Be concise but complete. Never be vague. "
    "Name actual files and patterns."
)


def build_violation_prompt(tgt: str, tgt_app: str, tgt_leaf: str,
                            src_mods: list, src_apps: list, memory=None) -> str:
    """Build the deep-analysis prompt for a single cross-app violation."""
    src_apps_str = src_apps[0] if src_apps else tgt_app
    memory_block = ""
    if memory:
        memory_lines = []
        for item in memory:
            trend = item.get("trend", "unknown")
            age_runs = item.get("age_runs", 0)
            first_seen = item.get("first_seen", "unknown")
            last_seen = item.get("last_seen", "unknown")
            memory_lines.append(
                f"- {item.get('violation_id', 'unknown')}: age {age_runs} run(s), "
                f"trend {trend}, first seen {first_seen}, last seen {last_seen}"
            )
        memory_block = (
            "HISTORY CONTEXT (last 5 runs):\n"
            + "\n".join(memory_lines)
            + "\n\n"
            + "Interpretation rules:\n"
            + "- new: first appeared this run; suggest the quickest safe fix.\n"
            + "- persistent: present across consecutive runs; propose a phased refactor.\n"
            + "- intermittent: appears and disappears; investigate environment or CI drift.\n"
            + "- resolved: was present before but not in the latest run.\n\n"
        )
    return f"""{ARCH_CONTEXT}

VIOLATION TO ANALYSE:
  Module path      : {tgt}
  Currently in app : {tgt_app}
  Imported by      : {", ".join(src_mods)}
  Importing apps   : {", ".join(src_apps)} ({len(src_apps)} app(s))

{memory_block}This is a STRICT cross-app boundary violation. Analyse it deeply and return ONLY a
valid JSON object — no markdown fences, no prose before or after, just the raw JSON.

{{
  "title": "Concise fix title (max 10 words, starts with a verb)",

  "why_harmful": "3-4 sentences that explain: (1) exactly what coupling this creates between {tgt_app} and the importing apps, (2) a CONCRETE real-world consequence — e.g. which deployment, test suite, or feature would break if {tgt} changes its interface, (3) what Django modularity principle this violates and why that principle exists.",

  "what_breaks_today": "One specific, concrete example of actual pain the team is experiencing RIGHT NOW because of this import — e.g. a test that must mock both apps, a redeployment that cascades, a circular import risk.",

  "correct_location": "exact.dotted.module.path where this code belongs and why that app owns it",

  "migration_steps": [
    "Step 1: specific file to create/move, naming the exact path",
    "Step 2: what to change inside the moved module",
    "Step 3: how to update each importing module with the new import path",
    "Step 4: how to verify nothing broke (test command or smoke test)"
  ],

  "before_code": "# CURRENT (violation)\\nfrom {tgt} import Something  # in {src_apps_str}",
  "after_code":  "# FIXED\\nfrom correct.location import Something  # update this path",

  "fix_effort": "< 1 hour",
  "fix_effort_rationale": "Single import redirection needed, no downstream changes",
  "effort": "S or M or L or XL",
  "priority": "HIGH",
  "confidence": 1
}}"""


def build_health_prompt(app: str, score: int, bv: int, sec: int,
                         is_core: bool) -> str:
    """Build the health narrative prompt for a single app."""
    vpts = bv * (3 if is_core else 5)
    spts = sec * 3
    return f"""{ARCH_CONTEXT}

APP: {app.upper()}
Score: {score}% | Boundary violations: {bv} (-{vpts} pts) | Security: {sec} (-{spts} pts)

Write a 4-sentence health narrative (plain text, no JSON, no bullet points):
1. What specifically causes the {score}% score (name the actual numbers)
2. Priority order of fixes with exact score gain per fix
3. Expected score after all fixes
4. One sentence on long-term risk if left unfixed
Use "{app}" not "the application"."""


def build_extraction_prompt(tgt: str, importers: list) -> str:
    """Build the shared-utility extraction prompt."""
    return f"""{ARCH_CONTEXT}

SHARED UTILITY PROBLEM:
  Module     : {tgt}  (currently in {tgt.split(".")[0]})
  Imported as violation by: {", ".join(importers)} ({len(importers)} apps)

Write a concrete extraction plan (plain text, numbered steps, no JSON):
1. Exact new module path
2. Changes needed inside {tgt} itself
3. How to update each of the {len(importers)} importing apps
4. Migration order to avoid breaking tests
5. Effort estimate"""


def build_upgrade_prompt(pkg_name: str, installed: str, latest: str,
                          cve_count: int) -> str:
    """Build the package upgrade advisor prompt."""
    return f"""{ARCH_CONTEXT}

OUTDATED PACKAGE IN NEXUS PROJECT:
  Package   : {pkg_name}
  Installed : {installed}
  Latest    : {latest}
  CVEs on installed version: {cve_count}

Return ONLY a JSON object (no markdown, no prose):
{{
  "upgrade_command": "exact pip install command to upgrade safely, e.g. pip install {pkg_name}=={latest}",
  "why_upgrade":     "2-3 sentences: security risk, performance improvements, or features gained",
  "breaking_changes":"Specific breaking changes between {installed} and {latest} that affect Django/Celery usage — or \\"None known\\" if safe",
  "test_after":      "One-line command to verify the upgrade worked in this Django project",
  "risk_if_skipped": "Concrete risk to nexus platform if this upgrade is not done",
  "confidence": 1
}}
"""


def build_cve_prompt(cve_id: str, pkg_name: str, severity: str,
                      summary: str) -> str:
    """Build the CVE security advisor prompt."""
    return f"""{ARCH_CONTEXT}

SECURITY VULNERABILITY IN NEXUS PROJECT DEPENDENCY:
  CVE ID   : {cve_id}
  Package  : {pkg_name}
  Severity : {severity}
  Summary  : {summary}

Nexus is a Django + Celery + Redis + WebSocket gaming platform handling real money (wallet),
user authentication, tournaments, and social features.

Return ONLY a JSON object (no markdown, no prose):
{{
  "attack_scenario":  "Concrete, specific way this CVE could be exploited in the Nexus platform — name the actual Django app and endpoint at risk",
  "nexus_risk_level": "CRITICAL / HIGH / MEDIUM / LOW with one-sentence justification specific to this platform",
  "fix_command":      "Exact pip install command to fix this CVE",
  "config_changes":   "Any settings.py or environment config changes needed, or \\"None required\\"",
  "verify_fixed":     "How to confirm this CVE is no longer exploitable after the fix",
  "confidence": 1
}}
"""
