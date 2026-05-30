#!/usr/bin/env python3
"""
Nexus Audit Tool - Pulse Command
=================================
Entry point for running the audit tool.
Usage: python pulse.py
"""

import sys
import os

# Add current directory to path so nexus_audit package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_audit.main import main
if __name__ == "__main__":
    main()
