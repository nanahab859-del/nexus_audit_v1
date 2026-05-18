src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# FIX 1: filterRecommendations() is called bare on line ~1022, crashing because
# rec-counter doesn't exist yet. Add a null guard inside filterRecommendations.
old1 = '''    const counter = document.getElementById('rec-counter');
    counter.textContent = `Showing ${shown} of ${total}`;'''
new1 = '''    const counter = document.getElementById('rec-counter');
    if (counter) counter.textContent = `Showing ${{shown}} of ${{total}}`;'''
if old1 in code:
    code = code.replace(old1, new1, 1)
    print('FIX 1 applied - null guard on rec-counter')
    fixes += 1
else:
    # Try alternate form (already has {{}} escaping)
    old1b = "    const counter = document.getElementById('rec-counter');\n    counter.textContent = `Showing ${{shown}} of ${{total}}`;"
    new1b = "    const counter = document.getElementById('rec-counter');\n    if (counter) counter.textContent = `Showing ${{shown}} of ${{total}}`;"
    if old1b in code:
        code = code.replace(old1b, new1b, 1)
        print('FIX 1b applied - null guard on rec-counter (f-string form)')
        fixes += 1
    else:
        print('FIX 1 SKIP - pattern not found')
        # Show what's near rec-counter
        idx = code.find("rec-counter")
        if idx > 0:
            print('  rec-counter context:', repr(code[idx-50:idx+100]))

# FIX 2: Remove the bare filterRecommendations() call at top level (line ~1022)
# It is called again inside DOMContentLoaded safely - the bare call is redundant and crashes
old2 = '''document.getElementById('recommendations').innerHTML = generateRecommendations();
filterRecommendations();
document.getElementById('manifest').innerHTML'''
new2 = '''document.getElementById('recommendations').innerHTML = generateRecommendations();
document.getElementById('manifest').innerHTML'''
if old2 in code:
    code = code.replace(old2, new2, 1)
    print('FIX 2 applied - removed bare filterRecommendations() crash call')
    fixes += 1
else:
    # Try with {{ escaping
    old2b = "document.getElementById('recommendations').innerHTML = generateRecommendations();\nfilterRecommendations();\ndocument.getElementById('manifest').innerHTML"
    new2b = "document.getElementById('recommendations').innerHTML = generateRecommendations();\ndocument.getElementById('manifest').innerHTML"
    if old2b in code:
        code = code.replace(old2b, new2b, 1)
        print('FIX 2b applied')
        fixes += 1
    else:
        print('FIX 2 SKIP - showing context')
        idx = code.find('generateRecommendations()')
        while idx > 0:
            print('  generateRecommendations() at:', repr(code[idx-20:idx+120]))
            idx = code.find('generateRecommendations()', idx+1)

# FIX 3: Also guard typeFilter and priorityFilter in DOMContentLoaded
# The agent wrote: if (searchInput) { typeFilter.addEventListener(...) }
# but typeFilter could be null too if rec-filter-type wasn't rendered yet
old3 = """    if (searchInput) {{
        searchInput.addEventListener('input', filterRecommendations);
        typeFilter.addEventListener('change', filterRecommendations);
        priorityFilter.addEventListener('change', filterRecommendations);
        // Initialize counter
        filterRecommendations();
    }}"""
new3 = """    if (searchInput) searchInput.addEventListener('input', filterRecommendations);
    if (typeFilter) typeFilter.addEventListener('change', filterRecommendations);
    if (priorityFilter) priorityFilter.addEventListener('change', filterRecommendations);"""
if old3 in code:
    code = code.replace(old3, new3, 1)
    print('FIX 3 applied - null guards on typeFilter and priorityFilter')
    fixes += 1
else:
    print('FIX 3 SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'\nTotal fixes applied: {fixes}')
