src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Add effortVal declaration at the top of filterRecommendations()
# right after the existing prioEl guard
old = "    const priorityVal = prioEl.value;\n"
new = "    const priorityVal = prioEl.value;\n    const effortVal = window.__effortFilter || '';\n"

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - effortVal declaration added to filterRecommendations()')
else:
    print('SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
