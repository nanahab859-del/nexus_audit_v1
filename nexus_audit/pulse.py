#!/usr/bin/env python3
"""
Nexus Audit Tool - CLI Entry Point
===================================
Simple wrapper that invokes the main audit orchestrator.
"""

import sys
import os

def main():
    """CLI entry point for the pulse command."""
    # Add the nexus_audit package to the path so it can be imported
    audit_dir = os.path.dirname(os.path.abspath(__file__))
    if audit_dir not in sys.path:
        sys.path.insert(0, os.path.dirname(audit_dir))

    from nexus_audit.main import main as audit_main
    
    try:
        audit_main()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
