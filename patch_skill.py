import os

html_report_path = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
backend_path = '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/backend.py'

with open(html_report_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

with open(backend_path, 'r', encoding='utf-8') as f:
    backend_code = f.read()

# Fix 1
f1_old = '''        if (r.description) {{
            html += `<p style="font-size:.82rem;color:#94a3b8;margin-bottom:8px;">${{r.description}}</p>`;
        }}'''
f1_new = '''        if (r.description) {{
            const _d = r.description || '';
            const _isRawJson = _d.trimStart().startsWith('{') || _d.trimStart().startsWith('[');
            if (!_isRawJson) {{
                html += `<p style="font-size:.82rem;color:#94a3b8;margin-bottom:8px;">${{_d}}</p>`;
            }}
        }}'''
# Wait, SKILL.md says: `const _isRawJson = _d.trimStart().startsWith('{{') || _d.trimStart().startsWith('[');`
f1_new = '''        if (r.description) {{
            const _d = r.description || '';
            const _isRawJson = _d.trimStart().startsWith('{{') || _d.trimStart().startsWith('[');
            if (!_isRawJson) {{
                html += `<p style="font-size:.82rem;color:#94a3b8;margin-bottom:8px;">${{_d}}</p>`;
            }}
        }}'''

# Fix 2
f2_old = '''        if ((r.affected_modules||[]).length) {{
            html += `<div style="font-size:.72rem;color:#475569;margin-top:6px;">Affects: ${{r.affected_modules.slice(0,5).map(m=>`<code>${{m}}</code>`).join(', ')}}</div>`;
        }}
        html += '</div>';
        return html;'''
f2_new = '''        if ((r.affected_modules||[]).length) {{
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

# Fix 3
f3_old = '''            <button class="ctrl-btn" onclick="resetView()">🌌 Reset View</button>
            <button class="ctrl-btn" onclick="fitAll()">🔭 Fit All</button>
            <span style="color:#475569;font-size:0.8rem;">
                Hover = highlight island · Click = isolate node · Dbl-click = reset
            </span>'''
f3_new = '''            <button class="ctrl-btn" onclick="resetView()">🌌 Reset View</button>
            <button class="ctrl-btn" onclick="fitAll()">🔭 Fit All</button>
            <button class="ctrl-btn" id="freeze-btn" onclick="toggleFreeze()">🧊 Freeze</button>
            <button class="ctrl-btn" id="sep-btn" onclick="toggleSeparation()">🏝️ Separate Apps</button>
            <button class="ctrl-btn" id="inspect-btn" onclick="toggleInspect()">🔍 Inspect Edges</button>
            <span style="color:#475569;font-size:0.8rem;">
                Hover = highlight · Click = isolate · Dbl-click = reset · Freeze = lock physics
            </span>'''

# Fix 4
f4_old = '''        <div class="node-info-bar" id="node-info">
            Hover a node to see details · Click to isolate · Double-click to reset
        </div>
        <div class="legend" id="legend"></div>'''
f4_new = '''        <div class="node-info-bar" id="node-info">
            Hover a node to see details · Click to isolate · Double-click to reset
        </div>
        <div id="edge-info-panel" style="display:none;background:rgba(15,23,42,.85);border:1px solid #334155;border-radius:10px;padding:14px 18px;margin-top:8px;font-size:.85rem;color:#f1f5f9;"></div>
        <div class="legend" id="legend"></div>'''

# Fix 5
f5_old = '''function resetView() {{'''
f5_new = '''/* Graph analysis tools */
let _frozen = false;
let _separated = false;
let _inspectMode = false;

function toggleFreeze() {{
    _frozen = !_frozen;
    const btn = document.getElementById('freeze-btn');
    if (_frozen) {{
        network.stopSimulation();
        btn.classList.add('active');
        btn.textContent = '\\u25b6 Unfreeze';
    }} else {{
        network.startSimulation();
        btn.classList.remove('active');
        btn.textContent = '\\U0001f9ca Freeze';
    }}
}}

function toggleSeparation() {{
    const btn = document.getElementById('sep-btn');
    if (_separated) {{
        resetSeparation();
        btn.classList.remove('active');
        btn.textContent = '\\U0001f3dd\\ufe0f Separate Apps';
        _separated = false;
    }} else {{
        separateApps();
        btn.classList.add('active');
        btn.textContent = '\\U0001f517 Merge View';
        _separated = true;
    }}
}}

function separateApps() {{
    const appGroups = {{}};
    nodesData.forEach(n => {{
        const app = n.id.split('.')[0];
        if (!appGroups[app]) appGroups[app] = [];
        appGroups[app].push(n.id);
    }});
    const appList = Object.keys(appGroups).sort();
    const COLS = Math.ceil(Math.sqrt(appList.length));
    const ZONE_W = 450, ZONE_H = 350, PAD = 80;
    const positions = {{}};
    appList.forEach((app, ai) => {{
        const col = ai % COLS;
        const row = Math.floor(ai / COLS);
        const zx = col * (ZONE_W + PAD);
        const zy = row * (ZONE_H + PAD);
        const nodes = appGroups[app];
        nodes.forEach((nid, ni) => {{
            const nc = Math.ceil(Math.sqrt(nodes.length));
            const nx = ni % nc;
            const ny = Math.floor(ni / nc);
            positions[nid] = {{ x: zx + nx * 90 + 40, y: zy + ny * 90 + 40 }};
        }});
    }});
    network.setOptions({{ physics: {{ enabled: false }} }});
    network.setData({{
        nodes: new vis.DataSet(nodesData.map(n => ({{
            ...n,
            x: positions[n.id] ? positions[n.id].x : 0,
            y: positions[n.id] ? positions[n.id].y : 0,
            fixed: true
        }}))),
        edges: new vis.DataSet(edgesData)
    }});
    network.fit({{ animation: {{ duration: 600, easingFunction: 'easeInOutQuad' }} }});
}}

function resetSeparation() {{
    network.setOptions({{ physics: {{ enabled: true }} }});
    network.setData({{ nodes: new vis.DataSet(nodesData), edges: new vis.DataSet(edgesData) }});
    network.fit({{ animation: true }});
}}

function toggleInspect() {{
    _inspectMode = !_inspectMode;
    const btn = document.getElementById('inspect-btn');
    const panel = document.getElementById('edge-info-panel');
    if (_inspectMode) {{
        btn.classList.add('active');
        btn.textContent = '\\U0001f50d Inspecting\\u2026';
        panel.style.display = 'block';
        panel.innerHTML = '<span style="color:#64748b;">Click any edge in the graph to inspect it.</span>';
    }} else {{
        btn.classList.remove('active');
        btn.textContent = '\\U0001f50d Inspect Edges';
        panel.style.display = 'none';
    }}
}}

network.on('selectEdge', function(params) {{
    if (!params.edges.length) return;
    const eid = params.edges[0];
    const edge = edgesData.find(e => e.id === eid);
    if (!edge) return;
    const panel = document.getElementById('edge-info-panel');
    panel.style.display = 'block';
    document.getElementById('inspect-btn').classList.add('active');
    _inspectMode = true;
    document.getElementById('inspect-btn').textContent = '\\U0001f50d Inspecting\\u2026';
    const src = edge.from || '';
    const tgt = edge.to   || '';
    const srcApp = src.split('.')[0].toUpperCase();
    const tgtApp = tgt.split('.')[0].toUpperCase();
    const edgeViolations = violations.filter(v => v.source === src && v.target === tgt);
    const edgeAllowed    = allowedComms.filter(c => {{ const d = c.details || ''; return d.includes(src) && d.includes(tgt); }});
    let html = `<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px;">
        <span style="font-size:1.1rem;font-weight:700;color:#38bdf8;">${{src.split('.').pop()}}.py</span>
        <span style="color:#475569;">\\u2014\\u25b6</span>
        <span style="font-size:1.1rem;font-weight:700;color:#38bdf8;">${{tgt.split('.').pop()}}.py</span>
        <span style="font-size:.75rem;color:#64748b;">(${{srcApp}} \\u2192 ${{tgtApp}})</span>
    </div>`;
    if (edgeViolations.length) {{
        html += '<div style="border-left:3px solid #ef4444;padding-left:10px;margin-bottom:8px;">';
        html += `<div style="color:#fca5a5;font-weight:600;margin-bottom:4px;">\\U0001f6a8 ${{edgeViolations.length}} Violation(s)</div>`;
        edgeViolations.forEach(v => {{
            html += `<div style="font-size:.8rem;color:#94a3b8;margin-bottom:3px;"><code style="color:#fcd34d;">${{v.source}}</code> imports <code style="color:#fcd34d;">${{v.target}}</code>${{v.type ? ' &middot; <span style="color:#fb923c;">' + v.type + '</span>' : ''}}${{v.penalty ? ' &middot; <span style="color:#ef4444;">\\u2212' + v.penalty + 'pts</span>' : ''}}</div>`;
        }});
        html += '</div>';
    }}
    if (edgeAllowed.length) {{
        html += '<div style="border-left:3px solid #10b981;padding-left:10px;">';
        html += `<div style="color:#6ee7b7;font-weight:600;margin-bottom:4px;">\\u2705 ${{edgeAllowed.length}} Allowed Communication(s)</div>`;
        edgeAllowed.forEach(c => {{ html += `<div style="font-size:.8rem;color:#94a3b8;margin-bottom:2px;">${{c.type || 'Allowed'}}${{c.details ? ' &middot; <code>' + c.details + '</code>' : ''}}</div>`; }});
        html += '</div>';
    }}
    if (!edgeViolations.length && !edgeAllowed.length) {{
        html += '<span style="color:#64748b;font-size:.85rem;">Internal edge — same-app import (no violation)</span>';
    }}
    panel.innerHTML = html;
}});

network.on('deselectEdge', function() {{ /* keep panel visible */ }});

function resetView() {{'''

# Fix 6
f6a_old = '''                    elif _gemini_http_err.code == 429:
                        global _GEMINI_RATE_LIMITED
                        _is_daily = (
                            "RESOURCE_EXHAUSTED" in _body_str
                            or "quota" in _body_str.lower()
                            or "daily" in _body_str.lower()
                        )
                        if _is_daily:
                            print(f"       \\u21b3 {_model}: daily quota exhausted \\u2014 trying next", flush=True)
                            continue
                        else:
                            _GEMINI_RATE_LIMITED = True
                            _backoff = 65
                            print(f"\\n   \\u26a0 [{_model}] rate limit hit. Cooling down {_backoff}s ", end="", flush=True)
                            for _tick in range(_backoff):
                                time.sleep(1)
                                print("|" if (_tick + 1) % 5 == 0 else ".", end="", flush=True)
                            print(" ready", flush=True)
                            _GEMINI_RATE_LIMITED = False
                            continue'''

f6a_new = '''                    elif _gemini_http_err.code == 429:
                        _is_daily = (
                            "RESOURCE_EXHAUSTED" in _body_str
                            or "quota" in _body_str.lower()
                            or "daily" in _body_str.lower()
                        )
                        if _is_daily:
                            key_pool.mark_daily(api_key)
                            print(f"       \\u21b3 {_model}: daily quota exhausted \\u2014 trying next model", flush=True)
                            continue
                        else:
                            key_pool.mark_rpm(api_key)
                            _backoff = 65
                            print(f"\\n   \\u26a0 [{_model}] RPM limit. Cooling down {_backoff}s ", end="", flush=True)
                            for _tick in range(_backoff):
                                time.sleep(1)
                                print("|" if (_tick + 1) % 5 == 0 else ".", end="", flush=True)
                            print(" ready", flush=True)
                            continue'''

f6b_old = '''                        if text:
                            return text'''
f6b_new = '''                        if text:
                            key_pool.mark_success(api_key)
                            return text'''


def apply_fix(code, old, new, fix_name):
    if old in code:
        print(f"Applying {fix_name}...")
        return code.replace(old, new, 1)
    else:
        print(f"SKIP {fix_name} - Not found!")
        return code

html_code = apply_fix(html_code, f1_old, f1_new, 'Fix 1')
html_code = apply_fix(html_code, f2_old, f2_new, 'Fix 2')
html_code = apply_fix(html_code, f3_old, f3_new, 'Fix 3')
html_code = apply_fix(html_code, f4_old, f4_new, 'Fix 4')
html_code = apply_fix(html_code, f5_old, f5_new, 'Fix 5')

backend_code = apply_fix(backend_code, f6a_old, f6a_new, 'Fix 6a')
backend_code = apply_fix(backend_code, f6b_old, f6b_new, 'Fix 6b')

with open(html_report_path, 'w', encoding='utf-8') as f:
    f.write(html_code)

with open(backend_path, 'w', encoding='utf-8') as f:
    f.write(backend_code)

print("Patching complete.")
