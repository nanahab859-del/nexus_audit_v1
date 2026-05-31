#!/bin/bash

# ============================================================================
# NEXUS PULSE — Full audit pipeline
# ============================================================================
# Phase 0 : Auto-sync live codebase  →  nexus_project_copy   (NEW)
# Phase 1 : Physical inventory scan
# Phase 2 : Per-app DNA scan (pydeps)
# Phase 3 : Weld master DNA
# Phase 4 : Run enhanced audit (command_center_galaxy.py)
# ============================================================================

# 1. Activate conda env ───────────────────────────────────────────────────────
CONDA_BASE="$HOME/my_tools/miniconda3"
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate audit_env

# 2. Directory definitions ────────────────────────────────────────────────────
SOURCE_DIR="$HOME/nexus-gaming"          # ← live codebase (never touch directly)
PROJECT_DIR="$HOME/my_tools/nexus_project_copy"   # ← audit working copy
AUDIT_DIR="$HOME/my_tools/nexus_audit"

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 0: AUTO-SYNC LIVE CODEBASE → WORKING COPY
# ─────────────────────────────────────────────────────────────────────────────
echo "🔄 PHASE 0: SYNCING CODEBASE FROM SOURCE..."
echo "   From : $SOURCE_DIR"
echo "   Into : $PROJECT_DIR"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source codebase not found at $SOURCE_DIR"
    exit 1
fi

mkdir -p "$PROJECT_DIR"

rsync -a --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='node_modules/' \
    --exclude='.env' \
    --exclude='*.log' \
    --exclude='logs/' \
    --exclude='scratch/' \
    --exclude='scratch_delete.py' \
    "$SOURCE_DIR/" "$PROJECT_DIR/"

RSYNC_EXIT=$?
if [ $RSYNC_EXIT -ne 0 ]; then
    echo "❌ rsync failed (exit $RSYNC_EXIT). Aborting."
    exit 1
fi

# Show what changed (files added/removed vs last sync)
SYNCED=$(rsync -a --delete --dry-run \
    --exclude='.git/' --exclude='.venv/' --exclude='__pycache__/' \
    --exclude='*.pyc' --exclude='*.pyo' --exclude='node_modules/' \
    --exclude='.env' --exclude='*.log' --exclude='logs/' \
    --exclude='scratch/' --exclude='scratch_delete.py' \
    --out-format="%n" \
    "$SOURCE_DIR/" "$PROJECT_DIR/" 2>/dev/null | wc -l)

if [ "$SYNCED" -eq 0 ]; then
    echo "   ✔ Already up-to-date — no files changed"
else
    echo "   ✔ Sync complete"
fi

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1: PHYSICAL INVENTORY
# ─────────────────────────────────────────────────────────────────────────────
cd "$PROJECT_DIR" || { echo "❌ Error: Project folder not found!"; exit 1; }
echo "📂 PHASE 1: MAPPING PHYSICAL REALITY..."

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

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: PER-APP DNA SCAN
# ─────────────────────────────────────────────────────────────────────────────
echo "🛰️  PHASE 2: REGENERATING INDIVIDUAL DNA..."

apps=("nexus_core" "nexus_gateway" "nexus_economy" "nexus_gaming" "nexus_tournaments" "nexus_content" "nexus_social")

for app in "${apps[@]}"; do
    echo "  -> Scanning $app (background)..."
    python3 -m pydeps "$app" \
        --show-deps \
        --noshow \
        --pylib \
        --exclude "migrations|tests|test_*|.venv|site-packages" \
        > "$AUDIT_DIR/factories/${app}_dna.json" 2>/dev/null &
done
wait
echo "  ✔ All app scans completed in parallel"

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3: WELD MASTER DNA
# ─────────────────────────────────────────────────────────────────────────────
cd "$AUDIT_DIR" || exit
echo "🧬 PHASE 3: WELDING MASTER DNA..."

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

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: ENHANCED AUDIT
# ─────────────────────────────────────────────────────────────────────────────
echo "🛡️  PHASE 4: RUNNING ENHANCED AUDIT..."
python3 "$AUDIT_DIR/pulse.py" "$@"
