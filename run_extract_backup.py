import ast

with open('/home/yusupha/my_tools/nexus_audit_backup_phase0/command_center_galaxy.py', 'r') as f:
    source = f.read()

class ClassExtractor(ast.NodeVisitor):
    def __init__(self):
        self.class_source = ''
    def visit_ClassDef(self, node):
        if node.name == 'EnhancedAuditReport':
            self.class_source = ast.get_source_segment(source, node)
        self.generic_visit(node)

class FuncExtractor(ast.NodeVisitor):
    def __init__(self):
        self.func_source = ''
    def visit_FunctionDef(self, node):
        if node.name == 'generate_comprehensive_markdown':
            self.func_source = ast.get_source_segment(source, node)
        self.generic_visit(node)

class MainExtractor(ast.NodeVisitor):
    def __init__(self):
        self.func_source = ''
    def visit_FunctionDef(self, node):
        if node.name == 'build_audit_fortress_enhanced':
            self.func_source = ast.get_source_segment(source, node)
        self.generic_visit(node)

ce = ClassExtractor()
ce.visit(ast.parse(source))

fe = FuncExtractor()
fe.visit(ast.parse(source))

me = MainExtractor()
me.visit(ast.parse(source))

with open('/home/yusupha/my_tools/nexus_audit/scratch_extract_backup.py', 'w') as f:
    f.write(ce.class_source)

with open('/home/yusupha/my_tools/nexus_audit/scratch_extract_backup_md.py', 'w') as f:
    f.write(fe.func_source)

with open('/home/yusupha/my_tools/nexus_audit/scratch_extract_backup_main.py', 'w') as f:
    f.write(me.func_source)

print('Extracted from backup.')
