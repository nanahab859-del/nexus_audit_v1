"""
Tier 2 Dependency Scanning
==========================
Offline-safe functions for scanning PyPI packages, detecting CVEs via OSV,
and checking for outdated versions. These functions only run when internet
is available (Tier 2 mode).
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple
from .config import TIER2_TIMEOUT, TIER2_PACKAGES

_REQ_TXT_PATHS = [
    os.path.expanduser('~/nexus-gaming/requirements.txt'),
    os.path.expanduser('~/my_tools/nexus_audit/requirements.txt'),
]


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
            break   # found the first valid requirements.txt
    if not pkg_names:   # hard fallback
        pkg_names = ['django','celery','channels','djangorestframework',
                     'redis','psycopg2','Pillow','cryptography',
                     'requests','urllib3','pyjwt','paramiko']
    return pkg_names, version_map


_REQ_PACKAGES, _REQ_VERSIONS = _load_requirements_packages()


def _detect_internet(timeout: int = TIER2_TIMEOUT) -> bool:
    """
    Fast check: can we reach PyPI? If yes, Tier 2 features activate.
    Uses a HEAD request so no body is downloaded.
    """
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
    """Fetch package metadata from PyPI. Returns None on any error."""
    try:
        url  = f'https://pypi.org/pypi/{package}/json'
        req  = urllib.request.Request(url, headers={'User-Agent': 'nexus-audit/1.0'})
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None


def _osv_query(package: str, ecosystem: str = 'PyPI',
                timeout: int = TIER2_TIMEOUT) -> List[Dict]:
    """
    Query the OSV (Open Source Vulnerabilities) database for known CVEs.
    https://osv.dev — free, no auth, covers PyPI, npm, Go, Maven, etc.
    Returns a list of vulnerability dicts, or [] on any error.
    """
    try:
        payload = json.dumps({
            'package': {'name': package, 'ecosystem': ecosystem}
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.osv.dev/v1/query',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent':   'nexus-audit/1.0',
            }
        )
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode('utf-8'))
        vulns = data.get('vulns', [])
        # Trim each CVE to only the fields the dashboard renders.
        # Full OSV objects are ~4KB each; trimmed objects are ~120 bytes.
        # With 150+ CVEs across 116 packages this saves ~700KB in the HTML.
        trimmed = []
        for v in vulns:
            sev = ''
            for s in (v.get('severity') or []):
                if s.get('score'):
                    sev = s['score']
                    break
            ref_url = ''
            refs = v.get('references') or []
            if refs:
                ref_url = refs[0].get('url', '')
            trimmed.append({
                'id':       v.get('id', ''),
                'summary':  v.get('summary', ''),
                'severity': sev,
                'url':      ref_url,
            })
        return trimmed
    except Exception:
        return []


def run_tier2_dependency_scan(project_path: str, force_rescan: bool = False) -> Dict:
    """
    Tier 2: scan installed packages for:
      1. Known CVEs via OSV
      2. Outdated versions via PyPI

    Returns a dict: {
        'packages': [{name, installed, latest, outdated, cve_count, cves}],
        'total_cves': int,
        'outdated_count': int,
        'critical_cves': [{package, id, summary, severity}],
    }
    Completely safe to call; any individual failure returns partial results.
    """
    import concurrent.futures
    from .dep_cache import load_cache, save_cache, get_requirements_hash, get_packages_to_scan, merge_results

    # 1. Load cache and compute hash
    cache = load_cache(project_path)
    req_hash = get_requirements_hash(_REQ_TXT_PATHS)
    
    # 2. Determine what needs scanning
    needs_scan, from_cache = get_packages_to_scan(
        cache=cache,
        all_packages=_REQ_PACKAGES,
        current_versions=_REQ_VERSIONS,
        req_hash=req_hash,
        force_rescan=force_rescan
    )
    
    total_pkgs = len(_REQ_PACKAGES)
    num_cached = len(from_cache)
    num_to_scan = len(needs_scan)
    
    if num_to_scan == 0:
        print(f"   📦 {total_pkgs} packages — 100% loaded from Dependency Vault (saved ~60s)")
        # Just merge everything from cache
        result, new_cache = merge_results(from_cache, [], req_hash)
        save_cache(project_path, new_cache)
        return result

    print(f"   📦 {total_pkgs} packages — {num_cached} from Vault, {num_to_scan} to scan...")
    
    def _scan_pkg(pkg_name: str) -> Dict:
        installed = _REQ_VERSIONS.get(pkg_name.lower(), 'unknown')
        pypi_data = _pypi_get(pkg_name)
        latest = pypi_data.get('info', {}).get('version', 'unknown') if pypi_data else 'unknown'
        outdated = (latest != 'unknown' and installed != 'unknown' and installed != latest)
        cves = _osv_query(pkg_name)
        
        return {
            'pkg_name': pkg_name,
            'installed': installed,
            'latest': latest,
            'outdated': outdated,
            'cves': cves,
            'cve_count': len(cves)
        }

    fresh_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_scan_pkg, pkg): pkg for pkg in needs_scan}
        completed = 0

        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            fresh_results.append(res)
            completed += 1
            
            pkg_name = res['pkg_name']
            
            # Build status line
            status_parts = []
            if res['installed'] != 'unknown':
                status_parts.append(res['installed'])
            if res['outdated']:
                status_parts.append(f"↗ {res['latest']} available")
            else:
                status_parts.append("✔ current")
            if res['cve_count']:
                status_parts.append(f"⚠ {res['cve_count']} CVE(s)")
            
            status_str = " | ".join(status_parts)
            print(f"   [{completed}/{num_to_scan}] {pkg_name:<30} {status_str}", flush=True)

    print(f"   ✔ Scanned {num_to_scan} package(s)")
    
    # Merge and save
    result, new_cache = merge_results(from_cache, fresh_results, req_hash)
    save_cache(project_path, new_cache)
    
    return result


# ============================================================================
# DEPENDENCY CLASSIFICATION & ANALYSIS
# ============================================================================

def classify_connection(source: str, target: str, first_party_apps: List[str]) -> Tuple[str, int, bool, Optional[str]]:
    """
    Django-aware cross-app import classification.
    Returns: (type, severity, is_violation, allowed_comm_type)

    ── EXEMPTION POLICY ────────────────────────────────────────
    Django projects have mandatory infrastructure files that MUST
    import across app boundaries (asgi.py, wsgi.py, apps.py,
    settings.py, celery.py, manage.py, routing.py).
    These never count as architectural violations.
    """
    from .config import is_first_party, is_django_framework, is_stdlib, CROSS_APP_IMPORT_PENALTY
    
    src_parts = source.split('.')
    tgt_parts = target.split('.')

    # 1. Same app → Internal (never a violation)
    if src_parts[0] == tgt_parts[0]:
        return "Internal", 0, False, None

    # 2. Framework / stdlib target → never a violation
    if is_django_framework(target) or is_stdlib(target):
        return "Framework/Stdlib", 0, False, None

    # 3. Source not first-party → ignore
    if not is_first_party(source):
        return "External", 0, False, None

    if is_first_party(source) and is_first_party(target):
        src_leaf  = src_parts[-1].lower()
        tgt_leaf  = tgt_parts[-1].lower()
        tgt_lower = target.lower()
        src_lower = source.lower()

        # 4. Django bootstrap files — EXEMPT
        BOOTSTRAP_LEAVES = {
            'asgi', 'wsgi', 'settings', 'celery', 'manage', 'routing', 'apps', 'admin',
        }
        if src_leaf in BOOTSTRAP_LEAVES:
            return "Django Bootstrap (Exempt)", 0, False, "bootstrap"

        # 5. Signal / receiver modules
        SIGNAL_LEAVES = {'signals', 'receivers', 'signal', 'receiver'}
        if ('django.dispatch' in tgt_lower
                or tgt_leaf in SIGNAL_LEAVES
                or src_leaf in SIGNAL_LEAVES):
            return "Django Signal", 0, False, "signal"

        # 6. Celery / async task modules
        TASK_KEYWORDS = {'task', 'tasks', 'celery', 'worker', 'beat'}
        if (tgt_leaf in TASK_KEYWORDS
                or any(k in tgt_lower for k in TASK_KEYWORDS)
                or any(k in src_lower for k in TASK_KEYWORDS)):
            return "Celery Task", 0, False, "task"

        # 7. Test files — cross-app but excluded from scoring
        src_parts_all = source.split('.')
        if any('test' in p for p in src_parts_all):
            return "Test Cross-App Import", 0, False, "test_cross_app"

        # 8. Everything else = architectural violation
        return "Cross-App Import", CROSS_APP_IMPORT_PENALTY, True, None

    return "Unknown", 5, False, None


def find_circular_dependencies_accurate(dna: Dict, first_party_apps: List[str]) -> List[Dict]:
    """
    Detect circular dependencies using iterative DFS (not recursive).
    Returns list of unique cycles with metadata.
    """
    from .config import is_first_party
    from collections import defaultdict

    # Build adjacency for all first-party modules
    graph: Dict[str, set] = defaultdict(set)
    for module, data in dna.items():
        if module == "__main__" or not is_first_party(module):
            continue
        for imp in data.get('imports', []):
            if is_first_party(imp) and imp in dna and imp != module:
                graph[module].add(imp)

    raw_cycles: List[List[str]] = []
    visited: set = set()

    for start in graph:
        if start in visited:
            continue

        path: List[str] = []
        path_set: set = set()
        stack: List[Tuple[str, any]] = [(start, iter(graph.get(start, [])))]
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
                    if len(cycle) > 2:  # ignore self-loops
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

    # Deduplicate cycles
    seen: set = set()
    unique_cycles: List[Dict] = []

    def _is_models_package_cycle(nodes: list) -> bool:
        """Check if this is a Django models/__init__.py ↔ models/submodule pattern."""
        parts = [set(n.split('.')) for n in nodes]
        return (
            all('models' in p for p in parts)
            and len(set(n.split('.')[0] for n in nodes)) == 1
        )

    for cycle in raw_cycles:
        key = frozenset(cycle)
        if key in seen:
            continue
        seen.add(key)
        nodes = cycle[:-1]  # drop repeated closing node
        src_apps = {n.split('.')[0] for n in nodes}
        is_cross = len(src_apps) > 1
        length = len(nodes)

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
            'nodes': nodes,
            'length': length,
            'severity': severity,
            'cross_app': is_cross,
            'apps': sorted(src_apps),
            'django_pattern': _is_models_package_cycle(nodes),
        })

    # Sort by severity
    sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    unique_cycles.sort(key=lambda c: (
        not c['cross_app'],
        sev_order.get(c['severity'], 9),
        c['length']
    ))
    return unique_cycles
