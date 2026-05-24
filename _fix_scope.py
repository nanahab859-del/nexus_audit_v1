src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/dashboard_template.html'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# Fix 1: Remove 'const' from visNodes/visEdges/network inside initGraph
# so they assign to the outer module-level variables instead of shadowing them
old1 = (
    'const visNodes = new vis.DataSet(nodesData);\n'
    'const visEdges = new vis.DataSet(edgesData);\n'
    '\n'
    'const network = new vis.Network('
)
new1 = (
    'visNodes = new vis.DataSet(nodesData);\n'
    'visEdges = new vis.DataSet(edgesData);\n'
    '\n'
    'network = new vis.Network('
)
if old1 in code:
    code = code.replace(old1, new1, 1)
    print('FIX 1 applied - removed const shadowing from visNodes/visEdges/network')
    fixes += 1
else:
    print('FIX 1 SKIP')

# Fix 2: Make sure network is also declared at module level (let network = null)
# Check if it already exists
if 'let network = null' not in code and 'let network;' not in code:
    old2 = 'let visNodes = null;\nlet visEdges = null;'
    new2 = 'let visNodes = null;\nlet visEdges = null;\nlet network = null;'
    if old2 in code:
        code = code.replace(old2, new2, 1)
        print('FIX 2 applied - added let network = null at module level')
        fixes += 1
    else:
        print('FIX 2 SKIP')
else:
    print('FIX 2 - network already declared at module level')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'Total fixes: {fixes}')
