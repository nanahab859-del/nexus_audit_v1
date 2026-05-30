import { loadAuditData, runAuditFromUI, startPolling } from './api.js';
import { renderDashboard } from './components/dashboard.js';
import { setupTabs, renderTabs } from './components/tabs.js';
import { renderTrendsTab } from './components/trends.js';
import { renderRecommendationsList, renderEffortSummary, setupRecommendations } from './components/recommendations.js';
import { initGraph } from './components/graph.js';
import { State } from './state.js';

// Setup Event Listeners and Initial Load
document.addEventListener('DOMContentLoaded', async () => {
    setupTabs();
    setupRecommendations();

    window.addEventListener('reload-data', async () => {
        const ok = await loadAuditData();
        if (ok) {
            State.graphInitialized = false; // allow redraw
            renderAll();
        }
    });

    const ok = await loadAuditData();
    if (ok) {
        renderAll();
        startPolling();
    } else {
        showEmptyState();
    }
});

function renderAll() {
    renderDashboard();
    renderTabs();
    renderTrendsTab();
    renderRecommendationsList();
    renderEffortSummary();
    
    // Slight delay to ensure DOM layout is complete for canvas size
    setTimeout(() => {
        initGraph();
    }, 50);
}

function showEmptyState() {
    const mg = document.getElementById('metrics-grid');
    if (mg) mg.innerHTML = '<div class="metric-card" style="grid-column:1/-1;text-align:center;"><div class="metric-label">Welcome to Nexus Audit</div><div style="font-size:0.9rem;color:#94a3b8;margin-top:8px;">No audit data found. Configure your project and run an audit.</div></div>';
}

// Expose runAuditFromUI to the global window object since it's called via inline onclick
window.runAuditFromUI = runAuditFromUI;
