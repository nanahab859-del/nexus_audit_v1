import { State, persistFixQueueState, fixQueueState } from '../state.js';

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

function fixQueueLabel(status) {
    return {
        open: 'Open',
        in_progress: 'In progress',
        done: 'Done',
        snoozed: 'Snoozed',
    }[status] || 'Open';
}

export function renderEffortSummary() {
    const el = document.getElementById('effort-summary');
    if (!el) return;
    const counts = { quick: 0, half_day: 0, multi_day: 0, major: 0, unknown: 0 };
    (State.recommendations || []).forEach(r => {
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

export function filterRecommendations() {
    const searchEl = document.getElementById('rec-search');
    const typeEl = document.getElementById('rec-filter-type');
    const prioEl = document.getElementById('rec-filter-priority');
    const effortVal = window.__effortFilter || '';

    if (!searchEl || !typeEl || !prioEl) return;

    const searchTerm = searchEl.value.toLowerCase();
    const typeVal = typeEl.value;
    const priorityVal = prioEl.value;

    const cards = document.querySelectorAll('.rec-card');
    let shown = 0;

    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const type = card.dataset.type || '';
        const priority = card.dataset.priority || '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesType = !typeVal || type === typeVal;
        const matchesPriority = !priorityVal || priority === priorityVal;
        const matchesEffort = !effortVal || (card.dataset.fixEffort || '').toLowerCase() === effortVal;
        
        const show = matchesSearch && matchesType && matchesPriority && matchesEffort;
        
        if (show) {
            card.style.display = 'block';
            shown++;
        } else {
            card.style.display = 'none';
        }
    });

    applyRecommendationSort(cards);

    const total = cards.length;
    const ctr = document.getElementById('rec-counter');
    if (ctr) ctr.textContent = `Showing ${shown} of ${total}`;

    const summary = document.getElementById('effort-summary');
    if (summary) {
        summary.querySelectorAll('[data-effort]').forEach(btn => btn.classList.toggle('active', (window.__effortFilter || '') === btn.dataset.effort));
    }
}

export function refreshFixQueueCard(card) {
    if (!card) return;
    const recId = card.dataset.recId;
    const entry = fixQueueState[recId] || {};
    const status = entry.status || 'open';
    card.dataset.fixStatus = status;
    const badge = card.querySelector('.status-badge');
    if (badge) {
        badge.className = `status-badge status-${status}`;
        badge.textContent = fixQueueLabel(status);
    }
    card.querySelectorAll('.status-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.status === status);
    });
}

export function setupRecommendations() {
    window.addEventListener('fix-queue-updated', () => {
        document.querySelectorAll('.rec-card').forEach(refreshFixQueueCard);
    });
    
    // Attach listeners
    const searchEl = document.getElementById('rec-search');
    const typeEl = document.getElementById('rec-filter-type');
    const prioEl = document.getElementById('rec-filter-priority');
    const sortSelect = document.getElementById('rec-sort');

    if (searchEl) searchEl.addEventListener('input', filterRecommendations);
    if (typeEl) typeEl.addEventListener('change', filterRecommendations);
    if (prioEl) prioEl.addEventListener('change', filterRecommendations);
    if (sortSelect) sortSelect.addEventListener('change', filterRecommendations);
    
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('status-btn') && e.target.closest('.rec-card')) {
            const card = e.target.closest('.rec-card');
            persistFixQueueState(card.dataset.recId, e.target.dataset.status);
        }
    });
}

