import ast

with open('/home/yusupha/my_tools/nexus_audit/command_center_galaxy.py.bak', 'r') as f:
    source = f.read()

class ClassExtractor(ast.NodeVisitor):
    def __init__(self):
        self.class_source = ''
    def visit_ClassDef(self, node):
        if node.name == 'EnhancedAuditReport':
            self.class_source = ast.get_source_segment(source, node)
        self.generic_visit(node)

extractor = ClassExtractor()
extractor.visit(ast.parse(source))

with open('/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py', 'w') as f:
    f.write('''#!/usr/bin/env python3
"""
HTML Report Generator
=====================
Generates interactive HTML dashboard with vis-network graph visualization.
"""

import json
from datetime import datetime
from .assets import get_vis_js


''')
    f.write(extractor.class_source)

print('Extracted EnhancedAuditReport.')
