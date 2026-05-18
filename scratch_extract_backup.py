class EnhancedAuditReport:
    def __init__(self, audit_data: Dict[str, Any]):
        self.data = audit_data
        self.timestamp = datetime.now()
    
    def generate_html_dashboard(self) -> str:
        apps_json           = json.dumps(self.data['applications'], default=str)
        modules_json        = json.dumps(self.data['modules'], default=str)
        violations_json     = json.dumps(self.data['violations'], default=str)
        security_json       = json.dumps(self.data['security_findings'], default=str)
        metrics_json        = json.dumps(self.data['metrics'], default=str)
        cycles_json         = json.dumps(self.data['circular_dependencies'], default=str)
        recommendations_json= json.dumps(self.data.get('recommendations', []), default=str)
        metadata_json       = json.dumps(self.data['metadata'], default=str)
        ghost_json          = json.dumps(self.data['metadata'].get('ghost_files', []), default=str)
        allowed_comms_json  = json.dumps(self.data.get('allowed_communications', []), default=str)
        trend_json          = json.dumps(self.data['metadata'].get('trend', {}), default=str)
        dep_scan_json       = json.dumps(self.data.get('dependency_scan', {}), default=str)
        capabilities_json   = json.dumps(self.data['metadata'].get('capabilities', {}), default=str)
        
        vis_js_content = get_vis_js()
        ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Audit Dashboard — {ts}</title>
    <script type="text/javascript">{vis_js_content}</script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
            padding: 20px;
        }}
        .dashboard {{ max-width: 1600px; margin: 0 auto; }}
        .header {{
            background: rgba(30,41,59,0.9);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #334155;
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metric-card {{
            background: rgba(15,23,42,0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
            transition: transform 0.3s;
        }}
        .metric-card:hover {{ transform: translateY(-2px); border-color: #38bdf8; }}
        .metric-value {{ font-size: 2.5rem; font-weight: 700; margin: 10px 0; }}
        .metric-label {{ color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .app-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .app-card {{
            background: rgba(30,41,59,0.9);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid #334155;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .app-card.critical {{ border-left: 4px solid #ef4444; }}
        .app-card.warning  {{ border-left: 4px solid #f59e0b; }}
        .app-card.healthy  {{ border-left: 4px solid #10b981; }}
        .app-card:hover    {{ border-color: #38bdf8; transform: translateY(-2px); }}
        .app-card.panel-highlight {{ border-color: #38bdf8 !important; background: rgba(30,41,59,1) !important; box-shadow: 0 0 0 2px #38bdf822; }}
        .app-card.panel-dimmed    {{ opacity: 0.55; filter: grayscale(30%); }}
        .app-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .app-name {{ font-size: 1.3rem; font-weight: 700; }}
        .app-score {{ font-size: 2rem; font-weight: 700; }}
        .score-bar {{ height: 8px; background: #1e293b; border-radius: 4px; overflow: hidden; margin: 15px 0; }}
        .score-fill {{ height: 100%; transition: width 1s ease; border-radius: 4px; }}
        .app-details {{ font-size: 0.85rem; color: #94a3b8; }}
        .grade-badge {{
            display: inline-block; padding: 3px 10px; border-radius: 12px;
            font-size: 0.75rem; font-weight: 700; margin-left: 8px;
        }}
        .grade-a {{ background: #064e3b; color: #6ee7b7; }}
        .grade-b {{ background: #1e3a5f; color: #93c5fd; }}
        .grade-c {{ background: #78350f; color: #fcd34d; }}
        .grade-d {{ background: #7c2d12; color: #fdba74; }}
        .grade-f {{ background: #7f1d1d; color: #fca5a5; }}
        .tab-container {{
            background: rgba(30,41,59,0.9);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
            flex-wrap: wrap;
        }}
        .tab {{
            padding: 10px 20px;
            background: transparent;
            border: none;
            color: #94a3b8;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            font-size: 0.9rem;
        }}
        .tab:hover {{ background: rgba(56,189,248,0.1); color: #38bdf8; }}
        .tab.active {{ background: #38bdf8; color: #0f172a; font-weight: 600; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .network-section {{
            background: rgba(30,41,59,0.9);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .network-section h2 {{ font-size: 1.3rem; font-weight: 700; margin-bottom: 15px; color: #f1f5f9; }}
        .network-controls {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .ctrl-btn {{
            padding: 8px 16px;
            background: rgba(15,23,42,0.6);
            border: 1px solid #334155;
            color: #94a3b8;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.85rem;
        }}
        .ctrl-btn:hover {{ border-color: #38bdf8; color: #38bdf8; }}
        .ctrl-btn.active {{ background: #38bdf8; color: #0f172a; border-color: #38bdf8; font-weight: 600; }}
        /* ── Network + sidebar wrapper ── */
        .network-wrap {{
            display: flex;
            gap: 0;
            align-items: stretch;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #1e293b;
        }}
        /* ── Island sidebar — lives LEFT of the canvas, always visible ── */
        .island-sidebar {{
            width: 150px;
            flex-shrink: 0;
            background: rgba(10,15,30,0.7);
            border-right: 1px solid #1e293b;
            padding: 12px 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            overflow-y: auto;
        }}
        .island-sidebar-title {{
            font-size: 0.6rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #334155;
            padding: 0 6px 6px;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 4px;
        }}
        .island-pill {{
            display: flex;
            align-items: center;
            gap: 7px;
            padding: 6px 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }}
        .island-pill:hover {{
            background: rgba(255,255,255,0.06);
        }}
        .island-pill.pill-active {{
            background: rgba(56,189,248,0.12);
            border-color: rgba(56,189,248,0.25);
        }}
        .island-pill.pill-dimmed {{
            opacity: 0.2;
        }}
        .island-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex-shrink: 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .island-pill.pill-active .island-dot {{
            transform: scale(1.4);
            box-shadow: 0 0 6px currentColor;
        }}
        .island-label {{
            font-size: 0.68rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            transition: color 0.2s;
        }}
        .island-pill.pill-active .island-label {{
            color: #38bdf8;
        }}
        .island-score {{
            font-size: 0.6rem;
            color: #334155;
            margin-left: auto;
            flex-shrink: 0;
        }}
        #network {{
            flex: 1;
            height: 540px;
            background: rgba(10,15,30,0.5);
        }}
        .node-info-bar {{
            background: rgba(15,23,42,0.7);
            border-radius: 8px;
            padding: 11px 16px;
            margin-top: 12px;
            min-height: 44px;
            border: 1px solid #1e293b;
            font-size: 0.85rem;
            color: #94a3b8;
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            padding: 14px;
            background: rgba(15,23,42,0.6);
            border-radius: 8px;
            margin-top: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 6px;
            transition: all 0.2s;
            border: 1px solid transparent;
        }}
        .legend-item:hover {{ background: rgba(255,255,255,0.07); }}
        .legend-item.active {{ background: rgba(56,189,248,0.12); border-color: #38bdf833; }}
        .legend-color {{
            width: 22px;
            height: 4px;
            border-radius: 2px;
            flex-shrink: 0;
        }}
        .legend-color.dashed {{
            background: repeating-linear-gradient(90deg, currentColor, currentColor 5px, transparent 5px, transparent 10px);
        }}
        .badge {{
            display: inline-block;
            padding: 3px 9px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-critical {{ background: #ef4444; color: white; }}
        .badge-high     {{ background: #f59e0b; color: white; }}
        .badge-medium   {{ background: #3b82f6; color: white; }}
        .badge-low      {{ background: #10b981; color: white; }}
        .badge-ok       {{ background: #064e3b; color: #6ee7b7; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 11px 14px; text-align: left; border-bottom: 1px solid #1e293b; font-size: 0.87rem; }}
        th {{ background: rgba(15,23,42,0.6); font-weight: 600; color: #38bdf8; position: sticky; top: 0; z-index: 1; }}
        tr:hover {{ background: rgba(56,189,248,0.04); }}
        .status-ok       {{ color: #10b981; }}
        .status-warning  {{ color: #f59e0b; }}
        .status-critical {{ color: #ef4444; }}
        .recommendation-card {{
            padding: 16px 20px;
            border-radius: 10px;
            margin-bottom: 14px;
            border: 1px solid #334155;
            background: rgba(15,23,42,0.4);
        }}
        .recommendation-card h3 {{ font-size: 0.95rem; margin-bottom: 6px; color: #f1f5f9; }}
        .recommendation-card p  {{ font-size: 0.83rem; color: #94a3b8; margin-bottom: 4px; }}
        .priority-critical {{ border-left: 4px solid #ef4444; }}
        .priority-high     {{ border-left: 4px solid #f59e0b; }}
        .priority-medium   {{ border-left: 4px solid #3b82f6; }}
        .priority-low      {{ border-left: 4px solid #10b981; }}
        .cycle-item {{
            padding: 8px 12px;
            background: rgba(239,68,68,0.1);
            border-left: 3px solid #ef4444;
            border-radius: 0 6px 6px 0;
            margin-bottom: 6px;
            font-size: 0.82rem;
            cursor: pointer;
            color: #fca5a5;
        }}
        .cycle-item:hover {{ background: rgba(239,68,68,0.2); }}
        .tier-badge{{
            display:inline-flex;align-items:center;gap:6px;
            padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:600;
            border:1px solid currentColor;margin-left:16px;
        }}
        .tier-online{{color:#10b981;border-color:#10b981;background:rgba(16,185,129,.08);}}
        .tier-offline{{color:#f59e0b;border-color:#f59e0b;background:rgba(245,158,11,.08);}}
        .tier-dot{{width:7px;height:7px;border-radius:50%;background:currentColor;animation:pulse 1.8s infinite;}}
        @keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.3;}}}}
        .dep-card{{background:rgba(15,23,42,.5);border-radius:10px;padding:12px 14px;
                   border:1px solid #1e293b;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;}}
        .dep-name{{font-size:.85rem;font-weight:600;color:#f1f5f9;}}
        .dep-meta{{font-size:.75rem;color:#64748b;}}
        .dep-badges{{display:flex;gap:6px;align-items:center;flex-shrink:0;}}
        .dep-badge{{padding:2px 8px;border-radius:12px;font-size:.7rem;font-weight:600;}}
        .dep-ok{{background:#064e3b;color:#6ee7b7;}}
        .dep-warn{{background:#78350f;color:#fcd34d;}}
        .dep-vuln{{background:#7f1d1d;color:#fca5a5;}}
        .dep-na{{background:#1e293b;color:#64748b;}}
    </style>
</head>
<body>
<div class="dashboard">

    <!-- ── Header ─────────────────────────────────────────────────────── -->
    <div class="header">
        <h1 style="display:flex;align-items:center;">🛡️ Nexus Architecture Audit
            <span id="tier-badge" class="tier-badge tier-offline">
                <span class="tier-dot"></span> Loading…
            </span>
        </h1>
        <p style="color:#94a3b8;margin-bottom:8px;">
            Generated: {ts} | Project: {PROJECT_PATH}
        </p>
        <p style="color:#10b981;margin-bottom:8px;">
            ✅ STRICT MODULARITY: Cross-app imports are violations.
            Signals, tasks &amp; receivers are allowed communications.
        </p>
        <div class="metrics-grid" id="metrics-grid"></div>
    </div>

    <!-- ── App Health Grid ────────────────────────────────────────────── -->
    <h2 style="margin:0 0 20px;font-size:1.3rem;">🏥 Application Health</h2>
    <div class="app-grid" id="app-grid"></div>

    <!-- ── Detail Tabs ───────────────────────────────────────────────── -->
    <div class="tab-container">
        <div class="tabs">
            <button class="tab active" onclick="showTab('violations')">🚨 Violations</button>
            <button class="tab" onclick="showTab('test-debt')">🧪 Test Debt</button>
            <button class="tab" onclick="showTab('allowed')">🔗 Allowed Comms</button>
            <button class="tab" onclick="showTab('security')">🔒 Security</button>
            <button class="tab" onclick="showTab('complexity')">📊 Complexity</button>
            <button class="tab" onclick="showTab('ghost')">👻 Ghost Files</button>
            <button class="tab" onclick="showTab('cycles')">🔄 Cycles</button>
            <button class="tab" id="dep-tab-btn" onclick="showTab('dependencies')" style="display:none;">📦 Dependencies</button>
            <button class="tab" onclick="showTab('recommendations')">💡 Recommendations</button>
            <button class="tab" onclick="showTab('manifest')">📋 Manifest</button>
        </div>
        <div id="violations"      class="tab-content active"></div>
        <div id="test-debt"       class="tab-content"></div>
        <div id="allowed"         class="tab-content"></div>
        <div id="security"        class="tab-content"></div>
        <div id="complexity"      class="tab-content"></div>
        <div id="ghost"           class="tab-content"></div>
        <div id="cycles"          class="tab-content"></div>
        <div id="dependencies"    class="tab-content"></div>
        <div id="recommendations" class="tab-content"></div>
        <div id="manifest"        class="tab-content"></div>
    </div>

    <!-- ── Network Graph ─────────────────────────────────────────────── -->
    <div class="network-section">
        <h2>🌐 Dependency Network</h2>
        <div class="network-controls">
            <button class="ctrl-btn" onclick="resetView()">🌌 Reset View</button>
            <button class="ctrl-btn" onclick="fitAll()">🔭 Fit All</button>
            <button class="ctrl-btn" id="freeze-btn" onclick="toggleFreeze()">🧊 Freeze</button>
            <button class="ctrl-btn" id="sep-btn" onclick="toggleSeparation()">🏝️ Separate Apps</button>
            <button class="ctrl-btn" id="inspect-btn" onclick="toggleInspect()">🔍 Inspect Edges</button>
            <span style="color:#475569;font-size:0.8rem;">
                Hover = highlight · Click = isolate · Dbl-click = reset · Freeze = lock physics
            </span>
        </div>
        <!-- Canvas + island sidebar side-by-side -->
        <div class="network-wrap">
            <!-- Island sidebar: always visible while looking at graph -->
            <div class="island-sidebar" id="island-sidebar">
                <div class="island-sidebar-title">Islands</div>
            </div>
            <!-- The actual vis-network canvas -->
            <div id="network"></div>
        </div>
        <div class="node-info-bar" id="node-info">
            Hover a node to see details · Click to isolate · Double-click to reset
        </div>
        <div id="edge-info-panel" style="display:none;background:rgba(15,23,42,.85);border:1px solid #334155;border-radius:10px;padding:14px 18px;margin-top:8px;font-size:.85rem;color:#f1f5f9;"></div>
        <div class="legend" id="legend"></div>
    </div>

</div>

<script>
/* ── All audit data embedded (file is fully standalone) ─────────────────── */
const apps             = {apps_json};
const modules          = {modules_json};
const violations       = {violations_json};
const securityFindings = {security_json};
const metrics          = {metrics_json};
const cycles           = {cycles_json};
const recommendations  = {recommendations_json};
const metadata         = {metadata_json};
const ghostFiles       = {ghost_json};
const allowedComms     = {allowed_comms_json};
const trendData        = {trend_json};
const depScan          = {dep_scan_json};
const capabilities     = {capabilities_json};

/* ── Tier badge ───────────────────────────────────────────────────────── */
(function() {{
    const badge  = document.getElementById('tier-badge');
    const tier   = capabilities.tier || 1;
    const online = capabilities.online || false;
    const aiBack = capabilities.ai_backend || null;
    const aiOn   = capabilities.ai_recommendations || false;

    badge.className = 'tier-badge ' + (online ? 'tier-online' : 'tier-offline');
    let label = online ? 'ONLINE · Enhanced Mode' : 'OFFLINE · Standard Mode';
    if (aiOn && aiBack) label += ` · 🤖 ${{aiBack}}`;
    badge.innerHTML = `<span class="tier-dot"></span> Tier ${{tier}} — ${{label}}`;

    if (online && document.getElementById('dep-tab-btn')) {{
        document.getElementById('dep-tab-btn').style.display = '';
    }}
}})();

/* ── Helpers ──────────────────────────────────────────────────────────── */
function getGrade(s) {{
    return s >= 90 ? 'A' : s >= 80 ? 'B' : s >= 70 ? 'C' : s >= 60 ? 'D' : 'F';
}}
function gradeClass(g) {{
    return {{A:'grade-a', B:'grade-b', C:'grade-c', D:'grade-d', F:'grade-f'}}[g] || 'grade-f';
}}
function scoreColor(s) {{ return s >= 80 ? '#10b981' : s >= 60 ? '#f59e0b' : '#ef4444'; }}

/* ── Metrics summary cards ────────────────────────────────────────────── */
const overallScore = Object.values(apps).reduce((s, a) => s + (a.score || 0), 0) / Math.max(1, Object.keys(apps).length);
const crossAppCount = violations.filter(v => v.type === 'Cross-App Import').length;
const prevTs   = (trendData._meta || {{}}).previous_timestamp || null;
const prevCross= (trendData._meta || {{}}).cross_violations_prev;
const crossDelta = (trendData._meta || {{}}).cross_violations_delta;
const trendLine = prevTs
    ? `<div style="font-size:0.78rem;color:#64748b;margin-top:4px;">vs ${{prevTs.slice(0,10)}}: violations ${{crossDelta > 0 ? '+' : ''}}${{crossDelta}}</div>`
    : '';
document.getElementById('metrics-grid').innerHTML = `
    <div class="metric-card">
        <div class="metric-label">Overall Health</div>
        <div class="metric-value" style="color:${{scoreColor(overallScore)}}">${{overallScore.toFixed(1)}}%</div>
        <div style="font-size:0.85rem;">Grade: ${{getGrade(overallScore)}}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Cross-App Violations</div>
        <div class="metric-value" style="color:#ef4444">${{crossAppCount}}</div>
        ${{trendLine}}
    </div>
    <div class="metric-card">
        <div class="metric-label">Allowed Communications</div>
        <div class="metric-value" style="color:#3b82f6">${{allowedComms.length}}</div>
        <div style="font-size:0.85rem;">Signals / Tasks</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Security Issues</div>
        <div class="metric-value" style="color:#f59e0b">${{securityFindings.length}}</div>
        <div style="font-size:0.85rem;">Bandit scan results</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Avg Complexity</div>
        <div class="metric-value">${{metrics.radon_available ? (metrics.average_complexity||0).toFixed(2) : 'N/A'}}</div>
        <div style="font-size:0.85rem;">Max: ${{metrics.radon_available ? (metrics.max_complexity||0) : 'N/A'}}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Maintainability</div>
        <div class="metric-value">${{metrics.radon_available && metrics.maintainability_index != null ? Math.round(metrics.maintainability_index) : 'N/A'}}</div>
        <div style="font-size:0.85rem;">${{metrics.radon_available ? 'Radon MI score' : '⚠ radon not installed'}}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Ghost Files</div>
        <div class="metric-value" style="color:${{ghostFiles.length ? '#f59e0b' : '#10b981'}}">${{ghostFiles.length}}</div>
        <div style="font-size:0.85rem;">Physical but not in DNA</div>
    </div>`;

/* ── App health cards ─────────────────────────────────────────────────── */
const appGrid = document.getElementById('app-grid');
Object.entries(apps).sort((a, b) => b[1].score - a[1].score).forEach(([name, app]) => {{
    const sc    = Math.round(app.score || 0);
    const grade = getGrade(sc);
    const cls   = sc >= 80 ? 'healthy' : sc >= 60 ? 'warning' : 'critical';
    const phys  = app.physical_files || (app.modules || []).length || 0;
    const mods  = (app.modules || []).length;
    const viol  = app.violations || 0;
    const bviol = app.boundary_violations || viol;
    const sec   = app.security_issues || 0;
    const dead  = app.dead_code || 0;

    /* trend arrow + delta */
    const tr    = trendData[name] || {{}};
    const dir   = tr.direction || '';
    const delta = tr.delta != null ? Math.abs(tr.delta).toFixed(1) : null;
    const trendColor = dir === '↑' ? '#10b981' : dir === '↓' ? '#ef4444' : '#64748b';
    const trendHtml  = delta != null
        ? `<span style="font-size:0.72rem;color:${{trendColor}};font-weight:700;margin-left:6px;">${{dir}}${{delta}}%</span>`
        : '';

    appGrid.innerHTML += `
        <div class="app-card ${{cls}}" id="card-${{name}}" data-app="${{name}}">
            <div class="app-header">
                <span class="app-name">${{name.toUpperCase()}}</span>
                <span>
                    <span class="app-score" style="color:${{scoreColor(sc)}}">${{sc}}%</span>
                    <span class="grade-badge ${{gradeClass(grade)}}">${{grade}}</span>
                    ${{trendHtml}}
                </span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width:${{sc}}%;background:${{scoreColor(sc)}}"></div>
            </div>
            <div class="app-details">
                📁 ${{phys}} physical | 🔍 ${{mods}} audited<br>
                ⚠️ ${{bviol}} boundary violation(s) | 🔒 ${{sec}} security | 💀 ${{dead}} dead
            </div>
        </div>`;
}});

/* ── Tab switching ────────────────────────────────────────────────────── */
function showTab(id) {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const btn = document.querySelector(`.tab[onclick="showTab('${{id}}')"]`);
    if (btn) btn.classList.add('active');
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
}}

/* ── Tab content generators ───────────────────────────────────────────── */
function generateTestDebtTable() {{
    const testComms = allowedComms.filter(c => c.type === 'Test Cross-App Import');
    if (!testComms.length) return '<p class="status-ok" style="padding:16px;">✅ No cross-app imports in test files.</p>';
    return `<p style="color:#f59e0b;margin-bottom:12px;font-size:0.88rem;">
        🧪 ${{testComms.length}} cross-app import(s) found in test files.
        These do not affect health scores but indicate tests are crossing app boundaries,
        which can make tests brittle and harder to isolate.
        Consider using mocks or factories instead of importing live app modules.
    </p>
    <table><thead><tr><th>Test File</th><th>Imports From</th></tr></thead><tbody>
    ${{testComms.map(c => `<tr><td style="color:#fcd34d;">${{c.source_app}} → ${{c.details.split(' → ')[0]}}</td><td>${{c.details.split(' → ')[1]||''}}</td></tr>`).join('')}}
    </tbody></table>`;
}}

function generateDependencyTable() {{
    const pkgs = (depScan.packages || []);
    if (!pkgs.length) {{
        return `<div style="padding:20px;text-align:center;color:#64748b;">
            <p style="font-size:1rem;margin-bottom:8px;">📦 Dependency scan not available</p>
            <p style="font-size:0.85rem;">This is a Tier 1 (offline) run. Re-run with internet access to enable the dependency vulnerability and freshness scan.</p>
        </div>`;
    }}

    const critCves = depScan.critical_cves || [];
    let h = '';

    if (critCves.length) {{
        h += `<div style="background:rgba(127,29,29,.25);border:1px solid #7f1d1d;border-radius:8px;padding:14px 18px;margin-bottom:16px;">
            <div style="font-size:.9rem;font-weight:600;color:#fca5a5;margin-bottom:8px;">⚠️ ${{critCves.length}} Critical CVE(s) require immediate attention</div>`;
        critCves.forEach(c => {{
            h += `<div style="font-size:.8rem;color:#fca5a5;margin-bottom:4px;">
                <strong>${{c.package}}</strong> — <code>${{c.id}}</code>: ${{c.summary}}
            </div>`;
        }});
        h += '</div>';
    }}

    h += `<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:6px;font-size:.72rem;font-weight:600;color:#64748b;padding:0 4px;">
        <span>Package</span><span>Version</span><span>Status</span></div>`;
    pkgs.forEach(p => {{
        const oudBadge  = p.outdated ? `<span class="dep-badge dep-warn">Outdated → ${{p.latest}}</span>` : `<span class="dep-badge dep-ok">Current</span>`;
        const cveBadge  = p.cve_count ? `<span class="dep-badge dep-vuln">${{p.cve_count}} CVE${{p.cve_count>1?'s':''}}</span>` : `<span class="dep-badge dep-ok">No CVEs</span>`;
        const instBadge = p.installed === 'unknown' ? `<span class="dep-badge dep-na">Not installed</span>` : `<span style="font-size:.8rem;color:#94a3b8;">${{p.installed}}</span>`;
        h += `<div class="dep-card">
            <div><div class="dep-name">${{p.name}}</div><div class="dep-meta">${{p.installed === 'unknown' ? 'not in env' : `installed: ${{p.installed}}`}}</div></div>
            <div class="dep-badges">${{instBadge}}${{oudBadge}}${{cveBadge}}</div>
        </div>`;
    }});

    const meta_line = `Scanned ${{pkgs.length}} packages · ${{depScan.total_cves||0}} CVEs · ${{depScan.outdated_count||0}} outdated`;
    h += `<p style="font-size:.72rem;color:#475569;margin-top:10px;">${{meta_line}}</p>`;
    return h;
}}

function generateViolationsTable() {{
    const cross = violations.filter(v => v.type === 'Cross-App Import');
    const other = violations.filter(v => v.type !== 'Cross-App Import');
    let h = '';
    if (!violations.length) return '<p class="status-ok" style="padding:16px;">✅ No violations detected!</p>';
    if (cross.length) {{
        h += `<p style="color:#fca5a5;margin-bottom:12px;font-size:0.88rem;">🔴 ${{cross.length}} cross-app boundary violation(s) — replace with signals, tasks, or API calls.</p>`;
        h += '<table><thead><tr><th>Source Module</th><th>Target Module</th><th>Recommendation</th></tr></thead><tbody>';
        cross.forEach(v => h += `<tr><td class="status-critical">${{v.source||''}}</td><td>${{v.target||''}}</td><td style="color:#94a3b8;font-size:0.8rem;">${{v.recommendation||''}}</td></tr>`);
        h += '</tbody></table>';
    }}
    if (other.length) {{
        h += `<h3 style="margin:24px 0 12px;font-size:1rem;">Other Violations</h3>`;
        h += '<table><thead><tr><th>Type</th><th>Source</th><th>Severity</th></tr></thead><tbody>';
        other.forEach(v => h += `<tr><td>${{v.type||''}}</td><td>${{v.source||''}}</td><td>${{v.severity||''}}</td></tr>`);
        h += '</tbody></table>';
    }}
    return h;
}}

function generateAllowedTable() {{
    if (!allowedComms.length) return '<p style="padding:16px;color:#94a3b8;">No allowed cross-app communications recorded.<br><small style="color:#475569;">Note: Run with the fixed signal-detection tool to see signals and tasks here.</small></p>';
    let h = '<p style="color:#10b981;margin-bottom:12px;font-size:0.88rem;">✅ These cross-app interactions use decoupled communication patterns.</p>';
    h += '<table><thead><tr><th>Type</th><th>Source App</th><th>Target App</th><th>Details</th></tr></thead><tbody>';
    allowedComms.forEach(c => h += `<tr><td class="status-ok">${{c.type||''}}</td><td>${{c.source_app||''}}</td><td>${{c.target_app||''}}</td><td style="color:#94a3b8;font-size:0.8rem;">${{c.details||''}}</td></tr>`);
    return h + '</tbody></table>';
}}

function generateSecurityTable() {{
    if (!securityFindings.length) return '<p class="status-ok" style="padding:16px;">✅ No security issues detected!</p>';
    let h = `<p style="color:#f59e0b;margin-bottom:12px;font-size:0.88rem;">⚠️ ${{securityFindings.length}} issue(s) found by Bandit. Test-file findings excluded from scoring.</p>`;
    h += '<table><thead><tr><th>Severity</th><th>File</th><th>Line</th><th>Issue</th></tr></thead><tbody>';
    securityFindings.forEach(s => {{
        const sev = (s.severity||'LOW').toUpperCase();
        const badgeCls = sev==='HIGH'?'badge-critical':sev==='MEDIUM'?'badge-high':'badge-low';
        const file = (s.file_path||s.source||'').split('/').pop();
        h += `<tr><td><span class="badge ${{badgeCls}}">${{sev}}</span></td><td>${{file}}</td><td>${{s.line||''}}</td><td style="color:#94a3b8;font-size:0.8rem;">${{(s.description||'').slice(0,90)}}</td></tr>`;
    }});
    return h + '</tbody></table>';
}}

function generateComplexityTable() {{
    const hcf = (metrics.high_complexity_functions || []).sort((a,b) => b.complexity - a.complexity);
    let h = `<div class="metrics-grid" style="margin-bottom:20px;">
        <div class="metric-card"><div class="metric-label">Avg Complexity</div><div class="metric-value">${{(metrics.average_complexity||0).toFixed(2)}}</div></div>
        <div class="metric-card"><div class="metric-label">Max Complexity</div><div class="metric-value">${{metrics.max_complexity||0}}</div></div>
        <div class="metric-card"><div class="metric-label">Maintainability</div><div class="metric-value">${{Math.round(metrics.maintainability_index||0)}}</div></div>
        <div class="metric-card"><div class="metric-label">Functions</div><div class="metric-value">${{metrics.functions_analyzed||0}}</div></div>
    </div>`;
    if (!hcf.length) {{ h += '<p class="status-ok">✅ No high-complexity functions (threshold: 10).</p>'; return h; }}
    h += '<h3 style="margin-bottom:12px;">High Complexity Functions (&gt;10)</h3>';
    h += '<table><thead><tr><th>Function</th><th>File</th><th>Complexity</th><th>Lines</th></tr></thead><tbody>';
    hcf.forEach(f => h += `<tr><td style="color:#fcd34d;">${{f.function||''}}</td><td>${{f.file||''}}</td><td style="color:${{(f.complexity||0)>15?'#ef4444':'#f59e0b'}};font-weight:700;">${{f.complexity||0}}</td><td>${{f.lines||''}}</td></tr>`);
    return h + '</tbody></table>';
}}

function generateGhostTable() {{
    if (!ghostFiles.length) return '<p class="status-ok" style="padding:16px;">✅ No ghost files — physical inventory matches DNA perfectly.</p>';
    let h = `<p style="color:#f59e0b;margin-bottom:12px;font-size:0.88rem;">⚠️ ${{ghostFiles.length}} file(s) exist physically but are absent from the DNA scan.</p>`;
    h += '<table><thead><tr><th>Module Path</th><th>App</th></tr></thead><tbody>';
    ghostFiles.forEach(g => h += `<tr><td class="status-warning">${{g}}</td><td>${{g.split('.')[0]}}</td></tr>`);
    return h + '</tbody></table>';
}}

function generateCyclesTab() {{
    if (!cycles.length) return '<p class="status-ok" style="padding:16px;">✅ No circular dependencies detected.</p>';
    let h = `<p style="color:#fca5a5;margin-bottom:16px;font-size:0.88rem;">🔄 ${{cycles.length}} circular dependency cycle(s). Click a cycle to highlight it in the network.</p>`;
    cycles.forEach((c, i) => {{
        const apps_involved = (c.apps||[]).join(', ') || '(same app)';
        const cross = c.cross_app ? '🌐 CROSS-APP' : '🔁 INTRA-APP';
        h += `<div class="cycle-item" onclick="highlightCycle(${{JSON.stringify(c.nodes||[])}})">
            <strong>${{cross}}</strong> — ${{(c.nodes||[]).join(' → ')}}
            <span style="float:right;font-size:0.75rem;color:#94a3b8;">Severity: ${{c.severity||'?'}} | Apps: ${{apps_involved}}</span>
        </div>`;
    }});
    return h;
}}

function generateRecommendations() {{
    if (!recommendations.length) return '<p style="padding:16px;color:#94a3b8;">✅ No recommendations generated.</p>';

    const effortColor = {{ S:'#10b981', M:'#3b82f6', L:'#f59e0b', XL:'#ef4444' }};
    const effortLabel = {{ S:'Small < 1h', M:'Medium 1-3h', L:'Large 3-8h', XL:'XL > 8h' }};

    return recommendations.map(r => {{
        const p  = (r.priority||'low').toLowerCase();
        const pc = p==='critical'?'#7f1d1d':p==='high'?'#78350f':p==='medium'?'#1e3a5f':'#1e3a2f';
        const tc = p==='critical'?'#fca5a5':p==='high'?'#fcd34d':p==='medium'?'#93c5fd':'#6ee7b7';
        const isAI  = r.ai_generated || false;
        const aiLbl = r.ai_backend || 'AI';
        const effort = r.effort || '';

        let html = `<div style="border-left:3px solid ${{tc}};padding:14px 18px;margin-bottom:14px;
                        background:rgba(30,41,59,.4);border-radius:0 8px 8px 0;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;">
                <span class="badge" style="background:${{pc}};color:${{tc}};">${{r.priority||'LOW'}}</span>
                ${{isAI ? `<span class="badge" style="background:#312e81;color:#a5b4fc;">🤖 ${{aiLbl}}</span>` : ''}}
                ${{effort ? `<span class="badge" style="background:rgba(15,23,42,.6);color:${{effortColor[effort]||'#94a3b8'}};">${{effortLabel[effort]||effort}}</span>` : ''}}
                <span style="font-size:.9rem;font-weight:600;color:#f1f5f9;">${{r.title||''}}</span>
            </div>`;

        if (r.why_harmful) {{
            html += `<p style="font-size:.84rem;color:#fcd34d;margin-bottom:8px;line-height:1.55;"><strong>\u26a0\ufe0f Why this is harmful:</strong><br>${{r.why_harmful}}</p>`;
        }}
        if (r.what_breaks_today) {{
            html += `<p style="font-size:.84rem;color:#fb923c;margin-bottom:8px;line-height:1.55;border-left:2px solid #fb923c;padding-left:8px;"><strong>🔥 What breaks today:</strong><br>${{r.what_breaks_today}}</p>`;
        }}
        if (r.description) {{
            const _d = r.description || '';
            const _isRawJson = _d.trimStart().startsWith('{{') || _d.trimStart().startsWith('[');
            if (!_isRawJson) {{
                html += `<p style="font-size:.82rem;color:#94a3b8;margin-bottom:8px;">${{_d}}</p>`;
            }}
        }}
        if (r.correct_location) {{
            html += `<p style="font-size:.82rem;color:#7dd3fc;margin-bottom:8px;"><strong>Should live in:</strong> <code>${{r.correct_location}}</code></p>`;
        }}
        if (r.migration_steps && r.migration_steps.length) {{
            html += `<div style="margin-bottom:8px;"><strong style="font-size:.8rem;color:#94a3b8;">Migration steps:</strong><ol style="margin:4px 0 0 18px;color:#94a3b8;font-size:.8rem;">`;
            r.migration_steps.forEach(s => {{ html += `<li style="margin-bottom:3px;">${{s}}</li>`; }});
            html += '</ol></div>';
        }}
        if (r.before_code || r.after_code) {{
            html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">`;
            if (r.before_code) {{
                html += `<div><div style="font-size:.72rem;color:#ef4444;margin-bottom:3px;">❌ Before</div>
                    <pre style="background:rgba(127,29,29,.2);border:1px solid #7f1d1d;border-radius:5px;
                        padding:8px;font-size:.72rem;color:#fca5a5;overflow-x:auto;white-space:pre-wrap;">${{r.before_code}}</pre></div>`;
            }}
            if (r.after_code) {{
                html += `<div><div style="font-size:.72rem;color:#10b981;margin-bottom:3px;">✅ After</div>
                    <pre style="background:rgba(6,78,59,.2);border:1px solid #064e3b;border-radius:5px;
                        padding:8px;font-size:.72rem;color:#6ee7b7;overflow-x:auto;white-space:pre-wrap;">${{r.after_code}}</pre></div>`;
            }}
            html += '</div>';
        }}
        if (r.action && !r.before_code) {{
            html += `<div style="font-size:.8rem;color:#7dd3fc;margin-top:6px;white-space:pre-wrap;"><strong>Action:</strong> ${{r.action}}</div>`;
        }}
        if ((r.affected_modules||[]).length) {{
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
        return html;
    }}).join('');
}}

function generateManifest() {{
    const byApp = {{}};
    Object.entries(modules).forEach(([name, mod]) => {{
        const app = name.split('.')[0];
        if (!byApp[app]) byApp[app] = [];
        byApp[app].push({{name, ...mod}});
    }});
    let h = '';
    Object.entries(byApp).sort().forEach(([app, mods]) => {{
        h += `<h3 style="margin:20px 0 10px;font-size:1rem;">${{app.toUpperCase()}} (${{mods.length}} modules)</h3>`;
        h += '<table><thead><tr><th>Module</th><th>Depth</th><th>Imports</th></tr></thead><tbody>';
        mods.sort((a,b) => a.name.localeCompare(b.name)).forEach(m => {{
            h += `<tr><td>${{m.name}}</td><td>${{m.bacon||m.bacon_depth||0}}</td><td>${{(m.imports||[]).length}}</td></tr>`;
        }});
        h += '</tbody></table>';
    }});
    return h;
}}

/* ── Populate tabs ────────────────────────────────────────────────────── */
document.getElementById('violations').innerHTML      = generateViolationsTable();
document.getElementById('test-debt').innerHTML       = generateTestDebtTable();
document.getElementById('allowed').innerHTML         = generateAllowedTable();
document.getElementById('security').innerHTML        = generateSecurityTable();
document.getElementById('complexity').innerHTML      = generateComplexityTable();
document.getElementById('ghost').innerHTML           = generateGhostTable();
document.getElementById('cycles').innerHTML          = generateCyclesTab();
document.getElementById('dependencies').innerHTML    = generateDependencyTable();
document.getElementById('recommendations').innerHTML = generateRecommendations();
document.getElementById('manifest').innerHTML        = generateManifest();

/* ── App card hover ↔ graph sync ─────────────────────────────────────── */
document.querySelectorAll('.app-card').forEach(card => {{
    card.addEventListener('mouseenter', () => highlightApp(card.dataset.app));
    card.addEventListener('mouseleave', clearHighlight);
    card.addEventListener('click', () => showTab('manifest'));
}});

/* ════════════════════════════════════════════════════════════════════════
   NETWORK GRAPH
   All vis-network interaction features:
     - hoverNode → highlight panels, update info bar, light up legend
     - selectNode / click → isolate node + direct connections
     - doubleClick → same as selectNode
     - legend hover → dim non-matching edges
     - legend click → toggle protocol filter
     - app card hover → dim non-app nodes in graph
     - highlightCycle() → highlight cycle nodes/edges
     - resetView() / fitAll()
═══════════════════════════════════════════════════════════════════════ */

/* Build nodes and edges */
const nodesData = Object.entries(modules).map(([id, mod]) => ({{
    id,
    label: id.split('.').pop() + '.py',
    group: id.split('.')[0],
    title: `<b>${{id.split('.')[0].toUpperCase()}}</b><br>${{id}}<br>Depth: ${{mod.bacon||1}}<br>Imports: ${{(mod.imports||[]).length}}`,
    bacon: mod.bacon || 1
}}));

const edgesData = [];
const edgeSeen  = new Set();
Object.entries(modules).forEach(([id, mod]) => {{
    (mod.imports || []).forEach(imp => {{
        if (!modules[imp] || imp === id) return;
        const key = id + '|' + imp;
        if (edgeSeen.has(key)) return;
        edgeSeen.add(key);
        const srcApp = id.split('.')[0], tgtApp = imp.split('.')[0];
        const isViol     = violations.some(v => v.type === 'Cross-App Import' && v.source === id && v.target === imp);
        const isBootstrap= allowedComms.some(c => c.type === 'Django Bootstrap (Exempt)' && c.details === `${{id}} → ${{imp}}`);
        const isAllow    = allowedComms.some(c => c.details === `${{id}} → ${{imp}}` && c.type !== 'Django Bootstrap (Exempt)');
        const tgtLeaf    = imp.split('.').pop().toLowerCase();
        const srcLeaf    = id.split('.').pop().toLowerCase();
        const BOOTSTRAP_LEAVES = ['asgi','wsgi','settings','celery','manage','routing','apps','admin'];

        let color = '#5DADE2', edgeType = 'internal', width = 1, dashes = false;
        if (srcApp === tgtApp) {{
            color = '#5DADE2'; edgeType = 'internal';
        }} else if (isBootstrap || BOOTSTRAP_LEAVES.includes(srcLeaf)) {{
            /* Bootstrap files: shown as subtle dashed grey — informative, not alarming */
            color = '#64748b'; edgeType = 'bootstrap'; dashes = [3, 5]; width = 1;
        }} else if (isAllow || ['signals','receivers','signal','receiver'].includes(tgtLeaf) || ['signals','receivers','signal','receiver'].includes(srcLeaf)) {{
            color = '#2ECC71'; edgeType = 'allowed'; dashes = true; width = 2;
        }} else if (['tasks','celery','worker'].includes(tgtLeaf) || ['tasks','celery','worker'].includes(srcLeaf)) {{
            color = '#A29BFE'; edgeType = 'celery'; dashes = [4, 4]; width = 2;
        }} else if (isViol) {{
            color = '#FF3333'; edgeType = 'violation'; width = 3;
        }} else if (srcApp !== tgtApp) {{
            /* Unknown cross-app — flag it orange until classified */
            color = '#FFA500'; edgeType = 'violation'; width = 2;
        }}
        edgesData.push({{ id: key, from: id, to: imp, arrows: 'to', color: {{color}}, edgeType, width, dashes }});
    }});
}});

/* ── Unified per-app colour scheme ────────────────────────────────────
   background : the island/node fill colour
   border     : 70% darkened version of the fill (always readable)
   text       : dark (#0f172a) for bright apps (gateway yellow),
                white (#f8fafc) for everything else
   This object is the single source of truth — sidebar dots, node fills,
   node borders, node labels, and score bar colors all read from here.
────────────────────────────────────────────────────────────────────── */
const APP_SCHEME = {{
    nexus_core:        {{ bg: '#1ABC9C', border: '#12836d', text: '#f8fafc' }},
    nexus_economy:     {{ bg: '#E67E22', border: '#a1581a', text: '#f8fafc' }},
    nexus_gaming:      {{ bg: '#34495E', border: '#243341', text: '#f8fafc' }},
    nexus_gateway:     {{ bg: '#F1C40F', border: '#a8890a', text: '#0f172a' }},
    nexus_social:      {{ bg: '#9B59B6', border: '#6c3e7f', text: '#f8fafc' }},
    nexus_tournaments: {{ bg: '#3498DB', border: '#246a99', text: '#f8fafc' }},
    nexus_content:     {{ bg: '#E74C3C', border: '#a1352a', text: '#f8fafc' }},
}};
const DEFAULT_SCHEME = {{ bg: '#475569', border: '#2d3a4a', text: '#f8fafc' }};

function appScheme(app) {{ return APP_SCHEME[app] || DEFAULT_SCHEME; }}
function appColor(app)  {{ return appScheme(app).bg; }}

/* ── Build island sidebar (LEFT of canvas, always in view) ───────────── */
const sidebarEl = document.getElementById('island-sidebar');
Object.entries(apps).sort((a,b) => b[1].score - a[1].score).forEach(([appName, appData]) => {{
    const col = appColor(appName);
    const sc  = Math.round(appData.score || 0);
    // Short label: strip "nexus_" prefix, uppercase
    const shortLabel = appName.replace(/^nexus_/, '').toUpperCase();
    const pill = document.createElement('div');
    pill.className = 'island-pill';
    pill.dataset.app = appName;
    pill.title = `${{appName}} — ${{sc}}%`;
    pill.innerHTML = `
        <div class="island-dot" style="background:${{col}};box-shadow:0 0 0 2px ${{col}}33;"></div>
        <span class="island-label">${{shortLabel}}</span>
        <span class="island-score">${{sc}}%</span>`;
    /* clicking an island pill focuses that app in the graph */
    pill.addEventListener('click', () => {{
        const isActive = pill.classList.contains('pill-active');
        if (isActive) {{ clearHighlight(); }}
        else          {{ highlightApp(appName); }}
    }});
    sidebarEl.appendChild(pill);
}});

/* Apply correct per-app colors to nodes (border + text from scheme) */
nodesData.forEach(n => {{
    const s = appScheme(n.group);
    n.color = {{ background: s.bg, border: s.border }};
    n.font  = {{ color: s.text, size: 13 }};
}});

const visNodes = new vis.DataSet(nodesData);
const visEdges = new vis.DataSet(edgesData);

const network = new vis.Network(
    document.getElementById('network'),
    {{ nodes: visNodes, edges: visEdges }},
    {{
        nodes: {{ shape: 'box', margin: 10 }},
        edges: {{ smooth: {{ type: 'curvedArrow', roundness: 0.2 }}, selectionWidth: 2, hoverWidth: 3 }},
        physics: {{
            solver: 'forceAtlas2Based',
            stabilization: {{ iterations: 150 }},
            timestep: 0.5, adaptiveTimestep: true
        }},
        interaction: {{ hover: true, tooltipDelay: 100, keyboard: true }}
    }}
);

/* hoverNode — highlight sidebar island, update info bar, light legend ── */
network.on('hoverNode', function(params) {{
    const nd = visNodes.get(params.node); if (!nd) return;
    const app = nd.group;
    const connEdges = edgesData.filter(e => e.from === params.node || e.to === params.node);
    const viols = connEdges.filter(e => e.edgeType === 'violation').length;

    /* Info bar update — stays in view below the canvas */
    document.getElementById('node-info').innerHTML =
        `<strong style="color:#38bdf8;">${{nd.label}}</strong>
         <span style="color:#475569;">|</span>
         App: <span style="color:#94a3b8;">${{app.toUpperCase()}}</span>
         <span style="color:#475569;">|</span>
         Depth: ${{nd.bacon||1}}
         <span style="color:#475569;">|</span>
         Connections: ${{connEdges.length}}
         <span style="color:#475569;">|</span>
         Violations: <span style="color:${{viols?'#ef4444':'#10b981'}};font-weight:700;">${{viols}}</span>`;

    /* Island sidebar — highlight the matching pill, dim others */
    document.querySelectorAll('.island-pill').forEach(p => {{
        const match = p.dataset.app === app;
        p.classList.toggle('pill-active', match);
        p.classList.toggle('pill-dimmed', !match);
    }});

    /* Top app cards — gentle highlight, NO scroll */
    document.querySelectorAll('.app-card').forEach(c => {{
        const match = c.dataset.app === app;
        c.classList.toggle('panel-dimmed', !match);
        c.classList.toggle('panel-highlight', match);
    }});

    /* Legend — light up protocols used by this node */
    const protos = new Set(connEdges.map(e => e.edgeType));
    document.querySelectorAll('.legend-item[data-edge-type]').forEach(li => {{
        li.classList.toggle('active', protos.has(li.dataset.edgeType));
    }});
}});

network.on('blurNode', function() {{
    document.getElementById('node-info').textContent =
        'Hover a node to see details · Click to isolate · Double-click to reset';
    document.querySelectorAll('.island-pill').forEach(p =>
        p.classList.remove('pill-active', 'pill-dimmed'));
    document.querySelectorAll('.app-card').forEach(c =>
        c.classList.remove('panel-dimmed', 'panel-highlight'));
    document.querySelectorAll('.legend-item[data-edge-type]').forEach(li =>
        li.classList.remove('active'));
    /* BUG FIX: restore BOTH color AND font — not just font.
       highlightCycle sets background to grey; blurNode must undo that. */
    visNodes.update(nodesData.map(n => ({{
        id: n.id,
        color: n.color,
        font:  {{ color: appScheme(n.group).text, size: 13 }}
    }})));
}});

/* selectNode: isolate node + direct connections ──────────────────────── */
network.on('selectNode', function(params) {{
    if (!params.nodes.length) return;
    const sid = params.nodes[0];
    const nd  = visNodes.get(sid); if (!nd) return;
    const connEdges  = edgesData.filter(e => e.from === sid || e.to === sid);
    const connNodes  = new Set([sid]);
    connEdges.forEach(e => {{ connNodes.add(e.from); connNodes.add(e.to); }});
    visNodes.update(nodesData.map(n => ({{ id: n.id, hidden: !connNodes.has(n.id) }})));
    visEdges.update(edgesData.map(e => ({{ id: e.id, hidden: e.from !== sid && e.to !== sid }})));
    const viols = connEdges.filter(e => e.edgeType === 'violation').length;
    document.getElementById('node-info').innerHTML =
        `<strong style="color:#38bdf8;">ISOLATED: ${{nd.label}}</strong>&nbsp;&nbsp;
         App: ${{nd.group.toUpperCase()}}&nbsp;&nbsp;
         Connections: ${{connEdges.length}}&nbsp;&nbsp;
         Violations: <span style="color:${{viols?'#ef4444':'#10b981'}}">${{viols}}</span>
         &nbsp;&nbsp;<button onclick="resetView()" style="padding:4px 10px;border:1px solid #334155;background:transparent;color:#94a3b8;border-radius:5px;cursor:pointer;font-size:0.8rem;">Reset</button>`;
    network.fit();
}});

network.on('doubleClick', function(params) {{
    if (params.nodes.length) network.selectNodes([params.nodes[0]]);
    else resetView();
}});

/* App card hover → dim non-app nodes + sync sidebar ──────────────────── */
function highlightApp(app) {{
    const rel = new Set(nodesData.filter(n => n.group === app).map(n => n.id));
    visNodes.update(nodesData.map(n => ({{
        id:      n.id,
        /* BUG FIX: always restore the original color so any prior cycle-grey
           is cleared for in-app nodes; dimmed nodes use opacity (not grey color)
           so they retain their app color and fade back cleanly on clearHighlight. */
        color:   n.color,
        opacity: rel.has(n.id) ? 1 : 0.06,
        font:    {{ color: rel.has(n.id) ? appScheme(n.group).text : '#334155', size: 13 }}
    }})));
    visEdges.update(edgesData.map(e => ({{
        id:    e.id,
        color: (rel.has(e.from)||rel.has(e.to)) ? e.color : {{ color:'rgba(255,255,255,0.02)' }}
    }})));
    document.querySelectorAll('.app-card').forEach(c => {{
        c.classList.toggle('panel-dimmed',    c.dataset.app !== app);
        c.classList.toggle('panel-highlight', c.dataset.app === app);
    }});
    document.querySelectorAll('.island-pill').forEach(p => {{
        p.classList.toggle('pill-active', p.dataset.app === app);
        p.classList.toggle('pill-dimmed',  p.dataset.app !== app);
    }});
}}
function clearHighlight() {{
    /* BUG FIX: restore color AND opacity — opacity alone doesn't undo a color change. */
    visNodes.update(nodesData.map(n => ({{
        id:      n.id,
        color:   n.color,
        opacity: 1,
        font:    {{ color: appScheme(n.group).text, size: 13 }}
    }})));
    visEdges.update(edgesData);
    document.querySelectorAll('.app-card').forEach(c =>
        c.classList.remove('panel-dimmed', 'panel-highlight'));
    document.querySelectorAll('.island-pill').forEach(p =>
        p.classList.remove('pill-active', 'pill-dimmed'));
}}

/* highlightCycle ─────────────────────────────────────────────────────── */
function highlightCycle(cycleNodes) {{
    const s = new Set(cycleNodes);
    visNodes.update(nodesData.map(n => ({{ id: n.id, opacity: s.has(n.id) ? 1 : 0.06, color: s.has(n.id) ? n.color : {{ background:'#1e293b', border:'#334155' }} }})));
    visEdges.update(edgesData.map(e => ({{ id: e.id, color: (s.has(e.from)&&s.has(e.to)) ? {{color:'#ff6b6b'}} : {{color:'rgba(255,255,255,0.02)'}}, width: (s.has(e.from)&&s.has(e.to)) ? 3 : 0.3 }})));
    network.fit();
    showTab('cycles');
}}
window.highlightCycle = highlightCycle;

/* ── Graph analysis tools ──────────────────────────────────────────────── */
let _frozen = false;
let _separated = false;
let _inspectMode = false;

function toggleFreeze() {{
    _frozen = !_frozen;
    const btn = document.getElementById('freeze-btn');
    if (_frozen) {{
        network.stopSimulation();
        btn.classList.add('active');
        btn.textContent = '▶ Unfreeze';
    }} else {{
        network.startSimulation();
        btn.classList.remove('active');
        btn.textContent = '🧊 Freeze';
    }}
}}

function toggleSeparation() {{
    const btn = document.getElementById('sep-btn');
    if (_separated) {{
        resetSeparation();
        btn.classList.remove('active');
        btn.textContent = '🏝️ Separate Apps';
        _separated = false;
    }} else {{
        separateApps();
        btn.classList.add('active');
        btn.textContent = '🔗 Merge View';
        _separated = true;
    }}
}}

function separateApps() {{
    /* Group nodes by app, place each app cluster in its own column zone.
       Connections remain visible — crossing lines show coupling visually. */
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
            positions[nid] = {{
                x: zx + nx * 90 + 40,
                y: zy + ny * 90 + 40
            }};
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
    /* Draw app zone labels as background titles */
    network.fit({{ animation: {{ duration: 600, easingFunction: 'easeInOutQuad' }} }});
}}

function resetSeparation() {{
    network.setOptions({{ physics: {{ enabled: true }} }});
    network.setData({{
        nodes: new vis.DataSet(nodesData),
        edges: new vis.DataSet(edgesData)
    }});
    network.fit({{ animation: true }});
}}

function toggleInspect() {{
    _inspectMode = !_inspectMode;
    const btn = document.getElementById('inspect-btn');
    const panel = document.getElementById('edge-info-panel');
    if (_inspectMode) {{
        btn.classList.add('active');
        btn.textContent = '🔍 Inspecting…';
        panel.style.display = 'block';
        panel.innerHTML = '<span style="color:#64748b;">Click any edge/connection in the graph to inspect it.</span>';
    }} else {{
        btn.classList.remove('active');
        btn.textContent = '🔍 Inspect Edges';
        panel.style.display = 'none';
    }}
}}

/* Edge click inspector */
network.on('selectEdge', function(params) {{
    if (!params.edges.length) return;
    const eid = params.edges[0];
    const edge = edgesData.find(e => e.id === eid);
    if (!edge) return;
    const panel = document.getElementById('edge-info-panel');
    /* Always show panel on edge click regardless of inspect toggle */
    panel.style.display = 'block';
    document.getElementById('inspect-btn').classList.add('active');
    _inspectMode = true;
    document.getElementById('inspect-btn').textContent = '🔍 Inspecting…';

    const src = edge.from || '';
    const tgt = edge.to   || '';
    const srcApp = src.split('.')[0].toUpperCase();
    const tgtApp = tgt.split('.')[0].toUpperCase();

    /* Look up all violations matching this edge */
    const edgeViolations = violations.filter(v => v.source === src && v.target === tgt);
    const edgeAllowed    = allowedComms.filter(c => {{
        const d = c.details || '';
        return d.includes(src) && d.includes(tgt);
    }});

    let html = `<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px;">
        <span style="font-size:1.1rem;font-weight:700;color:#38bdf8;">${{src.split('.').pop()}}.py</span>
        <span style="color:#475569;">──▶</span>
        <span style="font-size:1.1rem;font-weight:700;color:#38bdf8;">${{tgt.split('.').pop()}}.py</span>
        <span style="font-size:.75rem;color:#64748b;">(${{srcApp}} → ${{tgtApp}})</span>
    </div>`;

    if (edgeViolations.length) {{
        html += `<div style="border-left:3px solid #ef4444;padding-left:10px;margin-bottom:8px;">`;
        html += `<div style="color:#fca5a5;font-weight:600;margin-bottom:4px;">🚨 ${{edgeViolations.length}} Violation(s)</div>`;
        edgeViolations.forEach(v => {{
            html += `<div style="font-size:.8rem;color:#94a3b8;margin-bottom:3px;">
                <span style="color:#ef4444;">■</span>
                <code style="color:#fcd34d;">${{v.source}}</code> imports from <code style="color:#fcd34d;">${{v.target}}</code>
                ${{v.type ? '&nbsp;·&nbsp;<span style="color:#fb923c;">' + v.type + '</span>' : ''}}
                ${{v.penalty ? '&nbsp;·&nbsp;<span style="color:#ef4444;">−' + v.penalty + 'pts</span>' : ''}}
            </div>`;
        }});
        html += '</div>';
    }}
    if (edgeAllowed.length) {{
        html += `<div style="border-left:3px solid #10b981;padding-left:10px;">`;
        html += `<div style="color:#6ee7b7;font-weight:600;margin-bottom:4px;">✅ ${{edgeAllowed.length}} Allowed Communication(s)</div>`;
        edgeAllowed.forEach(c => {{
            html += `<div style="font-size:.8rem;color:#94a3b8;margin-bottom:2px;">
                <span style="color:#10b981;">■</span> ${{c.type || 'Allowed'}}
                ${{c.details ? '&nbsp;·&nbsp;<code>' + c.details + '</code>' : ''}}
            </div>`;
        }});
        html += '</div>';
    }}
    if (!edgeViolations.length && !edgeAllowed.length) {{
        html += `<span style="color:#64748b;font-size:.85rem;">Internal edge — same-app import (no violation)</span>`;
    }}

    panel.innerHTML = html;
}});

network.on('deselectEdge', function() {{
    /* keep panel visible so you can read it after deselecting */
}});

/* ── resetView / fitAll ─────────────────────────────────────────────────── */
function resetView() {{
    visNodes.update(nodesData.map(n => ({{
        id: n.id, hidden: false, opacity: 1,
        color: n.color,
        font: {{ color: appScheme(n.group).text, size: 13 }}
    }})));
    visEdges.update(edgesData.map(e => ({{
        id: e.id, hidden: false, color: e.color, width: e.width
    }})));
    document.querySelectorAll('.app-card').forEach(c =>
        c.classList.remove('panel-dimmed','panel-highlight'));
    document.querySelectorAll('.island-pill').forEach(p =>
        p.classList.remove('pill-active','pill-dimmed'));
    document.querySelectorAll('.legend-item[data-edge-type]').forEach(li =>
        li.classList.remove('active'));
    document.getElementById('node-info').textContent =
        'Hover a node to see details · Click to isolate · Double-click to reset';
    network.fit();
}}
function fitAll() {{ network.fit(); }}
window.resetView = resetView;
window.fitAll    = fitAll;

/* Legend build + interactions ────────────────────────────────────────── */
const legendDef = [
    {{ label:'Internal Import',                  color:'#5DADE2', type:'internal',   dashed:false }},
    {{ label:'Cross-App Violation',              color:'#FF3333', type:'violation',  dashed:false }},
    {{ label:'Django Bootstrap (Exempt)',         color:'#94a3b8', type:'bootstrap',  dashed:true  }},
    {{ label:'Signal / Receiver (Allowed)',       color:'#2ECC71', type:'allowed',    dashed:true  }},
    {{ label:'Celery Task (Allowed)',             color:'#A29BFE', type:'celery',     dashed:true  }},
];
let activeFilter = null;
const legendDiv = document.getElementById('legend');
legendDef.forEach(item => {{
    const div = document.createElement('div');
    div.className = 'legend-item';
    div.dataset.edgeType = item.type;
    div.innerHTML = `<div class="legend-color${{item.dashed?' dashed':''}}" style="background:${{item.color}};color:${{item.color}};"></div><span>${{item.label}}</span>`;
    /* hover = dim non-matching edges + fade non-connected nodes */
    div.addEventListener('mouseenter', () => {{
        if (activeFilter) return;
        visEdges.update(edgesData.map(e => ({{
            id: e.id,
            color: e.edgeType===item.type ? e.color : {{color:'rgba(255,255,255,0.04)'}},
            width: e.edgeType===item.type ? Math.max(e.width,2) : 0.4
        }})));
        const inv = new Set();
        edgesData.filter(e=>e.edgeType===item.type).forEach(e=>{{inv.add(e.from);inv.add(e.to);}});
        visNodes.update(nodesData.map(n=>({{id:n.id, opacity: inv.has(n.id)?1:0.07}})));
    }});
    /* BUG FIX: mouseleave restores color AND opacity (not just opacity).
       Without color restore, any prior highlightCycle grey stays visible. */
    div.addEventListener('mouseleave', () => {{
        if (activeFilter) return;
        visEdges.update(edgesData);
        visNodes.update(nodesData.map(n=>({{id:n.id, color:n.color, opacity:1}})));
    }});
    /* click = toggle persistent protocol filter */
    div.addEventListener('click', () => {{
        if (activeFilter === item.type) {{
            activeFilter = null;
            div.classList.remove('active');
            /* BUG FIX: deactivating filter restores color + hidden + opacity */
            visNodes.update(nodesData.map(n=>({{
                id:n.id, hidden:false, opacity:1, color:n.color,
                font:{{color:appScheme(n.group).text, size:13}}
            }})));
            visEdges.update(edgesData.map(e=>({{id:e.id,hidden:false,color:e.color,width:e.width}})));
        }} else {{
            activeFilter = item.type;
            document.querySelectorAll('.legend-item').forEach(l=>l.classList.remove('active'));
            div.classList.add('active');
            const inv=new Set();
            edgesData.filter(e=>e.edgeType===item.type).forEach(e=>{{inv.add(e.from);inv.add(e.to);}});
            visNodes.update(nodesData.map(n=>({{id:n.id, hidden:!inv.has(n.id)}})));
            visEdges.update(edgesData.map(e=>({{id:e.id,hidden:e.edgeType!==item.type}})));
            network.fit();
        }}
    }});
    legendDiv.appendChild(div);
}});
</script>
</body>
</html>'''
        return html