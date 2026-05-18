#!/bin/bash
cd /home/yusupha/my_tools/nexus_audit
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import nexus_audit
    print('nexus_audit OK')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
" > /home/yusupha/my_tools/nexus_audit/startup_err.txt 2>&1
echo "DONE EXIT:$?" >> /home/yusupha/my_tools/nexus_audit/startup_err.txt
