import sys, json, subprocess
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '*.pyc', '-delete'])
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '__pycache__', '-type', 'd',
                '-exec', 'rm', '-rf', '{}', '+'])

with open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/audit_data_complete.json') as f:
    data = json.load(f)

from nexus_audit.report.html_report import EnhancedAuditReport
html = EnhancedAuditReport(data).generate_html_dashboard()

main_start = html.rfind('<script>')
main_end   = html.rfind('</script>')
js = html[main_start+8:main_end]

# Check brace balance
balance = 0
in_d = in_s = tmpl = esc = False
for ch in js:
    if esc: esc=False; continue
    if ch == '\\': esc=True; continue
    if ch == '`' and not in_d and not in_s: tmpl = 1-tmpl; continue
    if tmpl: continue
    if ch == '"' and not in_s and not in_d: in_d=True; continue
    if ch == '"' and in_d: in_d=False; continue
    if ch == "'" and not in_d and not in_s: in_s=True; continue
    if ch == "'" and in_s: in_s=False; continue
    if in_d or in_s: continue
    if ch == '{': balance += 1
    elif ch == '}': balance -= 1

bt = js.count('`')
print(f"Brace balance: {balance} ({'OK' if balance==0 else 'BROKEN'})")
print(f"Backtick count: {bt} ({'EVEN OK' if bt%2==0 else 'ODD BROKEN'})")

out = '/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML written: {len(html):,} bytes ({len(html)//1024}KB)")
print('Done')
