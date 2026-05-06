#!/bin/bash

# 1. THE ENVIRONMENT LAW (Absolute Path Activation)
CONDA_BASE="$HOME/my_tools/miniconda3"
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate audit_env

# 2. DEFINE THE DIRECTORIES
PROJECT_DIR="$HOME/my_tools/nexus_project_copy"
AUDIT_DIR="$HOME/my_tools/nexus_audit"

# ---------------------------------------------------------
# NEW PHASE 0: PHYSICAL INVENTORY (The Ground Truth)
# ---------------------------------------------------------
cd "$PROJECT_DIR" || { echo "❌ Error: Project folder not found!"; exit 1; }
echo "📂 PHASE 0: MAPPING PHYSICAL REALITY..."

# We create a list of every .py file actually sitting in your folders
# We convert paths like ./nexus_core/views.py into nexus_core.views for the DNA comparison
find . -maxdepth 3 -name "*.py" | sed 's|./||' | sed 's|/|.|g' | sed 's|.py$||' > "$AUDIT_DIR/factories/physical_inventory.txt"

# 3. PHASE 1: DNA SCAN (Already working for you)
echo "🛰️  PHASE 1: REGENERATING INDIVIDUAL DNA..."

apps=("nexus_core" "nexus_gateway" "nexus_economy" "nexus_gaming" "nexus_tournaments" "nexus_content" "nexus_social")

for app in "${apps[@]}"; do
    echo "  -> Scanning $app..."
    python3 -m pydeps "$app" --show-deps --noshow > "$AUDIT_DIR/factories/${app}_dna.json"
done

# 4. PHASE 2: WELDING MASTER DNA (The Fix)
cd "$AUDIT_DIR" || exit
echo "🧬 PHASE 2: WELDING MASTER DNA..."

# We use 'jq' directly because it is already inside your activated audit_env
jq -s 'add' ./factories/*_dna.json > "$AUDIT_DIR/master_nexus_dna.json"

# Safety Check: If the file is empty, stop here to prevent Python crash
if [ ! -s "$AUDIT_DIR/master_nexus_dna.json" ]; then
    echo "❌ Error: Master DNA is empty. Check if jq is installed in audit_env."
    exit 1
fi

# 5. PHASE 3: BUILDING VISUALS (The Fix)
echo "🛡️  PHASE 3: UPDATING VISUALS & REPORT..."
python3 "$AUDIT_DIR/command_center_galaxy.py"

echo "✅ SUCCESS: Master DNA and Physical Inventory created."