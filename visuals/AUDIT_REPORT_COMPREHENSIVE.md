# 🛡️ NEXUS MASTER AUDIT REPORT

**Generated:** 2026-05-24 11:54:05  
**Project:** `/home/yusupha/my_tools/nexus_project_copy`  
**Tier:** 🌐 Tier 2 — ONLINE (Enhanced Mode)  
**Total modules:** 243  
**Physical files:** 217  
**Policy:** Strict modularity — cross-app imports are violations. Signals, tasks, and receivers are allowed communications.

## ⚙️ CAPABILITY MANIFEST

| Capability | Status |
| :--- | :--- |
| Dna Audit | ✅ Active |
| Violation Detection | ✅ Active |
| Security Scan | ✅ Active |
| Complexity Analysis | ✅ Active |
| Ghost File Detection | ✅ Active |
| Cycle Detection | ✅ Active |
| Trend Tracking | ✅ Active |
| Shared Util Detection | ✅ Active |
| Package Vuln Scan | ✅ Active |
| Dependency Freshness | ✅ Active |
| Cve Enrichment | ✅ Active |

## 📊 Executive Summary

| Metric | Value |
| :--- | :--- |
| Overall fleet health | 💛 **77.5%** (Grade C) |
| Apps audited | 6 |
| Cross-app violations | 13 |
| Violations vs last run | → unchanged (+0) — prev: 13 on 2026-05-24 |
| Allowed communications | 23 |
| Security findings | 109 |
| Ghost files | 6 |
| Circular dependency cycles | 15 |
| Avg cyclomatic complexity | 2.42 |
| Max cyclomatic complexity | 26 |
| Maintainability index | 100.0 |

## 🔄 CRITICAL: CIRCULAR DEPENDENCIES

Circular dependencies prevent clean testing and deployment isolation.

- **[HIGH / INTRA-APP]** `nexus_core.utils → nexus_core.utils.decorators`  
  Apps involved: nexus_core
