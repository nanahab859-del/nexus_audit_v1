import sys, json, re, subprocess
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '*.pyc', '-delete'])
subprocess.run(['find', '/home/yusupha/my_tools/nexus_audit', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'])

with open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/audit_data_complete.json') as f:
    data = json.load(f)

from nexus_audit.report.html_report import EnhancedAuditReport
reporter = EnhancedAuditReport(data)
html = reporter.generate_html_dashboard()

# Get just the main script
main_start = html.rfind('<script>')
main_end   = html.rfind('</script>')
js = html[main_start+8:main_end]

bt_count = js.count('`')
print(f"Backtick count in main script: {bt_count} ({'EVEN - OK' if bt_count%2==0 else 'ODD - STILL BROKEN'})")

# Verify vis-network
s1 = html.find('<script type="text/javascript">')
e1 = html.find('</script>', s1)
print(f"vis-network size: {e1-s1:,} chars ({(e1-s1)//1024}KB)")

# Verify recommendations backticks are escaped
recs_match = re.search(r'const recommendations\s*=\s*', html)
if recs_match:
    chunk = html[recs_match.end():recs_match.end()+100000]
    depth, in_str, esc = 0, False, False
    end_idx = 0
    for i, ch in enumerate(chunk):
        if esc: esc=False; continue
        if ch=='\\' and in_str: esc=True; continue
        if ch=='"' and not in_str: in_str=True; continue
        if ch=='"' and in_str: in_str=False; continue
        if in_str: continue
        if ch=='[': depth+=1
        elif ch==']':
            depth-=1
            if depth==0: end_idx=i; break
    rec_json = chunk[:end_idx+1]
    raw_bt = rec_json.count('`')
    escaped_bt = rec_json.count('\\u0060')
    print(f"Recommendations: {raw_bt} raw backticks, {escaped_bt} escaped (\\u0060)")

# Write output
out = '/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML written: {len(html):,} bytes ({len(html)//1024}KB)")
print("Done")
