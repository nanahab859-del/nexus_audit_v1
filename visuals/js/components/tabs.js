import { State } from '../state.js';

export function setupTabs() {
    window.showTab = function(tabId) {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        const btn = document.querySelector(`.tab[onclick="showTab('${tabId}')"]`);
        if (btn) btn.classList.add('active');
        const content = document.getElementById(tabId);
        if (content) content.classList.add('active');
    };
}

export function renderTabs() {
    const tabs = {
        'violations': generateViolationsTable,
        'test-debt': generateTestDebtTable,
        'allowed': generateAllowedTable,
        'security': generateSecurityTable,
        'complexity': generateComplexityTable,
        'ghost': generateGhostTable,
        'cycles': generateCyclesTable,
        'dependencies': generateDependencyTable,
        'config-health': generateConfigHealthTab,
        'coupling-map': generateCouplingMapTab
    };

    for (const [id, generator] of Object.entries(tabs)) {
        const el = document.getElementById(id);
        if (el) {
            el.innerHTML = generator();
        }
    }
}

function _dlBar(type, title) {
    return `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="color:#f1f5f9;margin:0;">${title}</h3>
    </div>`;
}

function generateViolationsTable() {
    let html = _dlBar('violations', 'Architecture Violations');
    if (!State.violations || !State.violations.length) return html + '<p class="status-ok">No violations found.</p>';
    
    html += `<table><thead><tr><th>Source</th><th>Target</th><th>Type</th><th>Penalty</th></tr></thead><tbody>`;
    State.violations.forEach(v => {
        html += `<tr>
            <td style="color:#fca5a5;">${v.source_module || 'unknown'}</td>
            <td style="color:#fcd34d;">${v.target_module || 'unknown'}</td>
            <td><span class="badge badge-high">${v.type || 'Violation'}</span></td>
            <td>${v.penalty || 0}</td>
        </tr>`;
    });
    html += `</tbody></table>`;
    return html;
}

function generateTestDebtTable() {
    let html = _dlBar('test-debt', 'Test Debt');
    return html + '<p class="status-ok">Test metrics not available in current audit.</p>';
}

function generateAllowedTable() {
    let html = _dlBar('allowed', 'Allowed Communications');
    if (!State.allowedComms || !State.allowedComms.length) return html + '<p class="status-warning">No allowed communications found.</p>';
    
    html += `<table><thead><tr><th>Source</th><th>Target</th><th>Reason</th></tr></thead><tbody>`;
    State.allowedComms.forEach(c => {
        html += `<tr>
            <td style="color:#93c5fd;">${c.source || 'unknown'}</td>
            <td style="color:#86efac;">${c.target || 'unknown'}</td>
            <td><span class="badge badge-medium">${c.type || 'Allowed'}</span></td>
        </tr>`;
    });
    html += `</tbody></table>`;
    return html;
}

function generateSecurityTable() {
    let html = _dlBar('security', 'Security Findings (Bandit)');
    if (!State.securityFindings || !State.securityFindings.length) return html + '<p class="status-ok">No security issues found.</p>';
    
    html += `<table><thead><tr><th>File</th><th>Issue</th><th>Severity</th></tr></thead><tbody>`;
    State.securityFindings.forEach(f => {
        const sevClass = f.severity === 'HIGH' ? 'badge-critical' : f.severity === 'MEDIUM' ? 'badge-high' : 'badge-low';
        html += `<tr>
            <td style="font-family:monospace;font-size:0.8rem;color:#94a3b8;">${f.filename || 'unknown'}:${f.line_number || ''}</td>
            <td>${f.issue_text || ''}</td>
            <td><span class="badge ${sevClass}">${f.severity || 'LOW'}</span></td>
        </tr>`;
    });
    html += `</tbody></table>`;
    return html;
}

function generateComplexityTable() {
    let html = _dlBar('complexity', 'Complexity Metrics');
    if (!State.metrics || !State.metrics.radon_available) return html + '<p class="status-warning">Radon is not installed. Complexity metrics unavailable.</p>';
    return html + `<p class="status-ok">Average Complexity: ${(State.metrics.average_complexity || 0).toFixed(2)}</p>`;
}

function generateGhostTable() {
    let html = _dlBar('ghost', 'Ghost Files');
    if (!State.ghostFiles || !State.ghostFiles.length) return html + '<p class="status-ok">No ghost files found.</p>';
    
    html += `<table><thead><tr><th>File Path</th></tr></thead><tbody>`;
    State.ghostFiles.forEach(f => {
        html += `<tr><td style="color:#fca5a5;font-family:monospace;font-size:0.8rem;">${f}</td></tr>`;
    });
    html += `</tbody></table>`;
    return html;
}

