src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/report/html_report.py'
lines = open(src).readlines()
total = len(lines)
print(f"Total lines: {total}")

# Find where the return statement is and structure of generate_html_dashboard
print("\n=== generate_html_dashboard structure ===")
in_method = False
for i, l in enumerate(lines, 1):
    ls = l.rstrip()
    if 'def generate_html_dashboard' in ls:
        in_method = True
    if in_method:
        if any(k in ls for k in ['return ', 'html_content', 'trends_js', '.format(', 'f"""', "f'''"]):
            print(f"  {i:4d}: {ls[:120]}")
        if i > 200 and 'def ' in ls and 'generate_html' not in ls:
            print(f"  {i:4d}: [next method starts] {ls[:60]}")
            break

# Find the return statement
print("\n=== Return statement ===")
for i, l in enumerate(lines, 1):
    if l.strip().startswith('return ') and ('html' in l or 'f' in l):
        print(f"  {i:4d}: {l.rstrip()[:120]}")

# Find all triple-quote boundaries
print("\n=== Triple-quote boundaries ===")
for i, l in enumerate(lines, 1):
    if '"""' in l:
        print(f"  {i:4d}: {l.rstrip()[:100]}")
