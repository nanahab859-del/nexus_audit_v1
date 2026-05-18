#!/usr/bin/env python3
"""Feature 2.4 & 2.5: Parallel AI + Progress Indicator"""
import os
rec_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/recommendations.py'
with open(rec_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FEATURES 2.4 & 2.5: Parallel AI + Progress ===")
# Add ThreadPoolExecutor import if not present
if 'from concurrent.futures import' not in code:
    old_imports = 'import time'
    new_imports = 'import time\nfrom concurrent.futures import ThreadPoolExecutor, as_completed'
    if old_imports in code:
        code = code.replace(old_imports, new_imports, 1)
        print("Added concurrent.futures import")
# Add a global progress tracking dict at the module level
progress_init = '''
# ── Progress tracking for parallel AI ─────────────────────────────────────
_ai_progress = {}  # {app_name: 'done'|'pending'}
_progress_lock = None
'''
# Insert after imports, before first function
if 'def build_health_prompt' in code:
    first_func = '\ndef build_health_prompt'
    code = code.replace(first_func, progress_init + '\n' + first_func, 1)
    print("Added progress tracking dict")
# Add a progress display function
progress_func = '''
def _show_ai_progress(app, status):
    """Update and display per-app AI progress."""
    import sys
    _ai_progress[app] = status
    done_count = sum(1 for s in _ai_progress.values() if s == 'done')
    total_count = len(_ai_progress)
    pending = [a for a, s in _ai_progress.items() if s == 'pending']
    status_str = ' '.join([
        f"{a} {'✅' if _ai_progress[a] == 'done' else '⏳'}"
        for a in sorted(_ai_progress.keys())
    ])
    print(f"\r[AI] {status_str:80s} {done_count}/{total_count}  ", end='', flush=True)
    sys.stdout.flush()
'''
# Look for where to insert the function (after build_health_prompt)
if 'def build_health_prompt' in code and '_show_ai_progress' not in code:
    # Insert before run_ai_recommendations
    to_insert = progress_func + '\n'
    if 'def run_ai_recommendations' in code:
        code = code.replace('\ndef run_ai_recommendations', to_insert + '\ndef run_ai_recommendations', 1)
        print("Added _show_ai_progress function")
with open(rec_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\nCompiling recommendations.py...")
result = os.system(f"python3 -m py_compile '{rec_file}'")
if result == 0:
    print("✓ Syntax OK")
else:
    print(f"✗ Compilation failed")
