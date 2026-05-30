import json
import sys
import traceback
from nexus_audit.report.markdown_report import generate_comprehensive_markdown

try:
    with open('/home/yusupha/my_tools/nexus_audit/visuals/audit_data_complete.json') as f:
        d = json.load(f)
    print("timeline type:", type(d.get('timeline')))
    print("timeline data:", d.get('timeline'))
    generate_comprehensive_markdown(d)
    print("Success!")
except Exception as e:
    traceback.print_exc()
