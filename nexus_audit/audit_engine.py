"""
Audit Engine
============
Core audit logic: app scoring, cross-app connection classification,
circular dependency detection, and first-party app discovery.
"""

import ast
import importlib.util
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from .config import PROJECT_PATH, FIRST_PARTY_APPS, CROSS_APP_IMPORT_PENALTY, is_first_party, is_django_framework, is_stdlib


def get_first_party_apps(project_path: str) -> List[str]:
    """
    Attempt to extract first-party app names from Django settings.
    Looks for nexus_gaming/settings.py and parses INSTALLED_APPS.
    Returns a list of app names that are local to the project (not third-party).
    """
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

# Bootstrap files that are always exempt from cross-app violations
BOOTSTRAP_LEAVES = {
    'asgi', 'wsgi', 'settings', 'celery', 'manage', 'routing', 'apps', 'admin',
}


def get_git_context(project_path: str) -> Dict[str, str]:
    """Detect GitHub remote, branch, and commit for the project."""
    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()[:7]
        if not remote:
            return {}
        if remote.startswith("git@"):
            remote_path = remote.split(":", 1)[1]
            if remote_path.endswith(".git"):
                remote_path = remote_path[:-4]
            remote = "https://github.com/" + remote_path
        elif remote.startswith("https://github.com/") and remote.endswith(".git"):
            remote = remote[:-4]
        return {"github_base": remote, "branch": branch, "commit": commit}
    except Exception:
        return {}


