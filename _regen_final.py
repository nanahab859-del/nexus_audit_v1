import sys, json, re, subprocess
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '*.pyc', '-delete'])
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'])

with open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/audit_data_complete.json') as f:
    data = json.load(f)

from nexus_audit.report.html_report import EnhancedAuditReport
reporter = EnhancedAuditReport(data)
html = reporter.generate_html_dashboard()

# Find vis-network script size
script1_start = html.find('<script type="text/javascript">')
script1_end = html.find('</script>', script1_start)
vis_size = script1_end - script1_start

checks = [
    ('Real vis-network (>400KB)',    vis_size > 400000),
    ('vis.Network in library',       'vis.Network' in html and vis_size > 400000),
    ('stopSimulation exists',        'stopSimulation' in html),
    ('setData exists',               'prototype.setData' in html or '.setData=' in html),
    ('rec-counter null guard',       'if (_ctr) _ctr.textContent' in html),
    ('toggleFreeze once',            len(re.findall(r'function toggleFreeze\b', html)) == 1),
    ('no bare counter crash',        "getElementById('rec-counter').textContent" not in html),
]

print('=== FINAL VERIFICATION ===')
all_ok = True
for name, check in checks:
    print(f'  {"PASS" if check else "FAIL ***"}: {name}')
    if not check: all_ok = False

out = '/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nHTML written: {len(html):,} bytes ({len(html)//1024}KB)')
print(f'vis-network script: {vis_size:,} bytes ({vis_size//1024}KB)')
print('All checks PASSED' if all_ok else 'SOME CHECKS FAILED')