function generateCyclesTable() {
    let html = _dlBar('cycles', 'Circular Dependencies');
    if (!State.cycles || !State.cycles.length) return html + '<p class="status-ok">No circular dependencies found.</p>';
    
    html += `<div>`;
    State.cycles.forEach(c => {
        html += `<div class="cycle-item">${(c.cycle || []).join(' → ')}</div>`;
    });
    html += `</div>`;
    return html;
}

function generateDependencyTable() {
    let html = _dlBar('dependencies', 'Dependency Scan (PyPI / OSV)');
    if (!State.depScan || !State.depScan.packages) return html + '<p class="status-warning">Dependency scan data not available.</p>';
    
    const pkgs = State.depScan.packages || [];
    if (!pkgs.length) return html + '<p class="status-ok">No vulnerable packages found.</p>';
    
    html += `<div>`;
    pkgs.forEach(pkg => {
        const hasVuln = pkg.vulnerabilities && pkg.vulnerabilities.length > 0;
        const statusClass = hasVuln ? 'dep-vuln' : 'dep-ok';
        html += `<div class="dep-card">
            <div>
                <div class="dep-name">${pkg.name} ${pkg.version || ''}</div>
                <div class="dep-meta">${hasVuln ? pkg.vulnerabilities[0].id : 'No known vulnerabilities'}</div>
            </div>
            <div class="dep-badges">
                <span class="dep-badge ${statusClass}">${hasVuln ? 'VULNERABLE' : 'SECURE'}</span>
            </div>
        </div>`;
    });
    html += `</div>`;
    return html;
}

function severityColor(sev) {
    return sev === 'CRITICAL' ? '#dc2626'
         : sev === 'HIGH'     ? '#ea580c'
         : sev === 'MEDIUM'   ? '#ca8a04'
         : '#16a34a';
}
function statusIcon(status) { return status === 'PASS' ? '✔' : status === 'FAIL' ? '❌' : '⚠️'; }
function statusColor(status) { return status === 'PASS' ? '#16a34a' : status === 'FAIL' ? '#dc2626' : '#d97706'; }

function getCheckExplanation(checkId) {
    const explanations = {
        'hardcoded_secret_key': 'The SECRET_KEY must never be hardcoded in your source files.',
        'debug_true': 'Running Django with DEBUG=True in production is extremely dangerous.',
        'missing_allowed_hosts': 'When DEBUG is False, Django requires ALLOWED_HOSTS to be set.',
        'secure_browser_xss_filter': 'Enables X-XSS-Protection header in modern browsers.',
        'secure_content_type_nosniff': 'Without this setting, browsers may ignore Content-Type.',
        'x_frame_options_deny': 'Protects against Clickjacking attacks.',
        'csrf_cookie_secure': 'Ensures CSRF cookie is only sent over HTTPS.',
        'session_cookie_secure': 'Ensures Session cookie is only sent over HTTPS.',
    };
    return explanations[checkId] || 'Review your configuration for security best practices.';
}

function generateConfigHealthTab() {
    const cfg = State.configHealth || {};
    const checks = cfg.checks || [];
    const summary = cfg.summary || {};
    const folderName = cfg.config_folder_name || 'config';

    if (!checks.length) return '<p class="status-warning">No config health data available.</p>';

    let html = `<div><h3 style="color:#f1f5f9;margin-bottom:12px;">Kernel Configuration (${folderName}/)</h3>`;
    const issues = checks.filter(c => c.status !== 'PASS');
    
    if (issues.length === 0) {
        html += `<div style="padding: 12px; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); border-radius: 8px; color: #34d399; font-size: 0.9rem; display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.2rem;">✨</span> All configuration checks passed successfully.
        </div>`;
    } else {
        html += `<div style="display: grid; gap: 12px;">`;
        issues.forEach((c, i) => {
            const sc = statusColor(c.status);
            const si = statusIcon(c.status);
            const sevC = severityColor(c.severity || 'LOW');
            const explanation = getCheckExplanation(c.check);
            html += `<div style="background: rgba(15,23,42,0.8); border: 1px solid #334155; border-left: 3px solid ${sc}; border-radius: 8px;">
                <div onclick="const el = document.getElementById('chk-exp-${i}'); el.style.display = el.style.display === 'none' ? 'block' : 'none'" style="padding: 12px; cursor: pointer; display: flex; flex-direction: column;">
                    <div style="display: flex; gap: 10px; align-items: flex-start;">
                        <span style="color: ${sc}; font-size: 1rem;">${si}</span>
                        <span style="color: #e2e8f0; font-size: 0.85rem; font-weight: 600;">${c.message || ''}</span>
                        <span style="margin-left:auto; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 800; background: ${sevC}22; color: ${sevC};">${c.severity || 'LOW'}</span>
                    </div>
                </div>
                <div id="chk-exp-${i}" style="display: none; padding: 0 12px 12px 12px; font-size: 0.8rem; color: #94a3b8; border-top: 1px dashed #334155; margin-top:8px;">
                    <strong style="color: #cbd5e1;">Recommendation:</strong><br>
                    <span style="display:inline-block; margin-top: 4px;">${explanation}</span>
                </div>
            </div>`;
        });
        html += `</div>`;
    }
    html += `</div>`;
    return html;
}

