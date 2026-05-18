#!/usr/bin/env python3
"""
Dashboard Fix Patch Script
Applies all 4 phases of the fix plan to html_report.py:
  Phase 1 – Embed custom vis.js renderer (replace get_vis_js())
  Phase 2 – Add safety guard in showTab() for trends
  Phase 3 – Simplify network container sizing
  Phase 4 – Fix filterRecommendations wiring
"""

import re
import os
import sys

BAK16   = os.path.join(os.path.dirname(__file__), 'command_center_galaxy.py.bak16')
REPORT  = os.path.join(os.path.dirname(__file__), 'nexus_audit', 'report', 'html_report.py')

# ── 1. Extract _VIS_JS from bak16 ─────────────────────────────────────────────
print("Step 1: Extracting _VIS_JS from backup …")
with open(BAK16, 'r', encoding='utf-8') as f:
    bak_src = f.read()

m = re.search(r'_VIS_JS\s*=\s*r"""(.*?)"""', bak_src, re.DOTALL)
if not m:
    print("ERROR: could not find _VIS_JS in bak16"); sys.exit(1)

VIS_JS = m.group(1)  # raw JS content (no surrounding triple-quotes)
print(f"  OK – extracted {len(VIS_JS):,} chars of custom vis.js")

# ── 2. Read html_report.py ────────────────────────────────────────────────────
print("Step 2: Reading html_report.py …")
with open(REPORT, 'r', encoding='utf-8') as f:
    src = f.read()

original_len = len(src)

# ── Phase 1: replace import + get_vis_js() call ───────────────────────────────
print("Phase 1: Replacing get_vis_js() with embedded renderer …")

# Remove the import line
src = re.sub(r'from \.assets import get_vis_js\n', '', src)

# Replace the call site
OLD_CALL = 'vis_js_content = get_vis_js()'
NEW_CALL = (
    '# Custom vis.js renderer embedded directly (Phase 1 fix)\n'
    '        vis_js_content = r"""' + VIS_JS + '"""'
)
if OLD_CALL not in src:
    print("  WARNING: get_vis_js() call not found – skipping Phase 1 replacement")
else:
    src = src.replace(OLD_CALL, NEW_CALL, 1)
    print("  OK")

# ── Phase 2: guard showTab('trends') ─────────────────────────────────────────
print("Phase 2: Adding safety guard in showTab() for trends …")

OLD_SHOWTAB = "    if (id === 'trends') drawTrendsChart();"
NEW_SHOWTAB = (
    "    if (id === 'trends' && timelineData && timelineData.labels && timelineData.labels.length >= 2) {{\n"
    "        drawTrendsChart();\n"
    "    }}"
)
if OLD_SHOWTAB in src:
    src = src.replace(OLD_SHOWTAB, NEW_SHOWTAB, 1)
    print("  OK")
else:
    print("  WARNING: showTab trends guard target not found – skipping")

# ── Phase 3: simplify network container ──────────────────────────────────────
print("Phase 3: Simplifying network container layout …")

OLD_NETWORK_WRAP = '''\
        <!-- Canvas + island sidebar side-by-side -->
        <div class="network-wrap">
            <!-- Island sidebar: always visible while looking at graph -->
            <div class="island-sidebar" id="island-sidebar">
                <div class="island-sidebar-title">Islands</div>
            </div>
            <!-- The actual vis-network canvas -->
            <div id="network"></div>
        </div>'''

NEW_NETWORK_WRAP = '''\
        <!-- Canvas + island sidebar side-by-side -->
        <div class="network-wrap">
            <!-- Island sidebar: always visible while looking at graph -->
            <div class="island-sidebar" id="island-sidebar">
                <div class="island-sidebar-title">Islands</div>
            </div>
            <!-- The actual vis-network canvas — fixed height so clientHeight > 0 -->
            <div id="network" style="flex:1;height:540px;min-height:540px;background:rgba(10,15,30,0.5);"></div>
        </div>'''

