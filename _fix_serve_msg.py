src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/main.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Add a clear transition message before the server starts
old = '''    if args.serve:
        from .features.server import serve

        serve(html_path, json_path, str(fix_queue_path), open_browser=True, watch=args.watch)'''

new = '''    if args.serve:
        from .features.server import serve

        print()
        print("   \u2500" * 31)
        print("   \u2705 AUDIT COMPLETE \u2014 starting dashboard server\u2026")
        print("   \u2500" * 31)
        serve(html_path, json_path, str(fix_queue_path), open_browser=True, watch=args.watch)'''

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - transition message added before server start')
else:
    print('SKIP')

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
