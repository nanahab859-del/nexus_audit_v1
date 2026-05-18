#!/usr/bin/env python3
"""Verify all 11 Phase 1 fix checks."""
new_html = open('/home/yusupha/my_tools/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html').read()
checks = [
    ('toggleFreeze function',   'function toggleFreeze'),
    ('separateApps function',   'function separateApps'),
    ('Freeze button',           'id="freeze-btn"'),
    ('Inspect button',          'id="inspect-btn"'),
    ('edge-info-panel',         'id="edge-info-panel"'),
    ('_isRawJson guard',        '_isRawJson'),
    ('upgrade rec_type',        "r.rec_type === 'upgrade'"),
    ('CVE rec_type',            "r.rec_type === 'cve'"),
    ('upgrade_command render',  'r.upgrade_command'),
    ('attack_scenario render',  'r.attack_scenario'),
]
# Also check dependency.py directly
dep_code = open('/home/yusupha/my_tools/nexus_audit/nexus_audit/dependency.py').read()
backend_code = open('/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/backend.py').read()
checks_with_source = [(n, p, new_html) for n, p in checks[:10]] + \
                     [('parallel dep scan (dependency.py)', 'ThreadPoolExecutor', dep_code),
                      ('KeyPool mark_rpm in backend', 'key_pool.mark_rpm', backend_code)]
print('=== HTML/Code Feature Check ===')
all_ok = True
for i, (name, pattern, source) in enumerate(checks_with_source, 1):
    found = pattern in source
    status = 'PASS' if found else 'FAIL'
    if not found:
        all_ok = False
    print(f'{i:2d}. {status:4s}  {name}')
print()
if all_ok:
    print('✓ All 11 checks PASSED')
else:
    print('✗ SOME CHECKS FAILED')
