#!/usr/bin/env python3
"""
Nexus Audit Tool - Data Models
Dataclasses, enums, and helper functions for type safety
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any


# ============================================================================
# ENUMS
# ============================================================================

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ViolationType(Enum):
    DIRECT_IMPORT = "Direct Cross-App Import"
    DIRECT_DB_ACCESS = "Direct Database Access"
    CIRCULAR_DEPENDENCY = "Circular Dependency"
    BARE_EXCEPT = "Bare Exception Handler"
    HARDCODED_SECRET = "Hardcoded Secret"
    COMPLEXITY_VIOLATION = "Excessive Complexity"
    GHOST_FILE = "Ghost File"


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class Violation:
    """Standardized violation record"""
    type: str
    severity: str
    source: str
    target: Optional[str] = None
    file_path: str = ""
    line: int = 0
    description: str = ""
    code_snippet: str = ""
    recommendation: str = ""


@dataclass
class AllowedCommunication:
    """Record of allowed cross-app communication (signals, tasks, etc.)"""
    type: str               # e.g., "Django Signal", "Celery Task"
    source_app: str
    target_app: str
    details: str


@dataclass
class ModuleMetrics:
    module_name: str
    app_name: str
    file_path: str
    lines_of_code: int = 0
    complexity: int = 0
    maintainability_index: float = 0.0
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    depth: int = 0
    test_coverage: Optional[float] = None
    docstring_coverage: float = 0.0
    type_hint_coverage: float = 0.0


@dataclass
class AppHealth:
    app_name: str
    overall_score: float
    grade: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    violations: List[Violation] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


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

FIRST_PARTY_APPS_FALLBACK = [
    'nexus_core', 'nexus_economy', 'nexus_gaming',
    'nexus_gateway', 'nexus_social', 'nexus_tournaments', 'nexus_content'
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_first_party(module_name: str, first_party_apps: List[str] = None) -> bool:
    """Check if a module belongs to the first-party apps."""
    if not module_name:
        return False
    apps = first_party_apps or FIRST_PARTY_APPS_FALLBACK
    return any(module_name.startswith(app) for app in apps)


def is_django_framework(module_name: str) -> bool:
    """Check if a module is part of Django or approved frameworks."""
    if module_name in DJANGO_ACCEPTABLE:
        return True
    return any(module_name.startswith(d) for d in [
        'django.', 'rest_framework', 'channels', 'celery.'
    ])


def is_stdlib(module_name: str) -> bool:
    """Check if a module is from the Python standard library."""
    if module_name in STDLIB_MODULES:
        return True
    return module_name.split('.')[0] in STDLIB_MODULES


def get_recommendation(test_id: str) -> str:
    """Get security recommendation for a bandit test ID."""
    recommendations = {
        'B105': 'Use environment variables for secrets, not hardcoded strings',
        'B106': 'Use environment variables for passwords',
        'B107': 'Use try-except with specific exceptions, not bare except',
        'B108': 'Use secure random number generators',
        'B110': 'Replace bare except: with except Exception:',
        'B112': 'Replace bare except: with specific exception handlers'
    }
    return recommendations.get(test_id, 'Review and fix based on security best practices')
