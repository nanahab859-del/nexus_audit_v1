import { State, appScheme } from '../state.js';

let network = null;
let visNodes = null;
let visEdges = null;
let nodesData = [];
let edgesData = [];
let graphPhysics = true;
let separationMode = false;

// Worker and Overlays
let physicsWorker = null;
let destroyOverlay = null;
let bundleMembers = {};
let fanoutEdgeIds = [];
let baseEdgeById = new Map();

// Debounce wrapper
let initTimer = null;

export function initGraph() {
    clearTimeout(initTimer);
    initTimer = setTimeout(_initGraph, 200);
}

function _initGraph() {
    if (State.graphInitialized || !State.modules) return;
    const container = document.getElementById('network');
    if (!container || container.clientHeight === 0) return;
    
    container.innerHTML = '';
    
    // Add info panels if they were cleared
    if (!document.getElementById('edge-info-panel')) {
        container.innerHTML += `<div id="edge-info-panel" aria-live="polite" style="display:none; position:absolute; right:16px; top:16px; width:340px; max-height:90%; overflow-y:auto; background:rgba(15,23,42,0.95); border:1px solid #334155; border-radius:12px; padding:16px; box-shadow:0 10px 25px rgba(0,0,0,0.5); z-index:100; color:#f8fafc; font-size:0.85rem; backdrop-filter:blur(4px);"></div>`;
    }
    if (!document.getElementById('bundle-panel')) {
        container.innerHTML += `<div id="bundle-panel" style="display:none; position:absolute; right:16px; top:16px; width:340px; max-height:400px; overflow-y:auto; background:rgba(15,23,42,0.95); border:1px solid #334155; border-radius:12px; padding:16px; box-shadow:0 10px 25px rgba(0,0,0,0.5); z-index:101; color:#f8fafc; font-size:0.85rem; backdrop-filter:blur(4px);"></div>`;
    }
    
    nodesData = [];
    edgesData = [];
    const moduleMap = {};
    const clusterMap = {};

    // 1. Build nodes
    Object.entries(State.modules).forEach(([path, info]) => {
        const parts = path.split('.');
        const app = parts[0];
        const name = parts[parts.length - 1];
        moduleMap[path] = path;
        clusterMap[path] = app;

        let nodeColor = appScheme(app).bg;
        let borderColor = appScheme(app).border;

        nodesData.push({
            id: path,
            label: name,
            title: `<b>${path}</b><br>App: ${app}<br>Complexity: ${info.complexity || 'N/A'}<br>Imports: ${(info.imports || []).length}`,
            group: app,
            value: (info.imports || []).length + 2,
            color: { background: nodeColor, border: borderColor },
            font: { color: appScheme(app).text, size: 13 }
        });
    });

    if (State.configHealth && State.configHealth.config_folder_name) {
        const folderName = State.configHealth.config_folder_name;
        nodesData.push({
            id: `config_${folderName}`,
            label: `${folderName}\n(Config)`,
            group: folderName,
            title: 'Project Configuration Kernel (audited separately)',
            value: 20,
            shape: 'hexagon',
            color: { background: '#b45309', border: '#f59e0b' },
            font: { color: '#fef3c7', size: 13 }
        });
    }

    // 2. Build edges
    Object.entries(State.modules).forEach(([path, info]) => {
        (info.imports || []).forEach(imp => {
            if (moduleMap[imp]) {
                const isCrossApp = clusterMap[path] !== clusterMap[imp];
                let isViol = false;
                let isAllowed = false;
                
                let edgeColor = '#5DADE2';
                let eType = 'internal';
                let dashes = false;
                let width = 1;

                if (isCrossApp) {
                    isViol = State.violations.some(v => v.source_module === path && v.target_module === imp);
                    const comm = State.allowedComms.find(c => c.source === path && c.target === imp);
                    
                    if (comm) {
                        const ct = (comm.type || '').toLowerCase();
                        if (ct.includes('celery')) {
                            edgeColor = '#A29BFE'; eType = 'celery'; width = 2; dashes = [4,4];
                        } else if (ct.includes('bootstrap')) {
                            edgeColor = '#94a3b8'; eType = 'bootstrap'; width = 2; dashes = [4,4];
                        } else {
                            edgeColor = '#2ECC71'; eType = 'allowed'; width = 2; dashes = [4,4];
                        }
                    } else if (isViol) {
                        edgeColor = '#FF3333'; eType = 'violation'; width = 2;
                    } else {
                        edgeColor = '#f59e0b'; eType = 'warning'; width = 1;
                    }
                }

                const id = `${path}->${imp}`;
                const edgeObj = {
                    id: id,
                    from: path,
                    to: imp,
                    color: { color: edgeColor, highlight: '#38bdf8', hover: '#38bdf8' },
                    edgeType: eType,
                    width: width,
                    dashes: dashes,
                    arrows: { to: { enabled: true, scaleFactor: 0.5 } }
                };
                edgesData.push(edgeObj);
                baseEdgeById.set(id, edgeObj);
            }
        });
    });

    visNodes = new vis.DataSet(nodesData);
    visEdges = new vis.DataSet(edgesData);

    const options = {
        nodes: {
            shape: 'dot',
            scaling: { min: 8, max: 25 },
            borderWidth: 2,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 8 }
        },
        edges: {
            smooth: { type: 'continuous', forceDirection: 'none' },
            hoverWidth: 1.5
        },
        physics: {
            enabled: graphPhysics,
            barnesHut: { gravitationalConstant: -3000, centralGravity: 0.1, springLength: 150 },
            stabilization: { iterations: 150 }
        },
        interaction: { hover: true, tooltipDelay: 200 }
    };

    network = new vis.Network(container, { nodes: visNodes, edges: visEdges }, options);
    State.graphInitialized = true;

    buildIslandSidebar();
    buildLegend();

    // Setup Web Worker for Physics
    if (window.Worker && !physicsWorker) {
        physicsWorker = new Worker('js/physics.worker.js');
        physicsWorker.onmessage = (e) => {
            if (e.data.type === 'LAYOUT_COMPLETE') {
                applyWorkerPositions(e.data.payload.nodePositions);
            }
        };
    }

    // Event listeners
    network.on('selectNode', handleSelectNode);
    network.on('selectEdge', handleSelectEdge);
    network.on('deselectEdge', handleDeselectEdge);
    network.on('blurNode', handleBlurNode);
    network.on('doubleClick', () => { resetView(); fitAll(); });

    // Expose globals for UI buttons
    window.resetView = resetView;
    window.fitAll = fitAll;
    window.toggleFreeze = toggleFreeze;
    window.toggleSeparation = toggleSeparation;
    window.toggleInspect = toggleInspect;
    window.highlightApp = highlightApp;
    window.clearHighlight = clearHighlight;
    window.highlightCycle = highlightCycle;
}

