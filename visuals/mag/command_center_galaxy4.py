import json
import os
from datetime import datetime
import urllib.request
import urllib.error
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import hashlib

# Fallback vis-network CDN URLs (multiple fallbacks for reliability)
VIS_CDN_FALLBACKS = [
    "https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js",
    "https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js",
    "https://cdn.skypack.dev/vis-network@9.1.2"
]

def find_cycles(dna: Dict) -> List[List[str]]:
    """Detects circular dependencies using DFS with enhanced detection."""
    cycles = []
    visited = set()
    path = []
    cycle_details = []
    
    def visit(node: str, depth: int = 0):
        if node in path:
            cycle_start_idx = path.index(node)
            cycle = path[cycle_start_idx:] + [node]
            # Avoid duplicate cycles (same set of nodes in different order)
            cycle_set = frozenset(cycle)
            if not any(frozenset(c) == cycle_set for c in cycles):
                cycles.append(cycle)
                # Calculate cycle length and impact
                cycle_details.append({
                    'nodes': cycle,
                    'length': len(cycle),
                    'depth': depth,
                    'severity': 'high' if len(cycle) <= 3 else 'medium'
                })
            return
        
        if node in visited:
            return
        
        visited.add(node)
        path.append(node)
        
        imports = dna.get(node, {}).get('imports', [])
        for imp in imports:
            if imp in dna:  # Only track internal imports
                visit(imp, depth + 1)
        
        path.pop()
    
    for module in dna:
        if module != "__main__":
            visit(module)
    
    return list(set([tuple(c) for c in cycles])), cycle_details

def get_connection_type_enhanced(source: str, target: str, dna: Dict, source_data: Dict = None) -> Tuple[str, int]:
    """
    Enhanced protocol detection using actual import analysis.
    Returns (connection_type, severity_weight)
    """
    src_app = source.split('.')[0]
    tgt_app = target.split('.')[0]
    
    # Internal connections are always allowed
    if src_app == tgt_app:
        return "Internal", 0
    
    # Get actual import details if available
    source_imports = dna.get(source, {}).get('imports', [])
    is_direct_import = target in source_imports
    
    # Heuristic-based detection with actual import verification
    tp, sp = target.lower(), source.lower()
    
    # Check for Django signals (actual signal usage)
    if 'signals' in tp or 'signals' in sp:
        # Verify it's actually a signal (check if it imports from django.dispatch)
        target_data = dna.get(target, {})
        if 'django.dispatch' in str(target_data.get('imports', [])):
            return "Django Signal", 5
    
    # API/Gateway calls (check for gateway patterns)
    if 'gateway' in tp or 'api' in tp or 'gateway' in sp or 'api' in sp:
        if is_direct_import:
            return "API/Gateway Call", 8
    
    # WebSocket/Channel detection
    if 'consumers' in tp or 'routing' in tp or 'websocket' in tp:
        return "Websocket/Channel", 6
    
    # Async Task/Celery detection
    if 'tasks' in tp or 'celery' in tp:
        target_data = dna.get(target, {})
        if 'celery' in str(target_data.get('imports', [])) or 'tasks' in target:
            return "Async Task/Celery", 7
    
    # Direct DB Access (most severe)
    if 'models' in tp:
        return "Direct DB Access (Coupling Warning)", 15
    
    # Direct Import (cross-app violation)
    if is_direct_import:
        return "Direct Import (Violation)", 10
    
    return "Unknown", 5

def calculate_improved_score(stats: Dict, app: str, cycle_info: List) -> int:
    """Enhanced scoring with weighted violations and cycle penalties."""
    violations_weight = stats[app]["violations"] * 10
    coupling_weight = stats[app]["coupling"] * 15  # DB coupling is worse
    
    # Calculate cycle penalty
    cycle_penalty = 0
    for cycle in cycle_info:
        if app in cycle['nodes']:
            if cycle['severity'] == 'high':
                cycle_penalty += 20
            else:
                cycle_penalty += 10
    
    # Check for circular dependencies within the app
    internal_cycles = 0
    for cycle in cycle_info:
        apps_in_cycle = set(node.split('.')[0] for node in cycle['nodes'])
        if app in apps_in_cycle and len(apps_in_cycle) == 1:
            internal_cycles += 1
    cycle_penalty += internal_cycles * 15
    
    # Integrity gap penalty
    integrity_gap = len(stats[app]["physical"]) - len(stats[app]["logical"])
    integrity_penalty = integrity_gap * 8 if integrity_gap > 0 else 0
    
    # Base score calculation
    base_score = 100 - violations_weight - coupling_weight - cycle_penalty - integrity_penalty
    
    # Ensure score is within bounds
    score = max(0, min(100, base_score))
    
    # Add bonus for good practices
    if stats[app]["healthy"] > stats[app]["violations"] * 2:
        score = min(100, score + 5)
    
    return score

