#!/usr/bin/env python3
"""
HTML Report Generator
=====================
Generates interactive HTML dashboard with vis-network graph visualization.
"""

import json
import os
from string import Template
from datetime import datetime
from typing import Dict, Any, List
from .assets import get_vis_js


class EnhancedAuditReport:
    def __init__(self, audit_data: Dict[str, Any]):
        self.data = audit_data
        self.timestamp = datetime.now()
    
    def _render_change_summary(self) -> str:
        # Render a client-side container that will be populated from the
        # injected `changeSummary` JS object so the banner is dynamic in-browser.
        return '<div id="change-summary-container"></div>'

    def _safe_json(self, data: Any) -> str:
        s = json.dumps(data, default=str)
        # Escape backticks: AI recommendations use markdown backticks for code
        # which break JS template literals when embedded as const values.
        return (s.replace("<", "\\u003c")
                 .replace(">", "\\u003e")
                 .replace("&", "\\u0026")
                 .replace("`", "\\u0060"))

    def _render_fix_queue_banner(self) -> str:
        fix_queue = (self.data.get('metadata', {}) or {}).get('fix_queue', {}) or {}
        count = int(fix_queue.get('reappeared_done_count', 0) or 0)
        if count <= 0:
            return ''
        ids = fix_queue.get('reappeared_done', []) or []
        sample = ', '.join(ids[:3])
        more = f" +{len(ids) - 3} more" if len(ids) > 3 else ''
        return (
            '<div class="fix-queue-banner" style="margin:14px 0 18px;padding:12px 16px;'
            'border:1px solid #7f1d1d;border-left:4px solid #ef4444;border-radius:12px;'
            'background:rgba(127,29,29,.18);color:#fca5a5;font-weight:600;">'
            f'⚠ {count} recommendation(s) marked done reappeared this run'
            f'{f" — {sample}{more}" if sample else ""}'
            '</div>'
        )

    def _inject_phase4_effort_support(self, template_content: str) -> str:
        """Inject phase 4 effort controls into the dashboard template."""
        effort_helpers = r"""
const EFFORT_BUCKETS = {
    quick: { rank: 0, label: 'Quick (< 1hr)', values: ['< 1 hour', '<1 hour', 'quick', 'small < 1h', 's'] },
    half_day: { rank: 1, label: 'Half day', values: ['half day', 'half-day', '1/2 day', 'm'] },
    multi_day: { rank: 2, label: 'Multi-day', values: ['1-2 days', '1 - 2 days', 'multi-day', 'l'] },
    major: { rank: 3, label: 'Major', values: ['1 week', 'major refactor (2+ weeks)', 'major', 'xl'] },
    unknown: { rank: 99, label: 'Unknown', values: ['unknown', ''] },
};
function normalizeFixEffort(raw) {
    const value = String(raw || 'unknown').trim().toLowerCase();
    for (const [key, bucket] of Object.entries(EFFORT_BUCKETS)) {
        if (bucket.values.includes(value)) return key;
    }
    if (value.includes('1 week') || value.includes('2+ weeks') || value.includes('major')) return 'major';
    if (value.includes('1-2 days') || value.includes('multi')) return 'multi_day';
    if (value.includes('half')) return 'half_day';
    if (value.includes('1 hour') || value.startsWith('<') || value.includes('quick') || value === 's') return 'quick';
    if (value === 'm') return 'half_day';
    if (value === 'l') return 'multi_day';
    if (value === 'xl') return 'major';
    return 'unknown';
}
function fixEffortRank(raw) {
    const bucket = normalizeFixEffort(raw);
    return (EFFORT_BUCKETS[bucket] || EFFORT_BUCKETS.unknown).rank;
}
function fixEffortLabel(raw) {
    const bucket = normalizeFixEffort(raw);
    return (EFFORT_BUCKETS[bucket] || EFFORT_BUCKETS.unknown).label;
}
function fixEffortColor(raw) {
    const bucket = normalizeFixEffort(raw);
    return bucket === 'quick' ? '#10b981' : bucket === 'half_day' ? '#3b82f6' : bucket === 'multi_day' ? '#f59e0b' : bucket === 'major' ? '#ef4444' : '#94a3b8';
}
function renderEffortSummary() {
    const el = document.getElementById('effort-summary');
    if (!el) return;
    const counts = { quick: 0, half_day: 0, multi_day: 0, major: 0, unknown: 0 };
    (recommendations || []).forEach(r => {
        const bucket = normalizeFixEffort(r.fix_effort || r.effort || 'unknown');
        counts[bucket] = (counts[bucket] || 0) + 1;
    });
    const current = window.__effortFilter || '';
    const bits = [
        ['quick', `Quick (< 1hr): ${counts.quick}`],
        ['half_day', `Half day: ${counts.half_day}`],
        ['multi_day', `Multi-day: ${counts.multi_day}`],
        ['major', `Major: ${counts.major}`],
    ];
    const unknown = counts.unknown ? `<span style="color:#64748b;font-size:.78rem;">Unknown: ${counts.unknown}</span>` : '';
    el.innerHTML = `<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:0 0 10px;">
        ${bits.map(([key, label]) => `<button type="button" class="status-btn${current === key ? ' active' : ''}" data-effort="${key}" style="padding:5px 10px;">${label}</button>`).join('')}
        ${unknown}
    </div>`;
    el.querySelectorAll('[data-effort]').forEach(btn => {
        btn.addEventListener('click', () => filterByEffort(btn.dataset.effort || ''));
    });
}
function filterByEffort(effortKey) {
    window.__effortFilter = effortKey || '';
    const select = document.getElementById('rec-sort');
    if (select && !select.value) {
        select.value = 'effort-asc';
    }
    filterRecommendations();
}
function applyRecommendationSort(cards) {
    const sortEl = document.getElementById('rec-sort');
    const mode = (sortEl && sortEl.value) || '';
    if (mode !== 'effort-asc' || !cards.length) return;
    const parent = cards[0].parentElement;
    if (!parent) return;
    const ordered = Array.from(cards).sort((a, b) => {
        const ar = Number(a.dataset.effortRank || 99);
        const br = Number(b.dataset.effortRank || 99);
        if (ar !== br) return ar - br;
        return (a.dataset.priority || '').localeCompare(b.dataset.priority || '');
    });
    ordered.forEach(card => parent.appendChild(card));
}
"""
        template_content = template_content.replace(
            'const changeSummary    = ${change_summary_json};\n',
            'const changeSummary    = ${change_summary_json};\n' + effort_helpers + '\n'
        )
        template_content = template_content.replace(
            '<div id="recommendations" class="tab-content">\n',
            '<div id="recommendations" class="tab-content">\n'
            '            <div id="effort-summary" style="margin-bottom:12px;"></div>\n'
        )
        template_content = template_content.replace(
            '</select>\n                <span id="rec-counter"',
            '</select>\n                <select id="rec-sort" style="padding: 8px 12px; background: rgba(15, 23, 42, 0.5); border: 1px solid #475569; border-radius: 6px; color: #e2e8f0; font-size: 0.9rem;">\n'
            '                    <option value="">Default order</option>\n'
            '                    <option value="effort-asc">Sort by effort (quick first)</option>\n'
            '                </select>\n                <span id="rec-counter"'
        )
        template_content = template_content.replace(
            '        const effort = r.effort || \'\';\n',
            '        const fixEffort = r.fix_effort || r.effort || \'unknown\';\n'
            '        const effort = r.effort || \'\';\n'
        )
        template_content = template_content.replace(
            'data-fix-status="$${fixStatus}" data-confidence="$${confidence}"',
            'data-fix-status="$${fixStatus}" data-confidence="$${confidence}" data-fix-effort="$${fixEffort}" data-effort-rank="$${fixEffortRank(fixEffort)}"'
        )
        template_content = template_content.replace(
            'effortColor[effort]||\'#94a3b8\'',
            'fixEffortColor(fixEffort)'
        )
        template_content = template_content.replace(
            'effortLabel[effort]||effort',
            'fixEffortLabel(fixEffort)'
        )
        template_content = template_content.replace(
            '        const confidence = Math.max(1, Math.min(10, Number(r.confidence ?? 5) || 5));\n',
            '        const confidence = Math.max(1, Math.min(10, Number(r.confidence ?? 5) || 5));\n'
            '        const gitBase = (gitContext || {}).github_base || \'\';\n'
            '        const gitBranch = (gitContext || {}).branch || \'main\';\n'
            '        const primaryModule = (r.affected_modules || [])[0] || r.file_path || \'\';\n'
            '        const relativePath = primaryModule\n'
            '            ? (primaryModule.includes(\'/\') || primaryModule.endsWith(\'.py\')\n'
            '                ? primaryModule.replace(/^\\/+/, \'\')\n'
            '                : primaryModule.replace(/\\./g, \'/\') + \'.py\')\n'
            '            : \'\';\n'
            '        const linkLine = Number(r.line_number || r.line || 0) || 0;\n'
            '        const githubLink = gitBase && relativePath\n'
            '            ? gitBase + \'/blob/\' + gitBranch + \'/\' + relativePath + (linkLine ? \'#L\' + linkLine : \'\')\n'
            '            : \'\';\n'
        )
        template_content = template_content.replace(
            '            </div>`;\n'
            '        }\n'
            '\n'
            '        /* Upgrade Advisor fields */\n',
            '            </div>`;\n'
            '        }\n'
            '        if (githubLink) {\n'
            '            html += `<div style="margin-top:8px;font-size:.76rem;">\n'
            '                <a href="$${githubLink}" target="_blank" rel="noopener" style="color:#7dd3fc;text-decoration:none;">View on GitHub</a>\n'
            '            </div>`;\n'
            '        }\n'
            '\n'
            '        /* Upgrade Advisor fields */\n'
        )
        template_content = template_content.replace(
            'function persistFixQueueState(recId, status) {\n'
            '    const current = fixQueueState[recId] || {};\n'
            '    fixQueueState = Object.assign({}, fixQueueState, {\n'
            '        [recId]: Object.assign({}, current, {\n'
            '            status,\n'
            '            updated_at: new Date().toISOString(),\n'
            '        }),\n'
            '    });\n'
            '    try {\n'
            '        localStorage.setItem(FIX_QUEUE_STORAGE_KEY, JSON.stringify(fixQueueState));\n'
            '    } catch (err) {\n'
            '        // Local storage is best-effort only.\n'
            '    }\n'
            '}\n',
            'function persistFixQueueState(recId, status) {\n'
            '    const current = fixQueueState[recId] || {};\n'
            '    fixQueueState = Object.assign({}, fixQueueState, {\n'
            '        [recId]: Object.assign({}, current, {\n'
            '            status,\n'
            '            updated_at: new Date().toISOString(),\n'
            '        }),\n'
            '    });\n'
            '    try {\n'
            '        localStorage.setItem(FIX_QUEUE_STORAGE_KEY, JSON.stringify(fixQueueState));\n'
            '    } catch (err) {\n'
            '        // Local storage is best-effort only.\n'
            '    }\n'
            '    if (USE_FIX_QUEUE_SERVER) {\n'
            "        fetch('/fix-queue', {\n"
            "            method: 'PUT',\n"
            "            headers: { 'Content-Type': 'application/json' },\n"
            "            body: JSON.stringify({ rec_id: recId, status, note: current.notes || '' }),\n"
            '        });\n'
            '    }\n'
            '}\n'
        )
        template_content = template_content.replace(
            '    const priorityVal = prioEl.value;\n',
            '    const priorityVal = prioEl.value;\n'
            '    const sortEl = document.getElementById(\'rec-sort\');\n'
        )
        template_content = template_content.replace(
            '        const matchesPriority = !priorityVal || priority === priorityVal;\n'
            '        const show = matchesSearch && matchesType && matchesPriority;\n',
            '        const matchesPriority = !priorityVal || priority === priorityVal;\n'
            '        const matchesEffort = !effortVal || (card.dataset.fixEffort || \'\').toLowerCase() === effortVal;\n'
            '        const show = matchesSearch && matchesType && matchesPriority && matchesEffort;\n'
        )
        template_content = template_content.replace(
            '    const total = cards.length;\n',
            '    applyRecommendationSort(cards);\n'
            '    const total = cards.length;\n'
        )
        template_content = template_content.replace(
            '    const _ctr = document.getElementById(\'rec-counter\'); if (_ctr) _ctr.textContent = `Showing $${shown} of $${total}`;\n',
            '    const _ctr = document.getElementById(\'rec-counter\'); if (_ctr) _ctr.textContent = `Showing $${shown} of $${total}`;\n'
            '    const summary = document.getElementById(\'effort-summary\');\n'
            '    if (summary) {\n'
            '        summary.querySelectorAll(\'[data-effort]\').forEach(btn => btn.classList.toggle(\'active\', (window.__effortFilter || \'\') === btn.dataset.effort));\n'
            '    }\n'
        )
        template_content = template_content.replace(
            '    if (priorityFilter) priorityFilter.addEventListener(\'change\', filterRecommendations);\n',
            '    if (priorityFilter) priorityFilter.addEventListener(\'change\', filterRecommendations);\n'
            '    const sortSelect = document.getElementById(\'rec-sort\');\n'
            '    if (sortSelect) sortSelect.addEventListener(\'change\', filterRecommendations);\n'
        )
        template_content = template_content.replace(
            'filterRecommendations(); // Phase 4 fix: call AFTER rec-card elements exist\n',
            'filterRecommendations(); // Phase 4 fix: call AFTER rec-card elements exist\n'
            'renderEffortSummary();\n'
            'document.getElementById(\'rec-sort\')?.addEventListener(\'change\', filterRecommendations);\n'
        )
        template_content = template_content.replace(
            'document.querySelectorAll(\'.rec-card\').forEach(refreshFixQueueCard);\n',
            'document.querySelectorAll(\'.rec-card\').forEach(refreshFixQueueCard);\n'
            'renderEffortSummary();\n'
            'hydrateFixQueueState();\n'
        )
        return template_content

    def _inject_phase4_coupling_support(self, template_content: str) -> str:
        """Inject the coupling heatmap tab and drill-down helpers."""
        coupling_helpers = r"""
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
function couplingAppIndex() {
    const apps = (couplingMatrix && couplingMatrix.apps) || [];
    return Object.fromEntries(apps.map((app, idx) => [app, idx]));
}
function couplingDetailsFor(src, tgt) {
    const key = `$${src}|$${tgt}`;
    const details = (((couplingMatrix || {}).details || {})[key]) || [];
    return Array.isArray(details) ? details : [];
}
function couplingRecommendationFor(src, tgt) {
    const rec = (recommendations || []).find(r => {
        const modules = r.affected_modules || [];
        return modules.some(m => m.startsWith(src + '.') || m.startsWith(tgt + '.'));
    });
    return rec || null;
}
function renderCouplingPlan(src, tgt, count) {
    const rec = couplingRecommendationFor(src, tgt);
    const planText = rec && (rec.action || rec.description)
        ? (rec.action || rec.description)
        : 'Consider extracting shared logic to nexus_core.services';
    if (count < 5) return '';
    return `<div style="margin-top:12px;padding:14px 16px;border:1px solid #92400e;border-left:4px solid #f59e0b;border-radius:12px;background:rgba(120,53,15,.16);">
        <div style="font-weight:700;color:#fcd34d;margin-bottom:6px;">Decoupling Plan</div>
        <div style="font-size:.85rem;color:#fbbf24;">$${planText}</div>
    </div>`;
}
function renderCouplingDrilldown(src, tgt) {
    const panel = document.getElementById('coupling-drilldown');
    if (!panel) return;
    const appIndex = couplingAppIndex();
    const srcIdx = appIndex[src];
    const tgtIdx = appIndex[tgt];
    const matrix = (couplingMatrix && couplingMatrix.matrix) || [];
    const count = (matrix[srcIdx] || [])[tgtIdx] || 0;
    const allowed = (couplingMatrix && couplingMatrix.allowed) || [];
    const allowedCount = (allowed[srcIdx] || [])[tgtIdx] || 0;
    const details = couplingDetailsFor(src, tgt);
    if (!count) {
        panel.innerHTML = `<div style="padding:14px 16px;border:1px dashed #334155;border-radius:12px;color:#94a3b8;">
            <strong>$${src}</strong> → <strong>$${tgt}</strong>: no coupling violations.
        </div>`;
        return;
    }
    const rows = details.map(d => `<tr>
        <td style="color:#e2e8f0;">$${d.module_path || ''}</td>
        <td>$${d.violation_type || ''}</td>
        <td>$${d.penalty_points || 0}</td>
    </tr>`).join('');
    panel.innerHTML = `<div style="padding:14px 16px;border:1px solid #334155;border-radius:12px;background:rgba(15,23,42,.55);">
        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;">
            <div style="font-weight:700;color:#f1f5f9;">$${src} → $${tgt}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <span class="badge badge-high">$${count} violation$${count === 1 ? '' : 's'}</span>
                <span class="badge badge-low">$${allowedCount} allowed</span>
            </div>
        </div>
        <table>
            <thead><tr><th>Module Path</th><th>Violation Type</th><th>Penalty</th></tr></thead>
            <tbody>$${rows}</tbody>
        </table>
        $${renderCouplingPlan(src, tgt, count)}
    </div>`;
}
function generateCouplingMapTab() {
    const apps = (couplingMatrix && couplingMatrix.apps) || [];
    const matrix = (couplingMatrix && couplingMatrix.matrix) || [];
    const allowed = (couplingMatrix && couplingMatrix.allowed) || [];
    if (!apps.length) {
        return '<p style="padding:16px;color:#94a3b8;">No coupling data available.</p>';
    }
    const summary = (couplingMatrix && couplingMatrix.summary) || {};
    const totalPairs = summary.possible_pairs || (apps.length * (apps.length - 1));
    const hitPairs = summary.violation_pairs || 0;
    let html = `<div style="margin-bottom:12px;color:#94a3b8;font-size:.86rem;">$${hitPairs} of $${totalPairs} possible app pairs have coupling violations.</div>`;
    html += `<div style="overflow:auto;border:1px solid #334155;border-radius:12px;">
        <table style="min-width:100%;border-collapse:collapse;">
            <thead><tr><th></th>$${apps.map(app => `<th style="text-transform:uppercase;font-size:.72rem;">$${app}</th>`).join('')}</tr></thead>
            <tbody>`;
    apps.forEach((src, i) => {
        html += `<tr><th style="text-transform:uppercase;font-size:.72rem;white-space:nowrap;">$${src}</th>`;
        apps.forEach((tgt, j) => {
            const count = (matrix[i] || [])[j] || 0;
            const allowedCount = (allowed[i] || [])[j] || 0;
            const clickable = i !== j;
            html += `<td data-src-app="$${src}" data-tgt-app="$${tgt}" onclick="$${clickable ? 'showCouplingDrilldown(this)' : ''}" style="background:$${couplingColor(count)};color:#f8fafc;text-align:center;cursor:$${clickable ? 'pointer' : 'default'};border:1px solid $${couplingBorder(count)};min-width:72px;font-weight:700;">
                <div>$${count}</div>
                <div style="font-size:.65rem;color:#d1fae5;">$${allowedCount} allowed</div>
            </td>`;
        });
        html += '</tr>';
    });
    html += `</tbody></table></div>
    <div id="coupling-drilldown" style="margin-top:14px;"></div>`;
    return html;
}
function showCouplingDrilldown(cell) {
    if (!cell) return;
    renderCouplingDrilldown(cell.dataset.srcApp || '', cell.dataset.tgtApp || '');
}
"""
        template_content = template_content.replace(
            'const fixQueueData     = ${fix_queue_json};\n\n',
            'const fixQueueData     = ${fix_queue_json};\n'
            'const couplingMatrix   = ${coupling_matrix_json};\n'
            'const gitContext       = ${git_context_json};\n\n'
        )
        template_content = template_content.replace(
            'function getFixQueueState() {\n',
            coupling_helpers + '\nfunction getFixQueueState() {\n'
        )
        template_content = template_content.replace(
            "const FIX_QUEUE_STORAGE_KEY = 'nexus-audit-fix-queue';\n",
            "const FIX_QUEUE_STORAGE_KEY = 'nexus-audit-fix-queue';\n"
            "const USE_FIX_QUEUE_SERVER = window.location.hostname === 'localhost';\n"
        )
        template_content = template_content.replace(
            'let fixQueueState = getFixQueueState();\n',
            'let fixQueueState = getFixQueueState();\n'
            'function hydrateFixQueueState() {\n'
            '    if (!USE_FIX_QUEUE_SERVER) return;\n'
            "    fetch('/fix-queue')\n"
            '        .then(resp => resp.ok ? resp.json() : null)\n'
            '        .then(data => {\n'
            '            if (!data || typeof data !== \'object\') return;\n'
            '            fixQueueState = Object.assign({}, fixQueueState, data);\n'
            '            document.querySelectorAll(\'.rec-card\').forEach(refreshFixQueueCard);\n'
            '        });\n'
            '}\n'
        )
        template_content = template_content.replace(
            '            <button class="tab" onclick="showTab(\'trends\')">📈 Trends</button>\n'
            '            <button class="tab" onclick="showTab(\'recommendations\')">💡 Recommendations</button>\n',
            '            <button class="tab" onclick="showTab(\'trends\')">📈 Trends</button>\n'
            '            <button class="tab" onclick="showTab(\'coupling-map\')">🔥 Coupling Map</button>\n'
            '            <button class="tab" onclick="showTab(\'recommendations\')">💡 Recommendations</button>\n'
        )
        template_content = template_content.replace(
            '        <div id="trends"          class="tab-content"></div>\n'
            '        <div id="recommendations" class="tab-content">\n',
            '        <div id="trends"          class="tab-content"></div>\n'
            '        <div id="coupling-map"    class="tab-content"></div>\n'
            '        <div id="recommendations" class="tab-content">\n'
        )
        template_content = template_content.replace(
            'document.getElementById(\'trends\').innerHTML          = generateTrendsTab();\n',
            'document.getElementById(\'trends\').innerHTML          = generateTrendsTab();\n'
            'document.getElementById(\'coupling-map\').innerHTML    = generateCouplingMapTab();\n'
        )
        return template_content

    def _inject_config_health_tab(self, template_content: str) -> str:
        """Inject the Config Health tab button, content div, and JS renderer."""
        # 1. Inject JS data variable after coupling_matrix
        template_content = template_content.replace(
            'const couplingMatrix   = ${coupling_matrix_json};\n'
            'const gitContext       = ${git_context_json};\n\n',
            'const couplingMatrix   = ${coupling_matrix_json};\n'
            'const gitContext       = ${git_context_json};\n'
            'const configHealth     = ${config_health_json};\n\n'
        )

        # 2. Inject JS render function alongside coupling helpers
        config_health_js = r"""
function severityColor(sev) {
    return sev === 'CRITICAL' ? '#dc2626'
         : sev === 'HIGH'     ? '#ea580c'
         : sev === 'MEDIUM'   ? '#ca8a04'
         : '#16a34a';
}
function statusIcon(status) {
    return status === 'PASS' ? '✔' : status === 'FAIL' ? '❌' : '⚠️';
}
function statusColor(status) {
    return status === 'PASS' ? '#16a34a' : status === 'FAIL' ? '#dc2626' : '#d97706';
}
function generateConfigHealthTab() {
    const cfg = configHealth || {};
    const checks = cfg.checks || [];
    const summary = cfg.summary || {};
    const score = summary.score ?? 0;
    const folderName = cfg.config_folder_name || 'config';

    if (!checks.length) {
        return '<p style="padding:16px;color:#94a3b8;">No config health data available.</p>';
    }

    const scoreColor = score >= 90 ? '#10b981' : score >= 70 ? '#f59e0b' : '#ef4444';
    const bar = Math.round(score / 10);

    let html = `
    <div style="margin-bottom:20px;padding:20px;background:rgba(15,23,42,.6);border:1px solid #334155;border-radius:14px;">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
            <div>
                <div style="font-size:1.05rem;font-weight:700;color:#f1f5f9;">⚙️ ${folderName}/</div>
                <div style="font-size:.82rem;color:#94a3b8;margin-top:4px;">Django Project Config Folder &mdash; Not an app, but audited separately</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2rem;font-weight:800;color:${scoreColor};">${score}%</div>
                <div style="font-size:.75rem;color:#64748b;">Config Health Score</div>
            </div>
        </div>
        <div style="margin-top:12px;background:#1e293b;border-radius:8px;height:10px;overflow:hidden;">
            <div style="width:${score}%;height:100%;background:${scoreColor};border-radius:8px;transition:width .4s;"></div>
        </div>
        <div style="display:flex;gap:16px;margin-top:12px;flex-wrap:wrap;font-size:.82rem;">
            <span style="color:#10b981;">✔ ${summary.passed || 0} passed</span>
            <span style="color:#f59e0b;">⚠️ ${summary.warnings || 0} warnings</span>
            <span style="color:#ef4444;">❌ ${summary.failures || 0} failures</span>
            <span style="color:#94a3b8;">${summary.total || 0} total checks</span>
        </div>
    </div>`;

    // Group checks by file
    const groups = {};
    checks.forEach(c => {
        const key = c.check || '';
        let group = 'General';
        if (key.includes('secret') || key.includes('debug') || key.includes('allowed_host') ||
            key.includes('middleware') || key.includes('encryption') || key.includes('session') ||
            key.includes('csrf') || key.includes('secure_ssl') || key.includes('installed_app')) {
            group = 'settings.py';
        } else if (key.includes('asgi')) {
            group = 'asgi.py';
        } else if (key.includes('wsgi')) {
            group = 'wsgi.py';
        } else if (key.includes('urls') || key.includes('url')) {
            group = 'urls.py';
        } else if (key.includes('celery')) {
            group = 'celery.py';
        } else if (key.includes('config_dir') || key.includes('unexpected')) {
            group = 'General';
        }
        if (!groups[group]) groups[group] = [];
        groups[group].push(c);
    });

    const fileOrder = ['General', 'settings.py', 'urls.py', 'asgi.py', 'wsgi.py', 'celery.py'];
    fileOrder.forEach(groupName => {
        const items = groups[groupName];
        if (!items || !items.length) return;

        const hasIssues = items.some(c => c.status !== 'PASS');
        const groupIcon = groupName === 'settings.py' ? '🔐'
            : groupName === 'urls.py'     ? '🔗'
            : groupName === 'asgi.py'     ? '📡'
            : groupName === 'wsgi.py'     ? '📡'
            : groupName === 'celery.py'   ? '⏰'
            : '📂';

        html += `<div style="margin-bottom:14px;border:1px solid ${hasIssues ? '#475569' : '#1e3a2f'};border-radius:12px;overflow:hidden;">
            <div style="padding:10px 16px;background:rgba(15,23,42,.5);font-weight:700;color:#e2e8f0;font-size:.88rem;">
                ${groupIcon} ${groupName}
            </div>`;

        items.forEach(c => {
            if (c.status === 'PASS') return; // Only show non-passing checks in detail
            const sc = statusColor(c.status);
            const si = statusIcon(c.status);
            const sevC = severityColor(c.severity || 'LOW');
            html += `<div style="padding:10px 16px;border-top:1px solid #1e293b;display:flex;gap:12px;align-items:flex-start;">
                <span style="color:${sc};font-size:1rem;flex-shrink:0;margin-top:1px;">${si}</span>
                <div style="flex:1;min-width:0;">
                    <span style="color:#e2e8f0;font-size:.86rem;">${c.message || ''}</span>
                </div>
                <span style="flex-shrink:0;padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:700;background:rgba(0,0,0,.3);color:${sevC};border:1px solid ${sevC};">${c.severity || ''}</span>
            </div>`;
        });

        const passedCount = items.filter(c => c.status === 'PASS').length;
        if (passedCount > 0) {
            html += `<div style="padding:8px 16px;border-top:1px solid #1e293b;color:#475569;font-size:.78rem;">✔ ${passedCount} check${passedCount === 1 ? '' : 's'} passed for ${groupName}</div>`;
        }

        html += '</div>';
    });

    return html;
}
""";
        template_content = template_content.replace(
            'function getFixQueueState() {\n',
            config_health_js + '\nfunction getFixQueueState() {\n'
        )

        # 3. Inject tab button (after Coupling Map)
        template_content = template_content.replace(
            '            <button class="tab" onclick="showTab(\'coupling-map\')">🔥 Coupling Map</button>\n'
            '            <button class="tab" onclick="showTab(\'recommendations\')">💡 Recommendations</button>\n',
            '            <button class="tab" onclick="showTab(\'coupling-map\')">🔥 Coupling Map</button>\n'
            '            <button class="tab" onclick="showTab(\'config-health\')">⚙️ Config Health</button>\n'
            '            <button class="tab" onclick="showTab(\'recommendations\')">💡 Recommendations</button>\n'
        )

        # 4. Inject content div (after coupling-map div)
        template_content = template_content.replace(
            '        <div id="coupling-map"    class="tab-content"></div>\n'
            '        <div id="recommendations" class="tab-content">\n',
            '        <div id="coupling-map"    class="tab-content"></div>\n'
            '        <div id="config-health"   class="tab-content"></div>\n'
            '        <div id="recommendations" class="tab-content">\n'
        )

        # 5. Inject render call (after coupling-map render call)
        template_content = template_content.replace(
            "document.getElementById('coupling-map').innerHTML    = generateCouplingMapTab();\n",
            "document.getElementById('coupling-map').innerHTML    = generateCouplingMapTab();\n"
            "document.getElementById('config-health').innerHTML   = generateConfigHealthTab();\n"
        )

        return template_content

    def generate_html_dashboard(self) -> str:
        ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        trends_js = r"""
function generateTrendsTab() {
    const labels = timelineData.labels || [];
    const fleet = timelineData.fleet_avg || [];
    const appsSeries = timelineData.apps || {};
    if (labels.length < 2) {
        return '<p class="status-ok" style="padding:16px;">Run at least twice to see trends.</p>'
    }
    const appNames = Object.keys(appsSeries).sort();
    const palette = ['#38bdf8', '#a78bfa', '#f59e0b', '#10b981', '#f97316', '#ec4899', '#22c55e', '#eab308'];
    const legend = appNames.slice(0, 8).map((app, idx) => {
        return `<span style="display:inline-flex;align-items:center;gap:6px;margin-right:10px;"><span style="width:10px;height:10px;border-radius:999px;background:${palette[idx % palette.length]};display:inline-block;"></span>${app.toUpperCase()}</span>`;
    }).join('');
    return `<div style="margin-bottom:10px;color:#94a3b8;font-size:.8rem;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;">${legend}<span style="color:#e2e8f0;">Fleet avg = dashed white line</span></div>
    <canvas id="trends-canvas" style="width:100%;height:420px;background:rgba(15,23,42,.55);border:1px solid #334155;border-radius:12px;"></canvas>
    <div style="font-size:.78rem;color:#64748b;margin-top:8px;">Y-axis spans 0–100. Each app line shows its score over the last ${labels.length} runs.</div>`;
}

function drawTrendsChart() {
    const canvas = document.getElementById('trends-canvas');
    if (!canvas) return;
    const labels = timelineData.labels || [];
    const fleet = timelineData.fleet_avg || [];
    const appsSeries = timelineData.apps || {};
    const appNames = Object.keys(appsSeries).sort();
    if (labels.length < 2) return;
    const rect = canvas.getBoundingClientRect();
    const cssW = Math.max(rect.width, 700);
    const cssH = 420;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(cssW * dpr);
    canvas.height = Math.floor(cssH * dpr);
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);
    const pad = { left: 52, right: 18, top: 18, bottom: 38 };
    const plotW = cssW - pad.left - pad.right;
    const plotH = cssH - pad.top - pad.bottom;
    const xAt = (idx) => pad.left + (labels.length === 1 ? plotW / 2 : (idx / (labels.length - 1)) * plotW);
    const yAt = (val) => pad.top + (1 - (Math.max(0, Math.min(100, val)) / 100)) * plotH;
    ctx.fillStyle = 'rgba(15,23,42,.15)';
    ctx.fillRect(0, 0, cssW, cssH);
    ctx.strokeStyle = 'rgba(51,65,85,.8)';
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px sans-serif';
    ctx.lineWidth = 1;
    for (let v = 0; v <= 100; v += 20) {
        const y = yAt(v);
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(cssW - pad.right, y);
        ctx.stroke();
        ctx.fillText(String(v), 12, y + 4);
    }
    ctx.strokeStyle = '#64748b';
    ctx.beginPath();
    ctx.moveTo(pad.left, pad.top);
    ctx.lineTo(pad.left, cssH - pad.bottom);
    ctx.lineTo(cssW - pad.right, cssH - pad.bottom);
    ctx.stroke();
    const palette2 = ['#38bdf8', '#a78bfa', '#f59e0b', '#10b981', '#f97316', '#ec4899', '#22c55e', '#eab308'];
    appNames.forEach((app, idx) => {
        const series = appsSeries[app] || [];
        const color = palette2[idx % palette2.length];
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        let started = false;
        series.forEach((raw, i) => {
            if (raw == null || Number.isNaN(raw)) { started = false; return; }
            const x = xAt(i);
            const y = yAt(Number(raw));
            if (!started) { ctx.moveTo(x, y); started = true; } else { ctx.lineTo(x, y); }
        });
        ctx.stroke();
    });
    ctx.save();
    ctx.setLineDash([8, 6]);
    ctx.strokeStyle = '#f8fafc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    let fleetStarted = false;
    fleet.forEach((raw, i) => {
        if (raw == null || Number.isNaN(raw)) { fleetStarted = false; return; }
        const x = xAt(i);
        const y = yAt(Number(raw));
        if (!fleetStarted) { ctx.moveTo(x, y); fleetStarted = true; } else { ctx.lineTo(x, y); }
    });
    ctx.stroke();
    ctx.restore();
    ctx.fillStyle = '#94a3b8';
    const step = Math.max(1, Math.ceil(labels.length / 8));
    labels.forEach((label, i) => {
        if (i % step !== 0 && i !== labels.length - 1) return;
        const x = xAt(i);
        ctx.save();
        ctx.translate(x, cssH - 12);
        ctx.rotate(-Math.PI / 8);
        ctx.fillText(String(label), 0, 0);
        ctx.restore();
    });
}
"""
        template_path = os.path.join(os.path.dirname(__file__), 'dashboard_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        template_content = self._inject_phase4_effort_support(template_content)
        template_content = self._inject_phase4_coupling_support(template_content)
        template_content = self._inject_config_health_tab(template_content)

        substitutions = {
            'apps_json': self._safe_json(self.data['applications']),
            'modules_json': self._safe_json(self.data['modules']),
            'violations_json': self._safe_json(self.data['violations']),
            'security_json': self._safe_json(self.data['security_findings']),
            'metrics_json': self._safe_json(self.data['metrics']),
            'cycles_json': self._safe_json(self.data['circular_dependencies']),
            'recommendations_json': self._safe_json(self.data.get('recommendations', [])),
            'metadata_json': self._safe_json(self.data['metadata']),
            'ghost_files_json': self._safe_json(self.data['metadata'].get('ghost_files', [])),
            'allowed_comms_json': self._safe_json(self.data.get('allowed_communications', [])),
            'trend_data_json': self._safe_json(self.data['metadata'].get('trend', {})),
            'timeline_json': self._safe_json(self.data.get('timeline', {})),
            'dep_scan_json': self._safe_json(self.data.get('dependency_scan', {})),
            'capabilities_json': self._safe_json(self.data['metadata'].get('capabilities', {})),
            'change_summary_json': self._safe_json(self.data.get('change_summary', {})),
            'fix_queue_json': self._safe_json(self.data.get('fix_queue', {})),
            'coupling_matrix_json': self._safe_json(self.data.get('coupling_matrix', {})),
            'git_context_json': self._safe_json(self.data.get('git_context', {})),
            'config_health_json': self._safe_json(self.data.get('config_health', {})),
            'vis_js_content': get_vis_js(),
            'trends_js': trends_js,
            'ts': ts,
            'project_path': self.data['metadata'].get('project_path', 'Unknown'),
            'change_summary_html': self._render_change_summary(),
            'fix_queue_banner_html': self._render_fix_queue_banner(),
        }
        return Template(template_content).safe_substitute(substitutions)
