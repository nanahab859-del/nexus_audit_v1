#!/usr/bin/env python3
"""Apply all 6 Phase 1 fixes."""
import os
import sys
# Read html_report.py
html_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(html_file, 'r', encoding='utf-8') as f:
    html_code = f.read()
# Read backend.py
backend_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/backend.py'
with open(backend_file, 'r', encoding='utf-8') as f:
    backend_code = f.read()
html_original = html_code
backend_original = backend_code
# FIX 1: _isRawJson guard on r.description
print("\n=== FIX 1: _isRawJson guard ===")
old1 = '''        if (r.description) {{
            html += `<p style="font-size:.82rem;color:#94a3b8;margin-bottom:8px;">${{r.description}}</p>`;
        }}'''
new1 = '''        if (r.description) {{
            const _d = r.description || '';
            const _isRawJson = _d.trimStart().startsWith('{{') || _d.trimStart().startsWith('[');
            if (!_isRawJson) {{
                html += `<p style="font-size:.82rem;color:#94a3b8;margin-bottom:8px;">${{_d}}</p>`;
            }}
        }}'''
if old1 in html_code:
    html_code = html_code.replace(old1, new1, 1)
    print("FIX 1 applied")
else:
    print("FIX 1 SKIP - pattern not found")
# FIX 2: Upgrade/CVE rec_type card rendering
print("\n=== FIX 2: upgrade/CVE rec_type rendering ===")
old2 = '''        if ((r.affected_modules||[]).length) {{
            html += `<div style="font-size:.72rem;color:#475569;margin-top:6px;">Affects: ${{r.affected_modules.slice(0,5).map(m=>`<code>${{m}}</code>`).join(', ')}}</div>`;
        }}
        html += '</div>';
        return html;'''
new2 = '''        if ((r.affected_modules||[]).length) {{
            html += `<div style="font-size:.72rem;color:#475569;margin-top:6px;">Affects: ${{r.affected_modules.slice(0,5).map(m=>`<code>${{m}}</code>`).join(', ')}}</div>`;
        }}
        /* Upgrade Advisor fields */
        if (r.rec_type === 'upgrade') {{
            if (r.upgrade_command) html += `<div style="margin:6px 0 4px;"><strong style="font-size:.78rem;color:#94a3b8;">Package upgrade:</strong><pre style="background:rgba(15,23,42,.6);border:1px solid #334155;border-radius:5px;padding:6px 10px;font-size:.78rem;color:#7dd3fc;overflow-x:auto;">${{r.upgrade_command}}</pre></div>`;
            if (r.why_upgrade) html += `<p style="font-size:.82rem;color:#6ee7b7;margin-bottom:6px;"><strong>Why upgrade:</strong> ${{r.why_upgrade}}</p>`;
            if (r.breaking_changes) html += `<p style="font-size:.82rem;color:#fcd34d;margin-bottom:6px;"><strong>Breaking changes:</strong> ${{r.breaking_changes}}</p>`;
            if (r.test_after) html += `<div style="font-size:.78rem;color:#94a3b8;margin-bottom:4px;"><strong>Verify:</strong> <code>${{r.test_after}}</code></div>`;
            if (r.risk_if_skipped) html += `<p style="font-size:.78rem;color:#fb923c;margin-bottom:4px;"><strong>Risk if skipped:</strong> ${{r.risk_if_skipped}}</p>`;
        }}
        /* CVE Advisor fields */
        if (r.rec_type === 'cve') {{
            if (r.attack_scenario) html += `<p style="font-size:.82rem;color:#fca5a5;margin-bottom:6px;border-left:2px solid #ef4444;padding-left:8px;"><strong>Attack scenario:</strong><br>${{r.attack_scenario}}</p>`;
            if (r.nexus_risk_level) html += `<p style="font-size:.82rem;color:#fcd34d;margin-bottom:6px;"><strong>Nexus risk:</strong> ${{r.nexus_risk_level}}</p>`;
            if (r.fix_command) html += `<div style="margin:6px 0 4px;"><strong style="font-size:.78rem;color:#94a3b8;">Fix command:</strong><pre style="background:rgba(15,23,42,.6);border:1px solid #334155;border-radius:5px;padding:6px 10px;font-size:.78rem;color:#7dd3fc;overflow-x:auto;">${{r.fix_command}}</pre></div>`;
            if (r.config_changes) html += `<p style="font-size:.82rem;color:#fb923c;margin-bottom:6px;"><strong>Config changes:</strong> ${{r.config_changes}}</p>`;
            if (r.verify_fixed) html += `<div style="font-size:.78rem;color:#6ee7b7;margin-bottom:4px;"><strong>Verify fixed:</strong> <code>${{r.verify_fixed}}</code></div>`;
        }}
        html += '</div>';
        return html;'''
if old2 in html_code:
    html_code = html_code.replace(old2, new2, 1)
    print("FIX 2 applied")
else:
    print("FIX 2 SKIP - pattern not found")
# FIX 3: Graph control buttons - need to find the exact section
print("\n=== FIX 3: Graph control buttons ===")
old3 = '''            <button class="ctrl-btn" onclick="resetView()">🌌 Reset View</button>
            <button class="ctrl-btn" onclick="fitAll()">🔭 Fit All</button>
            <span style="color:#475569;font-size:0.8rem;">
                Hover = highlight island  Click = isolate node  Dbl-click = reset
            </span>'''
new3 = '''            <button class="ctrl-btn" onclick="resetView()">🌌 Reset View</button>
            <button class="ctrl-btn" onclick="fitAll()">🔭 Fit All</button>
            <button class="ctrl-btn" id="freeze-btn" onclick="toggleFreeze()">🧊 Freeze</button>
            <button class="ctrl-btn" id="sep-btn" onclick="toggleSeparation()">🏝️ Separate Apps</button>
            <button class="ctrl-btn" id="inspect-btn" onclick="toggleInspect()">🔍 Inspect Edges</button>
            <span style="color:#475569;font-size:0.8rem;">
                Hover = highlight  Click = isolate  Dbl-click = reset  Freeze = lock physics
            </span>'''
if old3 in html_code:
    html_code = html_code.replace(old3, new3, 1)
    print("FIX 3 applied")
else:
    print("FIX 3 SKIP - pattern not found")
# Write html_report.py
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_code)
print("\n=== Compilation check: html_report.py ===")
os.system(f"python3 -m py_compile {html_file}")