// ---- INTERACTION HANDLERS ----

function highlightCycle(cycleNodes) {
    if (!network) return;
    State.activeFilter = 'cycle';
    
    const s = new Set(cycleNodes);
    const cycleEdges = new Set();
    for (let i = 0; i < cycleNodes.length; i++) {
        const from = cycleNodes[i];
        const to = cycleNodes[(i + 1) % cycleNodes.length];
        cycleEdges.add(from + '->' + to);
    }

    visNodes.update(nodesData.map(n => ({
        id: n.id,
        opacity: s.has(n.id) ? 1 : 0.06,
        color: s.has(n.id) ? n.color : { background:'#1e293b', border:'#334155' }
    })));
    
    visEdges.update(edgesData.map(e => ({
        id: e.id,
        color: cycleEdges.has(e.id) ? {color:'#ff6b6b'} : {color:'rgba(255,255,255,0.02)'},
        width: cycleEdges.has(e.id) ? 3 : 0.3
    })));
    
    network.fit();
}

function handleSelectNode(params) {
    if (!params.nodes.length) return;
    const sid = params.nodes[0];
    const nd = visNodes.get(sid); 
    if (!nd) return;
    
    if (State.inspectMode) {
        const panel = document.getElementById('edge-info-panel');
        if (panel) {
            panel.style.display = 'block';
            panel.innerHTML = '<span style="color:#64748b;">Click on bundled SVG lines to inspect connections.</span>';
        }
        return;
    }
    
    const connEdges = edgesData.filter(e => e.from === sid || e.to === sid);
    const connNodes = new Set([sid]);
    connEdges.forEach(e => { connNodes.add(e.from); connNodes.add(e.to); });
    
    visNodes.update(nodesData.map(n => ({ id: n.id, hidden: !connNodes.has(n.id) })));
    visEdges.update(edgesData.map(e => ({ id: e.id, hidden: e.from !== sid && e.to !== sid })));
    
    const viols = connEdges.filter(e => e.edgeType === 'violation').length;
    const infoBar = document.getElementById('node-info');
    if (infoBar) {
        infoBar.innerHTML = `<strong style="color:#38bdf8;">ISOLATED: ${nd.label}</strong>&nbsp;&nbsp;
         App: ${nd.group.toUpperCase()}&nbsp;&nbsp;
         Connections: ${connEdges.length}&nbsp;&nbsp;
         Violations: <span style="color:${viols?'#ef4444':'#10b981'}">${viols}</span>
         &nbsp;&nbsp;<button onclick="resetView()" style="padding:4px 10px;border:1px solid #334155;background:transparent;color:#94a3b8;border-radius:5px;cursor:pointer;font-size:0.8rem;">Reset</button>`;
    }
    network.fit();
}

