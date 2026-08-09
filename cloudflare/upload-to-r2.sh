#!/usr/bin/env zsh
# Upload private Parvotec HTML files to Cloudflare R2
# Prerequisites: wrangler CLI installed and authenticated (wrangler login)

set -euo pipefail

BUCKET="parvotec-private"
SRC="$HOME/workspace-active/parvotec/Machine learning for Rupert/transcripts"

upload() {
  local file="$1"
  local key="$2"
  local ctype="${3:-text/html; charset=utf-8}"
  if [[ -f "$file" ]]; then
    echo "→ $key"
    wrangler r2 object put "${BUCKET}/${key}" \
      --file "$file" \
      --content-type "$ctype"
  else
    echo "  skip (not found): $file"
  fi
}

echo "=== Uploading Parvotec private content to R2: $BUCKET ==="

# Core proposals (bilingual)
upload "$SRC/parvotec_proposal_de.html"               "parvotec_proposal_de.html"
upload "$SRC/parvotec_proposal_en.html"               "parvotec_proposal_en.html"
upload "$SRC/parvotec_proposal.html"                  "parvotec_proposal.html"

# ASGCT 2026 Analysis
upload "$SRC/parvotec_asgct2026_analysis.html"         "parvotec_asgct2026_analysis.html"
upload "$SRC/parvotec_asgct2026_analysis_bilingual.html" "parvotec_asgct2026_analysis_bilingual.html"

# Application specs
upload "$SRC/parvotec_app_workstation.html"            "parvotec_app_workstation.html"
upload "$SRC/parvotec_app_biophysics.html"             "parvotec_app_biophysics.html"
upload "$SRC/parvotec_app_computational.html"          "parvotec_app_computational.html"

# Other
upload "$SRC/parvotec_scientific_node.html"            "parvotec_scientific_node.html"
upload "$SRC/parvotec_workstation_wp.html"             "parvotec_workstation_wp.html"
upload "$SRC/parvotec_aorta_proposal.html"             "parvotec_aorta_proposal.html"
upload "$SRC/parvotec_aorta_saxs_analysis.html"        "parvotec_aorta_saxs_analysis.html"
upload "$SRC/index.html"                               "index.html"

echo ""
echo "✓ Done — verify at: wrangler r2 object list $BUCKET"
