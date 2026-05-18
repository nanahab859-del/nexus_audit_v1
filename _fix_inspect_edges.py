src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# In applyInspectLayout(), replace the edges line to only show intra-island edges
# Inter-island edges are handled by the SVG bundle overlay - hide them from vis-network
old = '''    // Apply layout
    network.setOptions({ physics: { enabled: false } });
    network.setData({
        nodes: new vis.DataSet(nodesData.map(n => ({
            ...n,
            x: nodePositions[n.id] ? nodePositions[n.id].x : 0,
            y: nodePositions[n.id] ? nodePositions[n.id].y : 0,
            fixed: true
        }))),
        edges: new vis.DataSet(edgesData)
    });
    network.fit({ animation: { duration: 500 } });
}

function buildBundleOverlay() {'''

new = '''    // Apply layout — hide inter-island edges (handled by SVG bundle overlay)
    const intraIslandEdges = edgesData.filter(e => {
        const srcApp = (e.from || '').split('.')[0];
        const tgtApp = (e.to   || '').split('.')[0];
        return srcApp === tgtApp;  // only same-app edges visible in vis-network
    });

    network.setOptions({ physics: { enabled: false } });
    network.setData({
        nodes: new vis.DataSet(nodesData.map(n => ({
            ...n,
            x: nodePositions[n.id] ? nodePositions[n.id].x : 0,
            y: nodePositions[n.id] ? nodePositions[n.id].y : 0,
            fixed: true
        }))),
        edges: new vis.DataSet(intraIslandEdges)
    });
    network.fit({ animation: { duration: 500 } });
}

function buildBundleOverlay() {'''

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - inter-island edges hidden in inspect mode')
else:
    print('SKIP - pattern not found')
    # Show what is there
    idx = code.find('// Apply layout')
    print('Context:', repr(code[idx:idx+300]))

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