function handleBlurNode() {
    const infoBar = document.getElementById('node-info');
    if (infoBar) infoBar.textContent = 'Hover a node to see details · Click to isolate · Double-click to reset';
    document.querySelectorAll('.island-pill').forEach(p => p.classList.remove('pill-active', 'pill-dimmed'));
    document.querySelectorAll('.legend-item[data-edge-type]').forEach(li => li.classList.remove('active'));
    
    if (!State.activeFilter && !separationMode && !State.inspectMode) {
        visNodes.update(nodesData.map(n => ({
            id: n.id, color: n.color, font: { color: appScheme(n.group).text, size: 13 }
        })));
    }
}

function handleSelectEdge(params) {
    if (!params.edges.length) return;
    const eid = params.edges[0];
    State.selectedEdge = eid;
    
    const panel = document.getElementById('edge-info-panel');
    if (!panel) return;
    panel.style.display = 'block';

    if (eid.startsWith('__bundle__')) {
        renderBundleEdgeInfo(eid, panel);
        return;
    }
    
    const edge = baseEdgeById.get(eid);
    if (!edge) return;
    
    const src = edge.from || '';
    const tgt = edge.to || '';
    const srcApp = src.split('.')[0].toUpperCase();
    const tgtApp = tgt.split('.')[0].toUpperCase();
    
    const edgeViolations = State.violations.filter(v => v.source_module === src && v.target_module === tgt);
    const edgeAllowed = State.allowedComms.filter(c => c.source === src && c.target === tgt);
    
    let html = `<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px;">
        <span style="font-size:1.1rem;font-weight:700;color:#38bdf8;">${src.split('.').pop()}.py</span>
        <span style="color:#475569;">\u2014\u25b6</span>
        <span style="font-size:1.1rem;font-weight:700;color:#38bdf8;">${tgt.split('.').pop()}.py</span>
        <span style="font-size:.75rem;color:#64748b;">(${srcApp} \u2192 ${tgtApp})</span>
    </div>`;
    
    if (edgeViolations.length) {
        html += '<div style="border-left:3px solid #ef4444;padding-left:10px;margin-bottom:8px;">';
        html += `<div style="color:#fca5a5;font-weight:600;margin-bottom:4px;">🚨 ${edgeViolations.length} Violation(s)</div>`;
        edgeViolations.forEach(v => {
            html += `<div style="font-size:.8rem;color:#94a3b8;margin-bottom:3px;"><code style="color:#fcd34d;">${v.source_module}</code> imports <code style="color:#fcd34d;">${v.target_module}</code> &middot; <span style="color:#fb923c;">${v.type}</span> &middot; <span style="color:#ef4444;">\u2212${v.penalty || 0}pts</span></div>`;
        });
        html += '</div>';
    }
    if (edgeAllowed.length) {
        html += '<div style="border-left:3px solid #10b981;padding-left:10px;">';
        html += `<div style="color:#6ee7b7;font-weight:600;margin-bottom:4px;">\u2705 ${edgeAllowed.length} Allowed Communication(s)</div>`;
        edgeAllowed.forEach(c => { html += `<div style="font-size:.8rem;color:#94a3b8;margin-bottom:2px;">${c.type || 'Allowed'}</div>`; });
        html += '</div>';
    }
    if (!edgeViolations.length && !edgeAllowed.length) {
        html += '<span style="color:#64748b;font-size:.85rem;">Internal edge or warning</span>';
    }
    panel.innerHTML = html;
}

