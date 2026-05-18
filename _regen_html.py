import sys, json, re
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

# Clear pycache first
import subprocess
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '*.pyc', '-delete'])
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'])

with open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/audit_data_complete.json') as f:
    data = json.load(f)

from nexus_audit.report.html_report import EnhancedAuditReport
reporter = EnhancedAuditReport(data)
html = reporter.generate_html_dashboard()

# Verify the fix is in the generated output
checks = [
    ('rec-counter null guard',     'if (_ctr) _ctr.textContent'),
    ('early return guard',         'if (!searchEl) return'),
    ('no bare counter crash',      "getElementById('rec-counter').textContent" not in html),
    ('toggleFreeze once',          len(re.findall(r'function toggleFreeze\b', html)) == 1),
    ('separateApps once',          len(re.findall(r'function separateApps\b', html)) == 1),
    ('graph network init',         'new vis.Network' in html),
    ('score cards will render',    'Object.entries(apps)' in html),
]

print('=== VERIFICATION ===')
all_ok = True
for name, check in checks:
    ok = check if isinstance(check, bool) else check in html
    print(f'  {"PASS" if ok else "FAIL ***"}: {name}')
    if not ok: all_ok = False

# Write the fixed HTML
out = '/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nHTML written: {len(html):,} bytes ({len(html)//1024}KB)')
print('All checks passed' if all_ok else 'SOME CHECKS FAILED')
