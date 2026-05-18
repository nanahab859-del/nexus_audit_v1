#!/usr/bin/env python3
"""Debug pulse startup — catch the exact error."""
import sys
import traceback

sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

out_lines = []

try:
    from nexus_audit.main import main
    out_lines.append("IMPORT OK\n")
    try:
        main()
        out_lines.append("MAIN COMPLETE\n")
    except SystemExit as e:
        out_lines.append(f"SystemExit: {e}\n")
    except Exception as e:
        out_lines.append(f"MAIN ERROR: {e}\n")
        out_lines.append(traceback.format_exc())
except Exception as e:
    out_lines.append(f"IMPORT ERROR: {e}\n")
    out_lines.append(traceback.format_exc())

with open('/home/yusupha/my_tools/nexus_audit/debug_pulse.txt', 'w') as f:
    f.writelines(out_lines)

print("debug written")