function handleDeselectEdge() {
    clearFanout();
    State.selectedEdge = null;
    const panel = document.getElementById('edge-info-panel');
    if (panel) {
        panel.style.display = State.inspectMode ? 'block' : 'none';
        if (State.inspectMode) {
            panel.innerHTML = '<span style="color:#64748b;">Hover a thick inter-app line to fan out. Click it to inspect underlying links.</span>';
        }
    }
}

// ---- APP HIGHLIGHTING & FILTERS ----

function highlightApp(app) {
    if (!network) return;
    State.activeFilter = 'app';
    const rel = new Set(nodesData.filter(n => n.group === app).map(n => n.id));
    
    visNodes.update(nodesData.map(n => ({
        id: n.id,
        color: n.color,
        opacity: rel.has(n.id) ? 1 : 0.06,
        font: { color: rel.has(n.id) ? appScheme(n.group).text : '#334155', size: 13 }
    })));
    
    visEdges.update(edgesData.map(e => ({
        id: e.id,
        color: (rel.has(e.from)||rel.has(e.to)) ? e.color : { color:'rgba(255,255,255,0.02)' }
    })));

    document.querySelectorAll('.island-pill').forEach(p => {
        p.classList.toggle('pill-active', p.dataset.app === app);
        p.classList.toggle('pill-dimmed', p.dataset.app !== app);
    });
}

function clearHighlight() {
    if (!network) return;
    State.activeFilter = null;
    visNodes.update(nodesData.map(n => ({
        id: n.id, color: n.color, opacity: 1, hidden: false, font: { color: appScheme(n.group).text, size: 13 }
    })));
    visEdges.update(edgesData.map(e => ({ id: e.id, color: e.color, hidden: false, width: e.width })));
    document.querySelectorAll('.island-pill').forEach(p => p.classList.remove('pill-active', 'pill-dimmed'));
}

function resetView() {
    clearFanout();
    if (separationMode) {
        toggleSeparation(); // turn it off
    }
    clearHighlight();
    document.getElementById('node-info').textContent = 'Hover a node to see details · Click to isolate · Double-click to reset';
    document.querySelectorAll('.legend-item[data-edge-type]').forEach(li => li.classList.remove('active'));
    network.fit();
}

function fitAll() {
    if (network) network.fit({ animation: true });
}

function toggleFreeze() {
    graphPhysics = !graphPhysics;
    if (network) network.setOptions({ physics: { enabled: graphPhysics } });
    const btn = document.getElementById('freeze-btn');
    if (btn) btn.classList.toggle('active', !graphPhysics);
}

// ---- CUSTOM PHYSICS (WORKER) ----