export function renderRecommendationsList() {
    const listEl = document.getElementById('recommendations-list');
    if (!listEl) return;
    
    let html = '';
    
    if (!State.recommendations || State.recommendations.length === 0) {
        html = `<div style="padding: 20px; text-align: center; color: #94a3b8; background: rgba(15, 23, 42, 0.4); border-radius: 10px; border: 1px dashed #334155;">
            No recommendations generated. Run the audit with AI enabled.
        </div>`;
    } else {
        State.recommendations.forEach(r => {
            const type = r.type || 'health';
            const priority = r.priority || 'MEDIUM';
            const prioClass = priority === 'CRITICAL' ? 'priority-critical' : priority === 'HIGH' ? 'priority-high' : priority === 'LOW' ? 'priority-low' : 'priority-medium';
            const recId = r.id || `${type}-${priority}-${Date.now()}`;
            
            const fixStatus = (fixQueueState[recId] || {}).status || 'open';
            const confidence = Math.max(1, Math.min(10, Number(r.confidence ?? 5) || 5));
            const fixEffort = r.fix_effort || r.effort || 'unknown';
            const effortRank = fixEffortRank(fixEffort);
            
            const gitBase = (State.gitContext || {}).github_base || '';
            const gitBranch = (State.gitContext || {}).branch || 'main';
            const primaryModule = (r.affected_modules || [])[0] || r.file_path || '';
            const relativePath = primaryModule ? (primaryModule.includes('/') || primaryModule.endsWith('.py') ? primaryModule.replace(/^\/+/, '') : primaryModule.replace(/\./g, '/') + '.py') : '';
            const linkLine = Number(r.line_number || r.line || 0) || 0;
            const githubLink = gitBase && relativePath ? gitBase + '/blob/' + gitBranch + '/' + relativePath + (linkLine ? '#L' + linkLine : '') : '';

            html += `<div class="recommendation-card rec-card ${prioClass}" data-type="${type}" data-priority="${priority}" data-rec-id="${recId}" data-fix-status="${fixStatus}" data-confidence="${confidence}" data-fix-effort="${fixEffort}" data-effort-rank="${effortRank}">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
                    <div style="flex:1;">
                        <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px;">
                            <span class="badge ${prioClass.replace('priority-', 'badge-')}">${priority}</span>
                            <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">${type}</span>
                        </div>
                        <h3>${r.action || r.description}</h3>
                        ${r.action ? `<p>${r.description || ''}</p>` : ''}
                        
                        ${(r.affected_modules && r.affected_modules.length) ? `
                            <div style="margin-top: 8px; font-family: monospace; font-size: 0.8rem; color: #cbd5e1; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px;">
                                ${r.affected_modules.join(', ')}
                            </div>
                        ` : ''}
                        
                        <div style="margin-top:12px; display:flex; gap:16px; font-size:0.8rem; color:#94a3b8; align-items:center; flex-wrap:wrap;">
                            <span style="display:flex;align-items:center;gap:4px;"><span style="color:#64748b;">Effort:</span> <span style="color:${fixEffortColor(fixEffort)};font-weight:600;">${fixEffortLabel(fixEffort)}</span></span>
                            ${r.ai_confidence ? `<span>AI Confidence: ${Math.round(r.ai_confidence * 100)}%</span>` : ''}
                        </div>
                        
                        ${githubLink ? `<div style="margin-top:8px;font-size:.76rem;"><a href="${githubLink}" target="_blank" rel="noopener" style="color:#7dd3fc;text-decoration:none;">View on GitHub</a></div>` : ''}
                    </div>
                    
                    <div style="text-align:right; min-width:180px;">
                        <div class="rec-status-row">
                            <span class="status-badge status-${fixStatus}">${fixQueueLabel(fixStatus)}</span>
                        </div>
                        <div class="status-btn-row" style="justify-content:flex-end;">
                            <button type="button" class="status-btn status-open ${fixStatus === 'open' ? 'active' : ''}" data-status="open">Open</button>
                            <button type="button" class="status-btn status-in_progress ${fixStatus === 'in_progress' ? 'active' : ''}" data-status="in_progress">In Prog</button>
                            <button type="button" class="status-btn status-done ${fixStatus === 'done' ? 'active' : ''}" data-status="done">Done</button>
                            <button type="button" class="status-btn status-snoozed ${fixStatus === 'snoozed' ? 'active' : ''}" data-status="snoozed">Snooze</button>
                        </div>
                    </div>
                </div>
            </div>`;
        });
    }
    
    listEl.innerHTML = html;
    
    document.querySelectorAll('.rec-card').forEach(refreshFixQueueCard);
    filterRecommendations();
}
