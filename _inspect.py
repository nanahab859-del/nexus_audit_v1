#!/usr/bin/env python3
"""Inspect command_center_galaxy.py and write its structure to disk."""
import os

src = '/home/yusupha/my_tools/nexus_audit/command_center_galaxy.py'
out = '/home/yusupha/my_tools/nexus_audit/_inspect_out.txt'

lines = open(src, encoding='utf-8').readlines()
results = [f"Total lines: {len(lines)}\n"]

for i, l in enumerate(lines, 1):
    s = l.rstrip()
    if s.startswith('def ') or s.startswith('class ') or s.startswith('async def '):
        results.append(f"{i}: {s[:100]}\n")

with open(out, 'w', encoding='utf-8') as f:
    f.writelines(results)

print(f"Written {len(results)-1} entries to {out}")
