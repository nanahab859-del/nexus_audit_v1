import { State } from '../state.js';

export function renderTrendsTab() {
    const el = document.getElementById('trends');
    if (!el) return;
    
    const labels = State.timelineData.labels || [];
    const appsSeries = State.timelineData.apps || {};
    
    if (labels.length < 2) {
        el.innerHTML = '<p class="status-ok" style="padding:16px;">Run at least twice to see trends.</p>';
        return;
    }
    
    const appNames = Object.keys(appsSeries).sort();
    const palette = ['#38bdf8', '#a78bfa', '#f59e0b', '#10b981', '#f97316', '#ec4899', '#22c55e', '#eab308'];
    const legend = appNames.slice(0, 8).map((app, idx) => {
        return `<span style="display:inline-flex;align-items:center;gap:6px;margin-right:10px;"><span style="width:10px;height:10px;border-radius:999px;background:${palette[idx % palette.length]};display:inline-block;"></span>${app.toUpperCase()}</span>`;
    }).join('');
    
    el.innerHTML = `<div style="margin-bottom:10px;color:#94a3b8;font-size:.8rem;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;">${legend}<span style="color:#e2e8f0;">Fleet avg = dashed white line</span></div>
    <canvas id="trends-canvas" style="width:100%;height:420px;background:rgba(15,23,42,.55);border:1px solid #334155;border-radius:12px;"></canvas>
    <div style="font-size:.78rem;color:#64748b;margin-top:8px;">Y-axis spans 0–100. Each app line shows its score over the last ${labels.length} runs.</div>`;
    
    drawTrendsChart();
}

function drawTrendsChart() {
    const canvas = document.getElementById('trends-canvas');
    if (!canvas) return;
    
    const labels = State.timelineData.labels || [];
    const fleet = State.timelineData.fleet_avg || [];
    const appsSeries = State.timelineData.apps || {};
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
