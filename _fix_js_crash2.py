src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# FIX 1: Add null guard on rec-counter in filterRecommendations()
old1 = "    document.getElementById('rec-counter').textContent = `Showing ${{shown}} of ${{total}}`;"
new1 = "    const _ctr = document.getElementById('rec-counter'); if (_ctr) _ctr.textContent = `Showing ${{shown}} of ${{total}}`;"
if old1 in code:
    code = code.replace(old1, new1, 1)
    print('FIX 1 applied - null guard on rec-counter')
    fixes += 1
else:
    print('FIX 1 SKIP - showing what is there:')
    idx = code.find('rec-counter')
    while idx >= 0:
        print(' ', repr(code[idx:idx+100]))
        idx = code.find('rec-counter', idx+1)

# FIX 2: Also add null guard on searchEl inside filterRecommendations
# searchEl is used without guard: const cards = searchEl ? ... but let's check
old2 = "    const searchEl = document.getElementById('rec-search');"
new2 = "    const searchEl = document.getElementById('rec-search');\n    if (!searchEl) return;  // elements not in DOM yet"
if old2 in code:
    code = code.replace(old2, new2, 1)
    print('FIX 2 applied - early return if rec-search not in DOM')
    fixes += 1
else:
    print('FIX 2 SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'Total fixes: {fixes}')
