import sys, os
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')
import nexus_audit.main
print("Main loaded")
nexus_audit.main.main()
print("Main done")