- **[HIGH / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views.leagues → nexus_tournaments.views`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.moderation`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.matches`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.results`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.announcements`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.escrow`  
  Apps involved: nexus_economy
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.payout`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks → nexus_tournaments.services.bracket_service`  
  Apps involved: nexus_tournaments
- **[MEDIUM / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks → nexus_tournaments.services.diagnostic_service`  
  Apps involved: nexus_tournaments
- **[MEDIUM / INTRA-APP]** `nexus_economy.tasks.refund → nexus_economy.services.refund_service → nexus_economy.tasks`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.payout → nexus_economy.services.payout_service`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.payout → nexus_economy.services.forfeiture_service`  
  Apps involved: nexus_economy
- **[INFO / INTRA-APP]** `nexus_tournaments.models → nexus_tournaments.models.league`  
  Apps involved: nexus_tournaments

## 👻 CRITICAL: GHOST FILES

These files exist on disk but were not scanned by pydeps. They may be dead code or unreachable entry points.

- `nexus_core.management.commands.dispatch_outbox_events`
- `nexus_core.management.commands.verify_backend`
- `nexus_core.serializers.auth`
- `nexus_core.serializers.token`
- `nexus_core.serializers.users`
- `nexus_tournaments.management.commands.dispatch_outbox_events`

## 🖤 APPLICATION FLEET HEALTH

| App | Score | Grade | Trend | Physical | Audited | Boundary Violations | Security | Ghosts |
| :--- | ---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: |
| **NEXUS_CONTENT** | 💚 92% | A | → | 18 | 21 | 0 | 3 | 0 |
| **NEXUS_CORE** | 💛 62% | D | → | 42 | 44 | 1 | 58 | 5 |
| **NEXUS_ECONOMY** | 💚 93% | A | → | 48 | 56 | 0 | 18 | 0 |
| **NEXUS_GATEWAY** | 💚 95% | A | → | 9 | 12 | 3 | 7 | 0 |
| **NEXUS_SOCIAL** | ❤️ 57% | F | → | 40 | 41 | 6 | 12 | 0 |
| **NEXUS_TOURNAMENTS** | 💛 67% | D | → | 60 | 69 | 3 | 11 | 1 |

## 🚨 VIOLATIONS

### Cross-App Imports (13 violations)

Direct imports between first-party apps violate strict modularity. Replace with Django signals, Celery tasks, or REST API calls.

| Source Module | Target Module | Recommendation |
| :--- | :--- | :--- |
| `nexus_social.services.event_consumers` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.services.event_consumers` | `nexus_core.utils.events` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.services.event_consumers` | `nexus_core.utils` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.views.events` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.views.events` | `nexus_core.utils` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.views.events` | `nexus_core.utils.events` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_gateway.consumers` | `nexus_tournaments.services` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_gateway.consumers` | `nexus_tournaments` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_gateway.consumers` | `nexus_tournaments.services.match_service` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_core.utils.feature_flags` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_core.utils` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_core.views.games` | `nexus_content` | Replace with Django signal, Celery task, or REST API call. |

### Other Violations (109)

| Type | Source | Severity |
| :--- | :--- | :--- |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `verify_backend.py` | LOW |
| Hardcoded Password | `verify_backend.py` | LOW |
| Bare Except | `verify_backend.py` | LOW |
| Bare Except | `middleware.py` | LOW |
| Hardcoded Password | `test_admin_panel.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_auth.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_new_endpoints.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_sessions_mfa_deletion.py` | LOW |
| Hardcoded Password | `test_signals.py` | LOW |
| Hardcoded Password | `test_signals.py` | LOW |
| Hardcoded Password | `test_signals.py` | LOW |
| Hardcoded Password | `test_users.py` | LOW |
| Hardcoded Password | `test_users.py` | LOW |
| Hardcoded Password | `test_users.py` | LOW |
| Hardcoded Password | `test_users.py` | LOW |
| Hardcoded Password | `test_users.py` | LOW |
| Bare Except | `admin_panel.py` | LOW |
| Bare Except | `auth.py` | LOW |
| Bare Except | `auth.py` | LOW |
| Bare Except | `auth.py` | LOW |
| Hardcoded Password | `test_financial_integrity.py` | LOW |
| Hardcoded Password | `test_financial_integrity.py` | LOW |
| Hardcoded Password | `test_financial_integrity.py` | LOW |
| Hardcoded Password | `test_forfeiture.py` | LOW |
| Hardcoded Password | `test_forfeiture.py` | LOW |
| Hardcoded Password | `test_forfeiture.py` | LOW |
| Hardcoded Password | `test_full_tournament.py` | LOW |
| Hardcoded Password | `test_full_tournament.py` | LOW |
| Hardcoded Password | `test_full_tournament.py` | LOW |
| Hardcoded Password | `test_full_tournament.py` | LOW |
| Hardcoded Password | `test_receivers.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_wallet_views.py` | LOW |
| Hardcoded Password | `test_wallet_views.py` | LOW |
| Hardcoded Password | `test_wallet_views.py` | LOW |
| Hardcoded Password | `test_wallet_views.py` | LOW |
| Bare Except | `consumers.py` | LOW |
| Bare Except | `consumers.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Bare Except | `apps.py` | LOW |
| Bare Except | `auto_flag.py` | LOW |
| Bare Except | `push_notifications.py` | LOW |
| Hardcoded Password | `test_chat.py` | LOW |
| Hardcoded Password | `test_notification_preferences.py` | LOW |
| Hardcoded Password | `test_read_receipts.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_views.py` | LOW |
| Hardcoded Password | `test_announcement_moderation.py` | LOW |
| Hardcoded Password | `test_announcement_service.py` | LOW |
| Hardcoded Password | `test_api.py` | LOW |
| Hardcoded Password | `test_final_contract_gaps.py` | LOW |
| Hardcoded Password | `test_invariants.py` | LOW |
| Hardcoded Password | `test_models.py` | LOW |
| Hardcoded Password | `test_ruleset_restrictions.py` | LOW |
| Hardcoded Password | `test_services.py` | LOW |
| Hardcoded Password | `test_tasks.py` | LOW |
| Hardcoded Password | `test_tasks.py` | LOW |
| Bare Except | `phash.py` | LOW |

## 🔗 ALLOWED CROSS-APP COMMUNICATIONS

These cross-app interactions use decoupled communication patterns and are permitted.

| Type | Source App | Target App | Details |
| :--- | :--- | :--- | :--- |
| Django Bootstrap (Exempt) | nexus_social | nexus_core | `nexus_social.apps → nexus_core` |
| Django Bootstrap (Exempt) | nexus_social | nexus_core | `nexus_social.apps → nexus_core.utils.events` |
| Django Bootstrap (Exempt) | nexus_social | nexus_core | `nexus_social.apps → nexus_core.utils` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_economy | `nexus_gateway.apps → nexus_economy.signals` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_core | `nexus_gateway.apps → nexus_core` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_tournaments | `nexus_gateway.apps → nexus_tournaments` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_economy | `nexus_gateway.apps → nexus_economy` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_tournaments | `nexus_gateway.apps → nexus_tournaments.signals` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_core | `nexus_gateway.apps → nexus_core.signals` |
| Django Signal | nexus_content | nexus_core | `nexus_content.receivers → nexus_core` |
| Django Signal | nexus_content | nexus_core | `nexus_content.receivers → nexus_core.signals` |
| Django Signal | nexus_tournaments | nexus_economy | `nexus_tournaments.receivers → nexus_economy.signals` |
| Django Signal | nexus_tournaments | nexus_economy | `nexus_tournaments.receivers → nexus_economy` |
| Celery Task | nexus_tournaments | nexus_core | `nexus_tournaments.tasks → nexus_core.utils.feature_flags` |
| Celery Task | nexus_tournaments | nexus_core | `nexus_tournaments.tasks → nexus_core` |
| Celery Task | nexus_tournaments | nexus_core | `nexus_tournaments.tasks → nexus_core.utils` |
| Test Cross-App Import | nexus_tournaments | nexus_core | `nexus_tournaments.tests.test_services → nexus_core` |
| Test Cross-App Import | nexus_tournaments | nexus_core | `nexus_tournaments.tests.test_services → nexus_core.models` |
| Celery Task | nexus_core | nexus_content | `nexus_core.views.games → nexus_content.tasks` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.receivers → nexus_tournaments` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.receivers → nexus_tournaments.signals` |
| Test Cross-App Import | nexus_economy | nexus_tournaments | `nexus_economy.tests.test_forfeiture → nexus_tournaments` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.tests.test_forfeiture → nexus_tournaments.signals` |

## 📦 DEPENDENCY HEALTH (Tier 2 — Online Scan)

Scanned 120 packages for CVEs (OSV database) and version freshness (PyPI).  
Total CVEs found: **397** | Outdated packages: **42**

### Package Summary

| Package | Installed | Latest | Status | CVEs |
| :--- | :--- | :--- | :--- | :--- |
| `﻿amqp` | 5.3.1 | 5.3.1 | ✅ Current | 0 |
| `Automat` | 25.4.16 | 25.4.16 | ✅ Current | 0 |
| `annotated-types` | 0.7.0 | 0.7.0 | ✅ Current | 0 |
| `asgiref` | 3.11.1 | 3.11.1 | ✅ Current | 0 |
| `anyio` | 4.13.0 | 4.13.0 | ✅ Current | 0 |
| `async-timeout` | 5.0.1 | 5.0.1 | ✅ Current | 0 |
| `attrs` | 26.1.0 | 26.1.0 | ✅ Current | 0 |
| `autobahn` | 24.4.2 | 25.12.2 | ⚠️ Outdated | 2 |
| `Authlib` | 1.6.9 | 1.7.2 | ⚠️ Outdated | 13 |
| `backports-datetime-fromisoformat` | 2.0.3 | 2.0.3 | ✅ Current | 0 |
| `billiard` | 4.2.4 | 4.2.4 | ✅ Current | 0 |
| `certifi` | 2026.2.25 | 2026.5.20 | ⚠️ Outdated | 6 |
| `bcrypt` | 5.0.0 | 5.0.0 | ✅ Current | 0 |
| `bleach` | 6.3.0 | 6.3.0 | ✅ Current | 10 |
| `celery` | 5.6.3 | 5.6.3 | ✅ Current | 4 |
| `cfgv` | 3.5.0 | 3.5.0 | ✅ Current | 0 |
| `black` | 26.3.1 | 26.5.1 | ⚠️ Outdated | 3 |
| `channels` | 4.3.2 | 4.3.2 | ✅ Current | 2 |
| `channels_redis` | 4.3.0 | 4.3.0 | ✅ Current | 0 |
| `cffi` | 2.0.0 | 2.0.0 | ✅ Current | 0 |
| `click-didyoumean` | 0.3.1 | 0.3.1 | ✅ Current | 0 |
| `click` | 8.3.1 | 8.4.1 | ⚠️ Outdated | 0 |
| `click-plugins` | 1.1.1.2 | 1.1.1.2 | ✅ Current | 0 |
| `constantly` | 23.10.4 | 23.10.4 | ✅ Current | 0 |
| `charset-normalizer` | 3.4.7 | 3.4.7 | ✅ Current | 0 |
| `click-repl` | 0.3.0 | 0.3.0 | ✅ Current | 0 |
| `cron-descriptor` | 1.4.5 | 2.0.8 | ⚠️ Outdated | 0 |
| `daphne` | 4.2.1 | 4.2.1 | ✅ Current | 0 |
| `distlib` | 0.4.0 | 0.4.0 | ✅ Current | 0 |
| `django-celery-beat` | 2.9.0 | 2.9.0 | ✅ Current | 0 |
| `django-ratelimit` | 4.1.0 | 4.1.0 | ✅ Current | 0 |
| `django-timezone-field` | 7.2.1 | 7.2.1 | ✅ Current | 0 |
| `annotated-doc` | 0.0.4 | 0.0.4 | ✅ Current | 0 |
| `dparse` | 0.6.4 | 0.6.4 | ✅ Current | 2 |
| `djangorestframework_simplejwt` | 5.5.1 | 5.5.1 | ✅ Current | 1 |
| `exceptiongroup` | 1.3.1 | 1.3.1 | ✅ Current | 0 |
| `djangorestframework` | 3.17.1 | 3.17.1 | ✅ Current | 3 |
| `cryptography` | 46.0.6 | 48.0.0 | ⚠️ Outdated | 30 |
| `google-cloud-vision` | 3.7.4 | 3.14.0 | ⚠️ Outdated | 0 |
| `filelock` | 3.25.2 | 3.29.0 | ⚠️ Outdated | 2 |
| `h11` | 0.16.0 | 0.16.0 | ✅ Current | 1 |
| `hyperlink` | 21.0.0 | 21.0.0 | ✅ Current | 0 |
| `iniconfig` | 2.3.0 | 2.3.0 | ✅ Current | 0 |
| `identify` | 2.6.18 | 2.6.19 | ⚠️ Outdated | 0 |
| `idna` | 3.11 | 3.16 | ⚠️ Outdated | 3 |
| `imagehash` | 4.3.1 | 4.3.2 | ⚠️ Outdated | 0 |
| `Incremental` | 24.11.0 | 24.11.0 | ✅ Current | 0 |
| `joblib` | 1.5.3 | 1.5.3 | ✅ Current | 3 |
| `Jinja2` | 3.1.6 | 3.1.6 | ✅ Current | 16 |
| `jsonschema` | 4.19.0 | 4.26.0 | ⚠️ Outdated | 0 |
| `kombu` | 5.6.2 | 5.6.2 | ✅ Current | 0 |
| `jsonschema-specifications` | 2025.9.1 | 2025.9.1 | ✅ Current | 0 |
| `markdown-it-py` | 4.0.0 | 4.2.0 | ⚠️ Outdated | 4 |
| `Django` | 5.2.12 | 6.0.5 | ⚠️ Outdated | 0 |
| `mypy_extensions` | 1.1.0 | 1.1.0 | ✅ Current | 0 |
| `marshmallow` | 4.3.0 | 4.3.0 | ✅ Current | 3 |
| `mdurl` | 0.1.2 | 0.1.2 | ✅ Current | 0 |
| `nodeenv` | 1.10.0 | 1.10.0 | ✅ Current | 0 |
| `pathspec` | 1.0.4 | 1.1.1 | ⚠️ Outdated | 0 |
| `MarkupSafe` | 3.0.3 | 3.0.3 | ✅ Current | 0 |
| `msgpack` | 1.1.2 | 1.1.2 | ✅ Current | 0 |
| `packaging` | 26.0 | 26.2 | ⚠️ Outdated | 0 |
| `nltk` | 3.9.4 | 3.9.4 | ✅ Current | 21 |
| `platformdirs` | 4.9.4 | 4.9.6 | ⚠️ Outdated | 0 |
| `pluggy` | 1.6.0 | 1.6.0 | ✅ Current | 0 |
| `pre_commit` | 4.5.1 | 4.6.0 | ⚠️ Outdated | 0 |
| `prometheus_client` | 0.25.0 | 0.25.0 | ✅ Current | 0 |
| `prompt_toolkit` | 3.0.52 | 3.0.52 | ✅ Current | 0 |
| `pycparser` | 3.0 | 3.0 | ✅ Current | 0 |
| `psycopg2-binary` | 2.9.11 | 2.9.12 | ⚠️ Outdated | 0 |
| `pyasn1` | 0.6.3 | 0.6.3 | ✅ Current | 2 |
| `pyasn1_modules` | 0.4.2 | 0.4.2 | ✅ Current | 0 |
| `Pygments` | 2.20.0 | 2.20.0 | ✅ Current | 9 |
| `pydantic` | 2.12.5 | 2.13.4 | ⚠️ Outdated | 3 |
| `PyJWT` | 2.12.1 | 2.13.0 | ⚠️ Outdated | 8 |
| `pyotp` | 2.9.0 | 2.9.0 | ✅ Current | 0 |
| `pyOpenSSL` | 26.0.0 | 26.2.0 | ⚠️ Outdated | 8 |
| `pytest-django` | 4.12.0 | 4.12.0 | ✅ Current | 0 |
| `python-crontab` | 3.3.0 | 3.3.0 | ✅ Current | 0 |
| `pytest` | 9.0.3 | 9.0.3 | ✅ Current | 1 |
| `Pillow` | 10.4.0 | 12.2.0 | ⚠️ Outdated | 118 |
| `python-dateutil` | 2.9.0.post0 | 2.9.0.post0 | ✅ Current | 0 |
| `python-discovery` | 1.2.2 | 1.3.1 | ⚠️ Outdated | 0 |
| `pytokens` | 0.4.1 | 0.4.1 | ✅ Current | 0 |
| `pydantic_core` | 2.41.5 | 2.47.0 | ⚠️ Outdated | 0 |
| `referencing` | 0.37.0 | 0.37.0 | ✅ Current | 0 |
| `redis` | 7.4.0 | 7.4.0 | ✅ Current | 4 |
| `PyYAML` | 6.0.3 | 6.0.3 | ✅ Current | 8 |
| `requests` | 2.33.1 | 2.34.2 | ⚠️ Outdated | 13 |
| `rich` | 14.3.3 | 15.0.0 | ⚠️ Outdated | 0 |
| `safety-schemas` | 0.0.16 | 0.0.18 | ⚠️ Outdated | 0 |
| `service-identity` | 24.2.0 | 24.2.0 | ✅ Current | 0 |
| `shellingham` | 1.5.4 | 1.5.4 | ✅ Current | 0 |
| `safety` | 3.7.0 | 3.7.0 | ✅ Current | 2 |
| `sentry-sdk` | 2.58.0 | 2.60.0 | ⚠️ Outdated | 2 |
| `six` | 1.17.0 | 1.17.0 | ✅ Current | 0 |
| `ruamel.yaml` | 0.19.1 | 0.19.1 | ✅ Current | 0 |
| `rpds-py` | 0.30.0 | 0.30.0 | ✅ Current | 0 |
| `sqlparse` | 0.5.5 | 0.5.5 | ✅ Current | 6 |
| `structlog` | 25.5.0 | 25.5.0 | ✅ Current | 0 |
| `tenacity` | 9.1.4 | 9.1.4 | ✅ Current | 0 |
| `tomli` | 2.4.1 | 2.4.1 | ✅ Current | 0 |
| `tomlkit` | 0.14.0 | 0.15.0 | ⚠️ Outdated | 0 |
| `ruff` | 0.15.9 | 0.15.14 | ⚠️ Outdated | 0 |
| `txaio` | 25.9.2 | 25.12.2 | ⚠️ Outdated | 0 |
| `typing-inspection` | 0.4.2 | 0.4.2 | ✅ Current | 0 |
| `typer` | 0.24.1 | 0.25.1 | ⚠️ Outdated | 0 |
| `tqdm` | 4.67.3 | 4.67.3 | ✅ Current | 3 |
| `Twisted` | 25.5.0 | 26.4.0 | ⚠️ Outdated | 28 |
| `tzdata` | 2025.3 | 2026.2 | ⚠️ Outdated | 0 |
| `typing_extensions` | 4.15.0 | 4.15.0 | ✅ Current | 0 |
| `tzlocal` | 5.3.1 | 5.3.1 | ✅ Current | 0 |
| `vine` | 5.1.0 | 5.1.0 | ✅ Current | 0 |
| `regex` | 2026.4.4 | 2026.5.9 | ⚠️ Outdated | 0 |
| `wcwidth` | 0.6.0 | 0.7.0 | ⚠️ Outdated | 0 |
| `websocket-client` | 1.9.0 | 1.9.0 | ✅ Current | 0 |
| `urllib3` | 2.6.3 | 2.7.0 | ⚠️ Outdated | 32 |
| `virtualenv` | 21.2.0 | 21.3.3 | ⚠️ Outdated | 5 |
| `zope.interface` | 8.2 | 8.4 | ⚠️ Outdated | 0 |
| `numpy` | 1.26.4 | 2.4.6 | ⚠️ Outdated | 16 |

## 🔒 SECURITY FINDINGS

Bandit scan found 109 issue(s). Test-file findings are excluded from health scoring.

| Severity | File | Line | Issue |
| :---: | :--- | ---: | :--- |
| **LOW** | `test_views.py` | 40 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 43 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 46 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `verify_backend.py` | 51 | B105: Possible hardcoded password: 'PASS' |
| **LOW** | `verify_backend.py` | 182 | B105: Possible hardcoded password: '✓' |
| **LOW** | `verify_backend.py` | 515 | B110: Try, Except, Pass detected. |
| **LOW** | `middleware.py` | 201 | B110: Try, Except, Pass detected. |
| **LOW** | `test_admin_panel.py` | 57 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_auth.py` | 30 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 42 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 50 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_auth.py` | 54 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 61 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_auth.py` | 65 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 74 | B105: Possible hardcoded password: '123' |
| **LOW** | `test_auth.py` | 84 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 97 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 156 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 164 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 176 | B105: Possible hardcoded password: 'wrongpassword' |
| **LOW** | `test_auth.py` | 184 | B105: Possible hardcoded password: 'whatever' |
| **LOW** | `test_auth.py` | 193 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 200 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 213 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 219 | B105: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 241 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_auth.py` | 263 | B105: Possible hardcoded password: 'NewSecurePass456!' |
| **LOW** | `test_auth.py` | 277 | B105: Possible hardcoded password: 'NewSecurePass456!' |
| **LOW** | `test_auth.py` | 286 | B105: Possible hardcoded password: 'invalid-token' |
| **LOW** | `test_auth.py` | 287 | B105: Possible hardcoded password: 'NewSecurePass456!' |
| **LOW** | `test_new_endpoints.py` | 45 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_new_endpoints.py` | 219 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 221 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_new_endpoints.py` | 239 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 241 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_new_endpoints.py` | 271 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 273 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_new_endpoints.py` | 303 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 325 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_sessions_mfa_deletion.py` | 33 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_sessions_mfa_deletion.py` | 59 | B106: Possible hardcoded password: 'abc123' |
| **LOW** | `test_sessions_mfa_deletion.py` | 83 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_sessions_mfa_deletion.py` | 99 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_sessions_mfa_deletion.py` | 101 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_sessions_mfa_deletion.py` | 103 | B106: Possible hardcoded password: 'tok3' |
| **LOW** | `test_sessions_mfa_deletion.py` | 117 | B106: Possible hardcoded password: 'current' |
| **LOW** | `test_sessions_mfa_deletion.py` | 119 | B106: Possible hardcoded password: 'other1' |
| **LOW** | `test_sessions_mfa_deletion.py` | 121 | B106: Possible hardcoded password: 'other2' |
| **LOW** | `test_sessions_mfa_deletion.py` | 139 | B106: Possible hardcoded password: 'tok' |
| **LOW** | `test_signals.py` | 24 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_signals.py` | 34 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_signals.py` | 44 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_users.py` | 29 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_users.py` | 64 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_users.py` | 79 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_users.py` | 113 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_users.py` | 168 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `admin_panel.py` | 109 | B110: Try, Except, Pass detected. |
| **LOW** | `auth.py` | 581 | B110: Try, Except, Pass detected. |
| **LOW** | `auth.py` | 604 | B110: Try, Except, Pass detected. |
| **LOW** | `auth.py` | 678 | B110: Try, Except, Pass detected. |
| **LOW** | `test_financial_integrity.py` | 41 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_financial_integrity.py` | 214 | B106: Possible hardcoded password: 'wave_token' |
| **LOW** | `test_financial_integrity.py` | 265 | B106: Possible hardcoded password: 'wave_token' |
| **LOW** | `test_forfeiture.py` | 27 | B106: Possible hardcoded password: 'p' |
| **LOW** | `test_forfeiture.py` | 28 | B106: Possible hardcoded password: 'p' |
| **LOW** | `test_forfeiture.py` | 45 | B106: Possible hardcoded password: 'p' |
| **LOW** | `test_full_tournament.py` | 45 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_full_tournament.py` | 160 | B106: Possible hardcoded password: 'token' |
| **LOW** | `test_full_tournament.py` | 225 | B106: Possible hardcoded password: 'token' |
| **LOW** | `test_full_tournament.py` | 294 | B106: Possible hardcoded password: 'bank-token' |
| **LOW** | `test_receivers.py` | 27 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 26 | B106: Possible hardcoded password: 'testpass123' |
| **LOW** | `test_views.py` | 113 | B106: Possible hardcoded password: 'testpass123' |
| **LOW** | `test_views.py` | 258 | B106: Possible hardcoded password: 'testpass123' |
| **LOW** | `test_wallet_views.py` | 27 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_wallet_views.py` | 173 | B105: Possible hardcoded password: 'token-abc' |
| **LOW** | `test_wallet_views.py` | 180 | B105: Possible hardcoded password: 'token-abc' |
| **LOW** | `test_wallet_views.py` | 192 | B105: Possible hardcoded password: 'tok' |
| **LOW** | `consumers.py` | 391 | B110: Try, Except, Pass detected. |
| **LOW** | `consumers.py` | 402 | B110: Try, Except, Pass detected. |
| **LOW** | `test_consumers.py` | 52 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_consumers.py` | 62 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_consumers.py` | 313 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_consumers.py` | 323 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_consumers.py` | 334 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `apps.py` | 16 | B110: Try, Except, Pass detected. |
| **LOW** | `auto_flag.py` | 77 | B110: Try, Except, Pass detected. |
| **LOW** | `push_notifications.py` | 102 | B110: Try, Except, Pass detected. |
| **LOW** | `test_chat.py` | 79 | B106: Possible hardcoded password: 'password123' |
| **LOW** | `test_notification_preferences.py` | 25 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_read_receipts.py` | 14 | B106: Possible hardcoded password: 'password' |
| **LOW** | `test_views.py` | 19 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 77 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 80 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 120 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 148 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 151 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_announcement_moderation.py` | 23 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_announcement_service.py` | 23 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_api.py` | 33 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_final_contract_gaps.py` | 25 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_invariants.py` | 26 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_models.py` | 22 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_ruleset_restrictions.py` | 37 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_services.py` | 34 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_tasks.py` | 16 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_tasks.py` | 261 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `phash.py` | 98 | B112: Try, Except, Continue detected. |

## 📊 COMPLEXITY METRICS

| Metric | Value |
| :--- | ---: |
| Average cyclomatic complexity | 2.42 |
| Maximum cyclomatic complexity | 26 |
| Maintainability index | 100.0 |
| Functions analysed | 1650 |

### High Complexity Functions (>10)

| Function | File | Complexity | Lines |
| :--- | :--- | ---: | ---: |
| `_check_11_financial` | `verify_backend.py` | 26 | 0 |
| `_check_01_env` | `verify_backend.py` | 23 | 0 |
| `HandshakeRecheckService` | `handshake_recheck_service.py` | 22 | 0 |
| `recheck` | `handshake_recheck_service.py` | 21 | 0 |
| `handle_timeout` | `match_service.py` | 21 | 0 |
| `create_tournament` | `league_service.py` | 20 | 0 |
| `_check_02_models` | `verify_backend.py` | 19 | 0 |
| `_check_12_invariants` | `verify_backend.py` | 19 | 0 |
| `join_tournament` | `participation_service.py` | 19 | 0 |
| `_render_text` | `verify_backend.py` | 16 | 0 |
| `modempay_webhook_handler` | `webhooks.py` | 15 | 0 |
| `fourteen_day_sweep` | `tasks.py` | 15 | 0 |
| `_render_json` | `verify_backend.py` | 14 | 0 |
| `_try_activate` | `match_service.py` | 14 | 0 |
| `_check_08_websockets` | `verify_backend.py` | 13 | 0 |
| `generate_single_elimination` | `bracket_service.py` | 13 | 0 |
| `_run_ai_verification` | `verification_service.py` | 13 | 0 |
| `auto_snatcher_backfill` | `tasks.py` | 13 | 0 |
| `MarkReadView` | `receipts.py` | 13 | 0 |
| `LoginView` | `auth.py` | 12 | 0 |
| `handle` | `verify_backend.py` | 12 | 0 |
| `_check_10_security` | `verify_backend.py` | 12 | 0 |
| `EscrowService` | `escrow_service.py` | 12 | 0 |
| `WithdrawalService` | `withdrawal_service.py` | 12 | 0 |
| `WalletWithdrawView` | `wallet.py` | 12 | 0 |
| `ingest_event` | `events.py` | 12 | 0 |
| `post` | `receipts.py` | 12 | 0 |
| `post` | `auth.py` | 11 | 0 |
| `_check_06_imports` | `verify_backend.py` | 11 | 0 |
| `PayoutService` | `payout_service.py` | 11 | 0 |
| `lock` | `escrow_service.py` | 11 | 0 |
| `process` | `withdrawal_service.py` | 11 | 0 |
| `WalletDepositView` | `wallet.py` | 11 | 0 |
| `post` | `wallet.py` | 11 | 0 |
| `patch` | `preferences.py` | 11 | 0 |

## 💡 RECOMMENDATIONS

### [CRITICAL] Refactor nexus_content boundary

1 cross-app violation(s) point at nexus_content. Apps involved: nexus_core.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_core.views.games`, `nexus_content`

### [CRITICAL] Refactor nexus_core boundary

3 cross-app violation(s) point at nexus_core. Apps involved: nexus_social, nexus_tournaments.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_social.services.event_consumers`, `nexus_social.views.events`, `nexus_tournaments.services.verification_service`, `nexus_core`

### [CRITICAL] Refactor utils boundary

3 cross-app violation(s) point at nexus_core.utils. Apps involved: nexus_social, nexus_tournaments.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_social.services.event_consumers`, `nexus_social.views.events`, `nexus_tournaments.services.verification_service`, `nexus_core.utils`

### [CRITICAL] Refactor events boundary

2 cross-app violation(s) point at nexus_core.utils.events. Apps involved: nexus_social.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_social.services.event_consumers`, `nexus_social.views.events`, `nexus_core.utils.events`

### [CRITICAL] Refactor feature_flags boundary

1 cross-app violation(s) point at nexus_core.utils.feature_flags. Apps involved: nexus_tournaments.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_tournaments.services.verification_service`, `nexus_core.utils.feature_flags`

### [CRITICAL] Refactor nexus_tournaments boundary

1 cross-app violation(s) point at nexus_tournaments. Apps involved: nexus_gateway.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_gateway.consumers`, `nexus_tournaments`

### [CRITICAL] Refactor services boundary

1 cross-app violation(s) point at nexus_tournaments.services. Apps involved: nexus_gateway.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_gateway.consumers`, `nexus_tournaments.services`

### [CRITICAL] Refactor match_service boundary

1 cross-app violation(s) point at nexus_tournaments.services.match_service. Apps involved: nexus_gateway.

**Action:** Replace the direct import with a signal, Celery task, REST call, or shared service boundary so each app owns its own implementation.

**Affected modules:** `nexus_gateway.consumers`, `nexus_tournaments.services.match_service`

### [MEDIUM] Fix Bare Except

12 bare except finding(s) were detected by Bandit.

**Action:** Replace broad exception handling with specific exception types. Narrow each catch block to the real failure mode and preserve the stack trace where needed.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/middleware.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/views/admin_panel.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/views/auth.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_gateway/consumers.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_social/apps.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_social/services/auto_flag.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_social/services/push_notifications.py`

### [MEDIUM] Fix Hardcoded Password

97 hardcoded password finding(s) were detected by Bandit.

**Action:** Move the password into an environment variable or secret manager. Replace hardcoded credentials with settings-backed secrets and rotate the exposed value.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_content/tests/test_views.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/tests/test_admin_panel.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/tests/test_auth.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/tests/test_new_endpoints.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/tests/test_sessions_mfa_deletion.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/tests/test_signals.py`, `/home/yusupha/my_tools/nexus_project_copy/nexus_core/tests/test_users.py`

### [MEDIUM] Refactor LoginView

LoginView in auth.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/views/auth.py`

### [MEDIUM] Refactor post

post in auth.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/views/auth.py`

### [MEDIUM] Refactor generate_single_elimination

generate_single_elimination in bracket_service.py has cyclomatic complexity 13.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_tournaments/services/bracket_service.py`

### [MEDIUM] Refactor EscrowService

EscrowService in escrow_service.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/escrow_service.py`

### [MEDIUM] Refactor lock

lock in escrow_service.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/escrow_service.py`

### [MEDIUM] Refactor ingest_event

ingest_event in events.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_social/views/events.py`

### [HIGH] Refactor HandshakeRecheckService

HandshakeRecheckService in handshake_recheck_service.py has cyclomatic complexity 22.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/handshake_recheck_service.py`

### [HIGH] Refactor recheck

recheck in handshake_recheck_service.py has cyclomatic complexity 21.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/handshake_recheck_service.py`

### [MEDIUM] Refactor create_tournament

create_tournament in league_service.py has cyclomatic complexity 20.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_tournaments/services/league_service.py`

### [MEDIUM] Refactor _try_activate

_try_activate in match_service.py has cyclomatic complexity 14.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_tournaments/services/match_service.py`

### [HIGH] Refactor handle_timeout

handle_timeout in match_service.py has cyclomatic complexity 21.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_tournaments/services/match_service.py`

### [MEDIUM] Refactor join_tournament

join_tournament in participation_service.py has cyclomatic complexity 19.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_tournaments/services/participation_service.py`

### [MEDIUM] Refactor PayoutService

PayoutService in payout_service.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/payout_service.py`

### [MEDIUM] Refactor patch

patch in preferences.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_social/views/preferences.py`

### [MEDIUM] Refactor MarkReadView

MarkReadView in receipts.py has cyclomatic complexity 13.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_social/views/receipts.py`

### [MEDIUM] Refactor post

post in receipts.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_social/views/receipts.py`

### [MEDIUM] Refactor auto_snatcher_backfill

auto_snatcher_backfill in tasks.py has cyclomatic complexity 13.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_content/tasks.py`

### [MEDIUM] Refactor fourteen_day_sweep

fourteen_day_sweep in tasks.py has cyclomatic complexity 15.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_content/tasks.py`

### [MEDIUM] Refactor _run_ai_verification

_run_ai_verification in verification_service.py has cyclomatic complexity 13.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_tournaments/services/verification_service.py`

### [HIGH] Refactor _check_01_env

_check_01_env in verify_backend.py has cyclomatic complexity 23.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _check_02_models

_check_02_models in verify_backend.py has cyclomatic complexity 19.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _check_06_imports

_check_06_imports in verify_backend.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _check_08_websockets

_check_08_websockets in verify_backend.py has cyclomatic complexity 13.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _check_10_security

_check_10_security in verify_backend.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [HIGH] Refactor _check_11_financial

_check_11_financial in verify_backend.py has cyclomatic complexity 26.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _check_12_invariants

_check_12_invariants in verify_backend.py has cyclomatic complexity 19.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _render_json

_render_json in verify_backend.py has cyclomatic complexity 14.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor _render_text

_render_text in verify_backend.py has cyclomatic complexity 16.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor handle

handle in verify_backend.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_core/management/commands/verify_backend.py`

### [MEDIUM] Refactor WalletDepositView

WalletDepositView in wallet.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/views/wallet.py`

### [MEDIUM] Refactor WalletWithdrawView

WalletWithdrawView in wallet.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/views/wallet.py`

### [MEDIUM] Refactor post

post in wallet.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/views/wallet.py`

### [MEDIUM] Refactor modempay_webhook_handler

modempay_webhook_handler in webhooks.py has cyclomatic complexity 15.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/views/webhooks.py`

### [MEDIUM] Refactor WithdrawalService

WithdrawalService in withdrawal_service.py has cyclomatic complexity 12.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/withdrawal_service.py`

### [MEDIUM] Refactor process

process in withdrawal_service.py has cyclomatic complexity 11.

**Action:** Split the function into smaller helpers, flatten branches, and move repeated logic into a shared utility so the code becomes easier to test.

**Affected modules:** `/home/yusupha/my_tools/nexus_project_copy/nexus_economy/services/withdrawal_service.py`

### [LOW] Review ghost files in nexus_core

5 ghost file(s) were discovered for nexus_core.

**Action:** Remove dead files that are no longer imported, or register the missing modules properly if they are still required.

**Affected modules:** `nexus_core.serializers.token`, `nexus_core.serializers.users`, `nexus_core.serializers.auth`, `nexus_core.management.commands.verify_backend`, `nexus_core.management.commands.dispatch_outbox_events`

### [LOW] Review ghost files in nexus_tournaments

1 ghost file(s) were discovered for nexus_tournaments.

**Action:** Remove dead files that are no longer imported, or register the missing modules properly if they are still required.

**Affected modules:** `nexus_tournaments.management.commands.dispatch_outbox_events`

### [HIGH] Resolve intra-app cycle

nexus_core.utils -> nexus_core.utils.decorators

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_core.utils`, `nexus_core.utils.decorators`

### [HIGH] Resolve intra-app cycle

nexus_tournaments.services.match_service -> nexus_tournaments.tasks

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_tournaments.services.match_service`, `nexus_tournaments.tasks`

### [HIGH] Resolve intra-app cycle

nexus_tournaments.views.leagues -> nexus_tournaments.views

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_tournaments.views.leagues`, `nexus_tournaments.views`

### [HIGH] Resolve intra-app cycle

nexus_tournaments.views -> nexus_tournaments.views.moderation

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_tournaments.views`, `nexus_tournaments.views.moderation`

### [HIGH] Resolve intra-app cycle

nexus_tournaments.views -> nexus_tournaments.views.matches

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_tournaments.views`, `nexus_tournaments.views.matches`

### [HIGH] Resolve intra-app cycle

nexus_tournaments.views -> nexus_tournaments.views.results

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_tournaments.views`, `nexus_tournaments.views.results`

### [HIGH] Resolve intra-app cycle

nexus_tournaments.views -> nexus_tournaments.views.announcements

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_tournaments.views`, `nexus_tournaments.views.announcements`

### [HIGH] Resolve intra-app cycle

nexus_economy.tasks -> nexus_economy.tasks.escrow

**Action:** Move the shared dependency into a lower-level module, then replace the direct edge with a signal, task, or helper import that does not re-enter the cycle.

**Affected modules:** `nexus_economy.tasks`, `nexus_economy.tasks.escrow`

## 📋 FULL MODULE MANIFEST

### NEXUS_CONTENT (21 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_content` | 1 | 0 | 6 |
| `nexus_content.admin` | 1 | 3 | 1 |
| `nexus_content.apps` | 1 | 4 | 1 |
| `nexus_content.models` | 1 | 4 | 7 |
| `nexus_content.models.announcement` | 1 | 4 | 5 |
| `nexus_content.models.game_icon` | 1 | 4 | 4 |
| `nexus_content.models.patch_note` | 1 | 4 | 7 |
| `nexus_content.models.sweep_record` | 1 | 3 | 4 |
| `nexus_content.receivers` | 1 | 7 | 2 |
| `nexus_content.serializers` | 1 | 1 | 3 |
| `nexus_content.serializers.content` | 1 | 3 | 4 |
| `nexus_content.services` | 1 | 0 | 1 |
| `nexus_content.tasks` | 1 | 19 | 4 |
| `nexus_content.tests` | 1 | 0 | 1 |
| `nexus_content.tests.test_tasks` | 1 | 17 | 1 |
| `nexus_content.tests.test_views` | 1 | 13 | 1 |
| `nexus_content.urls` | 1 | 0 | 1 |
| `nexus_content.urls.content` | 1 | 3 | 1 |
| `nexus_content.views` | 1 | 2 | 2 |
| `nexus_content.views.announcements` | 1 | 9 | 2 |
| `nexus_content.views.patch_notes` | 1 | 7 | 2 |

### NEXUS_CORE (44 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_core` | 1 | 0 | 27 |
| `nexus_core.admin` | 1 | 3 | 1 |
| `nexus_core.apps` | 1 | 4 | 1 |
| `nexus_core.generate_tree` | 1 | 4 | 1 |
| `nexus_core.middleware` | 1 | 5 | 1 |
| `nexus_core.models` | 1 | 8 | 8 |
| `nexus_core.models.auth` | 1 | 5 | 2 |
| `nexus_core.models.game` | 1 | 4 | 2 |
| `nexus_core.models.hub` | 1 | 7 | 2 |
| `nexus_core.models.outbox` | 1 | 3 | 2 |
| `nexus_core.models.session` | 1 | 5 | 2 |
| `nexus_core.models.user` | 1 | 7 | 2 |
| `nexus_core.receivers` | 1 | 11 | 2 |
| `nexus_core.services` | 1 | 0 | 5 |
| `nexus_core.services.deletion` | 1 | 9 | 3 |
| `nexus_core.services.mfa` | 1 | 11 | 3 |
| `nexus_core.services.sessions` | 1 | 7 | 4 |
| `nexus_core.signals` | 1 | 2 | 5 |
| `nexus_core.tasks` | 1 | 4 | 1 |
| `nexus_core.tests` | 1 | 0 | 1 |
| `nexus_core.tests.test_admin_panel` | 1 | 11 | 1 |
| `nexus_core.tests.test_auth` | 1 | 12 | 1 |
| `nexus_core.tests.test_new_endpoints` | 1 | 8 | 1 |
| `nexus_core.tests.test_sessions_mfa_deletion` | 1 | 13 | 1 |
| `nexus_core.tests.test_signals` | 1 | 8 | 1 |
| `nexus_core.tests.test_users` | 1 | 6 | 1 |
| `nexus_core.urls` | 1 | 0 | 1 |
| `nexus_core.urls.admin_panel` | 1 | 5 | 1 |
| `nexus_core.urls.auth` | 1 | 5 | 1 |
| `nexus_core.urls.games` | 1 | 5 | 1 |
| `nexus_core.urls.users` | 1 | 5 | 1 |
| `nexus_core.utils` | 1 | 5 | 12 |
| `nexus_core.utils.decorators` | 1 | 4 | 3 |
| `nexus_core.utils.encryption` | 1 | 4 | 2 |
| `nexus_core.utils.events` | 1 | 7 | 4 |
| `nexus_core.utils.feature_flags` | 1 | 1 | 5 |
| `nexus_core.utils.logging_config` | 1 | 3 | 1 |
| `nexus_core.utils.tier_permissions` | 1 | 1 | 2 |
| `nexus_core.utils.tokens` | 1 | 4 | 3 |
| `nexus_core.views` | 1 | 0 | 5 |
| `nexus_core.views.admin_panel` | 1 | 7 | 2 |
| `nexus_core.views.auth` | 1 | 22 | 2 |
| `nexus_core.views.games` | 1 | 10 | 2 |
| `nexus_core.views.users` | 1 | 12 | 2 |

### NEXUS_ECONOMY (56 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_economy` | 1 | 0 | 42 |
| `nexus_economy.admin` | 1 | 3 | 1 |
| `nexus_economy.apps` | 1 | 4 | 1 |
| `nexus_economy.generate_tree` | 1 | 4 | 1 |
| `nexus_economy.integrations` | 1 | 3 | 6 |
| `nexus_economy.integrations.modempay` | 1 | 9 | 6 |
| `nexus_economy.management` | 1 | 0 | 1 |
| `nexus_economy.management.commands` | 1 | 0 | 1 |
| `nexus_economy.management.commands.create_test_wallet` | 1 | 9 | 1 |
| `nexus_economy.management.commands.dispatch_outbox_events` | 1 | 16 | 1 |
| `nexus_economy.models` | 1 | 9 | 17 |
| `nexus_economy.models.deposit` | 1 | 5 | 2 |
| `nexus_economy.models.failed_task` | 1 | 5 | 2 |
| `nexus_economy.models.outbox` | 1 | 3 | 2 |
| `nexus_economy.models.settings` | 1 | 5 | 2 |
| `nexus_economy.models.transaction` | 1 | 4 | 2 |
| `nexus_economy.models.wallet` | 1 | 5 | 2 |
| `nexus_economy.models.withdrawal` | 1 | 5 | 2 |
| `nexus_economy.receivers` | 1 | 11 | 3 |
| `nexus_economy.services` | 1 | 0 | 12 |
| `nexus_economy.services.deposit_service` | 1 | 9 | 4 |
| `nexus_economy.services.escrow_service` | 1 | 9 | 5 |
| `nexus_economy.services.forfeiture_service` | 1 | 11 | 3 |
| `nexus_economy.services.handshake_recheck_service` | 1 | 11 | 2 |
| `nexus_economy.services.payout_service` | 1 | 13 | 4 |
| `nexus_economy.services.platform_revenue_service` | 1 | 7 | 2 |
| `nexus_economy.services.reconciliation_service` | 1 | 7 | 4 |
| `nexus_economy.services.refund_service` | 1 | 9 | 4 |
| `nexus_economy.services.tournament_escrow_service` | 1 | 9 | 3 |
| `nexus_economy.services.withdrawal_service` | 1 | 12 | 4 |
| `nexus_economy.signals` | 1 | 2 | 8 |
| `nexus_economy.tasks` | 1 | 7 | 11 |
| `nexus_economy.tasks.base` | 1 | 6 | 4 |
| `nexus_economy.tasks.escrow` | 1 | 8 | 2 |
| `nexus_economy.tasks.payout` | 1 | 7 | 2 |
| `nexus_economy.tasks.reconciliation` | 1 | 6 | 2 |
| `nexus_economy.tasks.refund` | 1 | 7 | 3 |
| `nexus_economy.tasks.settlement` | 1 | 8 | 2 |
| `nexus_economy.tests` | 1 | 0 | 1 |
| `nexus_economy.tests.test_financial_integrity` | 1 | 23 | 1 |
| `nexus_economy.tests.test_forfeiture` | 1 | 15 | 1 |
| `nexus_economy.tests.test_full_tournament` | 1 | 25 | 1 |
| `nexus_economy.tests.test_models` | 1 | 10 | 1 |
| `nexus_economy.tests.test_receivers` | 1 | 11 | 1 |
| `nexus_economy.tests.test_tasks` | 1 | 12 | 1 |
| `nexus_economy.tests.test_views` | 1 | 13 | 1 |
| `nexus_economy.tests.test_wallet_views` | 1 | 10 | 1 |
| `nexus_economy.urls` | 1 | 3 | 2 |
| `nexus_economy.urls.finance` | 1 | 5 | 1 |
| `nexus_economy.urls.wallet` | 1 | 5 | 2 |
| `nexus_economy.urls.webhooks` | 1 | 5 | 1 |
| `nexus_economy.views` | 1 | 5 | 6 |
| `nexus_economy.views.admin` | 1 | 5 | 2 |
| `nexus_economy.views.finance` | 1 | 5 | 3 |
| `nexus_economy.views.wallet` | 1 | 16 | 4 |
| `nexus_economy.views.webhooks` | 1 | 20 | 2 |

### NEXUS_GATEWAY (12 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_gateway` | 1 | 0 | 5 |
| `nexus_gateway.admin` | 1 | 3 | 1 |
| `nexus_gateway.apps` | 1 | 10 | 1 |
| `nexus_gateway.consumers` | 1 | 12 | 2 |
| `nexus_gateway.middleware` | 1 | 4 | 2 |
| `nexus_gateway.models` | 1 | 0 | 1 |
| `nexus_gateway.receivers` | 1 | 7 | 3 |
| `nexus_gateway.routing` | 1 | 4 | 2 |
| `nexus_gateway.tests` | 1 | 0 | 1 |
| `nexus_gateway.tests.test_consumers` | 1 | 15 | 1 |
| `nexus_gateway.tests.test_receivers` | 1 | 8 | 1 |
| `nexus_gateway.views` | 1 | 0 | 1 |

### NEXUS_SOCIAL (41 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_social` | 1 | 0 | 24 |
| `nexus_social.admin` | 1 | 3 | 1 |
| `nexus_social.apps` | 1 | 5 | 1 |
| `nexus_social.consumers` | 1 | 11 | 2 |
| `nexus_social.logging` | 1 | 5 | 3 |
| `nexus_social.management` | 1 | 0 | 1 |
| `nexus_social.management.commands` | 1 | 0 | 1 |
| `nexus_social.management.commands.cleanup_announcements` | 1 | 10 | 1 |
| `nexus_social.management.commands.replay_social_events` | 1 | 13 | 1 |
| `nexus_social.metrics` | 1 | 1 | 3 |
| `nexus_social.models` | 1 | 9 | 17 |
| `nexus_social.models.chat` | 1 | 5 | 3 |
| `nexus_social.models.cursors` | 1 | 4 | 2 |
| `nexus_social.models.infrastructure` | 1 | 4 | 2 |
| `nexus_social.models.moderation` | 1 | 5 | 2 |
| `nexus_social.models.preferences` | 1 | 4 | 2 |
| `nexus_social.models.projections` | 1 | 3 | 2 |
| `nexus_social.models.sequence` | 1 | 3 | 3 |
| `nexus_social.routing` | 1 | 4 | 2 |
| `nexus_social.serializers` | 1 | 3 | 4 |
| `nexus_social.serializers.social` | 1 | 2 | 4 |
| `nexus_social.services` | 1 | 0 | 7 |
| `nexus_social.services.auto_flag` | 1 | 13 | 2 |
| `nexus_social.services.banner_service` | 1 | 8 | 2 |
| `nexus_social.services.content_filter` | 1 | 3 | 2 |
| `nexus_social.services.event_consumers` | 1 | 17 | 3 |
| `nexus_social.services.push_notifications` | 1 | 11 | 2 |
| `nexus_social.services.sequencer` | 1 | 9 | 3 |
| `nexus_social.services.websocket_emitter` | 1 | 6 | 4 |
| `nexus_social.tasks` | 1 | 8 | 1 |
| `nexus_social.tests` | 1 | 0 | 1 |
| `nexus_social.urls` | 1 | 0 | 1 |
| `nexus_social.urls.social` | 1 | 4 | 1 |
| `nexus_social.urls.users` | 1 | 4 | 1 |
| `nexus_social.views` | 1 | 8 | 4 |
| `nexus_social.views.announcements` | 1 | 7 | 2 |
| `nexus_social.views.chat` | 1 | 18 | 2 |
| `nexus_social.views.events` | 1 | 22 | 2 |
| `nexus_social.views.health` | 1 | 8 | 2 |
| `nexus_social.views.preferences` | 1 | 3 | 2 |
| `nexus_social.views.receipts` | 1 | 17 | 2 |

### NEXUS_TOURNAMENTS (69 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_tournaments` | 1 | 0 | 45 |
| `nexus_tournaments.admin` | 1 | 5 | 1 |
| `nexus_tournaments.apps` | 1 | 4 | 1 |
| `nexus_tournaments.generate_tree` | 1 | 4 | 1 |
| `nexus_tournaments.models` | 1 | 18 | 16 |
| `nexus_tournaments.models.announcement` | 1 | 4 | 2 |
| `nexus_tournaments.models.bracket_seed` | 1 | 4 | 2 |
| `nexus_tournaments.models.dispute` | 1 | 4 | 2 |
| `nexus_tournaments.models.health` | 1 | 4 | 2 |
| `nexus_tournaments.models.invite` | 1 | 6 | 2 |
| `nexus_tournaments.models.leaderboard` | 1 | 4 | 2 |
| `nexus_tournaments.models.league` | 1 | 8 | 2 |
| `nexus_tournaments.models.league_standing` | 1 | 7 | 2 |
| `nexus_tournaments.models.match` | 1 | 5 | 3 |
| `nexus_tournaments.models.moderation` | 1 | 4 | 2 |
| `nexus_tournaments.models.outbox` | 1 | 3 | 2 |
| `nexus_tournaments.models.progression` | 1 | 4 | 2 |
| `nexus_tournaments.models.rules` | 1 | 4 | 2 |
| `nexus_tournaments.models.submission` | 1 | 4 | 2 |
| `nexus_tournaments.models.tournament_template` | 1 | 5 | 2 |
| `nexus_tournaments.models.verification_record` | 1 | 4 | 2 |
| `nexus_tournaments.receivers` | 1 | 13 | 2 |
| `nexus_tournaments.serializers` | 1 | 8 | 8 |
| `nexus_tournaments.serializers.announcements` | 1 | 0 | 2 |
| `nexus_tournaments.serializers.base` | 1 | 0 | 2 |
| `nexus_tournaments.serializers.leagues` | 1 | 2 | 2 |
| `nexus_tournaments.serializers.matches` | 1 | 2 | 2 |
| `nexus_tournaments.serializers.moderation` | 1 | 0 | 2 |
| `nexus_tournaments.serializers.results` | 1 | 0 | 2 |
| `nexus_tournaments.services` | 1 | 0 | 17 |
| `nexus_tournaments.services.announcement_service` | 1 | 7 | 3 |
| `nexus_tournaments.services.bracket_service` | 1 | 10 | 4 |
| `nexus_tournaments.services.diagnostic_service` | 1 | 9 | 3 |
| `nexus_tournaments.services.leaderboard_service` | 1 | 5 | 4 |
| `nexus_tournaments.services.league_service` | 1 | 13 | 5 |
| `nexus_tournaments.services.match_service` | 1 | 14 | 11 |
| `nexus_tournaments.services.participation_service` | 1 | 13 | 4 |
| `nexus_tournaments.services.verification_service` | 1 | 18 | 6 |
| `nexus_tournaments.signals` | 1 | 2 | 11 |
| `nexus_tournaments.tasks` | 1 | 19 | 6 |
| `nexus_tournaments.tests` | 1 | 0 | 1 |
| `nexus_tournaments.tests.test_announcement_moderation` | 1 | 10 | 1 |
| `nexus_tournaments.tests.test_announcement_service` | 1 | 12 | 1 |
| `nexus_tournaments.tests.test_api` | 1 | 10 | 1 |
| `nexus_tournaments.tests.test_final_contract_gaps` | 1 | 18 | 1 |
| `nexus_tournaments.tests.test_invariants` | 1 | 17 | 1 |
| `nexus_tournaments.tests.test_models` | 1 | 13 | 1 |
| `nexus_tournaments.tests.test_ruleset_restrictions` | 1 | 12 | 1 |
| `nexus_tournaments.tests.test_services` | 1 | 22 | 1 |
| `nexus_tournaments.tests.test_tasks` | 1 | 14 | 1 |
| `nexus_tournaments.urls` | 1 | 3 | 2 |
| `nexus_tournaments.urls.leagues` | 1 | 9 | 2 |
| `nexus_tournaments.urls.matches` | 1 | 6 | 1 |
| `nexus_tournaments.urls.moderation` | 1 | 5 | 1 |
| `nexus_tournaments.verification` | 1 | 0 | 7 |
| `nexus_tournaments.verification.load_balancer` | 1 | 11 | 2 |
| `nexus_tournaments.verification.phash` | 1 | 15 | 2 |
| `nexus_tournaments.verification.providers` | 1 | 0 | 4 |
| `nexus_tournaments.verification.providers.base` | 1 | 4 | 3 |
| `nexus_tournaments.verification.providers.google_cloud` | 1 | 11 | 2 |
| `nexus_tournaments.verification.providers.registry` | 1 | 4 | 2 |
| `nexus_tournaments.verification.result` | 1 | 2 | 5 |
| `nexus_tournaments.views` | 1 | 7 | 10 |
| `nexus_tournaments.views.announcements` | 1 | 9 | 3 |
| `nexus_tournaments.views.base` | 1 | 2 | 6 |
| `nexus_tournaments.views.leagues` | 1 | 14 | 3 |
| `nexus_tournaments.views.matches` | 1 | 10 | 4 |
| `nexus_tournaments.views.moderation` | 1 | 14 | 4 |
| `nexus_tournaments.views.results` | 1 | 10 | 4 |

---
*Report generated by Nexus Audit Command Center — 2026-05-24 11:54:05*