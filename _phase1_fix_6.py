#!/usr/bin/env python3
"""Apply Fix 6 - KeyPool mark_rpm/mark_daily in 429 handler"""
backend_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/backend.py'
with open(backend_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FIX 6: KeyPool mark_rpm/mark_daily in 429 handler ===")
# Fix 6A: Daily quota handler
old_daily = '''                        if _is_daily:
                            print(f"       \u21b3 {_model}: daily quota exhausted \u2014 trying next", flush=True)
                            continue'''
new_daily = '''                        if _is_daily:
                            key_pool.mark_daily(api_key)
                            print(f"       \u21b3 {_model}: daily quota exhausted \u2014 trying next model", flush=True)
                            continue'''
if old_daily in code:
    code = code.replace(old_daily, new_daily, 1)
    print("FIX 6A (daily) applied")
else:
    print("FIX 6A SKIP - pattern not found")
# Fix 6B: Rate limit handler
old_rpm = '''                        else:
                            _GEMINI_RATE_LIMITED = True
                            _backoff = 65
                            print(f"\n   \u26a0 [{_model}] rate limit hit."
                                  f" Cooling down {_backoff}s ", end="", flush=True)
                            for _tick in range(_backoff):
                                time.sleep(1)
                                print("|" if (_tick + 1) % 5 == 0 else ".", end="", flush=True)
                            print(" ready", flush=True)
                            _GEMINI_RATE_LIMITED = False
                            continue'''
new_rpm = '''                        else:
                            key_pool.mark_rpm(api_key)
                            _backoff = 65
                            print(f"\n   \u26a0 [{_model}] RPM limit. Cooling down {_backoff}s ", end="", flush=True)
                            for _tick in range(_backoff):
                                time.sleep(1)
                                print("|" if (_tick + 1) % 5 == 0 else ".", end="", flush=True)
                            print(" ready", flush=True)
                            continue'''
if old_rpm in code:
    code = code.replace(old_rpm, new_rpm, 1)
    print("FIX 6B (rpm) applied")
else:
    print("FIX 6B SKIP - pattern not found")
with open(backend_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\n=== Compilation check: backend.py ===")
import os
os.system(f"python3 -m py_compile {backend_file}")
print(f"Exit code: $?")
