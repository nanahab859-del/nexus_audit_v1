"""
Dependency Cache Vault
======================
Smart caching for Tier 2 dependency scans.
Minimizes network roundtrips to PyPI and OSV.
"""

import json
import os
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Any

CACHE_FILENAME = ".dep_cache.json"

# Store the cache next to this file (inside the nexus_audit package dir),
# NOT inside nexus_project_copy which gets wiped and recreated every run.
_CACHE_DIR = os.path.dirname(os.path.abspath(__file__))

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _parse_time(ts_str: str) -> datetime:
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)

def get_requirements_hash(req_paths: List[str]) -> str:
    """Computes a SHA-256 hash of the first found requirements.txt file."""
    for req_path in req_paths:
        if os.path.exists(req_path):
            try:
                with open(req_path, 'rb') as f:
                    return "sha256:" + hashlib.sha256(f.read()).hexdigest()
            except Exception:
                return "error"
    return "missing"

def load_cache(project_path: str = "") -> Dict[str, Any]:
    """Load the vault from the stable tool directory."""
    cache_path = os.path.join(_CACHE_DIR, CACHE_FILENAME)
    if not os.path.exists(cache_path):
        return {"packages": {}}
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "packages" not in data:
                data["packages"] = {}
            return data
    except Exception:
        return {"packages": {}}


def save_cache(project_path: str, data: Dict[str, Any]) -> None:
    """Save the vault to the stable tool directory."""
    cache_path = os.path.join(_CACHE_DIR, CACHE_FILENAME)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def get_ttl_for_package(pkg_entry: Dict[str, Any]) -> int:
    """Returns the TTL in hours based on risk level."""
    # Critical/High CVEs: 24 hours
    for cve in pkg_entry.get("cves", []):
        if cve.get("severity") in ("CRITICAL", "HIGH"):
            return 24
    # Outdated package: 48 hours
    if pkg_entry.get("outdated"):
        return 48
    # Clean, up-to-date package: 168 hours (7 days)
    return 168

def get_packages_to_scan(
    cache: Dict[str, Any],
    all_packages: List[str],
    current_versions: Dict[str, str],
    req_hash: str,
    force_rescan: bool = False
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Returns:
      needs_scan: List of package names that must be re-queried.
      from_cache: List of fully hydrated package dicts from cache.
    """
    needs_scan = []
    from_cache = []
    now = datetime.now(timezone.utc)
    
    cached_pkgs = cache.get("packages", {})
    
    # Fast path: if requirements haven't changed AND no force rescan,
    # we can potentially skip scanning entirely if TTLs are okay.
    req_changed = (cache.get("requirements_hash") != req_hash)
    
    for pkg in all_packages:
        pkg_lower = pkg.lower()
        installed_ver = current_versions.get(pkg_lower, 'unknown')
        
        if force_rescan:
            needs_scan.append(pkg)
            continue
            
        if pkg not in cached_pkgs:
            needs_scan.append(pkg)
            continue
            
        cached_entry = cached_pkgs[pkg]
        
        # Did the pinned version change?
        if cached_entry.get("installed") != installed_ver:
            needs_scan.append(pkg)
            continue
            
        # Is the cache stale?
        last_checked = _parse_time(cached_entry.get("last_checked", ""))
        ttl_hours = cached_entry.get("ttl_hours", 24)
        age_hours = (now - last_checked).total_seconds() / 3600.0
        
        if age_hours > ttl_hours:
            needs_scan.append(pkg)
            continue
            
        # Everything looks good, use cache
        from_cache.append(cached_entry)
        
    return needs_scan, from_cache

def merge_results(
    from_cache: List[Dict[str, Any]],
    fresh_results: List[Dict[str, Any]],
    req_hash: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Merges cached and fresh results to build the final result dict for dependency.py,
    and returns the new cache dictionary to be saved.
    """
    final_packages = []
    total_cves = 0
    outdated_count = 0
    critical_cves = []
    
    new_cache_pkgs = {}
    now_str = _utc_now()
    
    # Process cached results
    for pkg_entry in from_cache:
        final_packages.append(pkg_entry)
        new_cache_pkgs[pkg_entry["name"]] = pkg_entry
        
        if pkg_entry.get("outdated"):
            outdated_count += 1
        total_cves += pkg_entry.get("cve_count", 0)
        
        pkg_name = pkg_entry["name"]
        for cve in pkg_entry.get("cves", []):
            severity = cve.get("severity", "UNKNOWN")
            if severity in ("CRITICAL", "HIGH"):
                critical_cves.append({
                    "package": pkg_name,
                    "id": cve.get("id", "unknown"),
                    "summary": cve.get("summary", "No summary"),
                    "severity": severity
                })
                
    # Process fresh results
    for res in fresh_results:
        # Build the pkg_entry exactly like dependency.py does
        pkg_name = res["pkg_name"]
        installed = res["installed"]
        latest = res["latest"] if res["latest"] != "unknown" else installed
        outdated = res["outdated"]
        cve_count = res["cve_count"]
        cves = res["cves"]
        
        pkg_entry = {
            "name": pkg_name,
            "installed": installed,
            "latest": latest,
            "outdated": outdated,
            "cve_count": cve_count,
            "cves": cves,
            "upgrade_cmd": f"pip install --upgrade {pkg_name}=={latest}" if outdated else None,
            # Cache specific fields
            "last_checked": now_str,
        }
        # compute TTL
        pkg_entry["ttl_hours"] = get_ttl_for_package(pkg_entry)
        
        final_packages.append(pkg_entry)
        new_cache_pkgs[pkg_name] = pkg_entry
        
        if outdated:
            outdated_count += 1
        total_cves += cve_count
        
        for cve in cves:
            severity = cve.get("severity", "UNKNOWN")
            if severity in ("CRITICAL", "HIGH"):
                critical_cves.append({
                    "package": pkg_name,
                    "id": cve.get("id", "unknown"),
                    "summary": cve.get("summary", "No summary"),
                    "severity": severity
                })
                
    result = {
        "packages": final_packages,
        "total_cves": total_cves,
        "outdated_count": outdated_count,
        "critical_cves": critical_cves
    }
    
    new_cache = {
        "requirements_hash": req_hash,
        "last_full_scan": now_str,
        "packages": new_cache_pkgs
    }
    
    return result, new_cache
