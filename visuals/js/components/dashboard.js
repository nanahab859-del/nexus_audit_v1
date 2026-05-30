import { State, appScheme } from '../state.js';

function getGrade(s) {
    return s >= 90 ? 'A' : s >= 80 ? 'B' : s >= 70 ? 'C' : s >= 60 ? 'D' : 'F';
}
function gradeClass(g) {
    return {A:'grade-a', B:'grade-b', C:'grade-c', D:'grade-d', F:'grade-f'}[g] || 'grade-f';
}
function scoreColor(s) { return s >= 80 ? '#10b981' : s >= 60 ? '#f59e0b' : '#ef4444'; }

export function renderDashboard() {
    renderTierBadge();
    renderMetrics();
    renderChangeSummary();
    renderAppGrid();
}

function renderTierBadge() {
    const badge = document.getElementById('tier-badge');
    if (!badge) return;
    
    const capabilities = State.capabilities || {};
    const tier = capabilities.tier || 1;
    const online = capabilities.online || false;
    const aiBack = capabilities.ai_backend || null;
    const aiOn = capabilities.ai_recommendations || false;

    badge.className = 'tier-badge ' + (online ? 'tier-online' : 'tier-offline');
    let label = online ? 'ONLINE · Enhanced Mode' : 'OFFLINE · Standard Mode';
    if (aiOn && aiBack) label += ` · 🤖 ${aiBack}`;
    badge.innerHTML = `<span class="tier-dot"></span> Tier ${tier} — ${label}`;

    if (online && document.getElementById('dep-tab-btn')) {
        document.getElementById('dep-tab-btn').style.display = '';
    }
}

function renderMetrics() {
    const overallScore = Object.values(State.apps).reduce((s, a) => s + (a.score || 0), 0) / Math.max(1, Object.keys(State.apps).length);
    const crossAppCount = State.violations.filter(v => v.type === 'Cross-App Import').length;
    
    const prevTs = (State.trendData._meta || {}).previous_timestamp || null;
    const crossDelta = (State.trendData._meta || {}).cross_violations_delta;
    const trendLine = prevTs && crossDelta !== undefined
        ? `<div style="font-size:0.78rem;color:#64748b;margin-top:4px;">vs ${prevTs.slice(0,10)}: violations ${crossDelta > 0 ? '+' : ''}${crossDelta}</div>`
        : '';
        
    const mg = document.getElementById('metrics-grid');
    if (!mg) return;
    
    mg.innerHTML = `
        <div class="metric-card">
            <div class="metric-label">Overall Health</div>
            <div class="metric-value" style="color:${scoreColor(overallScore)}">${overallScore.toFixed(1)}%</div>
            <div style="font-size:0.85rem;">Grade: ${getGrade(overallScore)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Cross-App Violations</div>
            <div class="metric-value" style="color:#ef4444">${crossAppCount}</div>
            ${trendLine}
        </div>
        <div class="metric-card">
            <div class="metric-label">Allowed Communications</div>
            <div class="metric-value" style="color:#3b82f6">${State.allowedComms.length}</div>
            <div style="font-size:0.85rem;">Signals / Tasks</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Security Issues</div>
            <div class="metric-value" style="color:#f59e0b">${State.securityFindings.length}</div>
            <div style="font-size:0.85rem;">Bandit scan results</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Complexity</div>
            <div class="metric-value">${State.metrics.radon_available ? (State.metrics.average_complexity||0).toFixed(2) : 'N/A'}</div>
            <div style="font-size:0.85rem;">Max: ${State.metrics.radon_available ? (State.metrics.max_complexity||0) : 'N/A'}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Maintainability</div>
            <div class="metric-value">${State.metrics.radon_available && State.metrics.maintainability_index != null ? Math.round(State.metrics.maintainability_index) : 'N/A'}</div>
            <div style="font-size:0.85rem;">${State.metrics.radon_available ? 'Radon MI score' : '⚠ radon not installed'}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Ghost Files</div>
            <div class="metric-value" style="color:${State.ghostFiles.length ? '#f59e0b' : '#10b981'}">${State.ghostFiles.length}</div>
            <div style="font-size:0.85rem;">Physical but not in DNA</div>
        </div>
    `;
}

