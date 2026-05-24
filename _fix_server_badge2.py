src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Add server mode detection JS right after window.showTab
old = 'window.showTab = showTab;\nsetTimeout(initGraph, 50);'
new = ('window.showTab = showTab;\n'
       'setTimeout(initGraph, 50);\n'
       '\n'
       '// Server mode detection\n'
       '(function detectServerMode() {\n'
       "    const badge = document.getElementById('server-mode-badge');\n"
       "    if (!badge) return;\n"
       "    fetch('/fix-queue', { method: 'GET' })\n"
       '        .then(r => {\n'
       '            if (r.ok) {\n'
       "                badge.textContent = '\U0001f7e2 Live Server \u2014 localhost:8421';\n"
       "                badge.style.color = '#6ee7b7';\n"
       "                badge.style.display = 'inline-block';\n"
       '            }\n'
       '        })\n'
       '        .catch(() => {});\n'
       '})();')

if old in code:
    code = code.replace(old, new, 1)
    print('FIX 1 applied - server detection JS')
else:
    print('FIX 1 SKIP')

# Add badge element into header
old2 = '<p style="margin:4px 0 0;font-size:.82rem;color:#64748b;">'
new2 = ('<span id="server-mode-badge" style="display:none;font-size:.78rem;'
        'background:rgba(110,231,183,.12);border:1px solid #6ee7b7;border-radius:6px;'
        'padding:2px 10px;margin-left:12px;vertical-align:middle;"></span>\n'
        '            <p style="margin:4px 0 0;font-size:.82rem;color:#64748b;">')

if old2 in code:
    code = code.replace(old2, new2, 1)
    print('FIX 2 applied - server mode badge added to header')
else:
    print('FIX 2 SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
