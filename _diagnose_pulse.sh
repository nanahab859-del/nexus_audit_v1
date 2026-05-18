#!/bin/bash
cd /home/yusupha/my_tools/nexus_audit
python3 pulse.py > /home/yusupha/my_tools/nexus_audit/real_pulse_out.txt 2>&1
echo "EXIT_CODE:$?" >> /home/yusupha/my_tools/nexus_audit/real_pulse_out.txt
