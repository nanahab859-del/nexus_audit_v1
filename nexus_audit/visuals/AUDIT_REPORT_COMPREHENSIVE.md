# 🛡️ NEXUS MASTER AUDIT REPORT

**Generated:** 2026-05-24 08:12:54  
**Project:** `/home/yusupha/my_tools/nexus_project_copy`  
**Tier:** 🌐 Tier 2 — ONLINE (Enhanced Mode)  
**Total modules:** 238  
**Physical files:** 211  
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
| Overall fleet health | 💚 **80.2%** (Grade B) |
| Apps audited | 7 |
| Cross-app violations | 13 |
| Violations vs last run | → unchanged (+0) — prev: 13 on 2026-05-24 |
| Allowed communications | 28 |
| Security findings | 111 |
| Ghost files | 5 |
| Circular dependency cycles | 16 |
| Avg cyclomatic complexity | 2.43 |
| Max cyclomatic complexity | 26 |
| Maintainability index | 100.0 |

## 🔄 CRITICAL: CIRCULAR DEPENDENCIES

Circular dependencies prevent clean testing and deployment isolation.

- **[HIGH / INTRA-APP]** `nexus_core.utils → nexus_core.utils.decorators`  
  Apps involved: nexus_core
- **[HIGH / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views.results → nexus_tournaments.views`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.announcements`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.matches`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.moderation`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_tournaments.views → nexus_tournaments.views.leagues`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.refund`  
  Apps involved: nexus_economy
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.payout`  
  Apps involved: nexus_economy
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.escrow`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks → nexus_tournaments.services.diagnostic_service`  
  Apps involved: nexus_tournaments
- **[MEDIUM / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks → nexus_tournaments.services.bracket_service`  
  Apps involved: nexus_tournaments
- **[MEDIUM / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.refund → nexus_economy.services.refund_service`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.payout → nexus_economy.services.forfeiture_service`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_economy.tasks → nexus_economy.tasks.payout → nexus_economy.services.payout_service`  
  Apps involved: nexus_economy
- **[INFO / INTRA-APP]** `nexus_tournaments.models → nexus_tournaments.models.league`  
  Apps involved: nexus_tournaments

## 👻 CRITICAL: GHOST FILES

These files exist on disk but were not scanned by pydeps. They may be dead code or unreachable entry points.

- `nexus_core.management.commands.dispatch_outbox_events`
- `nexus_core.serializers.auth`
- `nexus_core.serializers.token`
- `nexus_core.serializers.users`
- `nexus_tournaments.management.commands.dispatch_outbox_events`

## 🖤 APPLICATION FLEET HEALTH

| App | Score | Grade | Trend | Physical | Audited | Boundary Violations | Security | Ghosts |
| :--- | ---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: |
| **NEXUS_CONTENT** | 💚 92% | A | → | 18 | 21 | 0 | 3 | 0 |
| **NEXUS_CORE** | 💛 64% | D | → | 41 | 44 | 1 | 58 | 4 |
| **NEXUS_ECONOMY** | 💚 93% | A | → | 48 | 56 | 0 | 18 | 0 |
| **NEXUS_GAMING** | 💚 94% | A | → | 7 | 7 | 0 | 2 | 0 |
| **NEXUS_GATEWAY** | 💚 95% | A | → | 9 | 12 | 3 | 7 | 0 |
| **NEXUS_SOCIAL** | ❤️ 57% | F | → | 40 | 41 | 6 | 12 | 0 |
| **NEXUS_TOURNAMENTS** | 💛 67% | D | → | 48 | 57 | 3 | 11 | 1 |

## 🚨 VIOLATIONS

### Cross-App Imports (13 violations)

Direct imports between first-party apps violate strict modularity. Replace with Django signals, Celery tasks, or REST API calls.

| Source Module | Target Module | Recommendation |
| :--- | :--- | :--- |
| `nexus_social.services.event_consumers` | `nexus_core.utils` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.services.event_consumers` | `nexus_core.utils.events` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.services.event_consumers` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.views.events` | `nexus_core.utils.events` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.views.events` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.views.events` | `nexus_core.utils` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_gateway.consumers` | `nexus_tournaments.services.match_service` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_gateway.consumers` | `nexus_tournaments` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_gateway.consumers` | `nexus_tournaments.services` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_core.utils` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_core.utils.feature_flags` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_core.views.games` | `nexus_content` | Replace with Django signal, Celery task, or REST API call. |

### Other Violations (111)

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
| Hardcoded Password | `settings.py` | LOW |
| Hardcoded Password | `settings.py` | LOW |
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
| Django Bootstrap (Exempt) | nexus_social | nexus_core | `nexus_social.apps → nexus_core.utils` |
| Django Bootstrap (Exempt) | nexus_social | nexus_core | `nexus_social.apps → nexus_core.utils.events` |
| Django Bootstrap (Exempt) | nexus_social | nexus_core | `nexus_social.apps → nexus_core` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_gateway | `nexus_gaming.asgi → nexus_gateway` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_social | `nexus_gaming.asgi → nexus_social` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_social | `nexus_gaming.asgi → nexus_social.routing` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_gateway | `nexus_gaming.asgi → nexus_gateway.routing` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_gateway | `nexus_gaming.asgi → nexus_gateway.middleware` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_core | `nexus_gateway.apps → nexus_core.signals` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_tournaments | `nexus_gateway.apps → nexus_tournaments.signals` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_core | `nexus_gateway.apps → nexus_core` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_economy | `nexus_gateway.apps → nexus_economy` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_economy | `nexus_gateway.apps → nexus_economy.signals` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_tournaments | `nexus_gateway.apps → nexus_tournaments` |
| Test Cross-App Import | nexus_gateway | nexus_gaming | `nexus_gateway.tests.test_consumers → nexus_gaming` |
| Test Cross-App Import | nexus_gateway | nexus_gaming | `nexus_gateway.tests.test_consumers → nexus_gaming.asgi` |
| Django Signal | nexus_content | nexus_core | `nexus_content.receivers → nexus_core.signals` |
| Django Signal | nexus_content | nexus_core | `nexus_content.receivers → nexus_core` |
| Django Signal | nexus_tournaments | nexus_economy | `nexus_tournaments.receivers → nexus_economy` |
| Django Signal | nexus_tournaments | nexus_economy | `nexus_tournaments.receivers → nexus_economy.signals` |
| Celery Task | nexus_tournaments | nexus_core | `nexus_tournaments.tasks → nexus_core.utils.feature_flags` |
| Celery Task | nexus_tournaments | nexus_core | `nexus_tournaments.tasks → nexus_core` |
| Celery Task | nexus_tournaments | nexus_core | `nexus_tournaments.tasks → nexus_core.utils` |
| Celery Task | nexus_core | nexus_content | `nexus_core.views.games → nexus_content.tasks` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.receivers → nexus_tournaments.signals` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.receivers → nexus_tournaments` |
| Test Cross-App Import | nexus_economy | nexus_tournaments | `nexus_economy.tests.test_forfeiture → nexus_tournaments` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.tests.test_forfeiture → nexus_tournaments.signals` |

## 📦 DEPENDENCY HEALTH (Tier 2 — Online Scan)

Scanned 120 packages for CVEs (OSV database) and version freshness (PyPI).  
Total CVEs found: **387** | Outdated packages: **42**

### Package Summary

| Package | Installed | Latest | Status | CVEs |
| :--- | :--- | :--- | :--- | :--- |
| `﻿amqp` | 5.3.1 | 5.3.1 | ✅ Current | 0 |
| `async-timeout` | 5.0.1 | 5.0.1 | ✅ Current | 0 |
| `annotated-doc` | 0.0.4 | 0.0.4 | ✅ Current | 0 |
| `Automat` | 25.4.16 | 25.4.16 | ✅ Current | 0 |
| `annotated-types` | 0.7.0 | 0.7.0 | ✅ Current | 0 |
| `attrs` | 26.1.0 | 26.1.0 | ✅ Current | 0 |
| `anyio` | 4.13.0 | 4.13.0 | ✅ Current | 0 |
| `asgiref` | 3.11.1 | 3.11.1 | ✅ Current | 0 |
| `autobahn` | 24.4.2 | 25.12.2 | ⚠️ Outdated | 2 |
| `Authlib` | 1.6.9 | 1.7.2 | ⚠️ Outdated | 13 |
| `billiard` | 4.2.4 | 4.2.4 | ✅ Current | 0 |
| `bcrypt` | 5.0.0 | 5.0.0 | ✅ Current | 0 |
| `cfgv` | 3.5.0 | 3.5.0 | ✅ Current | 0 |
| `certifi` | 2026.2.25 | 2026.5.20 | ⚠️ Outdated | 6 |
| `bleach` | 6.3.0 | 6.3.0 | ✅ Current | 10 |
| `black` | 26.3.1 | 26.5.1 | ⚠️ Outdated | 3 |
| `celery` | 5.6.3 | 5.6.3 | ✅ Current | 4 |
| `channels` | 4.3.2 | 4.3.2 | ✅ Current | 2 |
| `cffi` | 2.0.0 | 2.0.0 | ✅ Current | 0 |
| `channels_redis` | 4.3.0 | 4.3.0 | ✅ Current | 0 |
| `click-didyoumean` | 0.3.1 | 0.3.1 | ✅ Current | 0 |
| `constantly` | 23.10.4 | 23.10.4 | ✅ Current | 0 |
| `click-plugins` | 1.1.1.2 | 1.1.1.2 | ✅ Current | 0 |
| `click` | 8.3.1 | 8.4.1 | ⚠️ Outdated | 0 |
| `click-repl` | 0.3.0 | 0.3.0 | ✅ Current | 0 |
| `cron-descriptor` | 1.4.5 | 2.0.8 | ⚠️ Outdated | 0 |
| `backports-datetime-fromisoformat` | 2.0.3 | 2.0.3 | ✅ Current | 0 |
| `daphne` | 4.2.1 | 4.2.1 | ✅ Current | 0 |
| `distlib` | 0.4.0 | 0.4.0 | ✅ Current | 0 |
| `charset-normalizer` | 3.4.7 | 3.4.7 | ✅ Current | 0 |
| `django-celery-beat` | 2.9.0 | 2.9.0 | ✅ Current | 0 |
| `django-ratelimit` | 4.1.0 | 4.1.0 | ✅ Current | 0 |
| `django-timezone-field` | 7.2.1 | 7.2.1 | ✅ Current | 0 |
| `djangorestframework` | 3.17.1 | 3.17.1 | ✅ Current | 3 |
| `exceptiongroup` | 1.3.1 | 1.3.1 | ✅ Current | 0 |
| `dparse` | 0.6.4 | 0.6.4 | ✅ Current | 2 |
| `djangorestframework_simplejwt` | 5.5.1 | 5.5.1 | ✅ Current | 1 |
| `h11` | 0.16.0 | 0.16.0 | ✅ Current | 1 |
| `cryptography` | 46.0.6 | 48.0.0 | ⚠️ Outdated | 30 |
| `hyperlink` | 21.0.0 | 21.0.0 | ✅ Current | 0 |
| `filelock` | 3.25.2 | 3.29.0 | ⚠️ Outdated | 2 |
| `identify` | 2.6.18 | 2.6.19 | ⚠️ Outdated | 0 |
| `iniconfig` | 2.3.0 | 2.3.0 | ✅ Current | 0 |
| `Incremental` | 24.11.0 | 24.11.0 | ✅ Current | 0 |
| `imagehash` | 4.3.1 | 4.3.2 | ⚠️ Outdated | 0 |
| `idna` | 3.11 | 3.16 | ⚠️ Outdated | 3 |
| `joblib` | 1.5.3 | 1.5.3 | ✅ Current | 3 |
| `jsonschema` | 4.19.0 | 4.26.0 | ⚠️ Outdated | 0 |
| `Jinja2` | 3.1.6 | 3.1.6 | ✅ Current | 16 |
| `jsonschema-specifications` | 2025.9.1 | 2025.9.1 | ✅ Current | 0 |
| `kombu` | 5.6.2 | 5.6.2 | ✅ Current | 0 |
| `markdown-it-py` | 4.0.0 | 4.2.0 | ⚠️ Outdated | 4 |
| `Django` | 5.2.12 | 6.0.5 | ⚠️ Outdated | 0 |
| `MarkupSafe` | 3.0.3 | 3.0.3 | ✅ Current | 0 |
| `marshmallow` | 4.3.0 | 4.3.0 | ✅ Current | 3 |
| `mypy_extensions` | 1.1.0 | 1.1.0 | ✅ Current | 0 |
| `google-cloud-vision` | 3.7.4 | 3.14.0 | ⚠️ Outdated | 0 |
| `msgpack` | 1.1.2 | 1.1.2 | ✅ Current | 0 |
| `nodeenv` | 1.10.0 | 1.10.0 | ✅ Current | 0 |
| `packaging` | 26.0 | 26.2 | ⚠️ Outdated | 0 |
| `pathspec` | 1.0.4 | 1.1.1 | ⚠️ Outdated | 0 |
| `platformdirs` | 4.9.4 | 4.9.6 | ⚠️ Outdated | 0 |
| `pluggy` | 1.6.0 | 1.6.0 | ✅ Current | 0 |
| `nltk` | 3.9.4 | 3.9.4 | ✅ Current | 21 |
| `pre_commit` | 4.5.1 | 4.6.0 | ⚠️ Outdated | 0 |
| `prometheus_client` | 0.25.0 | 0.25.0 | ✅ Current | 0 |
| `prompt_toolkit` | 3.0.52 | 3.0.52 | ✅ Current | 0 |
| `pyasn1_modules` | 0.4.2 | 0.4.2 | ✅ Current | 0 |
| `pycparser` | 3.0 | 3.0 | ✅ Current | 0 |
| `psycopg2-binary` | 2.9.11 | 2.9.12 | ⚠️ Outdated | 0 |
| `mdurl` | 0.1.2 | 0.1.2 | ✅ Current | 0 |
| `pyasn1` | 0.6.3 | 0.6.3 | ✅ Current | 2 |
| `pydantic` | 2.12.5 | 2.13.4 | ⚠️ Outdated | 3 |
| `Pygments` | 2.20.0 | 2.20.0 | ✅ Current | 9 |
| `pyotp` | 2.9.0 | 2.9.0 | ✅ Current | 0 |
| `PyJWT` | 2.12.1 | 2.13.0 | ⚠️ Outdated | 8 |
| `pyOpenSSL` | 26.0.0 | 26.2.0 | ⚠️ Outdated | 8 |
| `python-crontab` | 3.3.0 | 3.3.0 | ✅ Current | 0 |
| `pytest-django` | 4.12.0 | 4.12.0 | ✅ Current | 0 |
| `Pillow` | 10.4.0 | 12.2.0 | ⚠️ Outdated | 118 |
| `pytest` | 9.0.3 | 9.0.3 | ✅ Current | 1 |
| `python-dateutil` | 2.9.0.post0 | 2.9.0.post0 | ✅ Current | 0 |
| `pydantic_core` | 2.41.5 | 2.47.0 | ⚠️ Outdated | 0 |
| `python-discovery` | 1.2.2 | 1.3.1 | ⚠️ Outdated | 0 |
| `pytokens` | 0.4.1 | 0.4.1 | ✅ Current | 0 |
| `referencing` | 0.37.0 | 0.37.0 | ✅ Current | 0 |
| `redis` | 7.4.0 | 7.4.0 | ✅ Current | 4 |
| `requests` | 2.33.1 | 2.34.2 | ⚠️ Outdated | 13 |
| `rich` | 14.3.3 | 15.0.0 | ⚠️ Outdated | 0 |
| `safety-schemas` | 0.0.16 | 0.0.18 | ⚠️ Outdated | 0 |
| `service-identity` | 24.2.0 | 24.2.0 | ✅ Current | 0 |
| `regex` | 2026.4.4 | 2026.5.9 | ⚠️ Outdated | 0 |
| `shellingham` | 1.5.4 | 1.5.4 | ✅ Current | 0 |
| `sentry-sdk` | 2.58.0 | 2.60.0 | ⚠️ Outdated | 2 |
| `ruamel.yaml` | 0.19.1 | 0.19.1 | ✅ Current | 0 |
| `six` | 1.17.0 | 1.17.0 | ✅ Current | 0 |
| `PyYAML` | 6.0.3 | 6.0.3 | ✅ Current | 0 |
| `structlog` | 25.5.0 | 25.5.0 | ✅ Current | 0 |
| `sqlparse` | 0.5.5 | 0.5.5 | ✅ Current | 6 |
| `tenacity` | 9.1.4 | 9.1.4 | ✅ Current | 0 |
| `tomli` | 2.4.1 | 2.4.1 | ✅ Current | 0 |
| `tomlkit` | 0.14.0 | 0.15.0 | ⚠️ Outdated | 0 |
| `txaio` | 25.9.2 | 25.12.2 | ⚠️ Outdated | 0 |
| `tqdm` | 4.67.3 | 4.67.3 | ✅ Current | 3 |
| `ruff` | 0.15.9 | 0.15.14 | ⚠️ Outdated | 0 |
| `rpds-py` | 0.30.0 | 0.30.0 | ✅ Current | 0 |
| `safety` | 3.7.0 | 3.7.0 | ✅ Current | 0 |
| `typer` | 0.24.1 | 0.25.1 | ⚠️ Outdated | 0 |
| `typing-inspection` | 0.4.2 | 0.4.2 | ✅ Current | 0 |
| `Twisted` | 25.5.0 | 26.4.0 | ⚠️ Outdated | 28 |
| `typing_extensions` | 4.15.0 | 4.15.0 | ✅ Current | 0 |
| `tzdata` | 2025.3 | 2026.2 | ⚠️ Outdated | 0 |
| `tzlocal` | 5.3.1 | 5.3.1 | ✅ Current | 0 |
| `wcwidth` | 0.6.0 | 0.7.0 | ⚠️ Outdated | 0 |
| `vine` | 5.1.0 | 5.1.0 | ✅ Current | 0 |
| `websocket-client` | 1.9.0 | 1.9.0 | ✅ Current | 0 |
| `virtualenv` | 21.2.0 | 21.3.3 | ⚠️ Outdated | 5 |
| `urllib3` | 2.6.3 | 2.7.0 | ⚠️ Outdated | 32 |
| `zope.interface` | 8.2 | 8.4 | ⚠️ Outdated | 0 |
| `numpy` | 1.26.4 | 2.4.6 | ⚠️ Outdated | 16 |

## 🔒 SECURITY FINDINGS

Bandit scan found 111 issue(s). Test-file findings are excluded from health scoring.

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
| **LOW** | `settings.py` | 104 | B105: Possible hardcoded password: 'nexus_pass' |
| **LOW** | `settings.py` | 183 | B105: Possible hardcoded password: 'nexus_core.serializers.token.NexusTokenObtainPairSerializer' |
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
| Average cyclomatic complexity | 2.43 |
| Maximum cyclomatic complexity | 26 |
| Maintainability index | 100.0 |
| Functions analysed | 1655 |

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
| `MarkReadView` | `receipts.py` | 13 | 0 |
| `generate_single_elimination` | `bracket_service.py` | 13 | 0 |
| `_run_ai_verification` | `verification_service.py` | 13 | 0 |
| `auto_snatcher_backfill` | `tasks.py` | 13 | 0 |
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

### [HIGH] Refactor: move events to correct app

```json
{
  "title": "Relocate event utilities from core to social app",
  "why_harmful": "This direct import creates a tight coupling where `nexus_social` is dependent on the internal implementation details of `nexus_

**Action:** Move nexus_core.utils.events to nexus_core or appropriate shared module.

**Affected modules:** `nexus_social.services.event_consumers`, `nexus_social.views.events`

### [HIGH] Refactor: move utils to correct app

```json
{
  "title": "Relocate generic utilities from `nexus_core` to `nexus_common`",
  "why_harmful": "Direct import of `nexus_core.utils` creates a tight compile-time coupling between `

**Action:** Move nexus_core.utils to nexus_core or appropriate shared module.

**Affected modules:** `nexus_social.services.event_consumers`, `nexus_social.views.events`, `nexus_tournaments.services.verification_service`

### [HIGH] Refactor: move match_service to correct app

```json
{
  "title": "Refactor nexus_gateway to consume nexus_tournaments API",
  "why_harmful": "This direct import tightly couples `nexus_gateway` to the internal implementation details of `nexus_tournaments.

**Action:** Move nexus_tournaments.services.match_service to nexus_core or appropriate shared module.

**Affected modules:** `nexus_gateway.consumers`

### [HIGH] Refactor: move nexus_core to correct app

```json
{
  "title": "Relocate shared utility from nexus_core to nexus_utils",
  "why_harmful": "This direct import creates tight coupling between `nexus_core` and both `nexus_social` and `nexus_tour

**Action:** Move nexus_core to nexus_core or appropriate shared module.

**Affected modules:** `nexus_social.services.event_consumers`, `nexus_social.views.events`, `nexus_tournaments.services.verification_service`

### [HIGH] Redirect nexus_tournaments imports from nexus_gateway



**Action:** 

**Affected modules:** `nexus_gateway.consumers`

### [HIGH] NEXUS_CORE — Health Analysis

**NEXUS_CORE Health Narrative:**

Nexus_

**Action:** Fix 1 boundary violation(s) first (+3 pts), then 58 security finding(s) (+174 pts). Projected score: 100%.

**Affected modules:** `nexus_core`, `nexus_core.utils`, `nexus_core.utils.events`, `nexus_core.signals`, `nexus_core.utils.feature_flags`

### [HIGH] NEXUS_SOCIAL — Health Analysis

**Health Narrative:**
The 57.0

**Action:** Fix 6 boundary violation(s) first (+30 pts), then 12 security finding(s) (+36 pts). Projected score: 100%.

**Affected modules:** `nexus_social`, `nexus_social.admin`, `nexus_social.apps`, `nexus_social.consumers`, `nexus_social.logging`

### [HIGH] NEXUS_TOURNAMENTS — Health Analysis

The 66.66% score is primarily driven by 3 boundary violations, costing 15 points, and 11 security vulnerabilities, costing 33 points. The highest priority fix is addressing the security vulnerabilities (gain 33 points), followed by resolving the boundary violations (gain 15 points). After these fixes, nexus_tournaments' score will be 81.66%. Leaving these unfixed poses a significant risk of data breaches and unauthorized access due to exploitable security flaws and architectural inconsistencies.

---

**ACTIONABLE GUIDANCE FOR NEXUS_TOURNAMENTS**

**1. Address Security Vulnerabilities (11 issues, -33 pts)**

*   **Problem:** Numerous security vulnerabilities identified. Specifics are not detailed here but are assumed to be common issues like SQL injection, XSS, insecure direct object references, etc., within `nexus_tournaments`.
*   **Action:** Conduct a thorough security audit of all `nexus_tournaments` code, focusing on input validation, output encoding, authentication, and authorization checks.
    *   **Specific Code Changes:**
        *   **`nexus_tournaments/views.py`:** Review all view functions for proper input sanitization (e.g., using `django.utils.safestring.mark_safe` judiciously, validating user-provided data against expected types and formats). Implement robust permission checks using `django.contrib.

**Action:** Fix 3 boundary violation(s) first (+15 pts), then 11 security finding(s) (+33 pts). Projected score: 100%.

**Affected modules:** `nexus_tournaments`, `nexus_tournaments.services`, `nexus_tournaments.services.match_service`, `nexus_tournaments.signals`, `nexus_tournaments.admin`

### [HIGH] Extract Shared Utility: nexus_core.utils

`nexus_core.utils` is imported by 2 app(s) (nexus_tournaments, nexus_social) as a cross-app violation. One refactor eliminates all 2 violations.

**Action:** Here's the extraction plan for `nexus_core.utils`:

1.  **New Module Path:** `nexus_shared.utils`

2.  **Changes in `nexus_core.utils`:**
    *   Identify functions/classes in `nexus_core.utils` that are *not* strictly related to core authentication, user models, tokens, middleware, or serializers.
    *   Move these identified functions/classes to `nexus_shared.utils`.
    *   Update `nexus_core.utils` to import from `nexus_shared.utils` for any moved functionality it now depends on.
    *   **Example:** If `nexus_core.utils` contains a generic `send_email` function, move it to `nexus_shared.utils`. `nexus_core.utils` would then import `send_email` from `nexus_shared.utils`.

3.  **Updating Importing Apps:**
    *   **`nexus_tournaments`:**
        *   Locate all imports of `from nexus_core.utils import ...`.
        *   Replace them with `from nexus_shared.utils import ...`.
        *   **File Example:** `nexus_tournaments/services.py` might change from `from nexus_core.utils import format_datetime` to `from nexus_shared.utils import format_datetime`.
    *   **`nexus_social`:**
        *   Locate all imports of `from nexus_core.utils import ...`.
        *   Replace them with `from nexus_shared.utils import ...`.
        *   **File Example:** `nexus_social/models.py` might change from `from nexus_core.utils import generate_unique_id` to `from nexus_shared.utils import generate_unique_id`.

4.  **Migration Order:**
    *

**Affected modules:** `nexus_core.utils`, `nexus_tournaments`, `nexus_social`

### [HIGH] Extract Shared Utility: nexus_core

`nexus_core` is imported by 2 app(s) (nexus_tournaments, nexus_social) as a cross-app violation. One refactor eliminates all 2 violations.

**Action:** **Shared Utility Extraction Plan**

**Problem:** A utility module currently in

**Affected modules:** `nexus_core`, `nexus_tournaments`, `nexus_social`

### [HIGH] Upgrade autobahn: 24.4.2 → 25.12.2



**Action:** pip install autobahn==25.12.2

Breaking changes: None known. Autobahn's core API for WebSocket clients and servers is generally stable. Focus on ensuring existing WebSocket connections and message handling logic remain functional.

Verify: python manage.py test nexus_gateway

**Affected modules:** `autobahn`

### [HIGH] Upgrade Authlib: 1.6.9 → 1.7.2



**Action:** pip install "Authlib>=1.7.2,<1.8.0"

Breaking changes: None known. Authlib 1.7.x is a minor release with backward-compatible changes. Focus on testing OAuth flows and token validation, which are core to nexus_core.

Verify: python manage.py test nexus_core nexus_gateway

**Affected modules:** `Authlib`

### [HIGH] Upgrade certifi: 2026.2.25 → 2026.5.20



**Action:** pip install certifi==2026.5.20

Breaking changes: None known. Certifi is a dependency for SSL certificate validation and typically does not introduce breaking changes in its minor version updates that would affect Django or Celery usage.

Verify: python manage.py test nexus_core.tests.test_ssl_validation

**Affected modules:** `certifi`

### [HIGH] Upgrade black: 26.3.1 → 26.5.1



**Action:** pip install black==26.5.1

Breaking changes: None known. Black is a code formatter and does not typically introduce breaking changes to application logic or Django/Celery functionality.

Verify: black --check .

**Affected modules:** `black`

### [HIGH] Upgrade cryptography: 46.0.6 → 48.0.0



**Action:** pip install cryptography==48.0.0

Breaking changes: None known. The cryptography library is a low-level dependency. Direct impact on Django or Celery usage is highly unlikely unless specific, advanced cryptographic primitives are being used in a way that has been deprecated or altered in the new version. Standard usage should be unaffected.

Verify: python manage.py test

**Affected modules:** `cryptography`

### [MEDIUM] Upgrade click: 8.3.1 → 8.4.1



**Action:** pip install click==8.4.1

Breaking changes: None known. Click is a dependency for CLI tools and management commands. Version 8.4.1 is a minor release and typically maintains backward compatibility for core functionality. No direct impact on Django ORM, views, or Celery tasks is anticipated.

Verify: python manage.py test nexus_core nexus_economy nexus_gaming nexus_gateway nexus_tournaments nexus_social nexus_content

**Affected modules:** `click`

### [MEDIUM] Upgrade cron-descriptor: 1.4.5 → 2.0.8



**Action:** pip install "cron-descriptor>=2.0.8,<2.1.0"

Breaking changes: None known. The changelog for 2.0.0 indicates a focus on internal refactoring and bug fixes, with no explicit mention of API changes that would impact typical usage within Django or Celery.

Verify: python manage.py shell -c "from cron_descriptor import get_description; assert get_description('* * * * *') == 'Every minute'"

**Affected modules:** `cron-descriptor`

### [HIGH] Upgrade filelock: 3.25.2 → 3.29.0



**Action:** pip install filelock==3.29.0

Breaking changes: None known. filelock is a low-level utility library, and changes between these minor versions are highly unlikely to introduce breaking changes for typical Django/Celery usage.

Verify: python manage.py test nexus_core nexus_economy nexus_gaming nexus_gateway nexus_tournaments nexus_social nexus_content

**Affected modules:** `filelock`

### [MEDIUM] Upgrade identify: 2.6.18 → 2.6.19



**Action:** pip install identify==2.6.19

Breaking changes: None known

Verify: python manage.py test nexus_core nexus_economy nexus_gaming nexus_gateway nexus_tournaments nexus_social nexus_content

**Affected modules:** `identify`

### [HIGH] Upgrade idna: 3.11 → 3.16



**Action:** pip install idna==3.16

Breaking changes: None known. The idna library primarily handles Internationalized Domain Names in Applications. Changes between these minor versions are unlikely to introduce breaking changes for typical Django or Celery usage, which rely on it indirectly for network operations.

Verify: python manage.py test nexus_core

**Affected modules:** `idna`

### [MEDIUM] Upgrade imagehash: 4.3.1 → 4.3.2



**Action:** pip install imagehash==4.3.2

```json
{
  "upgrade_command": "pip

**Affected modules:** `imagehash`

### [MEDIUM] Upgrade jsonschema: 4.19.0 → 4.26.0



**Action:** pip install jsonschema==4.26.0

Breaking changes: None known. The jsonschema library is primarily used for data validation. No direct API changes are expected to impact typical Django or Celery integrations between these versions.

Verify: python manage.py test nexus_core nexus_economy nexus_gaming nexus_gateway nexus_tournaments nexus_social nexus_content

**Affected modules:** `jsonschema`

### [HIGH] Upgrade markdown-it-py: 4.0.0 → 4.2.0



**Action:** pip install 'markdown-it-py==4.2.0'

Breaking changes: None known. The changelog for markdown-it-py between 4.0.0 and 4.2.0 indicates only bug fixes and minor improvements, with no API-breaking changes relevant to typical Django integrations.

Verify: python manage.py test nexus_content

**Affected modules:** `markdown-it-py`

### [MEDIUM] Upgrade Django: 5.2.12 → 6.0.5



**Action:** pip install "Django>=6.0.5,<6.1"

Breaking changes: None known for typical Django/Celery usage. Django 6.0 introduced minor changes, but most common patterns remain compatible. Review release notes for specific deprecations if custom middleware or complex ORM usage is heavily employed.

Verify: python manage.py test --settings=nexus.settings.test

**Affected modules:** `Django`

### [MEDIUM] Upgrade google-cloud-vision: 3.7.4 → 3.14.0



**Action:** pip install google-cloud-vision==3.14.0

Breaking changes: None known. The core API for image annotation and feature detection is generally stable across minor versions. Thorough testing of any existing image processing logic is recommended, but direct breaking changes impacting Django/Celery integration are unlikely.

Verify: python manage.py test nexus_content

**Affected modules:** `google-cloud-vision`

### [MEDIUM] Upgrade packaging: 26.0 → 26.2



**Action:** pip install packaging==26.2

Breaking changes: None known. The packaging library primarily deals with metadata and version handling, and minor version bumps like this typically do not introduce breaking changes for Django or Celery applications that consume it indirectly.

Verify: python manage.py check

**Affected modules:** `packaging`

### [MEDIUM] Upgrade pathspec: 1.0.4 → 1.1.1



**Action:** pip install pathspec==1.1.1

Breaking changes: None known. The pathspec library is a utility for matching file paths against patterns and is unlikely to have direct breaking changes impacting Django or Celery application logic unless explicitly used in a way that relies on internal implementation details that have changed.

Verify: python manage.py test

**Affected modules:** `pathspec`

### [MEDIUM] Upgrade platformdirs: 4.9.4 → 4.9.6



**Action:** pip install platformdirs==4.9.6

Breaking changes: None known

Verify: python manage.py test nexus_core nexus_economy nexus_gaming nexus_gateway nexus_tournaments nexus_social nexus_content

**Affected modules:** `platformdirs`

### [MEDIUM] Upgrade pre_commit: 4.5.1 → 4.6.0



**Action:** pip install pre_commit==4.6.0

```json
{
  "upgrade_command": "pip install pre_

**Affected modules:** `pre_commit`

### [HIGH] Upgrade pydantic: 2.12.5 → 2.13.4



**Action:** pip install pydantic==2.13.4

```json
{
  "upgrade_command": "pip

**Affected modules:** `pydantic`

### [MEDIUM] Upgrade psycopg2-binary: 2.9.11 → 2.9.12



**Action:** pip install psycopg2-binary==2.9.12

```json
{
  "upgrade_command": "pip install psycopg2

**Affected modules:** `psycopg2-binary`

### [HIGH] Upgrade PyJWT: 2.12.1 → 2.13.0



**Action:** pip install PyJWT==2.13.0

```json
{
  "upgrade_command": "pip

**Affected modules:** `PyJWT`

### [HIGH] Upgrade pyOpenSSL: 26.0.0 → 26.2.0



**Action:** pip install pyOpenSSL==26.2.0

```json
{
  "upgrade_command": "pip install py

**Affected modules:** `pyOpenSSL`

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
| `nexus_content.tasks` | 1 | 17 | 4 |
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
| `nexus_core` | 1 | 0 | 26 |
| `nexus_core.admin` | 1 | 3 | 1 |
| `nexus_core.apps` | 1 | 4 | 1 |
| `nexus_core.generate_tree` | 1 | 4 | 1 |
| `nexus_core.middleware` | 1 | 5 | 1 |
| `nexus_core.models` | 1 | 8 | 7 |
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
| `nexus_core.utils.events` | 1 | 6 | 4 |
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

### NEXUS_GAMING (7 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_gaming` | 1 | 1 | 2 |
| `nexus_gaming.asgi` | 1 | 9 | 2 |
| `nexus_gaming.celery` | 1 | 1 | 2 |
| `nexus_gaming.generate_tree` | 1 | 4 | 1 |
| `nexus_gaming.settings` | 1 | 4 | 1 |
| `nexus_gaming.urls` | 1 | 4 | 1 |
| `nexus_gaming.wsgi` | 1 | 4 | 1 |

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
| `nexus_social` | 1 | 0 | 23 |
| `nexus_social.admin` | 1 | 3 | 1 |
| `nexus_social.apps` | 1 | 5 | 1 |
| `nexus_social.consumers` | 1 | 7 | 2 |
| `nexus_social.logging` | 1 | 5 | 3 |
| `nexus_social.management` | 1 | 0 | 1 |
| `nexus_social.management.commands` | 1 | 0 | 1 |
| `nexus_social.management.commands.cleanup_announcements` | 1 | 10 | 1 |
| `nexus_social.management.commands.replay_social_events` | 1 | 13 | 1 |
| `nexus_social.metrics` | 1 | 1 | 3 |
| `nexus_social.models` | 1 | 9 | 16 |
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
| `nexus_social.tasks` | 1 | 0 | 1 |
| `nexus_social.tests` | 1 | 0 | 1 |
| `nexus_social.urls` | 1 | 0 | 1 |
| `nexus_social.urls.social` | 1 | 4 | 1 |
| `nexus_social.urls.users` | 1 | 4 | 1 |
| `nexus_social.views` | 1 | 8 | 4 |
| `nexus_social.views.announcements` | 1 | 7 | 2 |
| `nexus_social.views.chat` | 1 | 17 | 2 |
| `nexus_social.views.events` | 1 | 22 | 2 |
| `nexus_social.views.health` | 1 | 8 | 2 |
| `nexus_social.views.preferences` | 1 | 3 | 2 |
| `nexus_social.views.receipts` | 1 | 17 | 2 |

### NEXUS_TOURNAMENTS (57 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_tournaments` | 1 | 0 | 39 |
| `nexus_tournaments.admin` | 1 | 5 | 1 |
| `nexus_tournaments.apps` | 1 | 4 | 1 |
| `nexus_tournaments.generate_tree` | 1 | 4 | 1 |
| `nexus_tournaments.models` | 1 | 15 | 16 |
| `nexus_tournaments.models.announcement` | 1 | 4 | 2 |
| `nexus_tournaments.models.dispute` | 1 | 4 | 2 |
| `nexus_tournaments.models.health` | 1 | 4 | 2 |
| `nexus_tournaments.models.invite` | 1 | 6 | 2 |
| `nexus_tournaments.models.leaderboard` | 1 | 4 | 2 |
| `nexus_tournaments.models.league` | 1 | 8 | 2 |
| `nexus_tournaments.models.match` | 1 | 5 | 3 |
| `nexus_tournaments.models.moderation` | 1 | 4 | 2 |
| `nexus_tournaments.models.outbox` | 1 | 3 | 2 |
| `nexus_tournaments.models.progression` | 1 | 4 | 2 |
| `nexus_tournaments.models.rules` | 1 | 4 | 2 |
| `nexus_tournaments.models.submission` | 1 | 4 | 2 |
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
| `nexus_tournaments.services.verification_service` | 1 | 13 | 6 |
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
| `nexus_tournaments.tests.test_services` | 1 | 19 | 1 |
| `nexus_tournaments.tests.test_tasks` | 1 | 14 | 1 |
| `nexus_tournaments.urls` | 1 | 3 | 2 |
| `nexus_tournaments.urls.leagues` | 1 | 9 | 2 |
| `nexus_tournaments.urls.moderation` | 1 | 5 | 1 |
| `nexus_tournaments.views` | 1 | 7 | 9 |
| `nexus_tournaments.views.announcements` | 1 | 9 | 3 |
| `nexus_tournaments.views.base` | 1 | 2 | 6 |
| `nexus_tournaments.views.leagues` | 1 | 14 | 3 |
| `nexus_tournaments.views.matches` | 1 | 10 | 3 |
| `nexus_tournaments.views.moderation` | 1 | 14 | 4 |
| `nexus_tournaments.views.results` | 1 | 10 | 3 |

---
*Report generated by Nexus Audit Command Center — 2026-05-24 08:12:54*