function couplingColor(count) {
    if (count >= 7) return '#450a0a';
    if (count >= 4) return '#7c2d12';
    if (count >= 1) return '#713f12';
    return '#1e3a2f';
}
function couplingBorder(count) {
    if (count >= 7) return '#991b1b';
    if (count >= 4) return '#ea580c';
    if (count >= 1) return '#f59e0b';
    return '#14532d';
}

window.showCouplingDrilldown = function(src, tgt) {
    const panel = document.getElementById('coupling-drilldown');
    if (!panel) return;
    
    const apps = (State.couplingMatrix && State.couplingMatrix.apps) || [];
    const matrix = (State.couplingMatrix && State.couplingMatrix.matrix) || [];
    const srcIdx = apps.indexOf(src);
    const tgtIdx = apps.indexOf(tgt);
    const count = (matrix[srcIdx] || [])[tgtIdx] || 0;
    
    const key = `${src}|${tgt}`;
    const details = (((State.couplingMatrix || {}).details || {})[key]) || [];
    
    if (!count) {
        panel.innerHTML = `<div style="padding:14px 16px;border:1px dashed #334155;border-radius:12px;color:#94a3b8;">
            <strong>${src}</strong> → <strong>${tgt}</strong>: no coupling violations.
        </div>`;
        return;
    }
    
    const rows = details.map(d => `<tr>
        <td style="color:#e2e8f0;">${d.module_path || ''}</td>
        <td>${d.violation_type || ''}</td>
        <td>${d.penalty_points || 0}</td>
    </tr>`).join('');
    
    panel.innerHTML = `<div style="padding:14px 16px;border:1px solid #334155;border-radius:12px;background:rgba(15,23,42,.55);">
        <div style="font-weight:700;color:#f1f5f9;margin-bottom:10px;">${src} → ${tgt} (${count} violations)</div>
        <table>
            <thead><tr><th>Module Path</th><th>Violation Type</th><th>Penalty</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>
    </div>`;
}

function generateCouplingMapTab() {
    const apps = (State.couplingMatrix && State.couplingMatrix.apps) || [];
    const matrix = (State.couplingMatrix && State.couplingMatrix.matrix) || [];
    const allowed = (State.couplingMatrix && State.couplingMatrix.allowed) || [];
    
    if (!apps.length) return '<p class="status-warning" style="padding:16px;">No coupling data available.</p>';
    
    const summary = (State.couplingMatrix && State.couplingMatrix.summary) || {};
    const totalPairs = summary.possible_pairs || (apps.length * (apps.length - 1));
    const hitPairs = summary.violation_pairs || 0;
    
    let html = `<div style="margin-bottom:12px;color:#94a3b8;font-size:.86rem;">${hitPairs} of ${totalPairs} possible app pairs have coupling violations.</div>`;
    html += `<div style="overflow:auto;border:1px solid #334155;border-radius:12px;">
        <table style="min-width:100%;border-collapse:collapse;">
            <thead><tr><th></th>${apps.map(app => `<th style="text-transform:uppercase;font-size:.72rem;">${app}</th>`).join('')}</tr></thead>
            <tbody>`;
            
    apps.forEach((src, i) => {
        html += `<tr><th style="text-transform:uppercase;font-size:.72rem;white-space:nowrap;">${src}</th>`;
        apps.forEach((tgt, j) => {
            const count = (matrix[i] || [])[j] || 0;
            const allowedCount = (allowed[i] || [])[j] || 0;
            const clickable = i !== j;
            html += `<td onclick="${clickable ? `showCouplingDrilldown('${src}','${tgt}')` : ''}" style="background:${couplingColor(count)};color:#f8fafc;text-align:center;cursor:${clickable ? 'pointer' : 'default'};border:1px solid ${couplingBorder(count)};min-width:72px;font-weight:700;">
                <div>${count}</div>
                <div style="font-size:.65rem;color:#d1fae5;">${allowedCount} allowed</div>
            </td>`;
        });
        html += '</tr>';
    });
    
    html += `</tbody></table></div><div id="coupling-drilldown" style="margin-top:14px;"></div>`;
    return html;
}
