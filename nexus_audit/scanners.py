"""
Code Quality Scanners
======================
Security scanning via Bandit, dead code detection via Vulture,
and complexity analysis via Radon and Lizard.
"""

import json
import os
import shutil
import subprocess
from typing import Dict, List, Any, Set
from .models import Violation
from .config import PROJECT_PATH, FIRST_PARTY_APPS


def run_bandit_enhanced(project_path: str) -> List[Violation]:
    """Run Bandit security scan on first-party apps."""
    violations = []
    try:
        bandit_path = shutil.which('bandit')
        if not bandit_path:
            bandit_path = os.path.expanduser('~/my_tools/miniconda3/envs/audit_env/bin/bandit')
        
        nexus_dirs = [os.path.join(project_path, app) for app in FIRST_PARTY_APPS if os.path.exists(os.path.join(project_path, app))]
        if nexus_dirs:
            result = subprocess.run(
                [bandit_path, '-r'] + nexus_dirs + ['-f', 'json', '-q', '--skip', 'B101,B104'],
                capture_output=True, text=True, timeout=120
            )
            if result.stdout and result.stdout.strip():
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    test_id = issue.get('test_id', '')
                    severity = issue.get('issue_severity', 'LOW')
                    type_map = {
                        'B105': 'Hardcoded Password',
                        'B106': 'Hardcoded Password',
                        'B107': 'Hardcoded Secret',
                        'B108': 'Insecure Random',
                        'B110': 'Bare Except',
                        'B112': 'Bare Except',
                    }
                    v_type = type_map.get(test_id, 'Security Issue')
                    violations.append(Violation(
                        type=v_type,
                        severity=severity,
                        source=os.path.basename(issue.get('filename', '')),
                        file_path=issue.get('filename', ''),
                        line=issue.get('line_number', 0),
                        description=f"{test_id}: {issue.get('issue_text', '')}",
                        code_snippet=issue.get('code', '')[:200],
                        recommendation="Review security issue and fix according to Bandit guidelines."
                    ))
    except Exception as e:
        print(f"⚠️ Enhanced security scan warning: {e}")
    return violations


def run_dead_code_scan(project_path: str) -> List[Dict]:
    """Run Vulture dead code detection on first-party apps."""
    dead_code = []
    try:
        vulture_path = shutil.which('vulture')
        if not vulture_path:
            vulture_path = os.path.expanduser('~/my_tools/miniconda3/envs/audit_env/bin/vulture')
        for app in FIRST_PARTY_APPS:
            app_path = os.path.join(project_path, app)
            if not os.path.exists(app_path):
                continue
            result = subprocess.run(
                [vulture_path, app_path, '--min-confidence=60', '--json'],
                capture_output=True, text=True, timeout=60
            )
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        dead_code.append({
                            'type': item.get('type', 'unknown'),
                            'name': item.get('name', 'unknown'),
                            'file': os.path.basename(item.get('filename', 'unknown')),
                            'full_path': item.get('filename', 'unknown'),
                            'line': item.get('line', 0),
                            'confidence': item.get('confidence', 0)
                        })
                except:
                    pass
    except Exception as e:
        print(f"⚠️ Dead code scan warning: {e}")
    return dead_code


