src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix 1: Add import at top level (after existing imports, before class definition)
old_imports = 'import json\nfrom datetime import datetime\nfrom typing import Dict, Any, List'
new_imports = 'import json\nfrom datetime import datetime\nfrom typing import Dict, Any, List\nfrom .assets import get_vis_js'

if old_imports in code:
    code = code.replace(old_imports, new_imports, 1)
    print('Import added at top level')
elif 'from .assets import get_vis_js' in code:
    print('Import already present - checking location')
    idx = code.find('from .assets import get_vis_js')
    print(f'  Found at char {idx}')
    # Check if it is inside the class (bad) or at module level (good)
    class_idx = code.find('class EnhancedAuditReport')
    if idx > class_idx:
        print('  PROBLEM: import is inside class - moving to top level')
        code = code.replace('from .assets import get_vis_js\n', '', 1)
        code = code.replace(old_imports, new_imports, 1)
        print('  Fixed')
else:
    print('SKIP - base import pattern not found, showing top:')
    print(code[:300])

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
