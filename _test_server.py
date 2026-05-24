import sys, subprocess
sys.path.insert(0, '/home/yusupha/my_tools/nexus_audit')
from nexus_audit.features.server import serve
print('serve import OK')

# Test the pulse --serve argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--serve', action='store_true')
parser.add_argument('--watch', action='store_true')
args = parser.parse_args(['--serve'])
print('args.serve:', args.serve)

# Test cmd.exe
try:
    r = subprocess.run(['cmd.exe', '/c', 'echo', 'test'], capture_output=True, timeout=5)
    print('cmd.exe works, returncode:', r.returncode, 'stdout:', r.stdout.strip())
except Exception as e:
    print('cmd.exe failed:', e)

# Test starting browser
try:
    r2 = subprocess.run(['cmd.exe', '/c', 'start', 'http://localhost:8421'], capture_output=True, timeout=5)
    print('browser launch returncode:', r2.returncode)
except Exception as e:
    print('browser launch failed:', e)
