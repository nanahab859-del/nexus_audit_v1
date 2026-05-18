#!/usr/bin/env python3
"""
Nexus Audit Tool - Backward Compatibility Shim
==============================================
The audit tool has been refactored into the nexus_audit package.
This file remains only for legacy callers.
Please use 'python pulse.py' or 'python -m nexus_audit' going forward.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nexus_audit.main import main

if __name__ == "__main__":
    print("⚠️ WARNING: command_center_galaxy.py is deprecated.", file=sys.stderr)
    print("⚠️ Please use 'pulse.py' or the 'pulse' alias.", file=sys.stderr)
    main()