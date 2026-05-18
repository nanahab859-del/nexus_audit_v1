#!/usr/bin/env python3
"""Import-chain test for the nexus_audit package."""
import sys
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')

results = []

tests = [
    ("config",           "from nexus_audit.config import _load_dotenv, VAULT_PATH, _GEMINI_BASE"),
    ("key_pool",         "from nexus_audit.key_pool import key_pool"),
    ("models",           "from nexus_audit.models import Violation, AllowedCommunication"),
    ("scanners",         "from nexus_audit.scanners import run_bandit_enhanced"),
    ("audit_engine",     "from nexus_audit.audit_engine import classify_connection, find_circular_dependencies"),
    ("dependency",       "from nexus_audit.dependency import run_tier2_dependency_scan"),
    ("ai.backend",       "from nexus_audit.ai.backend import _detect_ai_backend, _ai_complete, _parse_ai_json"),
    ("ai.prompts",       "from nexus_audit.ai.prompts import AI_SYSTEM, build_violation_prompt"),
    ("ai.recommendations","from nexus_audit.ai.recommendations import run_ai_recommendations, generate_recommendations"),
    ("report.assets",    "from nexus_audit.report.assets import get_vis_js"),
    ("report.html",      "from nexus_audit.report.html_report import EnhancedAuditReport"),
    ("report.markdown",  "from nexus_audit.report.markdown_report import generate_comprehensive_markdown"),
    ("main",             "from nexus_audit.main import main"),
]

all_ok = True
for name, stmt in tests:
    try:
        exec(stmt)
        results.append(f"OK  {name}\n")
    except Exception as e:
        results.append(f"ERR {name}: {e}\n")
        all_ok = False

results.append("\nALL IMPORTS OK\n" if all_ok else "\nSOME IMPORTS FAILED\n")

out = '/home/yusupha/my_tools/nexus_audit/_import_out.txt'
with open(out, 'w') as fh:
    fh.writelines(results)
print(f"Written to {out}")