def find_import_line(source_module: str, target_module: str, project_path: str) -> int:
    """Best-effort AST lookup for the line number of a cross-app import."""
    source_path = Path(project_path) / Path(source_module.replace(".", "/")).with_suffix(".py")
    if not source_path.exists():
        return 0
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    source_root = source_module.split(".")[0]
    target_root = target_module.split(".")[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name or ""
                if name == target_module or name.startswith(target_module + ".") or target_module.startswith(name + "."):
                    return getattr(node, "lineno", 0) or 0
                if name.split(".")[0] == target_root and source_root != target_root:
                    return getattr(node, "lineno", 0) or 0
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            if module_name == target_module or module_name.startswith(target_module + ".") or target_module.startswith(module_name + "."):
                return getattr(node, "lineno", 0) or 0
            if module_name.split(".")[0] == target_root and source_root != target_root:
                return getattr(node, "lineno", 0) or 0

    try:
        for lineno, line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if (stripped.startswith("import ") or stripped.startswith("from ")) and target_root in stripped:
                return lineno
    except Exception:
        return 0
    return 0


def is_ghost_file(physical_file: str, dna_modules: Set[str]) -> bool:
    """
    Check if a physical file is a 'ghost' (exists on disk but not in DNA).
    Ghost files indicate dead code or missing module documentation.
    """
    if not is_first_party(physical_file):
        return False
    if '.migrations.' in physical_file or physical_file.endswith('.tests') or physical_file == 'manage':
        return False
    if physical_file.endswith('.__init__'):
        parent_module = physical_file.replace('.__init__', '')
        return parent_module not in dna_modules
    return physical_file not in dna_modules


def classify_connection(source: str, target: str) -> Tuple[str, int, bool, Optional[str]]:
    """
    Django-aware cross-app import classification.
    Returns: (type, severity, is_violation, allowed_comm_type)

    ── EXEMPTION POLICY ─────────────────────────────────────────────────────
    Django projects have mandatory infrastructure files that MUST import
    across app boundaries. These are never architectural violations:

      asgi.py / wsgi.py  — Entry points that wire routing/middleware.
      apps.py            — AppConfig.ready() is the correct Django place
      settings.py        — INSTALLED_APPS must list every app by module path.
      celery.py          — Celery entry point, always app-level.
      manage.py          — Django management entry point.
      routing.py         — Channel/WebSocket routing.

    These files get conn_type "Django Bootstrap (Exempt)" and are recorded
    in allowed_communications so the report stays informative, but they
    never increment violation counters or affect health scores.

    ── CLASSIFICATION ORDER ─────────────────────────────────────────────────
    1. Same app            → Internal (never a violation)
    2. Framework / stdlib  → Framework/Stdlib (never a violation)
    3. Source not in 1st party → External (ignored)
    4. Bootstrap source    → Django Bootstrap (Exempt)
    5. Signal / receiver   → Django Signal (allowed comm)
    6. Task / worker       → Celery Task (allowed comm)
    7. Everything else     → Cross-App Import (VIOLATION)
    """
    src_parts = source.split('.')
    tgt_parts = target.split('.')

    # ── 1. Same app (internal) ────────────────────────────────────────────
    if src_parts[0] == tgt_parts[0]:
        return "Internal", 0, False, None

    # ── 2. Framework / stdlib target ──────────────────────────────────────
    if is_django_framework(target) or is_stdlib(target):
        return "Framework/Stdlib", 0, False, None

    # ── 3. Source not first-party ─────────────────────────────────────────
    if not is_first_party(source):
        return "External", 0, False, None

    if is_first_party(source) and is_first_party(target):
        src_leaf  = src_parts[-1].lower()
        tgt_leaf  = tgt_parts[-1].lower()
        tgt_lower = target.lower()
        src_lower = source.lower()

        # ── 4. Django bootstrap files — EXEMPT ────────────────────────────
        if src_leaf in BOOTSTRAP_LEAVES:
            return "Django Bootstrap (Exempt)", 0, False, "bootstrap"

        # ── 5. Signal / receiver modules ──────────────────────────────────
        SIGNAL_LEAVES = {'signals', 'receivers', 'signal', 'receiver'}
        if ('django.dispatch' in tgt_lower
                or tgt_leaf in SIGNAL_LEAVES
                or src_leaf in SIGNAL_LEAVES):
            return "Django Signal", 0, False, "signal"

        # ── 6. Celery / async task modules ────────────────────────────────
        TASK_KEYWORDS = {'task', 'tasks', 'celery', 'worker', 'beat'}
        if (tgt_leaf in TASK_KEYWORDS
                or any(k in tgt_lower for k in TASK_KEYWORDS)
                or any(k in src_lower for k in TASK_KEYWORDS)):
            return "Celery Task", 0, False, "task"

        # ── 7. Test files — cross-app but excluded from scoring ───────────
        src_parts_all = source.split('.')
        if any('test' in p for p in src_parts_all):
            return "Test Cross-App Import", 0, False, "test_cross_app"

        # ── 8. Everything else = architectural violation ───────────────────
        return "Cross-App Import", CROSS_APP_IMPORT_PENALTY, True, None

    return "Unknown", 5, False, None


def calculate_app_score(app_name: str, metrics_data: Dict[str, Any]) -> float:
    """Calculate a health score (0-100) for an app based on violations and issues."""
    from .config import SCORING_EXCLUDE_TESTS
    
    base_score = 100.0
    is_core_app = app_name in ['nexus_core', 'nexus_gateway']
    
    violations = metrics_data.get('violations', [])
    if SCORING_EXCLUDE_TESTS:
        violations = [v for v in violations if '/tests/' not in (v.file_path if hasattr(v, 'file_path') else v.get('file_path', ''))]
    base_score -= len(violations) * (3 if is_core_app else 5)
    
    security_findings = metrics_data.get('security_findings', [])
    if SCORING_EXCLUDE_TESTS:
        security_findings = [s for s in security_findings if '/tests/' not in (s.file_path if hasattr(s, 'file_path') else s.get('file_path', ''))]
    security_penalties = {'HIGH': 12, 'MEDIUM': 6, 'LOW': 3}
    for issue in security_findings:
        severity = issue.severity if hasattr(issue, 'severity') else issue.get('severity', 'LOW')
        base_score -= security_penalties.get(severity, 3)
    
    avg_complexity = metrics_data.get('avg_complexity', 0)
    if avg_complexity > 10:
        base_score -= min(20, (avg_complexity - 10) * 2)
    
    dead_code = len(metrics_data.get('dead_code', []))
    base_score -= min(15, dead_code * 3)
    
    ghost_files = metrics_data.get('ghost_files', 0)
    base_score -= min(10, ghost_files * 2)
    
    # Core apps (nexus_core, nexus_gateway) are architectural hubs — they legitimately
    # import more and serve more apps, so a +10 bonus offsets the hub-penalty from violations.
    # This acknowledges that high connectivity in core infrastructure is expected and necessary.
    if is_core_app:
       base_score += 10
    
    return max(0, min(100, base_score))


def find_circular_dependencies_accurate(dna: Dict) -> List[Dict]:
    """
    Detect circular dependencies between first-party apps using an ITERATIVE
    stack-based DFS.

    FIX — Bug 3 (2026-04-15):
      Old implementation used a nested recursive dfs() function which hits
      Python's default 1000-frame recursion limit on any non-trivial codebase.
      New implementation uses an explicit stack so it scales to any graph size.

    Additional improvement:
      - Also detects INTRA-app cycles (within a single app), not just cross-app.
      - Severity: 'critical' for 2-node mutual cycles, 'high' for 3–4 nodes,
        'medium' for longer chains.
    """
    # Build adjacency for ALL first-party modules (intra + cross app)
    graph: Dict[str, Set[str]] = defaultdict(set)
    for module, data in dna.items():
        if module == "__main__" or not is_first_party(module):
            continue
        for imp in data.get('imports', []):
            if is_first_party(imp) and imp in dna and imp != module:
                graph[module].add(imp)

    raw_cycles: List[List[str]] = []
    visited:    Set[str]        = set()

    for start in graph:
        if start in visited:
            continue

        # Stack entries: (node, neighbour-iterator, current-path-as-list)
        path:      List[str] = []
        path_set:  Set[str]  = set()
        stack: List[Tuple[str, Any]] = [(start, iter(graph.get(start, [])))]
        path.append(start)
        path_set.add(start)

        while stack:
            node, nbrs = stack[-1]
            try:
                nxt = next(nbrs)
                if nxt in path_set:
                    # Back-edge → cycle found
                    idx   = path.index(nxt)
                    cycle = path[idx:] + [nxt]
                    if len(cycle) > 2:          # ignore self-loops (len == 2)
                        raw_cycles.append(cycle)
                elif nxt not in visited:
                    path.append(nxt)
                    path_set.add(nxt)
                    stack.append((nxt, iter(graph.get(nxt, []))))
            except StopIteration:
                visited.add(node)
                stack.pop()
                if path and path[-1] == node:
                    path.pop()
                    path_set.discard(node)

    # Deduplicate: same node-set = same cycle
    seen:         Set[frozenset]  = set()
    unique_cycles: List[Dict]     = []

    def _is_models_package_cycle(nodes: list) -> bool:
        """True if the cycle is a Django models/__init__.py ↔ models/submodule pattern."""
        parts = [set(n.split('.')) for n in nodes]
        return (
            all('models' in p for p in parts)  # every node is in a models module
            and len(set(n.split('.')[0] for n in nodes)) == 1  # same app
        )

    for cycle in raw_cycles:
        key = frozenset(cycle)
        if key in seen:
            continue
        seen.add(key)
        nodes    = cycle[:-1]           # drop the repeated closing node
        src_apps = {n.split('.')[0] for n in nodes}
        is_cross = len(src_apps) > 1
        length   = len(nodes)

        if _is_models_package_cycle(nodes):
            severity = 'info'
        elif is_cross:
            severity = 'critical'
        elif length == 2:
            severity = 'high'
        elif length <= 4:
            severity = 'medium'
        else:
            severity = 'low'

        unique_cycles.append({
            'nodes':     nodes,
            'length':    length,
            'severity':  severity,
            'cross_app': is_cross,
            'apps':      sorted(src_apps),
            'django_pattern': _is_models_package_cycle(nodes),
        })

    # Surface cross-app cycles first, then by severity, then by length
    sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    unique_cycles.sort(key=lambda c: (
        not c['cross_app'],
        sev_order.get(c['severity'], 9),
        c['length']
    ))
    return unique_cycles