function toggleSeparation() {
    const btn = document.getElementById('sep-btn');
    if (separationMode) {
        // Turn off
        if (destroyOverlay) { destroyOverlay(); destroyOverlay = null; }
        State.inspectMode = false;
        const ib = document.getElementById('inspect-btn');
        if (ib) { ib.classList.remove('active'); }
        
        network.setOptions({ physics: { enabled: true } });
        visNodes.update(nodesData.map(n => ({ id: n.id, fixed: false })));
        network.fit({ animation: true });
        
        btn.classList.remove('active');
        separationMode = false;
    } else {
        // Turn on via Worker
        separationMode = true;
        btn.classList.add('active');
        
        // Build data to send to worker
        const islands = {};
        nodesData.forEach(n => {
            const app = n.id.split('.')[0];
            if (!islands[app]) islands[app] = [];
            islands[app].push(n.id);
        });
        const appList = Object.keys(islands).sort();
        
        const weight = {};
        appList.forEach(a => { weight[a] = {}; appList.forEach(b => weight[a][b] = 0); });
        edgesData.forEach(e => {
            const src = (e.from || '').split('.')[0];
            const tgt = (e.to || '').split('.')[0];
            if (src !== tgt && weight[src] && weight[tgt]) {
                weight[src][tgt]++;
                weight[tgt][src]++;
            }
        });
        
        if (physicsWorker) {
            physicsWorker.postMessage({ type: 'CALCULATE_LAYOUT', payload: { islands, appList, weight } });
        }
    }
}

function applyWorkerPositions(posObj) {
    if (!network || !separationMode) return;
    network.setOptions({ physics: { enabled: false } });
    
    // Animate smoothly by updating nodes
    const updates = nodesData.map(n => {
        if (posObj[n.id]) {
            return { id: n.id, x: posObj[n.id].x, y: posObj[n.id].y, fixed: false };
        }
        return { id: n.id };
    });
    
    visNodes.update(updates);
    window.requestAnimationFrame(() => {
        network.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
    });
}

// ---- INSPECT MODE & SVG OVERLAYS ----

function toggleInspect() {
    State.inspectMode = !State.inspectMode;
    const btn = document.getElementById('inspect-btn');
    const panel = document.getElementById('edge-info-panel');
    const bundlePanel = document.getElementById('bundle-panel');

    if (State.inspectMode) {
        if (btn) btn.classList.add('active');
        if (panel) {
            panel.style.display = 'block';
            panel.innerHTML = '<span style="color:#64748b;">Click any bundled line to see connections.</span>';
        }
        applyInspectLayout();
        setTimeout(buildBundleOverlay, 700); // Wait for animation
    } else {
        if (btn) btn.classList.remove('active');
        if (panel) panel.style.display = 'none';
        if (bundlePanel) bundlePanel.style.display = 'none';

        if (destroyOverlay) { destroyOverlay(); destroyOverlay = null; }

        if (separationMode) {
            toggleSeparation(); // toggle it off
            setTimeout(toggleSeparation, 100); // toggle it back on to restore island layout
        } else {
            network.setOptions({ physics: { enabled: true } });
            visNodes.update(nodesData.map(n => ({ id: n.id, fixed: false })));
            visEdges.update(edgesData.map(e => ({ id: e.id, hidden: false })));
            network.fit({ animation: true });
        }
    }
}

