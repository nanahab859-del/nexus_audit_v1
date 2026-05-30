import { State, hydrateFixQueueState } from './state.js';

export async function loadAuditData() {
    try {
        const resp = await fetch('/data.json');
        if (!resp.ok) return false;
        const data = await resp.json();
        
        // Populate State
        Object.assign(State, {
            apps: data.applications || {},
            modules: data.modules || {},
            violations: data.violations || [],
            securityFindings: data.security_findings || [],
            metrics: data.metrics || {},
            cycles: data.circular_dependencies || [],
            recommendations: data.recommendations || [],
            metadata: data.metadata || {},
            ghostFiles: (data.metadata || {}).ghost_files || [],
            allowedComms: data.allowed_communications || [],
            trendData: (data.metadata || {}).trend || {},
            timelineData: data.timeline || {},
            depScan: data.dependency_scan || {},
            capabilities: (data.metadata || {}).capabilities || {},
            changeSummary: data.change_summary || {},
            fixQueueData: data.fix_queue || {},
            configHealth: data.config_health || {},
            couplingMatrix: data.coupling_matrix || {},
            gitContext: data.git_context || {}
        });
        
        hydrateFixQueueState();
        return true;
    } catch (e) {
        console.error('Failed to load audit data:', e);
        return false;
    }
}

export function runAuditFromUI() {
    const btn = document.getElementById('run-audit-btn');
    const logWrapper = document.getElementById('audit-log-wrapper');
    const logEl = document.getElementById('audit-log-content');

    if (!btn || !logWrapper || !logEl) return;

    btn.disabled = true;
    btn.textContent = '⏳ Running…';
    logWrapper.style.display = 'block';
    logEl.textContent = '';
    State.auditRunning = true;

    // Collect options
    const payload = {
        scan_deps: document.getElementById('tog-deps')?.checked ?? true,
        scan_security: document.getElementById('tog-security')?.checked ?? true,
        use_ai: document.getElementById('tog-ai')?.checked ?? true,
        deadcode: document.getElementById('tog-deadcode')?.checked ?? true,
        complexity: document.getElementById('tog-complexity')?.checked ?? true,
        ghosts: document.getElementById('tog-ghosts')?.checked ?? true,
        config: document.getElementById('tog-config')?.checked ?? true,
        cycles: document.getElementById('tog-cycles')?.checked ?? true,
        force_rescan: document.getElementById('tog-force-rescan')?.checked ?? false,
        single_app: document.getElementById('tog-app')?.value || null
    };

    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (!data.ok) {
            logEl.textContent = 'Error: ' + (data.error || 'Unknown');
            btn.disabled = false;
            btn.textContent = '▶ Run Audit';
            State.auditRunning = false;
            return;
        }
        
        const es = new EventSource('/api/stream');
        es.addEventListener('log', (e) => {
            try {
                const d = JSON.parse(e.data);
                logEl.textContent += d.message + '\n';
                logWrapper.scrollTop = logWrapper.scrollHeight;
            } catch(err) {}
        });
        es.addEventListener('status', (e) => {
            try {
                const d = JSON.parse(e.data);
                if (d.state === 'completed') {
                    es.close();
                    btn.disabled = false;
                    btn.textContent = '▶ Run Audit';
                    State.auditRunning = false;
                    logEl.textContent += '\n✅ Audit complete — reloading dashboard in 3s…';
                    setTimeout(() => {
                        window.dispatchEvent(new CustomEvent('reload-data'));
                    }, 3000);
                }
            } catch(err) {}
        });
        es.onerror = () => {
            es.close();
            btn.disabled = false;
            btn.textContent = '▶ Run Audit';
            State.auditRunning = false;
        };
    })
    .catch(err => {
        logEl.textContent = 'Network error: ' + err;
        btn.disabled = false;
        btn.textContent = '▶ Run Audit';
        State.auditRunning = false;
    });
}

// Live polling
let initialMtime = null;
export function startPolling() {
    setInterval(() => {
        if (State.auditRunning) return;
        fetch('/api/status')
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'running' && data.mtime) {
                    if (initialMtime === null) {
                        initialMtime = data.mtime;
                    } else if (data.mtime !== initialMtime) {
                        initialMtime = data.mtime;
                        console.log('New audit data detected. Refreshing...');
                        window.dispatchEvent(new CustomEvent('reload-data'));
                    }
                }
            })
            .catch(() => {});
    }, 3000);
}
