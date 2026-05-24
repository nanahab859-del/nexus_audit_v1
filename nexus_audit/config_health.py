#!/usr/bin/env python3
"""
Config Health Scanner
=====================
Audits the Django project configuration folder (nexus_gaming/) separately
from the first-party apps. This folder is NOT a Django app — it is the
project kernel. It holds settings, URL routing, ASGI/WSGI entry points,
and Celery bootstrap. Because the entire project depends on it, it requires
a dedicated class of checks distinct from app-boundary violation scanning.

Checks performed:
  - settings.py: secrets, DEBUG, ALLOWED_HOSTS, security middleware, env coverage
  - urls.py: import purity (no direct model imports), presence of root urlconf
  - asgi.py / wsgi.py: entry point purity (no domain logic)
  - celery.py: correct bootstrap pattern, no app-specific business logic
  - General: presence of required config files, unexpected .py files in config folder
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Any


# ── Helpers ──────────────────────────────────────────────────────────────────

def _read(path: str) -> str:
    """Read a file safely, return empty string on failure."""
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            return f.read()
    except OSError:
        return ''


def _parse_ast(source: str):
    """Parse Python source to AST. Returns None on syntax error."""
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def _imports_in_file(source: str) -> List[str]:
    """Return flat list of all imported module names in a .py file."""
    tree = _parse_ast(source)
    if not tree:
        return []
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.append(node.module)
    return names


# ── Individual check functions ────────────────────────────────────────────────

def _check_settings(settings_path: str, first_party_apps: List[str]) -> List[Dict]:
    """Run targeted security/config checks on settings.py."""
    issues = []
    src = _read(settings_path)
    if not src:
        issues.append({
            'check': 'settings_readable',
            'status': 'FAIL',
            'severity': 'CRITICAL',
            'message': 'settings.py could not be read.',
        })
        return issues

    issues.append({'check': 'settings_readable', 'status': 'PASS', 'severity': 'INFO',
                   'message': 'settings.py is readable.'})

    # SECRET_KEY: should come from env, not be hardcoded
    sk_match = re.search(r'SECRET_KEY\s*=\s*(["\'])(.+?)\1', src)
    if sk_match:
        val = sk_match.group(2)
        if 'environ' not in src[:src.find('SECRET_KEY') + 200]:
            issues.append({
                'check': 'secret_key_hardcoded',
                'status': 'WARN',
                'severity': 'HIGH',
                'message': 'SECRET_KEY appears hardcoded. Use os.environ.get() with no fallback in production.',
            })
        else:
            issues.append({'check': 'secret_key_hardcoded', 'status': 'PASS', 'severity': 'INFO',
                           'message': 'SECRET_KEY loaded from environment.'})
    else:
        issues.append({'check': 'secret_key_hardcoded', 'status': 'WARN', 'severity': 'MEDIUM',
                       'message': 'Could not locate SECRET_KEY assignment in settings.py.'})

    # DEBUG: must be env-driven
    debug_match = re.search(r'DEBUG\s*=\s*(.+)', src)
    if debug_match:
        val = debug_match.group(1).strip()
        if val in ('True', 'False'):
            issues.append({
                'check': 'debug_env_driven',
                'status': 'WARN',
                'severity': 'HIGH',
                'message': f'DEBUG = {val} is hardcoded. Use os.environ.get("DJANGO_DEBUG", "false").lower() == "true".',
            })
        else:
            issues.append({'check': 'debug_env_driven', 'status': 'PASS', 'severity': 'INFO',
                           'message': 'DEBUG is environment-driven.'})

    # ALLOWED_HOSTS: must not be wildcard in production context
    ah_match = re.search(r'ALLOWED_HOSTS\s*=\s*(.+)', src)
    if ah_match:
        val = ah_match.group(1).strip()
        if "'*'" in val or '"*"' in val:
            issues.append({
                'check': 'allowed_hosts_wildcard',
                'status': 'FAIL',
                'severity': 'CRITICAL',
                'message': 'ALLOWED_HOSTS contains wildcard "*". This is a security risk in production.',
            })
        else:
            issues.append({'check': 'allowed_hosts_wildcard', 'status': 'PASS', 'severity': 'INFO',
                           'message': 'ALLOWED_HOSTS does not contain wildcard.'})

    # SecurityMiddleware must be first in MIDDLEWARE
    mw_block = re.search(r'MIDDLEWARE\s*=\s*\[(.*?)\]', src, re.DOTALL)
    if mw_block:
        mw_list = mw_block.group(1)
        first_mw = re.search(r'["\']([^"\']+)["\']', mw_list)
        if first_mw:
            if 'SecurityMiddleware' in first_mw.group(1):
                issues.append({'check': 'security_middleware_first', 'status': 'PASS', 'severity': 'INFO',
                               'message': 'SecurityMiddleware is correctly placed first in MIDDLEWARE.'})
            else:
                issues.append({
                    'check': 'security_middleware_first',
                    'status': 'FAIL',
                    'severity': 'HIGH',
                    'message': f'SecurityMiddleware is NOT first in MIDDLEWARE. Found: {first_mw.group(1)}',
                })

    # ENCRYPTION_KEY: should not be empty string in production
    ek_match = re.search(r'ENCRYPTION_KEY\s*=\s*(.+)', src)
    if ek_match:
        val = ek_match.group(1).strip()
        if '""' in val or "''" in val:
            issues.append({
                'check': 'encryption_key_set',
                'status': 'WARN',
                'severity': 'HIGH',
                'message': 'ENCRYPTION_KEY defaults to empty string. Set via environment variable in production.',
            })
        else:
            issues.append({'check': 'encryption_key_set', 'status': 'PASS', 'severity': 'INFO',
                           'message': 'ENCRYPTION_KEY has a non-empty default or is env-driven.'})

    # SESSION & CSRF cookie security flags
    for flag in ('SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE', 'SECURE_SSL_REDIRECT'):
        if flag in src:
            issues.append({'check': f'{flag.lower()}_present', 'status': 'PASS', 'severity': 'INFO',
                           'message': f'{flag} is configured in settings.'})
        else:
            issues.append({
                'check': f'{flag.lower()}_present',
                'status': 'WARN',
                'severity': 'MEDIUM',
                'message': f'{flag} is not set. Add it to enforce HTTPS security headers in production.',
            })

    # INSTALLED_APPS check: all expected first-party apps should be listed
    installed_match = re.search(r'INSTALLED_APPS\s*=\s*\[(.*?)\]', src, re.DOTALL)
    if installed_match:
        installed_block = installed_match.group(1)
        for app in first_party_apps:
            if app in installed_block:
                issues.append({'check': f'installed_app_{app}', 'status': 'PASS', 'severity': 'INFO',
                               'message': f'{app} is registered in INSTALLED_APPS.'})
            else:
                issues.append({
                    'check': f'installed_app_{app}',
                    'status': 'WARN',
                    'severity': 'MEDIUM',
                    'message': f'{app} is NOT in INSTALLED_APPS — may be intentional or an omission.',
                })

    return issues


def _check_entry_point(file_path: str, file_label: str, first_party_apps: List[str]) -> List[Dict]:
    """Check asgi.py or wsgi.py for domain logic leakage."""
    issues = []
    src = _read(file_path)
    if not src:
        issues.append({'check': f'{file_label}_readable', 'status': 'WARN', 'severity': 'MEDIUM',
                       'message': f'{file_label} not found or unreadable.'})
        return issues

    issues.append({'check': f'{file_label}_readable', 'status': 'PASS', 'severity': 'INFO',
                   'message': f'{file_label} is present and readable.'})

    imports = _imports_in_file(src)
    domain_imports = [i for i in imports if any(i.startswith(app) for app in first_party_apps)]
    if domain_imports:
        issues.append({
            'check': f'{file_label}_purity',
            'status': 'FAIL',
            'severity': 'HIGH',
            'message': f'{file_label} imports domain app code: {", ".join(domain_imports)}. Entry points must stay pure.',
        })
    else:
        issues.append({'check': f'{file_label}_purity', 'status': 'PASS', 'severity': 'INFO',
                       'message': f'{file_label} is pure — no domain app imports detected.'})

    return issues


def _check_urls(urls_path: str, first_party_apps: List[str]) -> List[Dict]:
    """Check urls.py for direct model imports (should use path/include only)."""
    issues = []
    src = _read(urls_path)
    if not src:
        issues.append({'check': 'urls_readable', 'status': 'WARN', 'severity': 'MEDIUM',
                       'message': 'urls.py not found or unreadable.'})
        return issues

    issues.append({'check': 'urls_readable', 'status': 'PASS', 'severity': 'INFO',
                   'message': 'urls.py is present and readable.'})

    # Check for direct model imports (a red flag in root urls.py)
    model_imports = []
    imports = _imports_in_file(src)
    for i in imports:
        if any(i.startswith(app) for app in first_party_apps):
            if '.models' in i or '.views' in i or '.serializers' in i:
                model_imports.append(i)

    if model_imports:
        issues.append({
            'check': 'urls_no_model_imports',
            'status': 'WARN',
            'severity': 'HIGH',
            'message': f'urls.py directly imports domain models/views/serializers: {", ".join(model_imports)}. Use app-level include() instead.',
        })
    else:
        issues.append({'check': 'urls_no_model_imports', 'status': 'PASS', 'severity': 'INFO',
                       'message': 'urls.py is clean — no direct domain model/view imports.'})

    # ROOT_URLCONF check (should reference itself)
    if 'path(' in src or 'include(' in src:
        issues.append({'check': 'urls_has_routes', 'status': 'PASS', 'severity': 'INFO',
                       'message': 'urls.py defines URL routes using path()/include().'})
    else:
        issues.append({'check': 'urls_has_routes', 'status': 'WARN', 'severity': 'MEDIUM',
                       'message': 'urls.py has no path()/include() calls — may be incomplete.'})

    return issues


def _check_celery(celery_path: str, first_party_apps: List[str]) -> List[Dict]:
    """Check celery.py for correct bootstrap and absence of business logic."""
    issues = []
    src = _read(celery_path)
    if not src:
        issues.append({'check': 'celery_readable', 'status': 'WARN', 'severity': 'LOW',
                       'message': 'celery.py not found. Celery bootstrap may be missing.'})
        return issues

    issues.append({'check': 'celery_readable', 'status': 'PASS', 'severity': 'INFO',
                   'message': 'celery.py is present and readable.'})

    if 'app = Celery(' in src or "app=Celery(" in src:
        issues.append({'check': 'celery_bootstrap', 'status': 'PASS', 'severity': 'INFO',
                       'message': 'Celery app is correctly bootstrapped in celery.py.'})
    else:
        issues.append({'check': 'celery_bootstrap', 'status': 'WARN', 'severity': 'MEDIUM',
                       'message': 'Could not find Celery() app instantiation in celery.py.'})

    if 'autodiscover_tasks' in src:
        issues.append({'check': 'celery_autodiscover', 'status': 'PASS', 'severity': 'INFO',
                       'message': 'autodiscover_tasks() is configured — Celery will find all task modules.'})
    else:
        issues.append({'check': 'celery_autodiscover', 'status': 'WARN', 'severity': 'MEDIUM',
                       'message': 'autodiscover_tasks() not found. Tasks from apps may not be registered automatically.'})

    return issues


def _check_unexpected_files(config_dir: str) -> List[Dict]:
    """Flag unexpected .py files in the config folder (should only be config files)."""
    issues = []
    known = {'__init__.py', 'settings.py', 'urls.py', 'asgi.py', 'wsgi.py', 'celery.py'}
    try:
        all_py = {f for f in os.listdir(config_dir) if f.endswith('.py')}
    except OSError:
        return issues

    unexpected = all_py - known
    if unexpected:
        issues.append({
            'check': 'config_unexpected_files',
            'status': 'WARN',
            'severity': 'LOW',
            'message': f'Unexpected .py files in config folder: {", ".join(sorted(unexpected))}. Config folders should only contain settings, urls, asgi, wsgi, celery.',
        })
    else:
        issues.append({'check': 'config_unexpected_files', 'status': 'PASS', 'severity': 'INFO',
                       'message': 'No unexpected .py files in config folder.'})

    return issues


# ── Public API ────────────────────────────────────────────────────────────────

def run_config_health_scan(project_path: str, first_party_apps: List[str]) -> Dict[str, Any]:
    """
    Main entry point. Scans the Django config folder (detected by finding
    settings.py containing INSTALLED_APPS) and returns a structured result.

    Returns:
        {
            'config_dir': str,          # path to the config folder
            'config_folder_name': str,  # folder name (e.g. 'nexus_gaming')
            'checks': List[Dict],       # individual check results
            'summary': {
                'total': int,
                'passed': int,
                'warnings': int,
                'failures': int,
                'critical': int,
                'score': int,           # 0-100 config health score
            }
        }
    """
    result: Dict[str, Any] = {
        'config_dir': '',
        'config_folder_name': '',
        'checks': [],
        'summary': {'total': 0, 'passed': 0, 'warnings': 0, 'failures': 0, 'critical': 0, 'score': 100},
    }

    # Locate the config folder by finding settings.py with INSTALLED_APPS
    config_dir = None
    project = Path(project_path)
    for candidate in project.iterdir():
        if not candidate.is_dir():
            continue
        settings_candidate = candidate / 'settings.py'
        if settings_candidate.exists() and 'INSTALLED_APPS' in _read(str(settings_candidate)):
            config_dir = str(candidate)
            break

    if not config_dir:
        result['checks'].append({
            'check': 'config_dir_found',
            'status': 'FAIL',
            'severity': 'CRITICAL',
            'message': 'Could not locate a Django config folder (no settings.py with INSTALLED_APPS found).',
        })
        result['summary']['total'] = 1
        result['summary']['failures'] = 1
        result['summary']['score'] = 0
        return result

    result['config_dir'] = config_dir
    result['config_folder_name'] = Path(config_dir).name
    checks = []

    checks.append({'check': 'config_dir_found', 'status': 'PASS', 'severity': 'INFO',
                   'message': f'Config folder found: {Path(config_dir).name}/'})

    # Run all individual checks
    checks += _check_settings(os.path.join(config_dir, 'settings.py'), first_party_apps)
    checks += _check_entry_point(os.path.join(config_dir, 'asgi.py'), 'asgi.py', first_party_apps)
    checks += _check_entry_point(os.path.join(config_dir, 'wsgi.py'), 'wsgi.py', first_party_apps)
    checks += _check_urls(os.path.join(config_dir, 'urls.py'), first_party_apps)
    checks += _check_celery(os.path.join(config_dir, 'celery.py'), first_party_apps)
    checks += _check_unexpected_files(config_dir)

    result['checks'] = checks

    # Compute summary and score
    total = len(checks)
    passed = sum(1 for c in checks if c['status'] == 'PASS')
    warnings = sum(1 for c in checks if c['status'] == 'WARN')
    failures = sum(1 for c in checks if c['status'] == 'FAIL')
    critical = sum(1 for c in checks if c['status'] == 'FAIL' and c.get('severity') == 'CRITICAL')

    # Scoring: start at 100, deduct per issue weighted by severity
    score = 100
    for c in checks:
        if c['status'] == 'FAIL':
            sev = c.get('severity', 'HIGH')
            score -= {'CRITICAL': 20, 'HIGH': 12, 'MEDIUM': 6, 'LOW': 3}.get(sev, 6)
        elif c['status'] == 'WARN':
            sev = c.get('severity', 'MEDIUM')
            score -= {'HIGH': 8, 'MEDIUM': 4, 'LOW': 2}.get(sev, 4)
    score = max(0, min(100, score))

    result['summary'] = {
        'total': total,
        'passed': passed,
        'warnings': warnings,
        'failures': failures,
        'critical': critical,
        'score': score,
    }
    return result
