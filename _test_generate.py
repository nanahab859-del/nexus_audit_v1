import subprocess, sys, re, json

# Clear stale pycache
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '*.pyc', '-delete'])
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'])
print("pycache cleared")

sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

with open('/home/yusupha/my_tools/nexus_audit/visuals/audit_data_complete.json') as f:
    data = json.load(f)

from nexus_audit.report.html_report import EnhancedAuditReport
reporter = EnhancedAuditReport(data)
html = reporter.generate_html_dashboard()

print(f"Generated HTML size: {len(html):,} bytes ({len(html)//1024}KB)")
print()

# Check duplicates
for fn in ['toggleFreeze', 'separateApps', 'toggleSeparation', 'toggleInspect', 'resetSeparation']:
    count = len(re.findall('function ' + fn + r'\b', html))
    flag = " *** DUPLICATE ***" if count > 1 else " ok"
    print(f"  {fn}: {count}x{flag}")

# Check BOOTSTRAP_LEAVES
pat = r'BOOTSTRAP_LEAVES = \[.*?\]'
matches = re.findall(pat, html)
print()
for m in matches:
    print(f"  BOOTSTRAP: {m}")

# Check admin
print()
print("  admin in BOOTSTRAP:", "'admin'" in html and 'BOOTSTRAP' in html)
