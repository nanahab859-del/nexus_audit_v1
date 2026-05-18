src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Find the _safe_json method and add backtick escaping,
# OR find where recommendations_json is set and escape it there.

fixes = 0

# FIX 1: Add _safe_json method that escapes backticks
# Find existing _safe_json or json.dumps calls
old_safe = '    def _safe_json(self, obj) -> str:\n        return json.dumps(obj, ensure_ascii=False)'
new_safe = '    def _safe_json(self, obj) -> str:\n        """Serialize to JSON and escape backticks so they cannot break JS template literals."""\n        s = json.dumps(obj, ensure_ascii=False)\n        # Backticks inside JS const strings break template literals if the const\n        # is later referenced inside a template. Escape them as \\u0060.\n        return s.replace("`", "\\u0060")'

if old_safe in code:
    code = code.replace(old_safe, new_safe, 1)
    print('FIX 1 applied - _safe_json now escapes backticks')
    fixes += 1
else:
    # Try to find where json.dumps is used for the recommendations
    print('FIX 1 SKIP - _safe_json not found with expected signature')
    # Find all json.dumps calls
    import re
    for m in re.finditer(r'def _safe_json', code):
        idx = m.start()
        print(f'  Found _safe_json at char {idx}:')
        print(f'  {repr(code[idx:idx+200])}')

# FIX 2: If _safe_json doesn't exist, add backtick escape wherever recommendations are serialized
if fixes == 0:
    old_recs = "recommendations_json   = json.dumps(self.data.get('recommendations', []), ensure_ascii=False)"
    new_recs = "recommendations_json   = json.dumps(self.data.get('recommendations', []), ensure_ascii=False).replace('`', '\\u0060')"
    if old_recs in code:
        code = code.replace(old_recs, new_recs, 1)
        print('FIX 2 applied - recommendations_json backticks escaped')
        fixes += 1
    else:
        print('FIX 2 SKIP')
        # Show all json.dumps calls
        import re
        for m in re.finditer(r"json\.dumps.*recommendations", code):
            print(f'  Found: {repr(code[m.start():m.start()+150])}')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'Total fixes: {fixes}')
