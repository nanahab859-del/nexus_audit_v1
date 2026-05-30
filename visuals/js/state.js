export const State = {
    apps: {},
    modules: {},
    violations: [],
    securityFindings: [],
    metrics: {},
    cycles: [],
    recommendations: [],
    metadata: {},
    ghostFiles: [],
    allowedComms: [],
    trendData: {},
    timelineData: {},
    depScan: {},
    capabilities: {},
    changeSummary: {},
    fixQueueData: {},
    configHealth: {},
    couplingMatrix: {},
    gitContext: {},
    
    // UI State
    activeFilter: null,
    graphInitialized: false,
    auditRunning: false
};

const FIX_QUEUE_STORAGE_KEY = 'nexus-audit-fix-queue';
const USE_FIX_QUEUE_SERVER = window.location.hostname === 'localhost';

export function getFixQueueState() {
    let saved = {};
    try {
        saved = JSON.parse(localStorage.getItem(FIX_QUEUE_STORAGE_KEY) || '{}') || {};
    } catch (err) {
        saved = {};
    }
    return Object.assign({}, State.fixQueueData || {}, saved);
}

export let fixQueueState = getFixQueueState();

export function hydrateFixQueueState() {
    if (!USE_FIX_QUEUE_SERVER) return;
    fetch('/fix-queue')
        .then(resp => resp.ok ? resp.json() : null)
        .then(data => {
            if (!data || typeof data !== 'object') return;
            fixQueueState = Object.assign({}, fixQueueState, data);
            
            // Dispatch event to refresh UI
            window.dispatchEvent(new CustomEvent('fix-queue-updated'));
        });
}

export function persistFixQueueState(recId, status) {
    const current = fixQueueState[recId] || {};
    fixQueueState = Object.assign({}, fixQueueState, {
        [recId]: Object.assign({}, current, {
            status,
            updated_at: new Date().toISOString(),
        }),
    });
    try {
        localStorage.setItem(FIX_QUEUE_STORAGE_KEY, JSON.stringify(fixQueueState));
    } catch (err) {}
    
    if (USE_FIX_QUEUE_SERVER) {
        fetch('/fix-queue', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rec_id: recId, status, note: current.notes || '' }),
        });
    }
    window.dispatchEvent(new CustomEvent('fix-queue-updated'));
}

export const APP_SCHEME = {};
export function appScheme(name) {
    if (APP_SCHEME[name]) return APP_SCHEME[name];
    const hash = Array.from(name).reduce((h, c) => (h * 31 + c.charCodeAt(0)) | 0, 0);
    const hue = Math.abs(hash) % 360;
    APP_SCHEME[name] = { bg: `hsl(${hue}, 65%, 25%)`, border: `hsl(${hue}, 70%, 45%)`, text: `hsl(${hue}, 80%, 90%)` };
    return APP_SCHEME[name];
}