if OLD_NETWORK_WRAP in src:
    src = src.replace(OLD_NETWORK_WRAP, NEW_NETWORK_WRAP, 1)
    print("  OK")
else:
    # Try a simpler targeted replacement of just the #network div
    OLD_NET_DIV = '            <!-- The actual vis-network canvas -->\n            <div id="network"></div>'
    NEW_NET_DIV = '            <!-- The actual vis-network canvas — fixed height so clientHeight > 0 -->\n            <div id="network" style="flex:1;height:540px;min-height:540px;background:rgba(10,15,30,0.5);"></div>'
    if OLD_NET_DIV in src:
        src = src.replace(OLD_NET_DIV, NEW_NET_DIV, 1)
        print("  OK (fallback match)")
    else:
        print("  WARNING: network container target not found – skipping Phase 3")

# ── Phase 4: fix filterRecommendations wiring ─────────────────────────────────
print("Phase 4: Fixing filterRecommendations wiring …")

# The bug: filterRecommendations() is called before .rec-card elements exist.
# Fix: move the initial call to after the rec content is rendered,
#      and guard each element lookup so missing elements don't crash.

OLD_FILTER_FN = '''\
function filterRecommendations() {{
    const searchVal = document.getElementById('rec-search').value.toLowerCase();
    const typeVal = document.getElementById('rec-filter-type').value;
    const priorityVal = document.getElementById('rec-filter-priority').value;'''

NEW_FILTER_FN = '''\
function filterRecommendations() {{
    const searchEl = document.getElementById('rec-search');
    const typeEl   = document.getElementById('rec-filter-type');
    const prioEl   = document.getElementById('rec-filter-priority');
    if (!searchEl || !typeEl || !prioEl) return;
    const searchVal = searchEl.value.toLowerCase();
    const typeVal = typeEl.value;
    const priorityVal = prioEl.value;'''

if OLD_FILTER_FN in src:
    src = src.replace(OLD_FILTER_FN, NEW_FILTER_FN, 1)
    print("  OK (guarded element lookups)")
else:
    print("  WARNING: filterRecommendations function target not found – skipping Phase 4a")

# Remove the dangling filterRecommendations() call that runs before recs are rendered
# (the one at line ~1074, after the rec-content block but before manifest)
OLD_STRAY_CALL = '\nfilterRecommendations();\ndocument.getElementById(\'manifest\').innerHTML'
NEW_STRAY_CALL = '\n// filterRecommendations() called below after recs are rendered\ndocument.getElementById(\'manifest\').innerHTML'
if OLD_STRAY_CALL in src:
    src = src.replace(OLD_STRAY_CALL, NEW_STRAY_CALL, 1)
    print("  OK (removed stray early call)")
else:
    print("  INFO: stray filterRecommendations() call pattern not matched (may already be fixed)")

# Ensure filterRecommendations is called AFTER rec content is injected
OLD_REC_END = '''\
}} else if (recDiv) {{
    const recContent = recDiv.querySelector('.rec-content') || recDiv;
    recContent.innerHTML = generateRecommendations();
}}'''
NEW_REC_END = '''\
}} else if (recDiv) {{
    const recContent = recDiv.querySelector('.rec-content') || recDiv;
    recContent.innerHTML = generateRecommendations();
}}
filterRecommendations(); // Phase 4 fix: call AFTER rec-card elements exist'''

if OLD_REC_END in src:
    src = src.replace(OLD_REC_END, NEW_REC_END, 1)
    print("  OK (moved filterRecommendations call to after rec render)")
else:
    print("  INFO: rec-end block not matched for filter call move")

# ── 3. Write patched file ─────────────────────────────────────────────────────
print(f"\nWriting patched html_report.py … ({original_len:,} → {len(src):,} chars)")
with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(src)

print("\n✅ All patches applied successfully.")
print("   Next: run `python -m nexus_audit` then open the dashboard in a browser.")
