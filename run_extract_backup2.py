import ast
import traceback

try:
    with open('/home/yusupha/my_tools/nexus_audit_backup_phase0/command_center_galaxy.py', 'r') as f:
        source = f.read()

    print(f"Read {len(source)} bytes from source")

    class ClassExtractor(ast.NodeVisitor):
        def __init__(self):
            self.class_source = ''
        def visit_ClassDef(self, node):
            if node.name == 'EnhancedAuditReport':
                self.class_source = ast.get_source_segment(source, node)
                print(f"Found EnhancedAuditReport! len: {len(self.class_source) if self.class_source else 0}")
            self.generic_visit(node)

    class FuncExtractor(ast.NodeVisitor):
        def __init__(self):
            self.func_source = ''
        def visit_FunctionDef(self, node):
            if node.name == 'generate_comprehensive_markdown':
                self.func_source = ast.get_source_segment(source, node)
                print(f"Found generate_comprehensive_markdown! len: {len(self.func_source) if self.func_source else 0}")
            self.generic_visit(node)

    ce = ClassExtractor()
    ce.visit(ast.parse(source))
    if ce.class_source:
        with open('/home/yusupha/my_tools/nexus_audit/scratch_extract_backup.py', 'w') as f:
            f.write(ce.class_source)

    fe = FuncExtractor()
    fe.visit(ast.parse(source))
    if fe.func_source:
        with open('/home/yusupha/my_tools/nexus_audit/scratch_extract_backup_md.py', 'w') as f:
            f.write(fe.func_source)

    print('Extraction done.')
except Exception as e:
    traceback.print_exc()