function applyInspectLayout() {
    const NODE_W = 230, NODE_H = 80, ISLAND_PAD_X = 120, ISLAND_PAD_Y = 160, LEVELS = 4;
    const islands = {};
    nodesData.forEach(n => {
        const app = n.id.split('.')[0];
        if (!islands[app]) islands[app] = [];
        islands[app].push(n);
    });

    const importedBy = {};
    nodesData.forEach(n => importedBy[n.id] = 0);
    edgesData.forEach(e => { if (importedBy[e.to] !== undefined) importedBy[e.to]++; });

    const appList = Object.keys(islands).sort();
    const islandWidths = {}, islandHeights = {};
    appList.forEach(app => {
        const n = islands[app].length;
        const cols = Math.ceil(n / LEVELS);
        islandWidths[app] = cols * NODE_W + ISLAND_PAD_X;
        islandHeights[app] = LEVELS * NODE_H + ISLAND_PAD_Y;
    });

    const ISLAND_COLS = Math.ceil(Math.sqrt(appList.length));
    const islandOrigins = {};
    let rowX = 0, rowY = 0, rowMaxH = 0;
    appList.forEach((app, idx) => {
        const colInRow = idx % ISLAND_COLS;
        if (colInRow === 0 && idx > 0) { rowX = 0; rowY += rowMaxH; rowMaxH = 0; }
        islandOrigins[app] = { x: rowX, y: rowY };
        rowX += islandWidths[app];
        rowMaxH = Math.max(rowMaxH, islandHeights[app]);
    });

    const nodePositions = {};
    appList.forEach(app => {
        const nodes = islands[app].slice().sort((a, b) => importedBy[a.id] - importedBy[b.id]);
        const cols = Math.ceil(nodes.length / LEVELS);
        const ox = islandOrigins[app].x + ISLAND_PAD_X / 2;
        const oy = islandOrigins[app].y + ISLAND_PAD_Y / 2;
        nodes.forEach((n, i) => {
            const level = Math.floor(i / Math.max(1, cols));
            const posInLevel = i % cols;
            nodePositions[n.id] = { x: ox + posInLevel * NODE_W + NODE_W / 2, y: oy + level * NODE_H + NODE_H / 2 };
        });
    });

    const updates = nodesData.map(n => ({ id: n.id, x: nodePositions[n.id] ? nodePositions[n.id].x : 0, y: nodePositions[n.id] ? nodePositions[n.id].y : 0, fixed: false }));
    
    // Hide cross app edges (svg overlay will handle them)
    const edgeUpdates = edgesData.map(e => {
        const s = (e.from||'').split('.')[0], t = (e.to||'').split('.')[0];
        return { id: e.id, hidden: s !== t };
    });

    network.setOptions({ physics: { enabled: false } });
    visNodes.update(updates);
    visEdges.update(edgeUpdates);
    network.fit({ animation: { duration: 500 } });
}

function buildBundleOverlay() {
    if (destroyOverlay) { destroyOverlay(); destroyOverlay = null; }
    const old = document.getElementById('bundle-overlay');
    if (old) old.remove();

    const bundles = {};
    edgesData.forEach(e => {
        const sa = (e.from||'').split('.')[0], ta = (e.to||'').split('.')[0];
        if (sa === ta) return;
        const key = [sa, ta].sort().join('|');
        if (!bundles[key]) bundles[key] = { apps: [sa, ta], edges: [], hovered: false, clicked: false };
        bundles[key].edges.push(e);
    });

    const container = document.getElementById('network');
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.id = 'bundle-overlay';
    // Pointer-events none allows canvas interaction, but path segments will re-enable it for hover/clicks
    svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10;';
    container.appendChild(svg);

    function redraw() {
        if (!document.getElementById('bundle-overlay')) return;
        svg.innerHTML = '';
        Object.values(bundles).forEach(bundle => {
            if (!bundle.edges.length) return;
            try {
                const posA = network.getPosition(bundle.edges[0].from);
                const posB = network.getPosition(bundle.edges[0].to);
                if (!posA || !posB) return;
                const domA = network.canvasToDOM(posA);
                const domB = network.canvasToDOM(posB);
                const count = bundle.edges.length;
                const thickness = Math.min(16, 3 + count * 2);
                const bundleColor = bundle.edges[0].color.color || '#FF3333';

                if (bundle.hovered || bundle.clicked) {
                    bundle.edges.forEach(e => {
                        try {
                            const pA = network.canvasToDOM(network.getPosition(e.from));
                            const pB = network.canvasToDOM(network.getPosition(e.to));
                            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                            line.setAttribute('x1', pA.x); line.setAttribute('y1', pA.y);
                            line.setAttribute('x2', pB.x); line.setAttribute('y2', pB.y);
                            line.setAttribute('stroke', e.color.color || '#FF3333');
                            line.setAttribute('stroke-width', '2');
                            line.setAttribute('opacity', '0.85');
                            // Add glassy depth via drop-shadow on individual lines
                            line.style.filter = `drop-shadow(0px 0px 4px ${e.color.color || '#FF3333'})`;
                            svg.appendChild(line);
                        } catch(e) {}
                    });
                } else {
                    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    const mx = (domA.x + domB.x) / 2;
                    const my = (domA.y + domB.y) / 2 - 40;
                    path.setAttribute('d', `M ${domA.x} ${domA.y} Q ${mx} ${my} ${domB.x} ${domB.y}`);
                    path.setAttribute('stroke', bundleColor);
                    path.setAttribute('stroke-width', thickness);
                    path.setAttribute('fill', 'none');
                    path.setAttribute('opacity', '0.75');
                    path.style.pointerEvents = 'stroke';
                    path.style.cursor = 'pointer';
                    // Glassy depth
                    path.style.filter = `drop-shadow(0px 0px 8px ${bundleColor})`;
                    
                    path.addEventListener('mouseenter', () => { bundle.hovered = true; window.requestAnimationFrame(redraw); });
                    path.addEventListener('mouseleave', () => { bundle.hovered = false; if (!bundle.clicked) window.requestAnimationFrame(redraw); });
                    path.addEventListener('click', ev => {
                        ev.stopPropagation();
                        bundle.clicked = !bundle.clicked;
                        if (bundle.clicked) {
                            showBundlePanel(bundle);
                        } else {
                            const p = document.getElementById('bundle-panel');
                            if (p) p.style.display = 'none';
                        }
                        window.requestAnimationFrame(redraw);
                    });
                    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    text.setAttribute('x', mx); text.setAttribute('y', my - 8);
                    text.setAttribute('fill', '#94a3b8'); text.setAttribute('font-size', '11');
                    text.setAttribute('text-anchor', 'middle');
                    text.textContent = `${count} connection${count > 1 ? 's' : ''}`;
                    svg.appendChild(path);
                    svg.appendChild(text);
                }
            } catch(err) {}
        });
    }

    const onTransform = () => window.requestAnimationFrame(redraw);
    network.on('zoom', onTransform);
    network.on('dragging', onTransform);
    network.on('dragEnd', onTransform);

    container.addEventListener('click', () => {
        Object.values(bundles).forEach(b => { b.clicked = false; b.hovered = false; });
        const panel = document.getElementById('bundle-panel');
        if (panel) panel.style.display = 'none';
        window.requestAnimationFrame(redraw);
    });

    destroyOverlay = () => {
        network.off('zoom', onTransform);
        network.off('dragging', onTransform);
        network.off('dragEnd', onTransform);
        const o = document.getElementById('bundle-overlay');
        if (o) o.remove();
    };

    redraw();
}

