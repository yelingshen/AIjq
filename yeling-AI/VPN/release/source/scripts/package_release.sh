#!/usr/bin/env bash
set -euo pipefail
OUTDIR=release
ZIPNAME=multi_tool_release.zip
ROOT=$(pwd)
rm -rf "$OUTDIR"
mkdir -p "$OUTDIR/source"
# Copy source excluding build artifacts
rsync -a --exclude 'dist' --exclude 'build' --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' . "$OUTDIR/source/"
# include windows exe if present
if [ -f "dist/multi_tool.exe" ]; then
  cp dist/multi_tool.exe "$OUTDIR/"
fi
# ubuntu launcher
cat > "$OUTDIR/run_multi_tool_ubuntu.sh" <<'SH'
#!/usr/bin/env bash
cd "$(pwd)"
python3 -m multi_tool.cli "$@"
SH
chmod +x "$OUTDIR/run_multi_tool_ubuntu.sh"
cat > "$OUTDIR/README_RELEASE.txt" <<'TXT'
Release package for multi_tool

Contents:
- source/ : full source code
- multi_tool.exe : Windows executable (if present)
- run_multi_tool_ubuntu.sh : launcher for Ubuntu (requires python3)

Usage (Windows): run multi_tool.exe
Usage (Ubuntu): chmod +x run_multi_tool_ubuntu.sh; ./run_multi_tool_ubuntu.sh
TXT
# create zip
rm -f "$ZIPNAME"
zip -r "$ZIPNAME" "$OUTDIR"
echo "Created $ZIPNAME"
