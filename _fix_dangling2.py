src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# The fragment uses \\n inside the string literals, not real newlines
old = (
    "    '    }\\n'\n"
    "    '}\\n'\n"
    "'function filterRecommendations() {\\n'\n"
    "    '    const effortVal = window.__effortFilter || \\'\\';\\n'\n"
)
new = (
    "    '    }\\n'\n"
    "    '}\\n'\n"
)

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied')
else:
    print('SKIP - trying alternate match')
    # Find the exact lines
    lines = code.split('\n')
    for i, l in enumerate(lines, 1):
        if 'filterRecommendations' in l and 'function' in l and 'replace' not in l:
            print(f"  line {i}: {repr(l)}")

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
