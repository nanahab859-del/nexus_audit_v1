src = '/home/yusupha/my_tools/nexus_audit/nexus_audit/features/server.py'
with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix 1: Replace webbrowser.open() with a WSL-aware opener
# In WSL, use cmd.exe /c start to open the Windows default browser
old = (
    "    server = ThreadingHTTPServer((\"127.0.0.1\", port), AuditHandler)\n"
    "    url = f\"http://localhost:{port}\"\n"
    "    print(f\"\U0001f310 Serving dashboard at {url}\")\n"
    "    if open_browser:\n"
    "        webbrowser.open(url)\n"
    "    try:\n"
    "        server.serve_forever()\n"
    "    except KeyboardInterrupt:\n"
    "        pass\n"
    "    finally:\n"
    "        server.server_close()"
)
new = (
    "    server = ThreadingHTTPServer((\"127.0.0.1\", port), AuditHandler)\n"
    "    url = f\"http://localhost:{port}\"\n"
    "\n"
    "    print()\n"
    "    print(\"=\" * 62)\n"
    "    print(f\"\U0001f310  NEXUS AUDIT DASHBOARD SERVER\")\n"
    "    print(f\"   URL  : {url}\")\n"
    "    print(f\"   Watch: {'enabled' if watch else 'disabled'}\")\n"
    "    print(f\"   Stop : Ctrl+C\")\n"
    "    print(\"=\" * 62)\n"
    "    print()\n"
    "\n"
    "    if open_browser:\n"
    "        # WSL-aware browser launch: try cmd.exe first (Windows host),\n"
    "        # fall back to standard webbrowser module.\n"
    "        opened = False\n"
    "        try:\n"
    "            result = subprocess.run(\n"
    "                [\"cmd.exe\", \"/c\", \"start\", url],\n"
    "                capture_output=True, timeout=5\n"
    "            )\n"
    "            opened = result.returncode == 0\n"
    "        except Exception:\n"
    "            pass\n"
    "        if not opened:\n"
    "            try:\n"
    "                webbrowser.open(url)\n"
    "            except Exception:\n"
    "                pass\n"
    "        if not opened:\n"
    "            print(f\"   \U0001f4e2 Browser did not open automatically.\")\n"
    "            print(f\"   Open manually: {url}\")\n"
    "            print()\n"
    "\n"
    "    try:\n"
    "        server.serve_forever()\n"
    "    except KeyboardInterrupt:\n"
    "        print(\"\\n\U0001f6d1 Server stopped.\")\n"
    "    finally:\n"
    "        server.server_close()"
)

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - WSL-aware browser launch + clear terminal banner')
else:
    print('SKIP - pattern not found')
    idx = code.find('serve_forever')
    print('Context:', repr(code[idx-200:idx+100]))

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)
