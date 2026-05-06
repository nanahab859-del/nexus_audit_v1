#!/bin/bash

# 1. THE ENVIRONMENT LAW (Absolute Path Activation)
CONDA_BASE="$HOME/my_tools/miniconda3"
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate audit_env

# 2. DEFINE THE DIRECTORIES
PROJECT_DIR="$HOME/my_tools/nexus_project_copy"
AUDIT_DIR="$HOME/my_tools/nexus_audit"

# ---------------------------------------------------------
# PHASE 0: PHYSICAL INVENTORY (Enhanced - FIXED to exclude .venv)
# ---------------------------------------------------------
cd "$PROJECT_DIR" || { echo "❌ Error: Project folder not found!"; exit 1; }
echo "📂 PHASE 0: MAPPING PHYSICAL REALITY..."

# FIXED: Exclude .venv and site-packages directories
find . -name "*.py" \
    -not -path "*/.venv/*" \
    -not -path "*/site-packages/*" \
    -not -path "*/migrations/*" \
    -not -name "test_*.py" \
    -not -path "*/tests/*" \
    | sed 's|./||' \
    | sed 's|/|.|g' \
    | sed 's|.py$||' \
    > "$AUDIT_DIR/factories/physical_inventory.txt"

# 3. PHASE 1: DNA SCAN (Enhanced with better pydeps options)
echo "🛰️  PHASE 1: REGENERATING INDIVIDUAL DNA..."

apps=("nexus_core" "nexus_gateway" "nexus_economy" "nexus_gaming" "nexus_tournaments" "nexus_content" "nexus_social")

for app in "${apps[@]}"; do
    echo "  -> Scanning $app..."
    # FIXED: Added --exclude for .venv and site-packages
    python3 -m pydeps "$app" \
        --show-deps \
        --noshow \
        --pylib \
        --exclude "migrations|tests|test_*|.venv|site-packages" \
        > "$AUDIT_DIR/factories/${app}_dna.json" 2>/dev/null
done

# 4. PHASE 2: WELDING MASTER DNA (Improved merge)
cd "$AUDIT_DIR" || exit
echo "🧬 PHASE 2: WELDING MASTER DNA..."

# FIXED: Added error handling for file reading
python3 -c "
import json
import glob
from collections import defaultdict

master = {}

for dna_file in glob.glob('./factories/*_dna.json'):
    try:
        with open(dna_file, 'r') as f:
            data = json.load(f)
            for module, info in data.items():
                if module not in master:
                    master[module] = info
                else:
                    if 'imports' in info:
                        master[module].setdefault('imports', []).extend(info['imports'])
                    if 'imported_by' in info:
                        master[module].setdefault('imported_by', []).extend(info['imported_by'])
                    if info.get('bacon', 999) < master[module].get('bacon', 999):
                        master[module]['bacon'] = info['bacon']
    except Exception as e:
        print(f'Warning: Could not read {dna_file}: {e}')

for module in master:
    if 'imports' in master[module]:
        master[module]['imports'] = list(set(master[module]['imports']))
    if 'imported_by' in master[module]:
        master[module]['imported_by'] = list(set(master[module]['imported_by']))

with open('master_nexus_dna.json', 'w') as f:
    json.dump(master, f, indent=2)
"
echo "✅ Master DNA created with accurate depth information"

if [ ! -s "$AUDIT_DIR/master_nexus_dna.json" ]; then
    echo "❌ Error: Master DNA is empty."
    exit 1
fi

# 5. PHASE 3: ENHANCED AUDIT
echo "🛡️  PHASE 3: RUNNING ENHANCED AUDIT..."
python3 "$AUDIT_DIR/command_center_galaxy.py"

echo "✅ SUCCESS: Enhanced audit complete!"
echo "📁 Reports available in: $AUDIT_DIR/visuals/"