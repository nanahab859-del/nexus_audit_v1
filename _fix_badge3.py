src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

old = '            Generated: ${ts} | Project: ${project_path}\n        </p>'
new = ('            Generated: ${ts} | Project: ${project_path}\n'
       '            <span id="server-mode-badge" style="display:none;font-size:.78rem;'
       'background:rgba(110,231,183,.12);border:1px solid #6ee7b7;border-radius:6px;'
       'padding:2px 10px;margin-left:12px;vertical-align:middle;"></span>\n'
       '        </p>')

if old in code:
    code = code.replace(old, new, 1)
    print('FIX 2 applied - badge added to header')
else:
    print('FIX 2 SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
