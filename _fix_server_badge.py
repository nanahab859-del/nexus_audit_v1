src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Add server mode detection JS right after DOMContentLoaded
# It checks if /fix-queue responds and shows a badge
old = 'window.showTab = showTab;\nsetTimeout(initGraph, 50);'
new = '''window.showTab = showTab;
setTimeout(initGraph, 50);

// Server mode detection — check if Fix Queue API is reachable
(function detectServerMode() {
    const badge = document.getElementById('server-mode-badge');
    if (!badge) return;
    fetch('/fix-queue', { method: 'GET' })
        .then(r => {
            if (r.ok) {
                badge.textContent = '\u{1f7e2} Live Server \u2014 localhost:8421';
                badge.style.color = '#6ee7b7';
                badge.style.display = 'inline-block';
            }
        })
        .catch(() => {
            // Static file mode — badge stays hidden
        });
})();'''

if old in code:
    code = code.replace(old, new, 1)
    print('FIX 1 applied - server detection JS')
else:
    print('FIX 1 SKIP')

# Add the badge element into the header, after the title
old2 = '<p style="margin:4px 0 0;font-size:.82rem;color:#64748b;">'
new2 = '<span id="server-mode-badge" style="display:none;font-size:.78rem;background:rgba(110,231,183,.12);border:1px solid #6ee7b7;border-radius:6px;padding:2px 10px;margin-left:12px;vertical-align:middle;"></span>\n            <p style="margin:4px 0 0;font-size:.82rem;color:#64748b;">'

if old2 in code:
    code = code.replace(old2, new2, 1)
    print('FIX 2 applied - server mode badge element added to header')
else:
    print('FIX 2 SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
