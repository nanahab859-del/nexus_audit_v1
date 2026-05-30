import { State, appScheme } from '../state.js';

let network = null;
let visNodes = null;
let visEdges = null;
let nodesData = [];
let edgesData = [];
let graphPhysics = true;
let separationMode = false;
let inspectMode = false;

export function initGraph() {
    if (State.graphInitialized || !State.modules) return;
    const container = document.getElementById('network');
    if (!container || container.clientHeight === 0) return;
    
    // Clear out existing content (e.g. loading text)
    container.innerHTML = '';
    
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

    // Inject Config Node if present
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
                
                if (isCrossApp) {
                    isViol = State.violations.some(v => v.source_module === path && v.target_module === imp);
                    isAllowed = State.allowedComms.some(c => c.source === path && c.target === imp);
                }

                let edgeColor = 'rgba(255, 255, 255, 0.15)';
                let eType = 'normal';
                let dashes = false;
                let width = 1;

                if (isCrossApp) {
                    if (isAllowed) {
                        edgeColor = '#3b82f6';
                        eType = 'allowed';
                        width = 2;
                        dashes = [4, 4];
                    } else if (isViol) {
                        edgeColor = '#ef4444';
                        eType = 'violation';
                        width = 2;
                    } else {
                        edgeColor = '#f59e0b';
                        eType = 'warning';
                    }
                }

                edgesData.push({
                    id: `${path}->${imp}`,
                    from: path,
                    to: imp,
                    color: { color: edgeColor, highlight: '#38bdf8', hover: '#38bdf8' },
                    edgeType: eType,
                    width: width,
                    dashes: dashes,
                    arrows: { to: { enabled: true, scaleFactor: 0.5 } }
                });
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

    // Build sidebar
    buildIslandSidebar();
    buildLegend();

    // Event listeners
    network.on('click', (params) => {
        if (params.nodes.length > 0) {
            highlightNode(params.nodes[0]);
        } else {
            clearHighlight();
        }
    });
    
    network.on('doubleClick', () => { clearHighlight(); fitAll(); });

    // Expose globals for UI buttons
    window.resetView = clearHighlight;
    window.fitAll = fitAll;
    window.toggleFreeze = toggleFreeze;
    window.toggleSeparation = toggleSeparation;
    window.toggleInspect = toggleInspect;
    window.highlightApp = highlightApp;
    window.clearHighlight = clearHighlight;
}

function highlightNode(nodeId) {
    if (!network) return;
    const connected = network.getConnectedNodes(nodeId);
    const allConnected = new Set([...connected, nodeId]);

    visNodes.update(nodesData.map(n => ({
        id: n.id,
        opacity: allConnected.has(n.id) ? 1 : 0.1
    })));

    visEdges.update(edgesData.map(e => {
        const isConn = e.from === nodeId || e.to === nodeId;
        return {
            id: e.id,
            color: isConn ? { color: e.color.color, opacity: 1 } : { color: e.color.color, opacity: 0.05 },
            hidden: !isConn
        };
    }));
}

function highlightApp(app) {
    if (!network) return;
    State.activeFilter = 'app';
    
    visNodes.update(nodesData.map(n => ({
        id: n.id,
        opacity: n.group === app ? 1 : 0.1
    })));
    
    visEdges.update(edgesData.map(e => ({
        id: e.id,
        hidden: true
    })));

    document.querySelectorAll('.island-pill').forEach(el => {
        if (el.dataset.app === app) {
            el.classList.add('pill-active');
            el.classList.remove('pill-dimmed');
        } else {
            el.classList.remove('pill-active');
            el.classList.add('pill-dimmed');
        }
    });
    
    network.fit({ nodes: nodesData.filter(n => n.group === app).map(n => n.id), animation: true });
}

function clearHighlight() {
    if (!network) return;
    State.activeFilter = null;
    visNodes.update(nodesData.map(n => ({ id: n.id, opacity: 1, hidden: false })));
    visEdges.update(edgesData.map(e => ({ id: e.id, color: e.color, hidden: false })));
    document.querySelectorAll('.island-pill').forEach(el => {
        el.classList.remove('pill-active', 'pill-dimmed');
    });
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

function toggleSeparation() {
    separationMode = !separationMode;
    const btn = document.getElementById('sep-btn');
    if (btn) btn.classList.toggle('active', separationMode);
    
    if (network) {
        if (separationMode) {
            network.setOptions({
                physics: {
                    barnesHut: { gravitationalConstant: -1000, centralGravity: 0.05, springLength: 300, springConstant: 0.01 }
                }
            });
            visEdges.update(edgesData.map(e => {
                const isCross = e.from.split('.')[0] !== e.to.split('.')[0];
                return { id: e.id, hidden: isCross };
            }));
        } else {
            network.setOptions({
                physics: {
                    barnesHut: { gravitationalConstant: -3000, centralGravity: 0.1, springLength: 150 }
                }
            });
            visEdges.update(edgesData.map(e => ({ id: e.id, hidden: false })));
        }
    }
}

function toggleInspect() {
    inspectMode = !inspectMode;
    const btn = document.getElementById('inspect-btn');
    if (btn) btn.classList.toggle('active', inspectMode);
    // Simple mock logic for inspect mode; the SVG overlay was too buggy, this just highlights edges
    if (inspectMode) {
        State.activeFilter = 'inspect';
        visNodes.update(nodesData.map(n => ({ id: n.id, opacity: 0.3 })));
    } else {
        clearHighlight();
    }
}

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
        { type: 'violation', color: '#ef4444', label: 'Cross-App Violation' },
        { type: 'allowed', color: '#3b82f6', label: 'Allowed Communication', dashed: true },
        { type: 'warning', color: '#f59e0b', label: 'Implicit Coupling' },
        { type: 'normal', color: 'rgba(255,255,255,0.4)', label: 'Internal Import' }
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
        });
        
        div.addEventListener('mouseleave', () => {
            if (State.activeFilter) return;
            visEdges.update(edgesData);
        });
        
        div.addEventListener('click', () => {
            if (State.activeFilter === item.type) {
                clearHighlight();
                div.classList.remove('active');
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