function showBundlePanel(bundle) {
    const panel = document.getElementById('bundle-panel');
    if (!panel) return;
    const [a, b] = bundle.apps;
    
    panel.innerHTML = `
        <div style="font-weight:700;margin-bottom:10px;color:#38bdf8;">
            ${a.replace('nexus_','').toUpperCase()} ↔ ${b.replace('nexus_','').toUpperCase()}
            <span style="color:#64748b;font-size:.75rem;"> (${bundle.edges.length} connections)</span>
        </div>
        ${bundle.edges.map(e => `
            <div style="padding:4px 0;border-bottom:1px solid #1e293b;">
                <code style="color:#fcd34d;font-size:.78rem;">${e.from.split('.').pop()}</code>
                <span style="color:#475569;"> → </span>
                <code style="color:#7dd3fc;font-size:.78rem;">${e.to.split('.').pop()}</code>
            </div>
        `).join('')}
    `;
    panel.style.display = 'block';
}

function renderBundleEdgeInfo(eid, panel) {
    // Re-implemented if needed, otherwise handled by click event on svg line
}

function clearFanout() {
    if (fanoutEdgeIds.length) {
        visEdges.remove(fanoutEdgeIds);
        fanoutEdgeIds = [];
    }
}

// ---- SIDEBAR AND LEGEND ----

