content = open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html', encoding='utf-8', errors='replace').read()
import re

main_start = content.rfind('<script>')
main_end   = content.rfind('</script>')
js = content[main_start+8:main_end]
lines = js.split('\n')

# Track brace balance and record every function entry/exit
balance = 0
in_str_d = False
in_str_s = False
in_tmpl = 0
esc = False
fn_stack = []  # stack of (function_name, line_number, balance_at_entry)

import re

for lineno, line in enumerate(lines, 1):
    # Check for function definition at start of line (simplified)
    fn_match = re.match(r'\s*function\s+(\w+)\s*\(', line)
    
    for ch in line:
        if esc: esc=False; continue
        if ch == '\\': esc=True; continue
        if ch == '`' and not in_str_d and not in_str_s:
            in_tmpl = 1 - in_tmpl; continue
        if in_tmpl: continue
        if ch == '"' and not in_str_s and not in_str_d: in_str_d=True; continue
        if ch == '"' and in_str_d: in_str_d=False; continue
        if ch == "'" and not in_str_d and not in_str_s: in_str_s=True; continue
        if ch == "'" and in_str_s: in_str_s=False; continue
        if in_str_d or in_str_s: continue
        if ch == '{':
            balance += 1
            if fn_match:
                fn_stack.append((fn_match.group(1), lineno, balance))
                fn_match = None  # only push once per line
        elif ch == '}':
            balance -= 1
            # Check if this closes a function
            if fn_stack and fn_stack[-1][2] == balance + 1:
                # The balance just dropped to one below this function's entry balance
                fn_stack.pop()

print(f"Functions still open at end (never closed):")
for name, lineno, bal in fn_stack:
    print(f"  function {name}() opened at line {lineno} (balance was {bal})")

print(f"\nFinal balance: {balance}")
print(f"\nLast 30 lines of script:")
for i, l in enumerate(lines[-30:], start=len(lines)-29):
    print(f"  {i:4d}: {l[:120]}")
