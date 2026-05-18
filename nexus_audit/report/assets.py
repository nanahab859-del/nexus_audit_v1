#!/usr/bin/env python3
"""
Report Assets
=============
Helper functions and constants for report generation.
"""

import os
from ..config import MODULAR_ROOT


def get_vis_js() -> str:
    """Load vis-network.min.js from disk or return fallback."""
    search_paths = [
        os.path.join(MODULAR_ROOT, 'vis-network.min.js'),           # modular root
        os.path.expanduser('~/my_tools/nexus_audit/vis-network.min.js'),  # legacy
        os.path.join(os.path.dirname(__file__), 'vis-network.min.js'),
        os.path.join(os.getcwd(), 'vis-network.min.js'),
    ]
    for path in search_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            print(f"   ✔ vis-network.min.js loaded ({len(content)//1024}KB) from {path}")
            return content
    print(f"   ⚠ vis-network.min.js NOT FOUND — graph will not render.")
    print(f"     Place it at: {search_paths[0]}")
    print(f"     Download:    https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js")
    return "console.warn('vis-network.min.js not found. Place it in the nexus_audit folder.');"
