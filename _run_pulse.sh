#!/bin/bash
cd /home/yusupha/my_tools/nexus_audit
python3 pulse.py > /home/yusupha/my_tools/nexus_audit/pulse_direct.txt 2>&1
echo "EXIT:$?" >> /home/yusupha/my_tools/nexus_audit/pulse_direct.txt
