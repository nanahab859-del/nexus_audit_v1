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
            'vis_js_content': get_vis_js(),
            'trends_js': trends_js,
            'ts': ts,
            'project_path': self.data['metadata'].get('project_path', 'Unknown'),
            'change_summary_html': self._render_change_summary(),
            'fix_queue_banner_html': self._render_fix_queue_banner(),
        }
        return Template(template_content).safe_substitute(substitutions)
