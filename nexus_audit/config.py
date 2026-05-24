#!/usr/bin/env python3
"""
Nexus Audit Tool - Configuration module
Constants, .env loading, and global settings
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Optional
from pathlib import Path

# ============================================================================
# .ENV LOADER
# ============================================================================
# Reads ~/my_tools/nexus_audit/.env and exports every key=value line into
# os.environ — no third-party packages needed, pure Python.
#
# Your .env file should look like:
#   GEMINI_API_KEY=AIzaSy...
#   ANTHROPIC_API_KEY=sk-ant-...
#
# Lines starting with # are comments and are ignored.
# Blank lines are ignored.
# Keys are always trimmed of whitespace and quotes.
# ============================================================================

def _load_dotenv() -> Dict[str, str]:
    """
    Load .env from ~/my_tools/nexus_audit/.env into os.environ.
    Also checks the directory containing this script as a fallback.
    Returns a dict of keys that were loaded (for logging).
    """
    _VAULT   = os.path.expanduser('~/my_tools/nexus_audit')
    _SCRIPT  = os.path.dirname(os.path.abspath(__file__))

    loaded: Dict[str, str] = {}

    for env_path in [
        os.path.join(_VAULT,  '.env'),
        os.path.join(_SCRIPT, '.env'),
    ]:
        if not os.path.exists(env_path):
            continue

        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for raw_line in f:
                    line = raw_line.strip()
                    # Skip blank lines and comments
                    if not line or line.startswith('#'):
                        continue
                    # Strip bash "export " prefix — common mistake in .env files
                    if line.lower().startswith('export '):
                        line = line[7:].strip()
                    if '=' not in line:
                        continue
                    key, _, value = line.partition('=')
                    key   = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        # Don't overwrite a key that's already set in the shell
                        if key not in os.environ:
                            os.environ[key] = value
                        loaded[key] = '***'   # mask value in log output
            if loaded:
                print(f"   ✔ .env loaded from {env_path} "
                      f"({len(loaded)} key(s): {', '.join(loaded.keys())})")
            break   # use first .env found, don't merge multiple
        except OSError as exc:
            print(f"   ⚠ Could not read .env at {env_path}: {exc}")

    return loaded

# Load .env before anything else reads os.environ
_dotenv_keys = _load_dotenv()

# ============================================================================
# TIER 1 — ALWAYS AVAILABLE (zero internet required)
#   • Full DNA audit and violation detection
#   • Security scan (bandit), complexity (radon), dead code (vulture)
#   • Ghost file detection, cycle detection, shared-utility detection
#   • Trend tracking from previous runs
#   • Self-contained HTML dashboard, Markdown report, JSON data
#
# TIER 2 — ACTIVATES AUTOMATICALLY WHEN INTERNET IS DETECTED
#   • Package vulnerability scan (OSV — Google's Open Source Vulnerabilities DB)
#   • Dependency freshness check (PyPI latest-version API)
#   • CVE enrichment on security findings
#   • Additional dashboard section: "Dependency Health"
#
# Tier 2 features are additive and non-blocking. If internet is lost mid-run,
# Tier 1 completes fully. The JSON includes a 'capabilities' manifest so any
# downstream tool knows exactly what ran.
# ============================================================================

TIER2_TIMEOUT = 4          # seconds — fast timeout so offline runs don't hang

# ── AI / Gemini base URL ─────────────────────────────────────────────────────
_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Auto-loaded from requirements.txt so every project dep gets scanned.
_REQ_TXT_PATHS = [
    os.path.join(os.path.expanduser('~/my_tools/nexus_project_copy'), 'requirements.txt'),
    os.path.join(os.path.expanduser('~/nexus-gaming'), 'requirements.txt'),
]

# Nexus root directory
NEXUS_ROOT = os.path.expanduser('~/nexus-gaming')

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Modular root: the package directory where all new outputs go
# Path(__file__).resolve().parent points to ~/my_tools/nexus_audit/nexus_audit/
MODULAR_ROOT = Path(__file__).resolve().parent
DNA_PATH = os.path.join(MODULAR_ROOT, 'master_nexus_dna.json')
INVENTORY_PATH = os.path.join(MODULAR_ROOT, 'factories', 'physical_inventory.txt')
VISUALS_DIR = os.path.join(MODULAR_ROOT, 'visuals')
HISTORY_DIR = os.path.join(VISUALS_DIR, 'audit_history')

# Legacy vault path (read-only input only)
_MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_PATH = _MODULE_DIR  # ~/my_tools/nexus_audit/ (legacy, read-only)

PROJECT_PATH = os.path.expanduser('~/my_tools/nexus_project_copy')

# Create modular directories
os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

SCORING_EXCLUDE_TESTS = True           # Ignore test-file security issues for scoring
CROSS_APP_IMPORT_PENALTY = 15          # Heavy penalty for each cross-app import

# ============================================================================
# DYNAMIC FIRST-PARTY APPS DISCOVERY
# ============================================================================

def get_first_party_apps(project_path: str):
    """
    Attempt to extract first-party app names from Django settings.
    Looks for nexus_gaming/settings.py and parses INSTALLED_APPS.
    """
    import importlib.util
    import sys
    from pathlib import Path

    settings_path = Path(project_path) / "nexus_gaming" / "settings.py"
    if not settings_path.exists():
        for py_file in Path(project_path).rglob("*.py"):
            if "INSTALLED_APPS" in py_file.read_text():
                settings_path = py_file
                break

    if not settings_path.exists():
        print("⚠️ Could not locate Django settings. Using hardcoded fallback apps.")
        return FIRST_PARTY_APPS_FALLBACK

    try:
        spec = importlib.util.spec_from_file_location("settings", settings_path)
        settings = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(settings_path.parent.parent))
        spec.loader.exec_module(settings)

        installed_apps = getattr(settings, "INSTALLED_APPS", [])
        first_party = []
        for app in installed_apps:
            app_name = app.split('.')[-1] if isinstance(app, str) else app.__name__
            if app_name.startswith("nexus_"):
                first_party.append(app_name)
        return first_party if first_party else FIRST_PARTY_APPS_FALLBACK
    except Exception as e:
        print(f"⚠️ Error parsing settings: {e}. Using fallback.")
        return FIRST_PARTY_APPS_FALLBACK

FIRST_PARTY_APPS_FALLBACK = [
    'nexus_core', 'nexus_economy', 'nexus_gaming',
    'nexus_gateway', 'nexus_social', 'nexus_tournaments', 'nexus_content'
]

FIRST_PARTY_APPS = get_first_party_apps(PROJECT_PATH)
print(f"🎯 First-party apps discovered: {FIRST_PARTY_APPS}")

# ============================================================================
# WHITELISTS (FRAMEWORK & STDLIB)
# ============================================================================

DJANGO_ACCEPTABLE = {
    'django', 'django.db', 'django.db.models', 'django.conf', 'django.urls',
    'django.test', 'django.contrib', 'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.auth.models', 'django.shortcuts', 'django.utils',
    'django.utils.timezone', 'django.dispatch', 'django.core', 'django.apps',
    'django.core.asgi', 'django.core.wsgi', 'django.core.management',
    'django.core.management.base', 'django.db.transaction', 'django.http',
    'django.views', 'django.template', 'django.forms', 'django.middleware',
    'rest_framework', 'rest_framework_simplejwt', 'channels', 'channels_redis',
    'corsheaders', 'django_filters', 'django_celery_beat', 'celery'
}

STDLIB_MODULES = {
    'json', 'uuid', 'os', 'sys', 'datetime', 'pathlib', 'decimal', 'hashlib',
    'logging', 're', 'math', 'random', 'time', 'collections', 'itertools',
    'functools', 'typing', 'enum', 'dataclasses', 'abc', 'base64', 'binascii',
    'calendar', 'copy', 'csv', 'fnmatch', 'glob', 'io', 'string', 'tempfile',
    'textwrap', 'threading', 'traceback', 'unittest', 'unittest.mock',
    'unittest.case', 'urllib', 'warnings', 'weakref', 'xml', 'zipfile',
    'asgiref', 'asgiref.sync', 'importlib', 'importlib.util',
    'contextlib', 'operator', 'struct', 'socket', 'signal', 'subprocess',
    'shutil', 'stat', 'inspect', 'pprint', 'types', 'builtins',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_first_party(module_name: str) -> bool:
    if not module_name:
        return False
    return any(module_name.startswith(app) for app in FIRST_PARTY_APPS)

def is_django_framework(module_name: str) -> bool:
    if module_name in DJANGO_ACCEPTABLE:
        return True
    return any(module_name.startswith(d) for d in ['django.', 'rest_framework', 'channels', 'celery.'])

def is_stdlib(module_name: str) -> bool:
    if module_name in STDLIB_MODULES:
        return True
    return module_name.split('.')[0] in STDLIB_MODULES

# ============================================================================
# TIER 2 DEPENDENCY SCANNING
# ============================================================================

def _load_requirements_packages() -> tuple:
    """Parse requirements.txt -> (name_list, {name_lower: pinned_ver})."""
    pkg_names: list = []
    version_map: dict = {}
    for req_path in _REQ_TXT_PATHS:
        if not os.path.exists(req_path):
            continue
        with open(req_path, encoding='utf-8', errors='ignore') as _fh:
            for line in _fh:
                line = line.strip()
                if not line or line.startswith(('#', '-', 'git+', 'http')):
                    continue
                if '==' in line:
                    name, ver = line.split('==', 1)
                    name = name.strip()
                    ver  = ver.strip().split(';')[0].strip()
                    pkg_names.append(name)
                    version_map[name.lower()] = ver
        if pkg_names:
            break
    if not pkg_names:
        pkg_names = ['django','celery','channels','djangorestframework',
                     'redis','psycopg2','Pillow','cryptography',
                     'requests','urllib3','pyjwt','paramiko']
    return pkg_names, version_map

_REQ_PACKAGES, _REQ_VERSIONS = _load_requirements_packages()
TIER2_PACKAGES = _REQ_PACKAGES

def _detect_internet(timeout: int = TIER2_TIMEOUT) -> bool:
    """Fast check: can we reach PyPI?"""
    try:
        req = urllib.request.Request(
            'https://pypi.org/pypi/django/json',
            method='HEAD',
            headers={'User-Agent': 'nexus-audit/1.0'}
        )
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:
        return False

def _pypi_get(package: str, timeout: int = TIER2_TIMEOUT) -> Optional[Dict]:
    """Fetch package metadata from PyPI."""
    try:
        url  = f'https://pypi.org/pypi/{package}/json'
        req  = urllib.request.Request(url, headers={'User-Agent': 'nexus-audit/1.0'})
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

def _osv_query(package: str, ecosystem: str = 'PyPI',
                timeout: int = TIER2_TIMEOUT):
    """Query OSV for CVEs."""
    try:
        payload = json.dumps({
            'package': {'name': package, 'ecosystem': ecosystem}
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.osv.dev/v1/query',
            data=payload,
            headers={'Content-Type': 'application/json', 'User-Agent': 'nexus-audit/1.0'}
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode('utf-8'))
        return data.get('vulns', [])
    except Exception:
        return []

def run_tier2_dependency_scan(project_path: str) -> Dict:
    """Scan packages for CVEs and outdated versions."""
    result = {
        'packages': [],
        'total_cves': 0,
        'outdated_count': 0,
        'critical_cves': [],
    }

    installed = dict(_REQ_VERSIONS)
    total_pkgs = len(TIER2_PACKAGES)
    for pkg_idx, pkg in enumerate(TIER2_PACKAGES, 1):
        print(f"   [{pkg_idx}/{total_pkgs}] {pkg:<30} ", end="", flush=True)
        pkg_lower = pkg.lower()
        installed_v = installed.get(pkg_lower, 'unknown')
        pypi_data = _pypi_get(pkg)
        latest_v = pypi_data.get('info', {}).get('version', 'unknown') if pypi_data else 'unknown'

        def _vmaj(v: str) -> tuple:
            try:
                parts = [int(x) for x in v.split('.')[:2]]
                return tuple(parts + [0] * (2 - len(parts)))
            except Exception:
                return (0, 0)

        outdated = (_vmaj(installed_v) < _vmaj(latest_v)) if installed_v != 'unknown' else False
        vulns = _osv_query(pkg)
        cve_count = len(vulns)

        result['packages'].append({
            'name': pkg,
            'installed': installed_v,
            'latest': latest_v,
            'outdated': outdated,
            'cve_count': cve_count,
            'cves': [v.get('id','') for v in vulns[:10]],
        })
        result['total_cves'] += cve_count
        if outdated:
            result['outdated_count'] += 1

        status_parts = []
        if installed_v != 'unknown':
            status_parts.append(installed_v)
        if outdated:
            status_parts.append(f'↗ {latest_v} available')
        else:
            status_parts.append('✔ current')
        if cve_count:
            status_parts.append(f'⚠ {cve_count} CVE(s)')
        print(' | '.join(status_parts), flush=True)

    return result