def run_complexity_analysis(project_path: str) -> Dict[str, Any]:
    """Run Radon cyclomatic complexity analysis."""
    metrics = {
        'average_complexity': 0,
        'max_complexity': 0,
        'total_complexity': 0,
        'files_analyzed': 0,
        'functions_analyzed': 0,
        'high_complexity_functions': [],
        'maintainability_index': 0
    }
    try:
        radon_path = shutil.which('radon')
        if not radon_path:
            radon_path = os.path.expanduser('~/my_tools/miniconda3/envs/audit_env/bin/radon')
        file_complexity: Dict[str, Any] = {}
        for app in FIRST_PARTY_APPS:
            app_path = os.path.join(project_path, app)
            if not os.path.exists(app_path):
                continue
            result = subprocess.run(
                [radon_path, 'cc', app_path, '-a', '-s', '-j'],
                capture_output=True, text=True, timeout=60
            )
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for file_path, blocks in data.items():
                        file_comps = []
                        for block in blocks:
                            comp = block.get('complexity', 0)
                            metrics['total_complexity'] += comp
                            metrics['functions_analyzed'] += 1
                            metrics['max_complexity'] = max(metrics['max_complexity'], comp)
                            file_comps.append(comp)
                            if comp > 10:
                                metrics['high_complexity_functions'].append({
                                    'file': os.path.basename(file_path),
                                    'full_path': file_path,
                                    'function': block.get('name', 'unknown'),
                                    'complexity': comp,
                                    'line': block.get('lineno', 0),
                                    'lines': 0
                                })
                        if file_comps:
                            rel = os.path.relpath(file_path, project_path).replace('\\', '/')
                            file_complexity[rel] = {
                                'average': sum(file_comps) / len(file_comps),
                                'max': max(file_comps),
                                'functions': len(file_comps)
                            }
                            metrics['files_analyzed'] += 1
                except:
                    pass
        metrics['file_complexity'] = file_complexity
    except Exception as e:
        print(f"⚠️ Complexity analysis warning: {e}")
    if metrics['functions_analyzed'] > 0:
        metrics['average_complexity']   = metrics['total_complexity'] / metrics['functions_analyzed']
        metrics['maintainability_index'] = max(0, min(100, 171 - 5.2 * metrics['average_complexity']))
        metrics['radon_available']       = True
    else:
        metrics['average_complexity']   = 0.0
        metrics['maintainability_index'] = None
        metrics['radon_available']       = False
        print("   ⚠ radon not available — complexity metrics will show N/A in report.")
        print("     Install with: pip install radon")
    return metrics



def run_lizard_analysis(project_path: str) -> Dict[str, Any]:
    """Run Lizard complexity analysis (with Radon fallback)."""
    metrics = run_complexity_analysis(project_path)
    try:
        lizard_path = shutil.which('lizard')
        if not lizard_path:
            return metrics
        for app in FIRST_PARTY_APPS:
            app_path = os.path.join(project_path, app)
            if not os.path.exists(app_path):
                continue
            result = subprocess.run(
                [lizard_path, app_path, '-l', 'python', '--csv'],
                capture_output=True, text=True, timeout=120
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]
                complexities = []
                total_nloc = 0
                for line in lines:
                    parts = line.split(',')
                    if len(parts) >= 5:
                        nloc = int(parts[0])
                        ccn = int(parts[1])
                        function_name = parts[2].strip()
                        file_path = parts[4] if len(parts) > 4 else ''
                        if function_name.isdigit() or function_name == "":
                            continue
                        complexities.append(ccn)
                        metrics['total_complexity'] += ccn
                        metrics['functions_analyzed'] += 1
                        total_nloc += nloc
                        if ccn > 10:
                            metrics['high_complexity_functions'].append({
                                'file': os.path.basename(file_path),
                                'full_path': file_path,
                                'function': function_name,
                                'complexity': ccn,
                                'lines': nloc
                            })
                        metrics['max_complexity'] = max(metrics['max_complexity'], ccn)
                if complexities:
                    metrics['average_complexity'] = sum(complexities) / len(complexities)
                    metrics['maintainability_index'] = max(0, min(100,
                        171 - 5.2 * metrics['average_complexity'] - 0.23 * (total_nloc / max(1, metrics['functions_analyzed']))
                    ))
    except Exception as e:
        print(f"⚠️ Lizard analysis warning: {e}")
    return metrics


def is_ghost_file(physical_file: str, dna_modules: Set[str]) -> bool:
    """Check if a physical file exists but is not in the DNA scan."""
    from .config import is_first_party
    if not is_first_party(physical_file):
        return False
    if '.migrations.' in physical_file or physical_file.endswith('.tests') or physical_file == 'manage':
        return False
    if physical_file.endswith('.__init__'):
        parent_module = physical_file.replace('.__init__', '')
        return parent_module not in dna_modules
    return physical_file not in dna_modules
