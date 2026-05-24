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
import shutil

def sync_codebase():
    source = os.path.expanduser('~/nexus-gaming')
    target = os.path.expanduser('~/my_tools/nexus_project_copy')
    print("🔄 PHASE 0: SYNCING CODEBASE FROM SOURCE...")
    
    if not os.path.exists(source):
        print(f"❌ Error: Source codebase not found at {source}")
        sys.exit(1)
        
    ignore_patterns = shutil.ignore_patterns(
        '.git', '.venv', '__pycache__', '*.pyc', '*.pyo',
        'node_modules', '.env', '*.log', 'logs', 'scratch', 'scratch_delete.py'
    )
    
    if os.path.exists(target):
        shutil.rmtree(target)
        
    shutil.copytree(source, target, ignore=ignore_patterns)
    print("   ✔ Sync complete\n")

if __name__ == "__main__":
    sync_codebase()
    main()
