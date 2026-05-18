#!/usr/bin/env python3
"""Feature 2.4 Part 1: Add threading.Lock to KeyPool"""
import os
key_pool_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/key_pool.py'
with open(key_pool_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FEATURE 2.4 PART 1: Add threading.Lock to KeyPool ===")
# Add threading import if not present
if 'import threading' not in code:
    old_imports = 'import time'
    new_imports = 'import time\nimport threading'
    if old_imports in code:
        code = code.replace(old_imports, new_imports, 1)
        print("Added threading import")
# Add _lock to __init__
old_init_end = '''        self._rr = 0'''
new_init_end = '''        self._rr = 0
        self._lock = threading.Lock()'''
if old_init_end in code:
    code = code.replace(old_init_end, new_init_end, 1)
    print("Added _lock to __init__")
# Wrap _rr increment with lock in get_key
old_get_key = '''        if task in self.HEAVY:
            return av[0]["key"]
        idx = self._rr % len(av)
        self._rr += 1
        return av[idx]["key"]'''
new_get_key = '''        if task in self.HEAVY:
            return av[0]["key"]
        with self._lock:
            idx = self._rr % len(av)
            self._rr += 1
        return av[idx]["key"]'''
if old_get_key in code:
    code = code.replace(old_get_key, new_get_key, 1)
    print("Added lock to _rr round-robin counter")
with open(key_pool_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\nCompiling key_pool.py...")
result = os.system(f"python3 -m py_compile '{key_pool_file}'")
if result == 0:
    print("✓ Syntax OK")
else:
    print(f"✗ Compilation failed")