def safe_url_read(url: str, timeout: int = 10) -> Optional[str]:
    """Safely read URL content with timeout and error handling."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"⚠️ Failed to load {url}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error loading {url}: {e}")
        return None

def load_vis_js() -> Tuple[str, bool]:
    """Load vis-network JS from CDN with fallbacks."""
    for url in VIS_CDN_FALLBACKS:
        print(f"Attempting to load vis-network from: {url}")
        content = safe_url_read(url)
        if content:
            print(f"✅ Successfully loaded from {url}")
            return content, True
    
    print("❌ Failed to load vis-network from all CDNs. Using minimal fallback.")
    # Minimal fallback that shows an error message
    fallback = """
    console.error('vis-network library failed to load. Please check your internet connection.');
    alert('Network visualization library failed to load. The graph may not display correctly.');
    """
    return fallback, False

def sanitize_html_content(text: str) -> str:
    """Basic HTML sanitization to prevent XSS."""
    if not text:
        return ""
    # Replace potentially dangerous characters
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def build_audit_fortress() -> None:
    """Main auditing function with all improvements."""
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
    except json.JSONDecodeError as e:
        print(f"❌ Error: DNA file is malformed: {e}")
        return
    except Exception as e:
        print(f"❌ Error reading DNA file: {e}")
        return

    # Load physical inventory with better filtering
    physical_inventory = []
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r', encoding='utf-8') as f:
            physical_inventory = [
                line.strip() for line in f if line.strip() 
                and not line.strip().endswith('__init__.py')  # Exclude __init__.py
                and 'migrations' not in line  # Exclude migrations entirely
                and line.strip() != 'manage'  # Exclude manage.py
            ]

    # Detect cycles
    cycles, cycle_details = find_cycles(dna)
    
    nodes, edges = [], []
    app_stats = {}
    protocol_logs = {
        "Direct Import (Violation)": [],
        "Direct DB Access (Coupling Warning)": [],
        "Django Signal": [],
        "API/Gateway Call": [],
        "Websocket/Channel": [],
        "Async Task/Celery": [],
        "Internal": [],
        "Unknown": []
    }
    
    # Track import depth for bacon field analysis
    bacon_depths = defaultdict(list)
    
    island_colors = {
        'nexus_core': '#1ABC9C', 
        'nexus_economy': '#E67E22', 
        'nexus_gaming': '#34495E',
        'nexus_gateway': '#F1C40F', 
        'nexus_social': '#9B59B6', 
        'nexus_tournaments': '#3498DB',
        'nexus_content': '#E74C3C'
    }

    # Pre-fill stats from physical inventory
    for module in physical_inventory:
        app = module.split('.')[0]
        if app not in app_stats:
            app_stats[app] = {
                "physical": [], 
                "logical": [], 
                "violations": 0, 
                "coupling": 0, 
                "healthy": 0, 
                "score": 100,
                "bacon_min": float('inf'),
                "bacon_max": 0,
                "bacon_avg": 0
            }
        app_stats[app]["physical"].append(module)

    # 1. Full Discovery and bacon analysis
    for module in sorted(dna.keys()):
        if module == "__main__": 
            continue
        
        app = module.split('.')[0]
        if app not in app_stats:
            app_stats[app] = {
                "physical": [], 
                "logical": [], 
                "violations": 0, 
                "coupling": 0, 
                "healthy": 0, 
                "score": 100,
                "bacon_min": float('inf'),
                "bacon_max": 0,
                "bacon_avg": 0
            }
        app_stats[app]["logical"].append(module)
        
        # Track bacon depth
        bacon_value = dna[module].get('bacon', 0)
        bacon_depths[app].append(bacon_value)
        app_stats[app]["bacon_min"] = min(app_stats[app]["bacon_min"], bacon_value)
        app_stats[app]["bacon_max"] = max(app_stats[app]["bacon_max"], bacon_value)

    # Calculate average bacon depth
    for app in app_stats:
        if bacon_depths[app]:
            app_stats[app]["bacon_avg"] = sum(bacon_depths[app]) / len(bacon_depths[app])

    # 2. Enhanced Connection Mapping
    for module, data in dna.items():
        if module == "__main__": 
            continue
        
        app = module.split('.')[0]
        color = island_colors.get(app, '#7F8C8D')
        
        # Add bacon depth to tooltip
        bacon_value = data.get('bacon', 0)
        title = f"<b>APP:</b> {app.upper()}<br><b>FILE:</b> {module}<br><b>DEPTH:</b> {bacon_value}"
        
        nodes.append({
            "id": module, 
            "label": module.split('.')[-1] + ".py", 
            "group": app,
            "color": {"background": color, "border": "#ffffff"},
            "title": title, 
            "font": {"color": "white"},
            "bacon": bacon_value  # Store for potential use in coloring
        })

        if 'imports' in data:
            for imp in data['imports']:
                # Check if it's an internal import (starts with nexus_)
                if imp.startswith('nexus_') and imp in dna:
                    conn_type, severity = get_connection_type_enhanced(module, imp, dna, data)
                    protocol_logs[conn_type].append({"src": module, "tgt": imp})
                    
                    # Update stats with severity
                    if "Violation" in conn_type:
                        app_stats[app]["violations"] += 1
                    elif "Warning" in conn_type or "Coupling" in conn_type:
                        app_stats[app]["coupling"] += 1
                    elif conn_type != "Internal":
                        app_stats[app]["healthy"] += 1

                    # Style determination with severity-based width
                    style_color, is_dashed, width = "#5DADE2", False, 1
                    if "Violation" in conn_type:
                        style_color, width = "#FF3333", 3
                    elif "Warning" in conn_type or "Coupling" in conn_type:
                        style_color, is_dashed = "#FF8C00", True 
                        width = 2
                    elif "Signal" in conn_type:
                        style_color, is_dashed = "#2ECC71", True
                    elif "API" in conn_type:
                        style_color, is_dashed = "#FF1493", [2, 4]
                    elif "Websocket" in conn_type:
                        style_color, is_dashed = "#9B59B6", True
                    elif "Async" in conn_type or "Celery" in conn_type:
                        style_color, is_dashed = "#F39C12", [4, 4]

                    edges.append({
                        "from": module, 
                        "to": imp, 
                        "color": style_color, 
                        "width": width,
                        "dashes": is_dashed, 
                        "arrows": "to", 
                        "title": f"<b>{conn_type}</b><br>Severity: {severity}",
                        "protocol": conn_type,
                        "severity": severity
                    })

    # Ghost Files & Integrity (improved)
    ghost_files = []
    for f in physical_inventory:
        # Skip known non-module files
        if f == 'manage' or f.endswith('__init__.py') or 'migrations' in f:
            continue
        if f not in dna:
            ghost_files.append(f)

    # Calculate improved scores with cycle detection
    for app in app_stats:
        app_stats[app]["score"] = calculate_improved_score(app_stats, app, cycle_details)

    # --- MD MANIFEST GENERATION (Enhanced) ---
    with open(report_md, 'w', encoding='utf-8') as f:
        f.write(f"# 🛡️ NEXUS MASTER AUDIT MANIFEST\n")
        f.write(f"**Audit Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Circular Dependencies Section
        if cycles:
            f.write("## 🔄 CIRCULAR DEPENDENCIES DETECTED\n")
            f.write("| Severity | Cycle Length | Modules Involved |\n")
            f.write("| :--- | :--- | :--- |\n")
            for cycle_info in cycle_details:
                severity_emoji = "🔴" if cycle_info['severity'] == 'high' else "🟡"
                modules_str = " → ".join(cycle_info['nodes'])
                f.write(f"| {severity_emoji} {cycle_info['severity'].upper()} | {cycle_info['length']} | `{modules_str}` |\n")
            f.write("\n")
        
        # Ghost Files
        if ghost_files:
            f.write("## 👻 CRITICAL: GHOST FILES DETECTED\n")
            for ghost in ghost_files:
                f.write(f"- `{ghost}` (File exists in inventory but not in DNA)\n")
            f.write("\n")
        
        # Global Fleet Health with enhanced metrics
        f.write("## 🖤 GLOBAL FLEET HEALTH\n")
        f.write("| Island | Score | Physical | Audited | Violations | DB Coupling | Healthy | Depth (min/avg/max) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for app, s in sorted(app_stats.items()):
            emoji = "💚" if s['score'] > 85 else "💛" if s['score'] > 60 else "❤️"
            depth_str = f"{s['bacon_min']:.0f}/{s['bacon_avg']:.1f}/{s['bacon_max']:.0f}"
            f.write(f"| **{app.upper()}** | {emoji} {s['score']:.0f}% | {len(s['physical'])} | {len(s['logical'])} | {s['violations']} | {s['coupling']} | {s['healthy']} | {depth_str} |\n")
        
        # Protocol logs (including all types)
        for p_type, logs in protocol_logs.items():
            if p_type == "Internal" or p_type == "Unknown":
                continue
            f.write(f"\n## 📡 {p_type.upper()}\n")
            if not logs:
                f.write(f"✅ No records for {p_type}.\n")
            else:
                f.write("| Source File | Target File |\n")
                f.write("| :--- | :--- |\n")
                for log in logs:
                    f.write(f"| `{log['src']}` | `{log['tgt']}` |\n")
        
        # Full Project Manifest
        f.write(f"\n## 📋 FULL PROJECT MANIFEST (EVERY AUDITED FILE)\n")
        f.write("| File Path | App Island | Bacon Depth |\n")
        f.write("| :--- | :--- | :--- |\n")
        for module in sorted(dna.keys()):
            if module == "__main__": 
                continue
            bacon_value = dna[module].get('bacon', 0)
            f.write(f"| {module} | {module.split('.')[0]} | {bacon_value} |\n")

    # --- HTML COMMAND CENTER GENERATION (Enhanced) ---
    vis_js_content, cdn_success = load_vis_js()
    
    # Add CDN warning if needed
    cdn_warning = ""
    if not cdn_success:
        cdn_warning = """
        <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; background: #ff4444; color: white; padding: 10px; border-radius: 5px; font-size: 12px;">
            ⚠️ Network visualization library could not be loaded. The graph may not display correctly. Please check your internet connection.
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexus Commander - Enhanced Audit System</title>
        <script type="text/javascript">{vis_js_content}</script>
        <style>
            body {{ background: #0b1120; color: #f8fafc; margin: 0; font-family: 'Inter', system-ui, sans-serif; overflow: hidden; }}
            #mynetwork {{ width: 100vw; height: 100vh; position: absolute; z-index: 1; }}
            .panel {{ position: absolute; z-index: 100; background: rgba(15,23,42,0.9); backdrop-filter: blur(8px); border: 1px solid #1e293b; padding: 15px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
            .panel-left {{ top: 20px; left: 20px; width: 280px; max-height: 90vh; overflow-y: auto; }}
            .panel-right {{ top: 20px; right: 20px; width: 340px; height: 90vh; overflow-y: auto; scroll-behavior: smooth; }}
            .ui-box {{ background: rgba(30,41,59,0.5); padding: 12px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #334155; transition: all 0.3s ease; cursor: pointer; }}
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
            .cycle-warning {{ color: #ff6b6b; font-weight: bold; }}
            .panel-dimmed {{ opacity: 0.15; filter: grayscale(80%); }}
            .panel-highlight {{ opacity: 1; transform: scale(1.02); border-color: #38bdf8; background: rgba(30,41,59,0.9); }}
            .legend-active {{ color: #38bdf8; opacity: 1 !important; transform: translateX(5px); }}
            .severity-high {{ border-left: 3px solid #ff4444; }}
            .severity-medium {{ border-left: 3px solid #ffaa44; }}
        </style>
    </head>
    <body>
        <div id="mynetwork"></div>
        {cdn_warning}

        <div class="panel panel-left">
            <h2>🛰️ NEXUS COMMANDER (ENHANCED)</h2>
            <p style="font-size:0.75rem; color:#94a3b8; margin-bottom:15px;">Hover node or legend to analyze flow. Cycles detected: {len(cycles)}</p>
            <button onclick="resetView()">🌌 RESET GALAXY</button>
            
            <h2 style="margin-top:20px;">📡 SMART PROTOCOLS</h2>
            <div id="protocol-legend">
                <div class="legend-item proto-key" data-proto="Direct Import (Violation)"><div class="line-sample" style="border-top-color:#FF3333;"></div> VIOLATION (10 pts)</div>
                <div class="legend-item proto-key" data-proto="Direct DB Access (Coupling Warning)"><div class="line-sample" style="border-top-color:#FF8C00; border-top-style:dashed;"></div> DB COUPLING (15 pts)</div>
                <div class="legend-item proto-key" data-proto="Django Signal"><div class="line-sample" style="border-top-color:#2ECC71; border-top-style:dashed;"></div> SIGNAL (5 pts)</div>
                <div class="legend-item proto-key" data-proto="API/Gateway Call"><div class="line-sample" style="border-top-color:#FF1493; border-top-style:dotted;"></div> API CALL (8 pts)</div>
                <div class="legend-item proto-key" data-proto="Websocket/Channel"><div class="line-sample" style="border-top-color:#9B59B6; border-top-style:dashed;"></div> WEBSOCKET (6 pts)</div>
                <div class="legend-item proto-key" data-proto="Async Task/Celery"><div class="line-sample" style="border-top-color:#F39C12; border-top-style:dashed;"></div> ASYNC/CELERY (7 pts)</div>
                <div class="legend-item proto-key" data-proto="Internal"><div class="line-sample" style="border-top-color:#5DADE2;"></div> INTERNAL (0 pts)</div>
            </div>

            <h2 style="margin-top:20px;">🏝️ ISLAND KEY</h2>
            <div id="island-key"></div>
            
            {f'<h2 style="margin-top:20px;">🔄 CIRCULAR DEPENDENCIES</h2><div id="cycle-list"></div>' if cycles else ''}
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
            const cycles = {json.dumps(cycle_details)};

            const hud = document.getElementById('health-hud');
            const key = document.getElementById('island-key');
            
            // Add cycle information to HUD
            if (cycles.length > 0) {{
                const cycleDiv = document.createElement('div');
                cycleDiv.className = 'ui-box';
                cycleDiv.innerHTML = '<div class="health-row"><span>⚠️ CYCLES DETECTED</span><span>' + cycles.length + '</span></div>' +
                    '<div class="sub-stats">' + cycles.filter(c => c.severity === 'high').length + ' high severity cycles</div>';
                hud.appendChild(cycleDiv);
            }}
            
            Object.entries(appStats).forEach(([app, stats]) => {{
                const color = stats.score > 85 ? '#2ecc71' : stats.score > 60 ? '#f1c40f' : '#ef4444';
                const islandCol = islandColors[app] || '#7F8C8D';
                const gap = stats.physical.length - stats.logical.length;
                const gapWarning = gap > 0 ? `<span class="warning">⚠️ ${{gap}} Ghost Files</span>` : '✅ Synced';
                const severityClass = stats.score <= 60 ? 'severity-high' : (stats.score <= 85 ? 'severity-medium' : '');
                
                hud.innerHTML += `
                    <div class="ui-box health-card ${{severityClass}}" id="card-${{app}}" data-app="${{app}}">
                        <div class="health-row"><span>${{app.toUpperCase()}}</span><span>${{stats.score}}%</span></div>
                        <div class="score-bar"><div class="score-fill" style="width:${{stats.score}}%; background:${{color}}"></div></div>
                        <div class="sub-stats">
                            Physical: ${{stats.physical.length}} | Audited: ${{stats.logical.length}}<br>
                            ${{gapWarning}} | Violations: ${{stats.violations}} | DB Coupling: ${{stats.coupling}}<br>
                            Depth: ${{stats.bacon_min.toFixed(0)}}/${{stats.bacon_avg.toFixed(1)}}/${{stats.bacon_max.toFixed(0)}}
                        </div>
                    </div>`;
                
                key.innerHTML += `
                    <div class="legend-item island-marker" id="marker-${{app}}" data-app="${{app}}">
                        <div class="dot-circle" style="background:${{islandCol}}"></div>
                        ${{app.toUpperCase()}}
                    </div>`;
            }});
            
            // Add cycle list to left panel
            if (cycles.length > 0) {{
                const cycleList = document.getElementById('cycle-list');
                cycles.forEach((cycle, idx) => {{
                    const cycleDiv = document.createElement('div');
                    cycleDiv.className = 'legend-item';
                    cycleDiv.style.cursor = 'pointer';
                    cycleDiv.style.borderLeft = cycle.severity === 'high' ? '3px solid #ff4444' : '3px solid #ffaa44';
                    cycleDiv.style.paddingLeft = '10px';
                    cycleDiv.style.marginBottom = '10px';
                    cycleDiv.innerHTML = `
                        <div style="font-size:0.7rem;">
                            <span style="color:#ff6b6b">⚠️ Cycle ${{idx + 1}}</span><br>
                            <span style="font-size:0.6rem;">${{cycle.nodes.join(' → ')}}</span>
                        </div>
                    `;
                    cycleDiv.onclick = () => {{
                        const nodes = cycle.nodes;
                        const relevantNodes = new Set(nodes);
                        nodes.update(nodesData.map(n => ({{
                            id: n.id,
                            opacity: relevantNodes.has(n.id) ? 1 : 0.1,
                            color: relevantNodes.has(n.id) ? n.color : {{ background: '#555', border: '#777' }}
                        }})));
                        edges.update(edgesData.map(e => ({{
                            id: e.id,
                            color: (relevantNodes.has(e.from) && relevantNodes.has(e.to)) ? e.color : 'rgba(255,255,255,0.02)'
                        }})));
                    }};
                    cycleList.appendChild(cycleDiv);
                }});
            }}

            var nodes = new vis.DataSet(nodesData);
            var edges = new vis.DataSet(edgesData);
            
            var network = new vis.Network(document.getElementById('mynetwork'), {{nodes: nodes, edges: edges}}, {{
                nodes: {{ shape: 'box', margin: 10, font: {{ size: 14, color: '#ffffff' }} }},
                edges: {{ smooth: {{ type: 'curvedArrow' }}, selectionWidth: 3 }},
                physics: {{ 
                    solver: 'forceAtlas2Based', 
                    stabilization: {{ iterations: 150 }},
                    timestep: 0.5,
                    adaptiveTimestep: true
                }},
                interaction: {{ hover: true, tooltipDelay: 200 }} 
            }});

            // --- PROTOCOL LEGEND SMART INTERACTION --- //
            document.querySelectorAll('.proto-key').forEach(item => {{
                item.addEventListener('mouseenter', () => {{
                    const targetProto = item.dataset.proto;
                    item.classList.add('legend-active');
                    
                    edges.update(edgesData.map(e => ({{
                        id: e.id,
                        color: e.protocol === targetProto ? e.color : 'rgba(255,255,255,0.05)',
                        width: e.protocol === targetProto ? (e.width * 1.5) : 0.5
                    }})));
                    
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

            // --- CROSS-PANEL SYNC LOGIC --- //
            function syncAppFocus(targetApp) {{
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

                document.querySelectorAll('.island-marker').forEach(m => {{
                    if (m.dataset.app === targetApp) {{
                        m.classList.remove('panel-dimmed');
                        m.classList.add('legend-active');
                    }} else {{
                        m.classList.remove('legend-active');
                        m.classList.add('panel-dimmed');
                    }}
                }});

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

    print(f"✅ AUDIT MANIFEST REGENERATED (WITH CYCLES & ENHANCED METRICS)")
    print(f"✅ GALAXY COMMANDER UPDATED (WITH INTERACTIVE SIDEPANELS)")

if __name__ == "__main__":
    build_audit_fortress()