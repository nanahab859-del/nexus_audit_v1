import json
import os
from datetime import datetime

def get_connection_type(source, target):
    """Detects the protocol without changing the architectural logic."""
    src_app = source.split('.')[0]
    tgt_app = target.split('.')[0]
    if src_app == tgt_app:
        return "Internal"
    
    target_path = target.lower()
    source_path = source.lower()
    
    if 'signals' in target_path or 'signals' in source_path:
        return "Django Signal"
    if 'gateway' in target_path or 'api' in target_path:
        return "API/Gateway Call"
    if 'consumers' in target_path or 'routing' in target_path:
        return "Websocket/Channel"
    
    return "Direct Import (Violation)"

def build_audit_fortress():
    vault_path = os.path.expanduser('~/my_tools/nexus_audit')
    dna_path = os.path.join(vault_path, 'master_nexus_dna.json')
    visual_html = os.path.join(vault_path, 'visuals/NEXUS_COMMAND_CENTER.html')
    report_md = os.path.join(vault_path, 'visuals/NEXUS_AUDIT_REPORT.md')

    if not os.path.exists(dna_path):
        print("❌ Error: DNA not found!")
        return

    with open(dna_path, 'r') as f:
        dna = json.load(f)

    nodes = []
    edges = []
    full_audit_log = [] # New log for categorized report
    
    island_colors = {
        'nexus_core': '#1ABC9C', 'nexus_economy': '#E67E22',
        'nexus_gaming': '#34495E', 'nexus_gateway': '#F1C40F',
        'nexus_social': '#9B59B6', 'nexus_tournaments': '#3498DB',
        'nexus_content': '#E74C3C'
    }

    # Visual styles for different protocols
    styles = {
        "Direct Import (Violation)": {"color": "#FF3333", "width": 4, "dashes": False},
        "Django Signal": {"color": "#2ECC71", "width": 2, "dashes": [5, 5]},
        "API/Gateway Call": {"color": "#9B59B6", "width": 2, "dashes": [2, 2]},
        "Websocket/Channel": {"color": "#F1C40F", "width": 2, "dashes": False},
        "Internal": {"color": "#5DADE2", "width": 1, "dashes": False}
    }

    # 2. Process Data
    for module, data in dna.items():
        if module == "__main__": continue
        app = module.split('.')[0]
        color = island_colors.get(app, '#7F8C8D')
        
        nodes.append({
            "id": module,
            "label": module.split('.')[-1] + ".py",
            "group": app,
            "color": {"background": color, "border": "#ffffff"},
            "title": f"APP: {app.upper()}<br>FILE: {module}",
            "font": {"color": "white"}
        })

        if 'imports' in data:
            for imp in data['imports']:
                if imp.startswith('nexus_') and imp in dna:
                    imp_app = imp.split('.')[0]
                    is_cross = app != imp_app
                    
                    # NEW: Identify connection protocol
                    conn_type = get_connection_type(module, imp)
                    style = styles.get(conn_type, styles["Internal"])
                    
                    edges.append({
                        "from": module, "to": imp,
                        "color": style["color"],
                        "width": style["width"],
                        "dashes": style["dashes"],
                        "arrows": "to",
                        "isCross": is_cross,
                        "title": f"Protocol: {conn_type}",
                        "connType": conn_type
                    })
                    
                    # Track for report
                    full_audit_log.append({
                        "source": module, "target": imp,
                        "type": conn_type, "from_app": app, "to_app": imp_app
                    })

    # --- GENERATE ENHANCED MARKDOWN REPORT ---
    with open(report_md, 'w') as f:
        f.write(f"# 🛡️ Nexus Architecture & Protocol Audit\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Section 1: Violations
        violations = [l for l in full_audit_log if "Violation" in l['type']]
        f.write("## 🚩 Critical Violations (Direct Imports)\n")
        if violations:
            f.write("| Source | Target | Apps Involved |\n| :--- | :--- | :--- |\n")
            for v in violations:
                f.write(f"| `{v['source']}` | `{v['target']}` | {v['from_app']} -> {v['to_app']} |\n")
        else:
            f.write("✅ **Isolation confirmed.** No direct imports detected.\n")

        # Section 2: Valid Communications
        f.write("\n## 📡 Valid Decoupled Communication\n")
        decoupled = [l for l in full_audit_log if any(x in l['type'] for x in ["Signal", "API", "Websocket"])]
        if decoupled:
            f.write("| Protocol | Source | Target |\n| :--- | :--- | :--- |\n")
            for d in decoupled:
                f.write(f"| **{d['type']}** | `{d['source']}` | `{d['target']}` |\n")

    # --- GENERATE ENHANCED INTERACTIVE HTML ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexus Fortress - Protocol Commander</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            body {{ background: #0b0e14; color: #e2e8f0; margin: 0; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}
            #mynetwork {{ width: 100vw; height: 100vh; }}
            .overlay {{ position: absolute; padding: 20px; z-index: 10; pointer-events: none; }}
            .ui-box {{ 
                background: rgba(15,23,42,0.95); padding: 15px; border-radius: 8px; 
                border: 1px solid #1e293b; pointer-events: auto; margin-bottom: 10px;
            }}
            .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; font-size: 0.8rem; font-weight: bold; }}
            .color-dot {{ width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; border: 1px solid white; }}
            .line-sample {{ width: 30px; height: 0; margin-right: 10px; }}
            button {{ background: #ef4444; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; font-weight: bold; }}
            h2 {{ margin: 0; font-size: 1rem; color: #f8fafc; }}
        </style>
    </head>
    <body>
        <div class="overlay">
            <div class="ui-box">
                <h2>🛰️ NEXUS COMMANDER</h2>
                <p id="status" style="font-size: 0.7rem; color: #94a3b8;">Double-click Island for X-Ray</p>
                <button onclick="resetView()">🌌 RESET GALAXY</button>
            </div>
            
            <div class="ui-box">
                <h2 style="margin-bottom:10px;">📡 PROTOCOLS</h2>
                <div class="legend-item"><div class="line-sample" style="border-top: 4px solid #FF3333;"></div> VIOLATION</div>
                <div class="legend-item"><div class="line-sample" style="border-top: 4px dashed #2ECC71;"></div> SIGNAL</div>
                <div class="legend-item"><div class="line-sample" style="border-top: 4px dotted #9B59B6;"></div> API CALL</div>
                <div class="legend-item"><div class="line-sample" style="border-top: 2px solid #5DADE2;"></div> INTERNAL</div>
            </div>

            <div class="ui-box" id="legend">
                <h2 style="margin-bottom: 10px;">🏝️ ISLAND KEY</h2>
            </div>
        </div>
        <div id="mynetwork"></div>
        <script>
            const islandColors = {json.dumps(island_colors)};
            const legend = document.getElementById('legend');
            for (const [app, color] of Object.entries(islandColors)) {{
                legend.innerHTML += `<div class="legend-item"><div class="color-dot" style="background:${{color}}"></div>${{app.toUpperCase()}}</div>`;
            }}

            var nodesData = {json.dumps(nodes)};
            var edgesData = {json.dumps(edges)};
            var nodes = new vis.DataSet(nodesData);
            var edges = new vis.DataSet(edgesData);
            
            var container = document.getElementById('mynetwork');
            var network = new vis.Network(container, {{nodes: nodes, edges: edges}}, {{
                nodes: {{ shape: 'box', margin: 8, font: {{ size: 14 }} }},
                edges: {{ smooth: {{ type: 'cubicBezier' }} }},
                physics: {{ solver: 'forceAtlas2Based', forceAtlas2Based: {{ gravConstant: -80, centralGravity: 0.005 }} }}
            }});

            network.on("doubleClick", function (params) {{
                if (params.nodes.length > 0) {{
                    var targetId = params.nodes[0];
                    var targetApp = targetId.split('.')[0];
                    var relevantNodes = new Set();
                    nodesData.forEach(n => {{ if(n.group === targetApp) relevantNodes.add(n.id); }});
                    edgesData.forEach(e => {{
                        if (e.isCross) {{
                            if (e.from.split('.')[0] === targetApp) relevantNodes.add(e.to);
                            if (e.to.split('.')[0] === targetApp) relevantNodes.add(e.from);
                        }}
                    }});
                    nodes.update(nodesData.map(n => ({{ id: n.id, hidden: !relevantNodes.has(n.id) }})));
                    network.fit();
                }}
            }});

            function resetView() {{
                nodes.update(nodesData.map(n => ({{ id: n.id, hidden: false }})));
                network.fit();
            }}
        </script>
    </body>
    </html>
    """
    with open(visual_html, 'w') as f:
        f.write(html_content)
    print(f"✅ GALAXY VISUAL: {visual_html}")
    print(f"✅ AUDIT REPORT: {report_md}")

if __name__ == "__main__":
    build_audit_fortress()
