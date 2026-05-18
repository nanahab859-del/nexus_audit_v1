import ast

with open('/home/yusupha/my_tools/nexus_audit/command_center_galaxy.py.bak', 'r') as f:
    source = f.read()

class FuncExtractor(ast.NodeVisitor):
    def __init__(self):
        self.func_source = ''
    def visit_FunctionDef(self, node):
        if node.name == 'generate_comprehensive_markdown':
            self.func_source = ast.get_source_segment(source, node)
        self.generic_visit(node)

extractor = FuncExtractor()
extractor.visit(ast.parse(source))

with open('/home/yusupha/my_tools/nexus_audit/nexus_audit/report/markdown_report.py', 'w') as f:
    f.write('''#!/usr/bin/env python3
"""
Markdown Report Generator
=========================
Generates the comprehensive standalone Markdown audit report.
"""

from typing import Dict

''')
    f.write(extractor.func_source)

print('Extracted generate_comprehensive_markdown.')
