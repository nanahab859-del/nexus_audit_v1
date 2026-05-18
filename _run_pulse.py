#!/usr/bin/env python3
"""Run pulse end-to-end and capture output to file."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '/home/yusupha/my_tools/nexus_audit/pulse.py'],
    capture_output=True,
    text=True,
    timeout=300,
    cwd='/home/yusupha/my_tools/nexus_audit',
)

out = '/tmp/nexus_pulse_out.txt'
with open(out, 'w', encoding='utf-8') as fh:
    fh.write(f"=== STDOUT ===\n{result.stdout}\n")
    fh.write(f"=== STDERR ===\n{result.stderr}\n")
    fh.write(f"=== EXIT CODE: {result.returncode} ===\n")

# Also copy to nexus_audit dir using relative path
import shutil
shutil.copy(out, '/home/yusupha/my_tools/nexus_audit/pulse_run_out.txt')
print(f"Exit {result.returncode}. Output written.")
