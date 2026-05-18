import json
with open('/home/yusupha/my_tools/nexus_audit/visuals/audit_data_complete.json') as f:
    d = json.load(f)
with open('/home/yusupha/my_tools/nexus_audit/score_out.txt', 'w') as out:
    out.write(json.dumps(d['metadata'], indent=2))
