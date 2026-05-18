SRC = '/home/yusupha/my_tools/nexus_audit/nexus_audit/dependency.py'
with open(SRC, 'r', encoding='utf-8') as f:
    code = f.read()

# Trim full OSV vulnerability objects to only the 4 fields the dashboard uses.
# The full objects (details, affected, references, aliases, database_specific, etc.)
# were bloating the JSON to 808KB and making the HTML take 5+ seconds to parse.
# After trimming: ~4KB per CVE becomes ~120 bytes — roughly 30x smaller.

old = '''        return data.get('vulns', [])
    except Exception:
        return []'''

new = '''        vulns = data.get('vulns', [])
        # Trim each CVE to only the fields the dashboard renders.
        # Full OSV objects are ~4KB each; trimmed objects are ~120 bytes.
        # With 150+ CVEs across 116 packages this saves ~700KB in the HTML.
        trimmed = []
        for v in vulns:
            sev = ''
            for s in (v.get('severity') or []):
                if s.get('score'):
                    sev = s['score']
                    break
            ref_url = ''
            refs = v.get('references') or []
            if refs:
                ref_url = refs[0].get('url', '')
            trimmed.append({
                'id':       v.get('id', ''),
                'summary':  v.get('summary', ''),
                'severity': sev,
                'url':      ref_url,
            })
        return trimmed
    except Exception:
        return []'''

if old in code:
    code = code.replace(old, new, 1)
    print('FIX applied - CVE trimming added to _osv_query()')
else:
    print('FIX SKIP - pattern not found')

with open(SRC, 'w', encoding='utf-8') as f:
    f.write(code)
