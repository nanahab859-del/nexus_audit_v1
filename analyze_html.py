#!/usr/bin/env python3
import os

filepath = 'visuals/NEXUS_AUDIT_DASHBOARD.html'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find key locations
script_close_pos = content.find('</script>')
style_open_pos = content.find('<style>')
const_apps_pos = content.find('const apps')
const_changeSummary_pos = content.find('const changeSummary')

print("=" * 60)
print("HTML Structure Analysis")
print("=" * 60)
print(f"File size: {len(content)} bytes")
print(f"</script> first occurrence: {script_close_pos}")
print(f"<style> first occurrence: {style_open_pos}")
print(f"const apps first occurrence: {const_apps_pos}")
print(f"const changeSummary first occurrence: {const_changeSummary_pos}")
print()

if script_close_pos != -1:
    lines_before_script_close = content[:script_close_pos].count('\n')
    print(f"First </script> closes at line: {lines_before_script_close + 1}")
    # Show context around it
    start = max(0, script_close_pos - 200)
    end = min(len(content), script_close_pos + 100)
    print(f"\nContext around first </script>:")
    print(content[start:end])
    print()

if const_apps_pos != -1:
    lines_before_apps = content[:const_apps_pos].count('\n')
    print(f"const apps starts at line: {lines_before_apps + 1}")
    print(f"Context: {content[const_apps_pos:const_apps_pos+150]}")
else:
    print("ERROR: 'const apps' not found in HTML!")

if const_changeSummary_pos != -1:
    lines_before_cs = content[:const_changeSummary_pos].count('\n')
    print(f"\nconst changeSummary starts at line: {lines_before_cs + 1}")
    print(f"Context: {content[const_changeSummary_pos:const_changeSummary_pos+150]}")
else:
    print("\nERROR: 'const changeSummary' not found in HTML!")
