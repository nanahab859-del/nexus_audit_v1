import re

src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Find exact boundaries of the stub
# Starts at: "        # Custom vis.js renderer embedded directly (Phase 1 fix)"
# Ends at:   "})(typeof window !== 'undefined' ? window : this);\n\"\"\""
stub_start_marker = '        # Custom vis.js renderer embedded directly (Phase 1 fix)\n        vis_js_content = r"""'
stub_end_marker = '})(typeof window !== \'undefined\' ? window : this);\n"""'

start_idx = code.find(stub_start_marker)
end_idx = code.find(stub_end_marker, start_idx)

if start_idx < 0:
    print('SKIP - stub start marker not found')
    exit()

if end_idx < 0:
    print('SKIP - stub end marker not found')
    # Try to find approximate end
    idx = code.find('vis.DataSet = DataSet', start_idx)
    print(f'  vis.DataSet = DataSet at char {idx}')
    print(f'  Context: {repr(code[idx:idx+200])}')
    exit()

end_idx += len(stub_end_marker)
stub = code[start_idx:end_idx]
print(f'Stub found: chars {start_idx}-{end_idx} ({end_idx-start_idx} chars = {(end_idx-start_idx)//1024}KB)')
print(f'Stub starts: {repr(stub[:60])}')
print(f'Stub ends:   {repr(stub[-60:])}')

# Replace with the proper get_vis_js() call
replacement = '        vis_js_content = get_vis_js()'

code = code[:start_idx] + replacement + code[end_idx:]

# Also ensure the import is at the top
if 'from .assets import get_vis_js' not in code:
    # Add after the existing imports
    code = code.replace(
        'from .assets import',
        'from .assets import get_vis_js\nfrom .assets import',
        1
    )
    print('Added get_vis_js import')
else:
    print('get_vis_js import already present')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('FIX applied - vis_js_content now calls get_vis_js()')
print(f'File now: {len(code):,} chars')
