# 🛡️ NEXUS MASTER AUDIT REPORT

**Generated:** 2026-05-05 23:25:37  
**Project:** `/home/yusupha/my_tools/nexus_project_copy`  
**Tier:** 🌐 Tier 2 — ONLINE (Enhanced Mode)  
**Total modules:** 160  
**Physical files:** 139  
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
| Ai Recommendations | ⭕ Offline only |

## 📊 Executive Summary

| Metric | Value |
| :--- | :--- |
| Overall fleet health | 💚 **92.0%** (Grade A) |
| Apps audited | 7 |
| Cross-app violations | 9 |
| Violations vs last run | → unchanged (+0) — prev: 9 on 2026-05-03 |
| Allowed communications | 19 |
| Security findings | 85 |
| Ghost files | 8 |
| Circular dependency cycles | 5 |
| Avg cyclomatic complexity | 2.30 |
| Max cyclomatic complexity | 21 |
| Maintainability index | 100.0 |

## 🔄 CRITICAL: CIRCULAR DEPENDENCIES

Circular dependencies prevent clean testing and deployment isolation.

- **[HIGH / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks`  
  Apps involved: nexus_tournaments
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.services.payout_service`  
  Apps involved: nexus_economy
- **[HIGH / INTRA-APP]** `nexus_economy.tasks → nexus_economy.services.refund_service`  
  Apps involved: nexus_economy
- **[MEDIUM / INTRA-APP]** `nexus_tournaments.services.match_service → nexus_tournaments.tasks → nexus_tournaments.services.diagnostic_service`  
  Apps involved: nexus_tournaments
- **[INFO / INTRA-APP]** `nexus_tournaments.models → nexus_tournaments.models.league`  
  Apps involved: nexus_tournaments

## 👻 CRITICAL: GHOST FILES

These files exist on disk but were not scanned by pydeps. They may be dead code or unreachable entry points.

- `nexus_core.management.commands.dispatch_outbox_events`
- `nexus_core.serializers.auth`
- `nexus_core.serializers.users`
- `nexus_social.management.commands.replay_social_events`
- `nexus_social.services.banner_service`
- `nexus_social.services.event_consumers`
- `nexus_social.services.sequencer`
- `nexus_tournaments.management.commands.dispatch_outbox_events`

## 🖤 APPLICATION FLEET HEALTH

| App | Score | Grade | Trend | Physical | Audited | Boundary Violations | Security | Ghosts |
| :--- | ---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: |
| **NEXUS_CONTENT** | 💚 100% | A | → | 6 | 6 | 0 | 0 | 0 |
| **NEXUS_CORE** | 💚 86% | B | → | 28 | 32 | 1 | 55 | 3 |
| **NEXUS_ECONOMY** | 💚 95% | A | → | 29 | 37 | 1 | 15 | 0 |
| **NEXUS_GAMING** | 💚 91% | A | → | 12 | 12 | 0 | 3 | 0 |
| **NEXUS_GATEWAY** | 💚 100% | A | → | 9 | 12 | 0 | 2 | 0 |
| **NEXUS_SOCIAL** | 💛 79% | C | → | 20 | 18 | 2 | 2 | 4 |
| **NEXUS_TOURNAMENTS** | 💚 93% | A | → | 35 | 43 | 1 | 8 | 1 |

## 🚨 VIOLATIONS

### Cross-App Imports (9 violations)

Direct imports between first-party apps violate strict modularity. Replace with Django signals, Celery tasks, or REST API calls.

| Source Module | Target Module | Recommendation |
| :--- | :--- | :--- |
| `nexus_social.api_events` | `nexus_gaming` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.api_events` | `nexus_gaming.events` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.models.sequence` | `nexus_core.models` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_social.models.sequence` | `nexus_core` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_gaming` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_tournaments.services.verification_service` | `nexus_gaming.feature_flags` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_core.views.users` | `nexus_gaming` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_core.views.users` | `nexus_gaming.decorators` | Replace with Django signal, Celery task, or REST API call. |
| `nexus_economy.views.webhooks` | `nexus_gateway` | Replace with Django signal, Celery task, or REST API call. |

### Other Violations (85)

| Type | Source | Severity |
| :--- | :--- | :--- |
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
| Hardcoded Password | `settings.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Hardcoded Password | `test_consumers.py` | LOW |
| Bare Except | `apps.py` | LOW |
| Hardcoded Password | `test_notification_preferences.py` | LOW |
| Hardcoded Password | `test_announcement_moderation.py` | LOW |
| Hardcoded Password | `test_announcement_service.py` | LOW |
| Hardcoded Password | `test_api.py` | LOW |
| Hardcoded Password | `test_invariants.py` | LOW |
| Hardcoded Password | `test_models.py` | LOW |
| Hardcoded Password | `test_ruleset_restrictions.py` | LOW |
| Hardcoded Password | `test_services.py` | LOW |
| Hardcoded Password | `test_tasks.py` | LOW |

## 🔗 ALLOWED CROSS-APP COMMUNICATIONS

These cross-app interactions use decoupled communication patterns and are permitted.

| Type | Source App | Target App | Details |
| :--- | :--- | :--- | :--- |
| Django Bootstrap (Exempt) | nexus_social | nexus_gaming | `nexus_social.apps → nexus_gaming` |
| Django Bootstrap (Exempt) | nexus_social | nexus_gaming | `nexus_social.apps → nexus_gaming.events` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_gateway | `nexus_gaming.asgi → nexus_gateway.routing` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_gateway | `nexus_gaming.asgi → nexus_gateway` |
| Django Bootstrap (Exempt) | nexus_gaming | nexus_gateway | `nexus_gaming.asgi → nexus_gateway.middleware` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_tournaments | `nexus_gateway.apps → nexus_tournaments.signals` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_core | `nexus_gateway.apps → nexus_core` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_tournaments | `nexus_gateway.apps → nexus_tournaments` |
| Django Bootstrap (Exempt) | nexus_gateway | nexus_core | `nexus_gateway.apps → nexus_core.signals` |
| Test Cross-App Import | nexus_gateway | nexus_gaming | `nexus_gateway.tests.test_consumers → nexus_gaming` |
| Test Cross-App Import | nexus_gateway | nexus_gaming | `nexus_gateway.tests.test_consumers → nexus_gaming.asgi` |
| Celery Task | nexus_tournaments | nexus_gaming | `nexus_tournaments.tasks → nexus_gaming` |
| Celery Task | nexus_tournaments | nexus_gaming | `nexus_tournaments.tasks → nexus_gaming.feature_flags` |
| Test Cross-App Import | nexus_tournaments | nexus_core | `nexus_tournaments.tests.test_announcement_service → nexus_core.models` |
| Test Cross-App Import | nexus_tournaments | nexus_core | `nexus_tournaments.tests.test_announcement_service → nexus_core` |
| Django Bootstrap (Exempt) | nexus_economy | nexus_tournaments | `nexus_economy.apps → nexus_tournaments.signals` |
| Django Bootstrap (Exempt) | nexus_economy | nexus_tournaments | `nexus_economy.apps → nexus_tournaments` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.receivers → nexus_tournaments.signals` |
| Django Signal | nexus_economy | nexus_tournaments | `nexus_economy.receivers → nexus_tournaments` |

## 📦 DEPENDENCY HEALTH (Tier 2 — Online Scan)

Scanned 12 packages for CVEs (OSV database) and version freshness (PyPI).  
Total CVEs found: **215** | Outdated packages: **2**

### Package Summary

| Package | Installed | Latest | Status | CVEs |
| :--- | :--- | :--- | :--- | :--- |
| `django` | 5.2.13 | 6.0.5 | ⚠️ Outdated | 0 |
| `celery` | unknown | 5.6.3 | — Not installed | 4 |
| `channels` | unknown | 4.3.2 | — Not installed | 2 |
| `djangorestframework` | unknown | 3.17.1 | — Not installed | 3 |
| `redis` | unknown | 7.4.0 | — Not installed | 4 |
| `psycopg2` | unknown | 2.9.12 | — Not installed | 0 |
| `Pillow` | unknown | 12.2.0 | — Not installed | 118 |
| `cryptography` | 46.0.7 | 48.0.0 | ⚠️ Outdated | 28 |
| `requests` | 2.33.1 | 2.33.1 | ✅ Current | 13 |
| `urllib3` | 2.6.3 | 2.6.3 | ✅ Current | 28 |
| `pyjwt` | unknown | 2.12.1 | — Not installed | 6 |
| `paramiko` | unknown | 4.0.0 | — Not installed | 9 |

## 🔒 SECURITY FINDINGS

Bandit scan found 85 issue(s). Test-file findings are excluded from health scoring.

| Severity | File | Line | Issue |
| :---: | :--- | ---: | :--- |
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
| **LOW** | `test_new_endpoints.py` | 221 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 223 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_new_endpoints.py` | 241 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 243 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_new_endpoints.py` | 273 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 275 | B106: Possible hardcoded password: 'tok2' |
| **LOW** | `test_new_endpoints.py` | 305 | B106: Possible hardcoded password: 'tok1' |
| **LOW** | `test_new_endpoints.py` | 327 | B106: Possible hardcoded password: 'tok1' |
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
| **LOW** | `test_users.py` | 110 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_users.py` | 165 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `admin_panel.py` | 114 | B110: Try, Except, Pass detected. |
| **LOW** | `auth.py` | 581 | B110: Try, Except, Pass detected. |
| **LOW** | `auth.py` | 604 | B110: Try, Except, Pass detected. |
| **LOW** | `auth.py` | 678 | B110: Try, Except, Pass detected. |
| **LOW** | `test_financial_integrity.py` | 41 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_financial_integrity.py` | 214 | B106: Possible hardcoded password: 'wave_token' |
| **LOW** | `test_financial_integrity.py` | 265 | B106: Possible hardcoded password: 'wave_token' |
| **LOW** | `test_full_tournament.py` | 44 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_full_tournament.py` | 159 | B106: Possible hardcoded password: 'token' |
| **LOW** | `test_full_tournament.py` | 220 | B106: Possible hardcoded password: 'token' |
| **LOW** | `test_full_tournament.py` | 289 | B106: Possible hardcoded password: 'bank-token' |
| **LOW** | `test_receivers.py` | 27 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_views.py` | 25 | B106: Possible hardcoded password: 'testpass123' |
| **LOW** | `test_views.py` | 112 | B106: Possible hardcoded password: 'testpass123' |
| **LOW** | `test_views.py` | 247 | B106: Possible hardcoded password: 'testpass123' |
| **LOW** | `test_wallet_views.py` | 27 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_wallet_views.py` | 173 | B105: Possible hardcoded password: 'token-abc' |
| **LOW** | `test_wallet_views.py` | 180 | B105: Possible hardcoded password: 'token-abc' |
| **LOW** | `test_wallet_views.py` | 192 | B105: Possible hardcoded password: 'tok' |
| **LOW** | `settings.py` | 26 | B105: Possible hardcoded password: 'django-insecure-v!mejyc34!e4j2(pnvyn^dh!#@&lfd!-!@)wju-wc*)7trj= |
| **LOW** | `settings.py` | 97 | B105: Possible hardcoded password: 'nexus_pass' |
| **LOW** | `settings.py` | 164 | B105: Possible hardcoded password: 'nexus_core.token_serializer.NexusTokenObtainPairSerializer' |
| **LOW** | `test_consumers.py` | 39 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_consumers.py` | 49 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `apps.py` | 16 | B110: Try, Except, Pass detected. |
| **LOW** | `test_notification_preferences.py` | 25 | B106: Possible hardcoded password: 'SecurePass123!' |
| **LOW** | `test_announcement_moderation.py` | 23 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_announcement_service.py` | 23 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_api.py` | 33 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_invariants.py` | 26 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_models.py` | 22 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_ruleset_restrictions.py` | 37 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_services.py` | 34 | B106: Possible hardcoded password: 'pass' |
| **LOW** | `test_tasks.py` | 16 | B106: Possible hardcoded password: 'pass' |

## 📊 COMPLEXITY METRICS

| Metric | Value |
| :--- | ---: |
| Average cyclomatic complexity | 2.30 |
| Maximum cyclomatic complexity | 21 |
| Maintainability index | 100.0 |
| Functions analysed | 1268 |

### High Complexity Functions (>10)

| Function | File | Complexity | Lines |
| :--- | :--- | ---: | ---: |
| `handle_timeout` | `match_service.py` | 21 | 0 |
| `create_tournament` | `league_service.py` | 20 | 0 |
| `join_tournament` | `participation_service.py` | 19 | 0 |
| `HandshakeRecheckService` | `handshake_recheck_service.py` | 17 | 0 |
| `modempay_webhook_handler` | `webhooks.py` | 17 | 0 |
| `recheck` | `handshake_recheck_service.py` | 16 | 0 |
| `_try_activate` | `match_service.py` | 14 | 0 |
| `create_announcement` | `announcement_service.py` | 13 | 0 |
| `generate_single_elimination` | `bracket_service.py` | 13 | 0 |
| `LoginView` | `auth.py` | 12 | 0 |
| `EscrowService` | `escrow_service.py` | 12 | 0 |
| `WithdrawalService` | `withdrawal_service.py` | 12 | 0 |
| `WalletWithdrawView` | `wallet.py` | 12 | 0 |
| `ingest_event` | `api_events.py` | 12 | 0 |
| `post` | `auth.py` | 11 | 0 |
| `PayoutService` | `payout_service.py` | 11 | 0 |
| `lock` | `escrow_service.py` | 11 | 0 |
| `process` | `withdrawal_service.py` | 11 | 0 |
| `WalletDepositView` | `wallet.py` | 11 | 0 |
| `post` | `wallet.py` | 11 | 0 |

## 💡 RECOMMENDATIONS

### [CRITICAL] Eliminate Cross-App Direct Imports

Found 9 direct import(s) between first-party apps across 4 app(s). This violates strict modularity and creates tight coupling that makes independent deployment, testing, and scaling impossible. Breakdown: nexus_core: 2 import(s); nexus_economy: 1 import(s); nexus_social: 4 import(s); nexus_tournaments: 2 import(s).

**Action:** Replace direct imports with one of: (a) Django signals for event-driven communication, (b) Celery tasks for async work, (c) REST API calls via nexus_gateway, (d) shared service interfaces in nexus_core.

**Affected modules:** `nexus_core.views.users`, `nexus_economy.views.webhooks`, `nexus_social.api_events`, `nexus_social.models.sequence`, `nexus_tournaments.services.verification_service`

### [HIGH] Reduce Cyclomatic Complexity

Average complexity is 2.30 (target: ≤10). Max complexity is 21 in a single function. 20 function(s) exceed the threshold of 10, making them hard to test, understand, and maintain safely.

**Action:** Refactor high-complexity functions by: (a) extracting helper methods for distinct logical branches, (b) replacing long if/elif chains with strategy pattern or dispatch dicts, (c) breaking functions >50 lines into smaller composable units. Aim for cyclomatic complexity ≤10 per function.

**Affected modules:** `announcement_service.py`, `api_events.py`, `auth.py`, `bracket_service.py`, `escrow_service.py`, `handshake_recheck_service.py`

### [LOW] Investigate Ghost Files

8 file(s) exist on disk but were not discovered by pydeps. Affected apps: nexus_core (3), nexus_social (4), nexus_tournaments (1). These may be dead code, unreachable entry points, or files that need to be added to the project's module tree.

**Action:** For each ghost file: (a) check if it is imported anywhere — if not, delete it, (b) if it is needed, ensure it is properly included in the app's __init__.py or referenced in the project's module graph, (c) update physical_inventory.txt after changes.

**Affected modules:** `nexus_social.services.sequencer`, `nexus_social.services.event_consumers`, `nexus_social.services.banner_service`, `nexus_social.management.commands.replay_social_events`, `nexus_tournaments.management.commands.dispatch_outbox_events`, `nexus_core.serializers.users`, `nexus_core.serializers.auth`, `nexus_core.management.commands.dispatch_outbox_events`

### [HIGH] Resolve Intra-App Circular Imports

5 circular dependency cycle(s) exist within a single app. These cause ImportError at startup if import order changes and hide design problems.

**Action:** Move shared constants and type definitions to a dedicated `types.py` or `constants.py` module that nothing in the app imports from. Use lazy imports (inside function bodies) as a last resort.

**Affected modules:** `nexus_economy.services.payout_service`, `nexus_economy.tasks`, `nexus_economy.services.refund_service`, `nexus_tournaments.services.match_service`, `nexus_tournaments.tasks`

### [HIGH] Move Shared Utilities to nexus_core

1 module(s) are imported by 2 or more apps as violations. This means they are shared utilities living in the wrong app: `nexus_gaming` (used by nexus_social, nexus_tournaments, nexus_core).

**Action:** Move these modules to nexus_core (or create a nexus_shared package). Update all imports. The violation count will drop to zero for these once the module lives in the right place.

**Affected modules:** `nexus_gaming`

## 📋 FULL MODULE MANIFEST

### NEXUS_CONTENT (6 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_content` | 1 | 0 | 1 |
| `nexus_content.admin` | 1 | 3 | 1 |
| `nexus_content.apps` | 1 | 2 | 1 |
| `nexus_content.models` | 1 | 4 | 1 |
| `nexus_content.tests` | 1 | 2 | 1 |
| `nexus_content.views` | 1 | 2 | 1 |

### NEXUS_CORE (32 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_core` | 1 | 0 | 19 |
| `nexus_core.admin` | 1 | 3 | 1 |
| `nexus_core.apps` | 1 | 4 | 1 |
| `nexus_core.encryption` | 1 | 5 | 2 |
| `nexus_core.generate_tree` | 1 | 4 | 1 |
| `nexus_core.middleware` | 1 | 5 | 1 |
| `nexus_core.models` | 1 | 8 | 8 |
| `nexus_core.receivers` | 1 | 11 | 2 |
| `nexus_core.services` | 1 | 0 | 5 |
| `nexus_core.services.deletion` | 1 | 9 | 3 |
| `nexus_core.services.mfa` | 1 | 10 | 3 |
| `nexus_core.services.sessions` | 1 | 7 | 4 |
| `nexus_core.signals` | 1 | 2 | 4 |
| `nexus_core.tests` | 1 | 0 | 1 |
| `nexus_core.tests.test_admin_panel` | 1 | 11 | 1 |
| `nexus_core.tests.test_auth` | 1 | 11 | 1 |
| `nexus_core.tests.test_new_endpoints` | 1 | 8 | 1 |
| `nexus_core.tests.test_sessions_mfa_deletion` | 1 | 13 | 1 |
| `nexus_core.tests.test_signals` | 1 | 8 | 1 |
| `nexus_core.tests.test_users` | 1 | 6 | 1 |
| `nexus_core.token_serializer` | 1 | 0 | 1 |
| `nexus_core.tokens` | 1 | 5 | 3 |
| `nexus_core.urls` | 1 | 0 | 1 |
| `nexus_core.urls.admin_panel` | 1 | 5 | 1 |
| `nexus_core.urls.auth` | 1 | 5 | 1 |
| `nexus_core.urls.games` | 1 | 5 | 1 |
| `nexus_core.urls.users` | 1 | 5 | 1 |
| `nexus_core.views` | 1 | 0 | 5 |
| `nexus_core.views.admin_panel` | 1 | 7 | 2 |
| `nexus_core.views.auth` | 1 | 21 | 2 |
| `nexus_core.views.games` | 1 | 8 | 2 |
| `nexus_core.views.users` | 1 | 11 | 2 |

### NEXUS_ECONOMY (37 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_economy` | 1 | 0 | 25 |
| `nexus_economy.admin` | 1 | 3 | 1 |
| `nexus_economy.apps` | 1 | 6 | 1 |
| `nexus_economy.generate_tree` | 1 | 4 | 1 |
| `nexus_economy.management` | 1 | 0 | 1 |
| `nexus_economy.management.commands` | 1 | 0 | 1 |
| `nexus_economy.management.commands.create_test_wallet` | 1 | 9 | 1 |
| `nexus_economy.management.commands.dispatch_outbox_events` | 1 | 16 | 1 |
| `nexus_economy.models` | 1 | 7 | 14 |
| `nexus_economy.modempay` | 1 | 9 | 5 |
| `nexus_economy.receivers` | 1 | 8 | 3 |
| `nexus_economy.services` | 1 | 0 | 6 |
| `nexus_economy.services.deposit_service` | 1 | 9 | 3 |
| `nexus_economy.services.escrow_service` | 1 | 7 | 4 |
| `nexus_economy.services.handshake_recheck_service` | 1 | 11 | 2 |
| `nexus_economy.services.payout_service` | 1 | 13 | 4 |
| `nexus_economy.services.platform_revenue_service` | 1 | 7 | 2 |
| `nexus_economy.services.reconciliation_service` | 1 | 7 | 4 |
| `nexus_economy.services.refund_service` | 1 | 9 | 4 |
| `nexus_economy.services.tournament_escrow_service` | 1 | 7 | 3 |
| `nexus_economy.services.withdrawal_service` | 1 | 11 | 4 |
| `nexus_economy.signals` | 1 | 2 | 3 |
| `nexus_economy.tasks` | 1 | 15 | 7 |
| `nexus_economy.tests` | 1 | 0 | 1 |
| `nexus_economy.tests.test_financial_integrity` | 1 | 22 | 1 |
| `nexus_economy.tests.test_full_tournament` | 1 | 25 | 1 |
| `nexus_economy.tests.test_models` | 1 | 10 | 1 |
| `nexus_economy.tests.test_receivers` | 1 | 11 | 1 |
| `nexus_economy.tests.test_tasks` | 1 | 12 | 1 |
| `nexus_economy.tests.test_views` | 1 | 11 | 1 |
| `nexus_economy.tests.test_wallet_views` | 1 | 10 | 1 |
| `nexus_economy.urls` | 1 | 8 | 1 |
| `nexus_economy.views` | 1 | 5 | 4 |
| `nexus_economy.views.admin` | 1 | 5 | 3 |
| `nexus_economy.views.finance` | 1 | 5 | 3 |
| `nexus_economy.views.wallet` | 1 | 15 | 4 |
| `nexus_economy.views.webhooks` | 1 | 19 | 2 |

### NEXUS_GAMING (12 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_gaming` | 1 | 1 | 8 |
| `nexus_gaming.asgi` | 1 | 7 | 2 |
| `nexus_gaming.celery` | 1 | 1 | 2 |
| `nexus_gaming.decorators` | 1 | 3 | 2 |
| `nexus_gaming.events` | 1 | 6 | 3 |
| `nexus_gaming.feature_flags` | 1 | 1 | 4 |
| `nexus_gaming.generate_tree` | 1 | 4 | 1 |
| `nexus_gaming.logging_config` | 1 | 3 | 1 |
| `nexus_gaming.settings` | 1 | 4 | 1 |
| `nexus_gaming.tier_permissions` | 1 | 1 | 1 |
| `nexus_gaming.urls` | 1 | 4 | 1 |
| `nexus_gaming.wsgi` | 1 | 4 | 1 |

### NEXUS_GATEWAY (12 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_gateway` | 1 | 0 | 6 |
| `nexus_gateway.admin` | 1 | 3 | 1 |
| `nexus_gateway.apps` | 1 | 8 | 1 |
| `nexus_gateway.consumers` | 1 | 4 | 2 |
| `nexus_gateway.middleware` | 1 | 4 | 2 |
| `nexus_gateway.models` | 1 | 3 | 1 |
| `nexus_gateway.receivers` | 1 | 7 | 3 |
| `nexus_gateway.routing` | 1 | 4 | 2 |
| `nexus_gateway.tests` | 1 | 0 | 1 |
| `nexus_gateway.tests.test_consumers` | 1 | 10 | 1 |
| `nexus_gateway.tests.test_receivers` | 1 | 8 | 1 |
| `nexus_gateway.views` | 1 | 2 | 1 |

### NEXUS_SOCIAL (18 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_social` | 1 | 0 | 6 |
| `nexus_social.admin` | 1 | 3 | 1 |
| `nexus_social.api_events` | 1 | 16 | 2 |
| `nexus_social.apps` | 1 | 4 | 1 |
| `nexus_social.models` | 1 | 9 | 5 |
| `nexus_social.models.chat` | 1 | 5 | 3 |
| `nexus_social.models.cursors` | 1 | 4 | 2 |
| `nexus_social.models.infrastructure` | 1 | 4 | 2 |
| `nexus_social.models.moderation` | 1 | 5 | 2 |
| `nexus_social.models.preferences` | 1 | 4 | 2 |
| `nexus_social.models.projections` | 1 | 3 | 2 |
| `nexus_social.models.sequence` | 1 | 5 | 2 |
| `nexus_social.tasks` | 1 | 4 | 1 |
| `nexus_social.tests` | 1 | 0 | 1 |
| `nexus_social.tests.test_notification_preferences` | 1 | 6 | 1 |
| `nexus_social.urls` | 1 | 6 | 1 |
| `nexus_social.views` | 1 | 3 | 2 |
| `nexus_social.views_announcements` | 1 | 7 | 2 |

### NEXUS_TOURNAMENTS (43 modules)

| Module | Depth | Imports | Imported By |
| :--- | ---: | ---: | ---: |
| `nexus_tournaments` | 1 | 0 | 26 |
| `nexus_tournaments.admin` | 1 | 5 | 1 |
| `nexus_tournaments.api` | 1 | 0 | 3 |
| `nexus_tournaments.api.serializers` | 1 | 5 | 2 |
| `nexus_tournaments.api.urls` | 1 | 5 | 1 |
| `nexus_tournaments.api.views` | 1 | 19 | 2 |
| `nexus_tournaments.apps` | 1 | 4 | 1 |
| `nexus_tournaments.generate_tree` | 1 | 4 | 1 |
| `nexus_tournaments.models` | 1 | 15 | 15 |
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
| `nexus_tournaments.receivers` | 1 | 10 | 2 |
| `nexus_tournaments.services` | 1 | 0 | 9 |
| `nexus_tournaments.services.announcement_service` | 1 | 7 | 3 |
| `nexus_tournaments.services.bracket_service` | 1 | 7 | 3 |
| `nexus_tournaments.services.diagnostic_service` | 1 | 9 | 2 |
| `nexus_tournaments.services.leaderboard_service` | 1 | 5 | 3 |
| `nexus_tournaments.services.league_service` | 1 | 13 | 5 |
| `nexus_tournaments.services.match_service` | 1 | 14 | 6 |
| `nexus_tournaments.services.participation_service` | 1 | 11 | 4 |
| `nexus_tournaments.services.verification_service` | 1 | 10 | 3 |
| `nexus_tournaments.signals` | 1 | 2 | 10 |
| `nexus_tournaments.tasks` | 1 | 14 | 4 |
| `nexus_tournaments.tests` | 1 | 0 | 1 |
| `nexus_tournaments.tests.test_announcement_moderation` | 1 | 10 | 1 |
| `nexus_tournaments.tests.test_announcement_service` | 1 | 14 | 1 |
| `nexus_tournaments.tests.test_api` | 1 | 10 | 1 |
| `nexus_tournaments.tests.test_invariants` | 1 | 17 | 1 |
| `nexus_tournaments.tests.test_models` | 1 | 13 | 1 |
| `nexus_tournaments.tests.test_ruleset_restrictions` | 1 | 12 | 1 |
| `nexus_tournaments.tests.test_services` | 1 | 19 | 1 |
| `nexus_tournaments.tests.test_tasks` | 1 | 14 | 1 |

---
*Report generated by Nexus Audit Command Center — 2026-05-05 23:25:37*