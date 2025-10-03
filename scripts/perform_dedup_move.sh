#!/usr/bin/env bash
set -euo pipefail

# Move exact-duplicate files (by md5 hash) to archive/removed_scripts/<ts>/ keeping one canonical copy
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

HASH_FILE="scripts/_hashes.txt"
REPORT="scripts/_duplicates_report.txt"
TS=$(date -u +%Y%m%dT%H%M%SZ)
ARCHIVE_DIR="archive/removed_scripts/$TS"

mkdir -p "$ARCHIVE_DIR"
echo "Duplicate move report - $TS" > "$REPORT"
echo "Archive dir: $ARCHIVE_DIR" >> "$REPORT"
echo "" >> "$REPORT"

if [ ! -f "$HASH_FILE" ]; then
  echo "Hash file $HASH_FILE not found" | tee -a "$REPORT"
  exit 1
fi

# build associative array of hash -> files
declare -A seen

while read -r hash rest; do
  # rest may contain filename with spaces; get the filename after first two fields
  file=$(echo "$rest" | sed -e 's/^\s*//')
  # fallback: if rest empty, try reading whole line
  if [ -z "$file" ]; then
    # read entire line and extract filename after the md5
    file=$(echo "$hash" | sed -n 's/^[^ ]*  //p')
  fi
  # if file still empty, skip
  if [ -z "$file" ]; then
    continue
  fi
  # skip files in .git or archive or virtualenvs
  case "$file" in
    .git/*|archive/*|venv/*|.venv*|node_modules/*|__pycache__/*)
      continue
      ;;
  esac
  if [ ! -f "$file" ]; then
    # file may not exist anymore
    continue
  fi
  key="$hash"
  if [ -z "${seen[$key]:-}" ]; then
    seen[$key]="$file"
  else
    # move this duplicate to archive, preserving path
    keeper="${seen[$key]}"
    src="$file"
    dest="$ARCHIVE_DIR/$file"
    mkdir -p "$(dirname "$dest")"
    mv "$src" "$dest"
    echo "Moved duplicate: $src -> $dest (keeper: $keeper)" | tee -a "$REPORT"
  fi
done < <(awk '{ $1=$1; print }' "$HASH_FILE")

echo "Done. See $REPORT for details." 
