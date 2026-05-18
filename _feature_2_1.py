#!/usr/bin/env python3
"""Feature 2.1: Change Summary Banner"""
import os
main_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/main.py'
with open(main_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FEATURE 2.1: Change Summary Banner ===")
# Add imports if needed
if 'import glob' not in code:
    old_line = "import os"
    new_lines = "import os\nimport glob"
    code = code.replace(old_line, new_lines, 1)
    print("Added glob import")
# Add helper functions before main()
helper_functions = '''
def load_previous_audit(history_dir: str) -> dict | None:
    """Load most recent audit JSON from history_dir. Returns None if none exists."""
    files = sorted(glob.glob(os.path.join(history_dir, '*.json')))
    if not files:
        return None
    try:
        with open(files[-1], 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None
def compute_change_summary(current: dict, previous: dict | None) -> dict:
    """Compare current audit with previous run. Return change summary."""
    if not previous:
        return {'first_run': True}
    cur_viols  = {str(v.get('source','')) + str(v.get('target','')) 
                  for v in current.get('violations', [])}
    prev_viols = {str(v.get('source','')) + str(v.get('target','')) 
                  for v in previous.get('violations', [])}
    cur_scores  = {a: s.get('score', 0) 
                   for a, s in current.get('app_stats', {}).items()}
    prev_scores = {a: s.get('score', 0) 
                   for a, s in previous.get('app_stats', {}).items()}
    return {
        'first_run': False,
        'new_violations': len(cur_viols - prev_viols),
        'resolved': len(prev_viols - cur_viols),
        'score_deltas': {a: cur_scores.get(a, 0) - prev_scores.get(a, 0) 
                        for a in cur_scores},
    }
'''
# Find where to insert the functions (before main() or at the end of imports)
if 'def main(' in code:
    # Insert before main()
    old_pattern = '\ndef main('
    new_pattern = helper_functions + '\ndef main('
    code = code.replace(old_pattern, new_pattern, 1)
    print("Added helper functions")
else:
    print("SKIP: Could not find main() function")
with open(main_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\nCompiling main.py...")
result = os.system(f"python3 -m py_compile '{main_file}'")
if result == 0:
    print("✓ Syntax OK")
else:
    print(f"✗ Compilation failed")
