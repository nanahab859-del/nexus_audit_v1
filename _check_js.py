content = open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html', encoding='utf-8', errors='replace').read()

main_start = content.rfind('<script>')
main_end   = content.rfind('</script>')
js = content[main_start+8:main_end]
lines = js.split('\n')

print(f"Main script: {len(lines)} lines, {len(js):,} chars")

# Track brace balance ignoring strings and template literals
balance = 0
in_str_d = False  # double-quote string
in_str_s = False  # single-quote string
in_tmpl = 0
esc = False

for lineno, line in enumerate(lines, 1):
    for ch in line:
        if esc:
            esc = False
            continue
        if ch == '\\':
            esc = True
            continue
        if ch == '`' and not in_str_d and not in_str_s:
            in_tmpl = 1 - in_tmpl
            continue
        if in_tmpl:
            continue
        if ch == '"' and not in_str_s and not in_str_d:
            in_str_d = True
            continue
        if ch == '"' and in_str_d:
            in_str_d = False
            continue
        if ch == "'" and not in_str_d and not in_str_s:
            in_str_s = True
            continue
        if ch == "'" and in_str_s:
            in_str_s = False
            continue
        if in_str_d or in_str_s:
            continue
        if ch == '{':
            balance += 1
        elif ch == '}':
            balance -= 1

    if balance < 0:
        print(f"BALANCE GOES NEGATIVE at line {lineno}: balance={balance}")
        for j, ctx in enumerate(lines[max(0,lineno-6):lineno+2], start=max(1,lineno-5)):
            print(f"  {j:4d}: {ctx[:120]}")
        break

print(f"\nFinal balance: {balance}")

# Also check for unclosed template literals
tcount = js.count('`')
print(f"Backtick count: {tcount} ({'EVEN OK' if tcount%2==0 else 'ODD - PARSE ERROR'})")

# Find last 10 function definitions to see if any are unclosed
import re
fns = [(m.start(), content[:main_start+8+m.start()].count('\n')+1) for m in re.finditer(r'^function \w+', js, re.MULTILINE)]
print(f"\nLast 5 function definitions:")
for pos, lineno in fns[-5:]:
    print(f"  line {lineno}: {js[pos:pos+60]}")
