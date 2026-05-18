src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Remove the broken fragment that appends 'function filterRecommendations() {'
# after persistFixQueueState's closing brace. That fragment opens a function
# body that is never closed, causing "Unexpected end of input".
old = (
    '    }\n'
    '}\n'
    'function filterRecommendations() {\n'
    "    const effortVal = window.__effortFilter || '';\n"
)
new = (
    '    }\n'
    '}\n'
)

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - removed dangling filterRecommendations fragment')
else:
    print('SKIP - pattern not found, showing context:')
    idx = code.find('function filterRecommendations')
    print(repr(code[idx-100:idx+100]))

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
