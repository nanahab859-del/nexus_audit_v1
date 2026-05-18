#!/usr/bin/env python3
"""Compile ALL nexus_audit modules and write results to file."""
import subprocess
import sys

files = [
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/config.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/key_pool.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/models.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/scanners.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/audit_engine.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/dependency.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/backend.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/prompts.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/ai/recommendations.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/assets.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/markdown_report.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/main.py',
    '/home/yusupha/my_tools/nexus_audit/nexus_audit/pulse.py',
    '/home/yusupha/my_tools/nexus_audit/pulse.py',
]

lines = []
all_ok = True
for f in files:
    result = subprocess.run([sys.executable, '-m', 'py_compile', f], capture_output=True, text=True)
    label = f.replace('/home/yusupha/my_tools/nexus_audit/', '')
    if result.returncode == 0:
        lines.append(f"OK  {label}\n")
    else:
        lines.append(f"ERR {label}:\n    {result.stderr.strip()}\n")
        all_ok = False

lines.append("\nALL PASS\n" if all_ok else "\nSOME FAILED\n")

out = '/home/yusupha/my_tools/nexus_audit/_compile_out.txt'
with open(out, 'w') as fh:
    fh.writelines(lines)
print(f"Written to {out}")
