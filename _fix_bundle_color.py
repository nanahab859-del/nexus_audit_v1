src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# Fix 1: bundle line colour - use violation red instead of blue
# The bundle represents cross-app violations so should be red/orange
# Use edge colour from first edge in bundle if available, else default red
old1 = '''    function redraw() {
        svg.innerHTML = '';
        Object.values(bundles).forEach(bundle => {
            // Get canvas positions of first node in each app
            const posA = network.getPosition(bundle.edges[0].from);
            const posB = network.getPosition(bundle.edges[0].to);
            const domA = network.canvasToDOM(posA);
            const domB = network.canvasToDOM(posB);
            const count = bundle.edges.length;
            const thickness = Math.min(12, 2 + count * 1.5);

            if (bundle.hovered || bundle.clicked) {
                // Fan out individual threads
                bundle.edges.forEach((e, i) => {
                    const pA = network.canvasToDOM(network.getPosition(e.from));
                    const pB = network.canvasToDOM(network.getPosition(e.to));
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', pA.x); line.setAttribute('y1', pA.y);
                    line.setAttribute('x2', pB.x); line.setAttribute('y2', pB.y);
                    line.setAttribute('stroke', '#38bdf8'); line.setAttribute('stroke-width', '1.5');
                    line.setAttribute('opacity', '0.7');
                    svg.appendChild(line);
                });
            } else {
                // Single thick bundled line
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const mx = (domA.x + domB.x) / 2, my = (domA.y + domB.y) / 2 - 40;
                const d = `M ${domA.x} ${domA.y} Q ${mx} ${my} ${domB.x} ${domB.y}`;
                path.setAttribute('d', d);
                path.setAttribute('stroke', '#38bdf8');
                path.setAttribute('stroke-width', thickness);'''

new1 = '''    function redraw() {
        svg.innerHTML = '';
        Object.values(bundles).forEach(bundle => {
            // Get canvas positions of first node in each app
            const posA = network.getPosition(bundle.edges[0].from);
            const posB = network.getPosition(bundle.edges[0].to);
            const domA = network.canvasToDOM(posA);
            const domB = network.canvasToDOM(posB);
            const count = bundle.edges.length;
            const thickness = Math.min(16, 3 + count * 2);
            // Use violation colour from the first edge (red for violations, orange for warnings)
            const bundleColor = bundle.edges[0].color || '#FF3333';

            if (bundle.hovered || bundle.clicked) {
                // Fan out individual threads
                bundle.edges.forEach((e, i) => {
                    const pA = network.canvasToDOM(network.getPosition(e.from));
                    const pB = network.canvasToDOM(network.getPosition(e.to));
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', pA.x); line.setAttribute('y1', pA.y);
                    line.setAttribute('x2', pB.x); line.setAttribute('y2', pB.y);
                    line.setAttribute('stroke', e.color || '#FF3333');
                    line.setAttribute('stroke-width', '2');
                    line.setAttribute('opacity', '0.85');
                    svg.appendChild(line);
                });
            } else {
                // Single thick bundled line
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const mx = (domA.x + domB.x) / 2, my = (domA.y + domB.y) / 2 - 40;
                const d = `M ${domA.x} ${domA.y} Q ${mx} ${my} ${domB.x} ${domB.y}`;
                path.setAttribute('d', d);
                path.setAttribute('stroke', bundleColor);
                path.setAttribute('stroke-width', thickness);'''

if old1 in code:
    code = code.replace(old1, new1, 1)
    print('FIX 1 applied - bundle lines now use violation colours (red/orange)')
    fixes += 1
else:
    print('FIX 1 SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'Total fixes: {fixes}')
