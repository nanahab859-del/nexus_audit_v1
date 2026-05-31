// Web Worker for Fruchterman-Reingold Layout Calculation

self.onmessage = function(e) {
    const { type, payload } = e.data;
    
    if (type === 'CALCULATE_LAYOUT') {
        const { islands, appList, weight } = payload;
        
        const N = appList.length;
        if (N === 0) {
            self.postMessage({ type: 'LAYOUT_COMPLETE', payload: { nodePositions: {} } });
            return;
        }

        const CANVAS_W = 6000;
        const CANVAS_H = 4500;
        const pos = {};
        
        // Initial circular layout
        appList.forEach((app, i) => {
            const angle = (2 * Math.PI * i) / N;
            pos[app] = { 
                x: CANVAS_W/2 + Math.cos(angle) * 700, 
                y: CANVAS_H/2 + Math.sin(angle) * 500 
            };
        });

        const ITER = 150; // Increased iterations for smoother convergence since we're off main thread
        const k = Math.sqrt(CANVAS_W * CANVAS_H / N);

        for (let iter = 0; iter < ITER; iter++) {
            const temp = 300 * (1 - iter / ITER);
            const disp = {};
            appList.forEach(a => disp[a] = {x: 0, y: 0});

            // Repulsion
            for (let i = 0; i < appList.length; i++) {
                for (let j = i+1; j < appList.length; j++) {
                    const a = appList[i], b = appList[j];
                    const dx = pos[a].x - pos[b].x, dy = pos[a].y - pos[b].y;
                    const dist = Math.max(1, Math.sqrt(dx*dx + dy*dy));
                    const f = k*k / dist;
                    disp[a].x += (dx/dist)*f; disp[a].y += (dy/dist)*f;
                    disp[b].x -= (dx/dist)*f; disp[b].y -= (dy/dist)*f;
                }
            }

            // Attraction
            appList.forEach(a => {
                appList.forEach(b => {
                    if (a >= b) return;
                    const w = weight[a] && weight[a][b] ? weight[a][b] : 0;
                    if (!w) return;
                    
                    const dx = pos[b].x - pos[a].x, dy = pos[b].y - pos[a].y;
                    const dist = Math.max(1, Math.sqrt(dx*dx + dy*dy));
                    // Stronger attraction for higher weight
                    const f = dist*dist / k * (1 + w * 0.5);
                    disp[a].x += (dx/dist)*f; disp[a].y += (dy/dist)*f;
                    disp[b].x -= (dx/dist)*f; disp[b].y -= (dy/dist)*f;
                });
            });

            // Apply with temperature and boundary clamping
            appList.forEach(a => {
                const d = Math.sqrt(disp[a].x**2 + disp[a].y**2);
                if (d > 0) {
                    const scale = Math.min(d, temp) / d;
                    pos[a].x = Math.max(200, Math.min(CANVAS_W-200, pos[a].x + disp[a].x * scale));
                    pos[a].y = Math.max(200, Math.min(CANVAS_H-200, pos[a].y + disp[a].y * scale));
                }
            });
            
            // Optionally, we could post 'LAYOUT_STEP' here if we wanted to animate the physics converging.
            // But usually, it's so fast we just want the final result.
        }

        // 4. Assign each node a position inside its island bounding box
        const NODE_W = 220;
        const NODE_H = 70;
        const ISLAND_PAD = 60;

        const nodePositions = {};
        
        appList.forEach(app => {
            const cx = pos[app].x;
            const cy = pos[app].y;
            const nodes = islands[app];
            
            const cols = Math.max(1, Math.ceil(Math.sqrt(nodes.length)));
            const rows = Math.ceil(nodes.length / cols);
            
            const islandW = cols * NODE_W + ISLAND_PAD * 2;
            const islandH = rows * NODE_H + ISLAND_PAD * 2;
            
            nodes.forEach((nid, i) => {
                const col = i % cols;
                const row = Math.floor(i / cols);
                nodePositions[nid] = {
                    x: cx - islandW / 2 + ISLAND_PAD + col * NODE_W + NODE_W / 2,
                    y: cy - islandH / 2 + ISLAND_PAD + row * NODE_H + NODE_H / 2
                };
            });
        });

        self.postMessage({ type: 'LAYOUT_COMPLETE', payload: { nodePositions } });
    }
};