function renderChangeSummary() {
    const container = document.getElementById('change-summary-container');
    if (!container) return;
    const summary = State.changeSummary || {};
    if (!summary || Object.keys(summary).length === 0) { container.innerHTML = ''; return; }
    
    if (summary.first_run) {
        container.innerHTML = `<details open style="margin:14px 0 18px;background:rgba(15,23,42,.88);border:1px solid #334155;border-radius:12px;overflow:hidden;">
            <summary style="cursor:pointer;list-style:none;padding:12px 16px;font-weight:700;color:#cbd5e1;display:flex;justify-content:space-between;align-items:center;gap:12px;">
                <span>📊 First run — no history to compare.</span>
                <span style="color:#64748b;font-size:.78rem;">Click to expand/collapse</span>
            </summary>
        </details>`;
        return;
    }
    
    const resolved = parseInt(summary.resolved || 0) || 0;
    const new_violations = parseInt(summary.new_violations || 0) || 0;
    const score_deltas = summary.score_deltas || {};
    const prev_ts = summary.previous_timestamp || '';
    const title = 'Since last run' + (prev_ts ? ` (${prev_ts.slice(0,10)})` : '');
    const delta_bits = [];
    
    Object.keys(score_deltas).sort().forEach(app => {
        let delta = parseInt(score_deltas[app]);
        if (!delta) return;
        const direction = delta > 0 ? '↑' : '↓';
        const color = delta > 0 ? '#10b981' : '#ef4444';
        const sign = delta > 0 ? '+' : '';
        delta_bits.push(`<span style="padding:5px 10px;border-radius:999px;background:rgba(15,23,42,.75);border:1px solid #334155;color:${color};font-size:.8rem;font-weight:700;">${direction} ${app} ${sign}${delta}pts</span>`);
    });
    
    if (!delta_bits.length) delta_bits.push('<span style="padding:5px 10px;border-radius:999px;background:rgba(15,23,42,.75);border:1px solid #334155;color:#64748b;font-size:.8rem;">No app score changes</span>');
    
    container.innerHTML = `<details open style="margin:14px 0 18px;background:rgba(15,23,42,.88);border:1px solid #334155;border-radius:12px;overflow:hidden;">
        <summary style="cursor:pointer;list-style:none;padding:12px 16px;font-weight:700;color:#f1f5f9;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
            <span>${title}</span>
            <span style="color:#94a3b8;font-size:.8rem;">✅ ${resolved} resolved · 🔴 ${new_violations} new violations</span>
        </summary>
        <div style="border-top:1px solid #334155;padding:12px 16px;background:rgba(30,41,59,.55);">
            <div style="display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin-bottom:10px;">${delta_bits.join('')}</div>
            <div style="font-size:.8rem;color:#94a3b8;">Tip: expand or collapse this banner to compare the current run against the previous snapshot.</div>
        </div>
    </details>`;
}

function renderAppGrid() {
    const appGrid = document.getElementById('app-grid');
    if (!appGrid) return;
    
    appGrid.innerHTML = '';
    
    // Config Health (if available)
    if (State.configHealth && State.configHealth.config_folder_name) {
        const cfg = State.configHealth;
        const cfgName = cfg.config_folder_name;
        const cfgSum = cfg.summary || {};
        const cfgSc = cfgSum.score != null ? cfgSum.score : 100;
        const cfgCls = cfgSc >= 80 ? 'healthy' : cfgSc >= 60 ? 'warning' : 'critical';
        const cfgGrade = getGrade(cfgSc);
        appGrid.innerHTML += `
            <div class="app-card ${cfgCls}" data-app="${cfgName}" style="border-left-color:#8b5cf6;" title="Project configuration layer">
                <div class="app-header">
                    <span class="app-name">⚙️ ${cfgName.toUpperCase()}</span>
                    <span>
                        <span class="app-score" style="color:${scoreColor(cfgSc)}">${cfgSc}%</span> 
                        <span class="grade-badge ${gradeClass(cfgGrade)}">${cfgGrade}</span> 
                        <span style="font-size:0.68rem;color:#8b5cf6;margin-left:6px;font-weight:600;">KERNEL</span>
                    </span>
                </div>
                <div class="score-bar">
                    <div class="score-fill" style="width:${cfgSc}%;background:${scoreColor(cfgSc)}"></div>
                </div>
                <div class="app-details">
                    ⚙️ Settings · URL conf · ASGI/WSGI · Celery<br>
                    ✅ ${cfgSum.passed||0} passed · ⚠️ ${cfgSum.warnings||0} warnings · ❌ ${cfgSum.failures||0} failures
                </div>
            </div>`;
    }
    
    // Regular Apps
    Object.entries(State.apps).sort((a, b) => b[1].score - a[1].score).forEach(([name, app]) => {
        const sc = Math.round(app.score || 0);
        const grade = getGrade(sc);
        const cls = sc >= 80 ? 'healthy' : sc >= 60 ? 'warning' : 'critical';
        const phys = app.physical_files || (app.modules || []).length || 0;
        const mods = (app.modules || []).length;
        const bviol = app.boundary_violations || app.violations || 0;
        const sec = app.security_issues || 0;
        const dead = app.dead_code || 0;
        
        const tr = State.trendData[name] || {};
        const dir = tr.direction || '';
        const delta = tr.delta != null ? Math.abs(tr.delta).toFixed(1) : null;
        const trendColor = dir === '↑' ? '#10b981' : dir === '↓' ? '#ef4444' : '#64748b';
        const trendHtml = delta != null ? `<span style="font-size:0.72rem;color:${trendColor};font-weight:700;margin-left:6px;">${dir}${delta}%</span>` : '';
        
        appGrid.innerHTML += `
            <div class="app-card ${cls}" data-app="${name}">
                <div class="app-header">
                    <span class="app-name">${name.toUpperCase()}</span>
                    <span>
                        <span class="app-score" style="color:${scoreColor(sc)}">${sc}%</span> 
                        <span class="grade-badge ${gradeClass(grade)}">${grade}</span>${trendHtml}
                    </span>
                </div>
                <div class="score-bar">
                    <div class="score-fill" style="width:${sc}%;background:${scoreColor(sc)}"></div>
                </div>
                <div class="app-details">
                    📁 ${phys} physical | 🔍 ${mods} audited<br>
                    ⚠️ ${bviol} boundary violation(s) | 🔒 ${sec} security | 💀 ${dead} dead
                </div>
            </div>`;
    });
}
