content = open('/home/yusupha/my_tools/nexus_audit/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html', encoding='utf-8', errors='replace').read()

main_start = content.rfind('<script>')
main_end   = content.rfind('</script>')
js = content[main_start+8:main_end]
lines = js.split('\n')

# Show lines 310-340 (where filterRecommendations opens in generated script)
print("=== Lines 310-345 of generated main script ===")
for i, l in enumerate(lines[309:345], start=310):
    print(f"  {i:4d}: {l[:160]}")
