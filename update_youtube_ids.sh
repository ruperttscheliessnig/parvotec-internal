#!/usr/bin/env zsh
# Nach YouTube-Upload: Video-IDs hier eintragen und Script ausführen.
# YouTube-ID = der Teil nach ?v= in der YouTube-URL
# Beispiel: https://youtube.com/watch?v=dQw4w9WgXcQ → ID = dQw4w9WgXcQ

set -euo pipefail

TALKS="$HOME/workspace-active/parvotec/Machine learning for Rupert/transcripts/talks"

# ─── HIER DIE IDs EINTRAGEN (nach Upload) ───────────────────────────────────
declare -A YOUTUBE_IDS=(
  [AAV_Engineering_III]="PENDING"
  [AAV_Engineering_IV]="PENDING"
  [AAV_Trafficking]="PENDING"
  [Lir_AAV_LLM]="PENDING"
  [ShapeTX_AAV5engineering]="PENDING"
  [TuningReceptorInteractions_Caltech]="PENDING"
)
# ────────────────────────────────────────────────────────────────────────────

for name ytid in ${(kv)YOUTUBE_IDS}; do
  file="$TALKS/${name}.html"
  if [[ ! -f "$file" ]]; then
    echo "  skip: $name.html not found"
    continue
  fi
  if [[ "$ytid" == "PENDING" ]]; then
    echo "  skip: $name — kein YouTube-ID gesetzt"
    continue
  fi
  # Replace data-ytid="PENDING" or previous ID with new ID
  sed -i '' "s/data-ytid=\"[^\"]*\"/data-ytid=\"${ytid}\"/g" "$file"
  echo "  ✓ $name → $ytid"
done

echo ""
echo "✓ Fertig. Jetzt committen und deployen:"
echo "  cd ~/workspace-active/parvotec"
echo "  git add 'Machine learning for Rupert/transcripts/talks/'"
echo "  git commit -m 'feat: YouTube video IDs eingetragen'"
echo "  git push origin main && git push origin main:gh-pages"
