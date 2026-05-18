src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Exact match from sed output
old = (
    "            '    }\\n'\n"
    "            '}\\n'\n"
    "            'function filterRecommendations() {\\n'\n"
    "            '    const effortVal = window.__effortFilter || \\'\\';\\n'\n"
    "        )\n"
)
new = (
    "            '    }\\n'\n"
    "            '}\\n'\n"
    "        )\n"
)

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - dangling filterRecommendations fragment removed')
else:
    print('SKIP')
    # Show exact chars around line 235
    idx = code.find("'function filterRecommendations() {\\n'")
    print('Context:', repr(code[idx-150:idx+200]))

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