function buildIslandSidebar() {
    const sidebar = document.getElementById('island-sidebar');
    if (!sidebar) return;
    sidebar.innerHTML = '<div class="island-sidebar-title">Islands</div>';
    
    if (State.configHealth && State.configHealth.config_folder_name) {
        const folderName = State.configHealth.config_folder_name;
        const sc = (State.configHealth.summary || {}).score || 0;
        const pill = document.createElement('div');
        pill.className = 'island-pill';
        pill.dataset.app = folderName;
        pill.innerHTML = `<div class="island-dot" style="background:#b45309;"></div><span class="island-label">CONFIG</span><span class="island-score">${sc}%</span>`;
        pill.addEventListener('click', () => {
            if (pill.classList.contains('pill-active')) clearHighlight();
            else highlightApp(folderName);
        });
        sidebar.appendChild(pill);
    }
    
    Object.keys(State.apps).sort().forEach(app => {
        const sc = Math.round(State.apps[app].score || 0);
        const col = appScheme(app).bg;
        const pill = document.createElement('div');
        pill.className = 'island-pill';
        pill.dataset.app = app;
        pill.innerHTML = `<div class="island-dot" style="background:${col};"></div><span class="island-label">${app}</span><span class="island-score">${sc}%</span>`;
        pill.addEventListener('click', () => {
            if (pill.classList.contains('pill-active')) clearHighlight();
            else highlightApp(app);
        });
        sidebar.appendChild(pill);
    });
}

function buildLegend() {
    const legendDiv = document.getElementById('legend');
    if (!legendDiv) return;
    legendDiv.innerHTML = '';
    
    const legendDef = [
        { type: 'internal', color: '#5DADE2', label: 'Internal Import', dashed: false },
        { type: 'violation', color: '#FF3333', label: 'Cross-App Violation', dashed: false },
        { type: 'bootstrap', color: '#94a3b8', label: 'Django Bootstrap (Exempt)', dashed: true },
        { type: 'allowed', color: '#2ECC71', label: 'Signal/Receiver (Allowed)', dashed: true },
        { type: 'celery', color: '#A29BFE', label: 'Celery Task (Allowed)', dashed: true },
        { type: 'warning', color: '#f59e0b', label: 'Implicit Coupling', dashed: false }
    ];
    
    legendDef.forEach(item => {
        const div = document.createElement('div');
        div.className = 'legend-item';
        div.dataset.edgeType = item.type;
        div.innerHTML = `<div class="legend-color${item.dashed?' dashed':''}" style="background:${item.color};color:${item.color};"></div><span>${item.label}</span>`;
        
        div.addEventListener('mouseenter', () => {
            if (State.activeFilter) return;
            visEdges.update(edgesData.map(e => ({
                id: e.id,
                color: e.edgeType === item.type ? e.color : {color:'rgba(255,255,255,0.04)'},
                width: e.edgeType === item.type ? Math.max(e.width, 2) : 0.4
            })));
            const inv = new Set();
            edgesData.filter(e => e.edgeType === item.type).forEach(e => { inv.add(e.from); inv.add(e.to); });
            visNodes.update(nodesData.map(n => ({ id: n.id, opacity: inv.has(n.id) ? 1 : 0.07 })));
        });
        
        div.addEventListener('mouseleave', () => {
            if (State.activeFilter) return;
            visEdges.update(edgesData);
            visNodes.update(nodesData.map(n => ({ id: n.id, color: n.color, opacity: 1 })));
        });
        
        div.addEventListener('click', () => {
            if (State.activeFilter === item.type) {
                State.activeFilter = null;
                div.classList.remove('active');
                visNodes.update(nodesData.map(n => ({
                    id: n.id, hidden: false, opacity: 1, color: n.color,
                    font: { color: appScheme(n.group).text, size: 13 }
                })));
                visEdges.update(edgesData.map(e => ({ id: e.id, hidden: false, color: e.color, width: e.width })));
            } else {
                State.activeFilter = item.type;
                document.querySelectorAll('.legend-item').forEach(l => l.classList.remove('active'));
                div.classList.add('active');
                const inv = new Set();
                edgesData.filter(e => e.edgeType === item.type).forEach(e => { inv.add(e.from); inv.add(e.to); });
                visNodes.update(nodesData.map(n => ({ id: n.id, hidden: !inv.has(n.id) })));
                visEdges.update(edgesData.map(e => ({ id: e.id, hidden: e.edgeType !== item.type })));
                network.fit();
            }
        });
        legendDiv.appendChild(div);
    });
}
