src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

old = (
    'def _safe_json(self, data: Any) -> str:\n'
    '        s = json.dumps(data, default=str)\n'
    '        return s.replace("<", "\\\\u003c").replace(">", "\\\\u003e").replace("&", "\\\\u0026")'
)
new = (
    'def _safe_json(self, data: Any) -> str:\n'
    '        s = json.dumps(data, default=str)\n'
    '        # Escape backticks: AI recommendations use markdown backticks for code\n'
    '        # which break JS template literals when embedded as const values.\n'
    '        return (s.replace("<", "\\\\u003c")\n'
    '                 .replace(">", "\\\\u003e")\n'
    '                 .replace("&", "\\\\u0026")\n'
    '                 .replace("`", "\\\\u0060"))'
)

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - backtick escape added to _safe_json')
else:
    print('SKIP - pattern not found, showing actual:')
    idx = code.find('def _safe_json')
    print(repr(code[idx:idx+300]))

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
