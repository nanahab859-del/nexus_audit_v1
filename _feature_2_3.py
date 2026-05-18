#!/usr/bin/env python3
"""Feature 2.3: Recommendations Search and Filter"""
import os
html_file = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(html_file, 'r', encoding='utf-8') as f:
    code = f.read()
print("\n=== FEATURE 2.3: Search and Filter Controls ===")
# Add filter controls HTML before the generateRecommendations function
old_pattern = '''function generateRecommendations() {{'''
new_pattern = '''    <div style="margin-bottom:16px;display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
        <input id="rec-search" type="text" placeholder="Filter by app, module, or keyword…" 
               style="padding:8px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:4px;flex:1;min-width:200px;" />
        <select id="rec-filter-type" style="padding:8px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:4px;">
            <option value="">All types</option>
            <option value="violation">violation</option>
            <option value="upgrade">upgrade</option>
            <option value="cve">cve</option>
            <option value="complexity">complexity</option>
        </select>
        <select id="rec-filter-priority" style="padding:8px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:4px;">
            <option value="">All priorities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
        </select>
        <span id="rec-counter" style="color:#94a3b8;font-size:.9rem;">Showing N of M</span>
    </div>
function generateRecommendations() {{'''
if old_pattern in code:
    # Need to add the controls div WITHIN the HTML dashboard f-string
    # Find a better location - inside the recommendations tab HTML
    alt_pattern = '''<div id="recommendations" style="'''
    if alt_pattern in code:
        # Insert the filter controls after the tab opening
        code = code.replace(alt_pattern, alt_pattern + '\n        ' + new_pattern.replace('\n', '\n        '), 1)
        print("Added filter controls (alternative)")
else:
    print("NOTE: Adding filter controls requires manual HTML placement")
# Add data attributes to each recommendation card
# Modify generateRecommendations to include data attributes
old_rec_class = '''<div style="border-left:3px solid ${{tc}};padding:14px 18px;margin-bottom:14px;'''
new_rec_class = '''<div class="rec-card" data-rec-type="${{r.rec_type or 'unknown'}}" data-priority="${{(r.priority or 'LOW').toUpperCase()}}" style="border-left:3px solid ${{tc}};padding:14px 18px;margin-bottom:14px;'''
if old_rec_class in code:
    code = code.replace(old_rec_class, new_rec_class, 1)
    print("Added data attributes to recommendation cards")
# Add the filterRecommendations JavaScript function
filter_js = '''
function filterRecommendations() {{
    const searchVal = document.getElementById('rec-search').value.toLowerCase();
    const typeVal = document.getElementById('rec-filter-type').value;
    const priorityVal = document.getElementById('rec-filter-priority').value;
    const cards = document.querySelectorAll('.rec-card');
    let shown = 0;
    cards.forEach(card => {{
        const text = card.textContent.toLowerCase();
        const recType = card.dataset.recType;
        const priority = card.dataset.priority;
        const matchesSearch = text.includes(searchVal);
        const matchesType = !typeVal || recType === typeVal;
        const matchesPriority = !priorityVal || priority === priorityVal;
        const show = matchesSearch && matchesType && matchesPriority;
        card.style.display = show ? 'block' : 'none';
        if (show) shown++;
    }});
    const total = cards.length;
    document.getElementById('rec-counter').textContent = `Showing ${{shown}} of ${{total}}`;
}}
document.addEventListener('DOMContentLoaded', function() {{
    const searchInput = document.getElementById('rec-search');
    const typeFilter = document.getElementById('rec-filter-type');
    const priorityFilter = document.getElementById('rec-filter-priority');
    if (searchInput) {{
        searchInput.addEventListener('input', filterRecommendations);
        typeFilter.addEventListener('change', filterRecommendations);
        priorityFilter.addEventListener('change', filterRecommendations);
        // Initialize counter
        filterRecommendations();
    }}
}});
'''
# Add the filter function before the document population section
if 'document.getElementById(\'recommendations\').innerHTML = generateRecommendations();' in code:
    code = code.replace('document.getElementById(\'recommendations\').innerHTML = generateRecommendations();',
                       filter_js + '\n\ndocument.getElementById(\'recommendations\').innerHTML = generateRecommendations();\nfilterRecommendations();', 1)
    print("Added filterRecommendations JS function")
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(code)
print("\nCompiling html_report.py...")
result = os.system(f"python3 -m py_compile '{html_file}'")
if result == 0:
    print("✓ Syntax OK")
else:
    print(f"✗ Compilation failed")
