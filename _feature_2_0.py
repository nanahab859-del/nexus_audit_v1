#!/usr/bin/env python3
"""Feature 2.0: Parallel Scanner Execution"""
import os
main_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/main.py'
with open(main_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FEATURE 2.0: Parallel Scanner Execution ===")
# Step 1: Add ThreadPoolExecutor import if not already present
if 'from concurrent.futures import ThreadPoolExecutor' not in code:
    # Find the imports section and add after other concurrent imports
    old_imports = """import json
import os
from datetime import datetime"""
    new_imports = """import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor"""
    if old_imports in code:
        code = code.replace(old_imports, new_imports, 1)
        print("Added concurrent.futures import")
    else:
        print("SKIP: Could not find import section to add ThreadPoolExecutor")
else:
    print("ThreadPoolExecutor already imported")
# Step 2: Replace sequential scanner calls with parallel execution
old_scanners = """    # ── Run scanners ──────────────────────────────────────────────────────
    security_violations = run_bandit_enhanced(PROJECT_PATH)
    dead_code = run_dead_code_scan(PROJECT_PATH)
    complexity_metrics = run_lizard_analysis(PROJECT_PATH)"""
new_scanners = """    # ── Run scanners ──────────────────────────────────────────────────────
    print("   Running scanners in parallel (bandit + dead code + complexity)...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_security   = executor.submit(run_bandit_enhanced, PROJECT_PATH)
        f_dead_code  = executor.submit(run_dead_code_scan,  PROJECT_PATH)
        f_complexity = executor.submit(run_lizard_analysis, PROJECT_PATH)
    security_violations = f_security.result()
    dead_code           = f_dead_code.result()
    complexity_metrics  = f_complexity.result()
    print(f"   Scanners complete — {len(security_violations)} security findings, "
          f"{len(dead_code)} dead code items")"""
if old_scanners in code:
    code = code.replace(old_scanners, new_scanners, 1)
    print("Replaced scanner calls with parallel execution")
else:
    print("SKIP: Could not find scanner calls to replace")
with open(main_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\nCompiling main.py...")
result = os.system(f"python3 -m py_compile '{main_file}'")
if result == 0:
    print("✓ Syntax OK")
else:
    print(f"✗ Compilation failed")
