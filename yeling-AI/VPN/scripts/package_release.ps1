Param(
    [string]$OutDir = "release",
    [string]$ZipName = "multi_tool_release.zip"
)

$root = (Get-Location).Path
if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

# Copy source (exclude virtualenv, editor folders and the output dir itself to avoid recursion)
$src = Join-Path $OutDir 'source'
if (Test-Path $src) { Remove-Item $src -Recurse -Force }
# Build exclude patterns/names and copy items one-by-one to avoid Copy-Item container-to-leaf errors
$excludes = @('*.pyc', '__pycache__', 'dist', 'build', 'build_installer', '.venv', '.vscode', '.git', $OutDir)
Get-ChildItem -LiteralPath $root -Force | ForEach-Object {
    $name = $_.Name
    # Skip the output folder and any explicitly excluded folder names
    if ($excludes -contains $name) { return }
    # Skip files matching excluded patterns (like *.pyc)
    $skip = $false
    foreach ($pat in $excludes) {
        if ($pat -like '*.*' -and -not ($pat -match '^\\.')) {
            if ($name -like $pat) { $skip = $true; break }
        }
    }
    if ($skip) { return }

    if ($_.PSIsContainer) {
        Copy-Item -LiteralPath $_.FullName -Destination $src -Recurse -Force
    } else {
        Copy-Item -LiteralPath $_.FullName -Destination $src -Force
    }
}

# Include Windows exe if exists
$exe = Join-Path $root 'dist\multi_tool.exe'
if (Test-Path $exe) {
    Copy-Item $exe -Destination $OutDir -Force
}

# Include Python launcher if present
$launcher_py = Join-Path $root 'run_multi_tool.py'
if (Test-Path $launcher_py) {
    Copy-Item $launcher_py -Destination $OutDir -Force
}

# Create a simple ubuntu launcher script
$launcher = Join-Path $OutDir 'run_multi_tool_ubuntu.sh'
$launcherContent = @'
#!/usr/bin/env bash
cd "$(pwd)"
python3 -m multi_tool.cli "$@"
'@
Set-Content -Path $launcher -Value $launcherContent -Encoding UTF8

# Add README
$readme = Join-Path $OutDir 'README_RELEASE.txt'
$readmeContent = @"
Release package for multi_tool

Contents:
- source/ : full source code
- multi_tool.exe : Windows executable (if present)
- run_multi_tool_ubuntu.sh : launcher for Ubuntu (requires python3)

Usage (Windows): run multi_tool.exe
Usage (Ubuntu): chmod +x run_multi_tool_ubuntu.sh; ./run_multi_tool_ubuntu.sh
"@
Set-Content -Path $readme -Value $readmeContent -Encoding UTF8

# Zip
$zipPath = Join-Path $root $ZipName
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($OutDir, $zipPath)
Write-Host "Created $zipPath"

# Create a cleaned zip that strips .pyc and __pycache__ to avoid shipping caches
$cleanZip = [System.IO.Path]::Combine($root, 'multi_tool_release_clean.zip')
if (Test-Path $cleanZip) { Remove-Item $cleanZip -Force }
[System.IO.Compression.ZipFile]::CreateFromDirectory($OutDir, $cleanZip)
Write-Host "Also created cleaned copy: $cleanZip"
