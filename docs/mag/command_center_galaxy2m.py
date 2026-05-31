import json
import os
from datetime import datetime

def find_cycles(dna):
    """Detects circular dependencies using Depth First Search (DFS)."""
    cycles = []
    visited = set()
    path = []

    def visit(node):
        if node in path:
            cycle_start_idx = path.index(node)
            cycles.append(path[cycle_start_idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        imports = dna.get(node, {}).get('imports', [])
        for imp in imports:
            if imp in dna: 
                visit(imp)
        path.pop()

    for module in dna:
        if module != "__main__":
            visit(module)
    return list(set([tuple(c) for c in cycles]))

def get_connection_type(source: str, target: str) -> str:
    """Deep protocol detection for decoupled architectures."""
    src_app = source.split('.')[0]
    tgt_app = target.split('.')[0]
    if src_app == tgt_app: return "Internal"
    
    tp, sp = target.lower(), source.lower()
    if 'signals' in tp or 'signals' in sp: return "Django Signal"
    if 'gateway' in tp or 'api' in tp: return "API/Gateway Call"
    if 'consumers' in tp or 'routing' in tp: return "Websocket/Channel"
    if 'tasks' in tp: return "Async Task/Celery"
    if 'models' in tp: return "Direct DB Access (Coupling Warning)"
    return "Direct Import (Violation)"

def build_audit_fortress() -> None:
    vault_path = os.path.expanduser('~/my_tools/nexus_audit')
    dna_path = os.path.join(vault_path, 'master_nexus_dna.json')
    inventory_path = os.path.join(vault_path, 'factories/physical_inventory.txt')
    visuals_dir = os.path.join(vault_path, 'visuals')
    visual_html = os.path.join(visuals_dir, 'NEXUS_COMMAND_CENTER.html')
    report_md = os.path.join(visuals_dir, 'NEXUS_AUDIT_REPORT.md')

    os.makedirs(visuals_dir, exist_ok=True)
    if not os.path.exists(dna_path):
        print("❌ Error: DNA not found!")
        return

    try:
        with open(dna_path, 'r', encoding='utf-8') as f:
            dna = json.load(f)
    except json.JSONDecodeError:
        print("❌ Error: DNA file is malformed.")
        return

    physical_inventory = []
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r', encoding='utf-8') as f:
            physical_inventory = [line.strip() for line in f if line.strip()]

    nodes, edges = [], []
    app_stats = {}
    protocol_logs = {
        "Direct Import (Violation)": [], "Direct DB Access (Coupling Warning)": [],
        "Django Signal": [], "API/Gateway Call": [], "Websocket/Channel": [],
        "Async Task/Celery": [], "Internal": []
    }
    
    island_colors = {
        'nexus_core': '#1ABC9C', 'nexus_economy': '#E67E22', 'nexus_gaming': '#34495E',
        'nexus_gateway': '#F1C40F', 'nexus_social': '#9B59B6', 'nexus_tournaments': '#3498DB',
        'nexus_content': '#E74C3C'
    }

    # Pre-fill stats from physical inventory
    for module in physical_inventory:
        app = module.split('.')[0]
        if app not in app_stats:
            app_stats[app] = {"physical": [], "logical": [], "violations": 0, "coupling": 0, "healthy": 0, "score": 100}
        app_stats[app]["physical"].append(module)

    # 1. Full Discovery
    for module in sorted(dna.keys()):
        if module == "__main__": continue
        app = module.split('.')[0]
        if app not in app_stats:
            app_stats[app] = {"physical": [], "logical": [], "violations": 0, "coupling": 0, "healthy": 0, "score": 100}
        app_stats[app]["logical"].append(module)

    # 2. Connection Mapping
    for module, data in dna.items():
        if module == "__main__": continue
        app = module.split('.')[0]
        color = island_colors.get(app, '#7F8C8D')
        
        nodes.append({
            "id": module, "label": module.split('.')[-1] + ".py", "group": app,
            "color": {"background": color, "border": "#ffffff"},
            "title": f"<b>APP:</b> {app.upper()}<br><b>FILE:</b> {module}", "font": {"color": "white"}
        })

        if 'imports' in data:
            for imp in data['imports']:
                if imp.startswith('nexus_') and imp in dna:
                    conn_type = get_connection_type(module, imp)
                    protocol_logs[conn_type].append({"src": module, "tgt": imp})
                    
                    if "Violation" in conn_type: app_stats[app]["violations"] += 1
                    elif "Warning" in conn_type: app_stats[app]["coupling"] += 1
                    else: app_stats[app]["healthy"] += 1

                    style_color, is_dashed, width = "#5DADE2", False, 1
                    if "Violation" in conn_type: style_color, width = "#FF3333", 3
                    elif "Warning" in conn_type: style_color, is_dashed = "#FF8C00", True 
                    elif "Signal" in conn_type: style_color, is_dashed = "#2ECC71", True
                    elif "API" in conn_type: style_color, is_dashed = "#FF1493", [2, 4] 

                    edges.append({
                        "from": module, "to": imp, "color": style_color, "width": width,
                        "dashes": is_dashed, "arrows": "to", "title": f"<b>{conn_type}</b>",
                        "protocol": conn_type # ADDED: Protocol metadata for the Smart Legend
                    })

    # Ghost Files & Integrity
    ghost_files = [f for f in physical_inventory if f not in dna and "__init__" not in f and "migrations" not in f]

    for app in app_stats:
        s = 100 - (app_stats[app]["violations"] * 25) - (app_stats[app]["coupling"] * 10)
        integrity_gap = len(app_stats[app]["physical"]) - len(app_stats[app]["logical"])
        if integrity_gap > 0: s -= (integrity_gap * 5)
        app_stats[app]["score"] = max(0, s)

    # --- MD MANIFEST GENERATION ---
    with open(report_md, 'w', encoding='utf-8') as f:
        f.write(f"# 🛡️ NEXUS MASTER AUDIT MANIFEST\n")
        f.write(f"**Audit Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        if ghost_files:
            f.write("## 👻 CRITICAL: GHOST FILES DETECTED\n")
            for ghost in ghost_files: f.write(f"- `{ghost}`\n")
            f.write("\n")
        f.write("## 🖤 GLOBAL FLEET HEALTH\n")
        f.write("| Island | Score | Physical | Audited | Violations | DB Coupling | Healthy Connections |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for app, s in sorted(app_stats.items()):
            emoji = "💚" if s['score'] > 85 else "💛" if s['score'] > 60 else "❤️"
            f.write(f"| **{app.upper()}** | {emoji} {s['score']}% | {len(s['physical'])} | {len(s['logical'])} | {s['violations']} | {s['coupling']} | {s['healthy']} |\n")
        for p_type, logs in protocol_logs.items():
            if p_type == "Internal": continue
            f.write(f"\n## 📡 {p_type.upper()}\n")
            if not logs: f.write(f"✅ No records for {p_type}.\n")
            else:
                f.write("| Source File | Target File |\n| :--- | :--- |\n")
                for log in logs: f.write(f"| `{log['src']}` | `{log['tgt']}` |\n")
        f.write(f"\n## 📋 FULL PROJECT MANIFEST (EVERY AUDITED FILE)\n")
        f.write("| File Path | App Island |\n| :--- | :--- |\n")
        for module in sorted(dna.keys()):
            if module == "__main__": continue
            f.write(f"| {module} | {module.split('.')[0]} |\n")

    # --- HTML COMMAND CENTER GENERATION ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexus Commander</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            body {{ background: #0b1120; color: #f8fafc; margin: 0; font-family: 'Inter', system-ui, sans-serif; overflow: hidden; }}
            #mynetwork {{ width: 100vw; height: 100vh; position: absolute; z-index: 1; }}
            .panel {{ position: absolute; z-index: 100; background: rgba(15,23,42,0.9); backdrop-filter: blur(8px); border: 1px solid #1e293b; padding: 15px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
            .panel-left {{ top: 20px; left: 20px; width: 280px; }}
            /* ADDED: scroll-behavior: smooth for panel syncing */
            .panel-right {{ top: 20px; right: 20px; width: 340px; height: 90vh; overflow-y: auto; scroll-behavior: smooth; }}
            .ui-box {{ background: rgba(30,41,59,0.5); padding: 12px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #334155; transition: all 0.3s ease; }}
            .health-row {{ display: flex; justify-content: space-between; font-size: 0.9rem; font-weight: 800; margin-bottom: 8px; }}
            .sub-stats {{ font-size: 0.75rem; color: #94a3b8; margin-top: 6px; line-height: 1.4; }}
            .score-bar {{ height: 6px; background: #0f172a; border-radius: 3px; overflow: hidden; }}
            .score-fill {{ height: 100%; transition: width 0.5s ease; }}
            .legend-item {{ display: flex; align-items: center; margin-bottom: 8px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; transition: all 0.3s ease; cursor: pointer; }}
            .line-sample {{ width: 30px; height: 0; margin-right: 12px; border-top-width: 3px; border-top-style: solid; }}
            .dot-circle {{ width: 12px; height: 12px; border-radius: 50%; margin-right: 12px; }}
            button {{ background: #ef4444; color: white; border: none; padding: 12px; width: 100%; cursor: pointer; border-radius: 6px; font-weight: 900; letter-spacing: 1px; transition: 0.2s; }}
            button:hover {{ filter: brightness(1.2); transform: scale(1.02); }}
            h2 {{ font-size: 0.8rem; color: #38bdf8; display: flex; align-items: center; gap: 8px; margin: 0 0 15px 0; }}
            .warning {{ color: #f1c40f; font-weight: bold; }}
            .hidden {{ display: none !important; }}
            
            /* Smart classes for interactive legend and panels */
            .panel-dimmed {{ opacity: 0.15; filter: grayscale(80%); }}
            .panel-highlight {{ opacity: 1; transform: scale(1.02); border-color: #38bdf8; background: rgba(30,41,59,0.9); }}
            .legend-active {{ color: #38bdf8; opacity: 1 !important; transform: translateX(5px); }}
        </style>
    </head>
    <body>
        <div id="mynetwork"></div>

        <div class="panel panel-left">
            <h2>🛰️ NEXUS COMMANDER</h2>
            <p style="font-size:0.75rem; color:#94a3b8; margin-bottom:15px;">Hover node or legend to analyze flow.</p>
            <button onclick="resetView()">🌌 RESET GALAXY</button>
            
            <h2 style="margin-top:20px;">📡 SMART PROTOCOLS</h2>
            <div id="protocol-legend">
                <div class="legend-item proto-key" data-proto="Direct Import (Violation)"><div class="line-sample" style="border-top-color:#FF3333;"></div> VIOLATION</div>
                <div class="legend-item proto-key" data-proto="Direct DB Access (Coupling Warning)"><div class="line-sample" style="border-top-color:#FF8C00; border-top-style:dashed;"></div> DB COUPLING</div>
                <div class="legend-item proto-key" data-proto="Django Signal"><div class="line-sample" style="border-top-color:#2ECC71; border-top-style:dashed;"></div> SIGNAL</div>
                <div class="legend-item proto-key" data-proto="API/Gateway Call"><div class="line-sample" style="border-top-color:#FF1493; border-top-style:dotted;"></div> API CALL</div>
                <div class="legend-item proto-key" data-proto="Internal"><div class="line-sample" style="border-top-color:#5DADE2;"></div> INTERNAL</div>
            </div>

            <h2 style="margin-top:20px;">🏝️ ISLAND KEY</h2>
            <div id="island-key"></div>
        </div>

        <div class="panel panel-right">
            <h2>🖤 BLACK HEART HUD</h2>
            <div id="health-hud"></div>
        </div>

        <script>
            const appStats = {json.dumps(app_stats)};
            const nodesData = {json.dumps(nodes)};
            const edgesData = {json.dumps(edges)};
            const islandColors = {json.dumps(island_colors)};

            const hud = document.getElementById('health-hud');
            const key = document.getElementById('island-key');
            
            Object.entries(appStats).forEach(([app, stats]) => {{
                const color = stats.score > 85 ? '#2ecc71' : stats.score > 60 ? '#f1c40f' : '#ef4444';
                const islandCol = islandColors[app] || '#7F8C8D';
                const gap = stats.physical.length - stats.logical.length;
                const gapWarning = gap > 0 ? `<span class="warning">⚠️ ${{gap}} Ghost Files</span>` : '✅ Synced';
                
                hud.innerHTML += `
                    <div class="ui-box health-card" id="card-${{app}}" data-app="${{app}}">
                        <div class="health-row"><span>${{app.toUpperCase()}}</span><span>${{stats.score}}%</span></div>
                        <div class="score-bar"><div class="score-fill" style="width:${{stats.score}}%; background:${{color}}"></div></div>
                        <div class="sub-stats">
                            Physical: ${{stats.physical.length}} | Audited: ${{stats.logical.length}}<br>
                            ${{gapWarning}} | Violations: ${{stats.violations}}
                        </div>
                    </div>`;
                
                key.innerHTML += `
                    <div class="legend-item island-marker" id="marker-${{app}}" data-app="${{app}}">
                        <div class="dot-circle" style="background:${{islandCol}}"></div>
                        ${{app.toUpperCase()}}
                    </div>`;
            }});

            var nodes = new vis.DataSet(nodesData);
            var edges = new vis.DataSet(edgesData);
            
            var network = new vis.Network(document.getElementById('mynetwork'), {{nodes: nodes, edges: edges}}, {{
                nodes: {{ shape: 'box', margin: 10, font: {{ size: 14, color: '#ffffff' }} }},
                edges: {{ smooth: {{ type: 'curvedArrow' }}, selectionWidth: 3 }},
                physics: {{ solver: 'forceAtlas2Based', stabilization: {{ iterations: 100 }} }},
                interaction: {{ hover: true }} 
            }});

            // --- PROTOCOL LEGEND SMART INTERACTION --- //
            document.querySelectorAll('.proto-key').forEach(item => {{
                item.addEventListener('mouseenter', () => {{
                    const targetProto = item.dataset.proto;
                    item.classList.add('legend-active');
                    
                    // Highlight ONLY edges matching this protocol
                    edges.update(edgesData.map(e => ({{
                        id: e.id,
                        color: e.protocol === targetProto ? e.color : 'rgba(255,255,255,0.05)',
                        width: e.protocol === targetProto ? (e.width * 1.5) : 0.5
                    }})));
                    
                    // Highlight ONLY nodes involved in this protocol
                    const involvedNodes = new Set();
                    edgesData.filter(e => e.protocol === targetProto).forEach(e => {{
                        involvedNodes.add(e.from); involvedNodes.add(e.to);
                    }});
                    nodes.update(nodesData.map(n => ({{
                        id: n.id,
                        opacity: involvedNodes.has(n.id) ? 1 : 0.1
                    }})));
                }});
                
                item.addEventListener('mouseleave', () => {{
                    item.classList.remove('legend-active');
                    edges.update(edgesData);
                    nodes.update(nodesData.map(n => ({{ id: n.id, opacity: 1 }})));
                }});
            }});

            // --- SMART PANEL & REVERSE LEGEND LOGIC --- //
            network.on("hoverNode", function (params) {{
                const hoveredNodeId = params.node;
                const nodeData = nodes.get(hoveredNodeId);
                const targetApp = nodeData.group;

                // Sync side panels
                document.querySelectorAll('.health-card').forEach(c => {{
                    if (c.dataset.app === targetApp) {{
                        c.classList.remove('panel-dimmed');
                        c.classList.add('panel-highlight');
                    }} else {{
                        c.classList.remove('panel-highlight');
                        c.classList.add('panel-dimmed');
                    }}
                }});

                document.querySelectorAll('.island-marker').forEach(m => {{
                    m.classList.toggle('panel-dimmed', m.dataset.app !== targetApp);
                }});

                // Sync Legend Protocols: Highlight only protocols used by this node
                const nodeEdges = edgesData.filter(e => e.from === hoveredNodeId || e.to === hoveredNodeId);
                const activeProtos = new Set(nodeEdges.map(e => e.protocol));
                document.querySelectorAll('.proto-key').forEach(k => {{
                    k.classList.toggle('legend-active', activeProtos.has(k.dataset.proto));
                    if (!activeProtos.has(k.dataset.proto)) k.style.opacity = "0.2";
                }});
            }});

            network.on("blurNode", function (params) {{
                document.querySelectorAll('.health-card').forEach(c => c.classList.remove('panel-dimmed', 'panel-highlight'));
                document.querySelectorAll('.island-marker').forEach(m => m.classList.remove('panel-dimmed'));
                document.querySelectorAll('.proto-key').forEach(k => {{
                    k.classList.remove('legend-active');
                    k.style.opacity = "1";
                }});
            }});

            // --- ASYNC CROSS-PANEL SYNC LOGIC (NEW ADDITION) --- //
            function syncAppFocus(targetApp) {{
                // 1. Sync Right Panel (HUD)
                document.querySelectorAll('.health-card').forEach(c => {{
                    if (c.dataset.app === targetApp) {{
                        c.classList.remove('panel-dimmed');
                        c.classList.add('panel-highlight');
                        c.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                    }} else {{
                        c.classList.remove('panel-highlight');
                        c.classList.add('panel-dimmed');
                    }}
                }});

                // 2. Sync Left Panel (Island Key)
                document.querySelectorAll('.island-marker').forEach(m => {{
                    if (m.dataset.app === targetApp) {{
                        m.classList.remove('panel-dimmed');
                        m.classList.add('legend-active');
                    }} else {{
                        m.classList.remove('legend-active');
                        m.classList.add('panel-dimmed');
                    }}
                }});

                // 3. Sync Galaxy Map
                const relevantNodes = new Set();
                nodesData.forEach(n => {{
                    if (n.group === targetApp) relevantNodes.add(n.id);
                }});
                
                nodes.update(nodesData.map(n => ({{
                    id: n.id,
                    opacity: relevantNodes.has(n.id) ? 1 : 0.05
                }})));
                
                edges.update(edgesData.map(e => ({{
                    id: e.id,
                    color: (relevantNodes.has(e.from) || relevantNodes.has(e.to)) ? e.color : 'rgba(255,255,255,0.02)'
                }})));
            }}

            function clearAppFocus() {{
                document.querySelectorAll('.health-card').forEach(c => c.classList.remove('panel-dimmed', 'panel-highlight'));
                document.querySelectorAll('.island-marker').forEach(m => m.classList.remove('panel-dimmed', 'legend-active'));
                
                nodes.update(nodesData.map(n => ({{ id: n.id, opacity: 1 }})));
                edges.update(edgesData);
            }}

            // Attach listeners to Right Panel (Health Cards)
            document.querySelectorAll('.health-card').forEach(card => {{
                card.addEventListener('mouseenter', () => syncAppFocus(card.dataset.app));
                card.addEventListener('mouseleave', () => clearAppFocus());
            }});

            // Attach listeners to Left Panel (Island Markers)
            document.querySelectorAll('.island-marker').forEach(marker => {{
                marker.addEventListener('mouseenter', () => syncAppFocus(marker.dataset.app));
                marker.addEventListener('mouseleave', () => clearAppFocus());
            }});
            // --------------------------------------------------- //

            function resetView() {{
                nodes.update(nodesData.map(n => ({{ id: n.id, hidden: false, opacity: 1 }})));
                edges.update(edgesData);
                document.querySelectorAll('.health-card').forEach(c => c.classList.remove('hidden'));
                network.fit();
            }}

            network.on("doubleClick", function (params) {{
                if (params.nodes.length > 0) {{
                    const targetApp = params.nodes[0].split('.')[0];
                    const relevant = new Set();
                    nodesData.forEach(n => {{ if(n.group === targetApp) relevant.add(n.id); }});
                    edgesData.forEach(e => {{
                        if (e.from.split('.')[0] === targetApp || e.to.split('.')[0] === targetApp) {{
                            relevant.add(e.from); relevant.add(e.to);
                        }}
                    }});
                    nodes.update(nodesData.map(n => ({{ id: n.id, hidden: !relevant.has(n.id) }})));
                    document.querySelectorAll('.health-card').forEach(c => c.classList.toggle('hidden', !c.id.includes(targetApp)));
                    network.fit();
                }}
            }});
        </script>
    </body>
    </html>
    """
    with open(visual_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ AUDIT MANIFEST REGENERATED (WITH FULL FILE LIST & GHOST CHECK)")
    print(f"✅ GALAXY COMMANDER UPDATED (WITH SMART PROTOCOLS & HOVER SYNC)")

if __name__ == "__main__":
    build_audit_fortress()