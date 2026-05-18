#!/usr/bin/env python3
"""Feature 2.1: Inject change_summary into audit_data - Version 2"""
import os
main_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/main.py'
with open(main_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FEATURE 2.1: Inject change_summary (v2) ===")
# Find the spot before report generation - simpler pattern
old_pattern = "    reporter = EnhancedAuditReport(audit_data)"
new_pattern = """    # ── Load previous audit and compute change summary ───────────────────
    prev = load_previous_audit(HISTORY_DIR)
    audit_data['change_summary'] = compute_change_summary(audit_data, prev)
    reporter = EnhancedAuditReport(audit_data)"""
if old_pattern in code:
    code = code.replace(old_pattern, new_pattern, 1)
    print("Injected change_summary calculation")
else:
    print("SKIP: Could not find EnhancedAuditReport line")
with open(main_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\nCompiling main.py...")
result = os.system(f"python3 -m py_compile '{main_file}'")
if result == 0:
    print("✓ Syntax OK")
else:
    print(f"✗ Compilation failed")
