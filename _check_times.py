import os, datetime
import glob
files = glob.glob('/home/yusupha/my_tools/nexus_audit/visuals/*')
out = []
for f in files:
    mtime = os.path.getmtime(f)
    dt = datetime.datetime.fromtimestamp(mtime)
    out.append(f"{os.path.basename(f)}: {dt.isoformat()}\n")

with open('/home/yusupha/my_tools/nexus_audit/_times.txt', 'w') as f:
    f.writelines(out)
