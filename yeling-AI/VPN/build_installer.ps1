# Build the graphical installer exe using PyInstaller
# Usage: .\build_installer.ps1

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$venv = ".venv"
if (!(Test-Path $venv)) {
    Write-Host "Virtualenv not found, creating..."
    python -m venv $venv
}

# Activate
$activate = Join-Path $venv 'Scripts\Activate.ps1'
if (Test-Path $activate) { . $activate } else { Write-Host "Activate script not found, run manually"; exit 1 }

# Ensure PyInstaller is installed
python -m pip install --upgrade pip
python -m pip install pyinstaller

# Ensure multi_tool.exe exists (the main CLI) - if not, build it first
if (-not (Test-Path .\dist\multi_tool.exe)) {
    Write-Host "multi_tool.exe not found in dist; building it first..."
    .\build_windows.ps1
}

# Package installer_app.py into installer.exe and include dist\multi_tool.exe as data
$hiddenArgs = ""
$srcExe = Join-Path (Get-Location) 'dist\multi_tool.exe'
if (Test-Path $srcExe) {
    $targetDir = Join-Path (Get-Location) 'build_installer\dist'
    if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }
    Copy-Item -Path $srcExe -Destination (Join-Path $targetDir 'multi_tool.exe') -Force
    $addData = Join-Path $targetDir 'multi_tool.exe' + ';dist\\multi_tool.exe'
} else {
    Write-Host "Warning: dist\multi_tool.exe not found; installer will not include CLI exe" -ForegroundColor Yellow
    $addData = ""
}

pyinstaller --onefile --name multi_tool_installer ${addData:+--add-data} $addData --distpath dist_installer --workpath build_installer --specpath build_installer installer_app.py $hiddenArgs

if ($LASTEXITCODE -ne 0) { Write-Host "Installer build failed"; exit $LASTEXITCODE }

Write-Host "Installer created at dist_installer\multi_tool_installer.exe" -ForegroundColor Green
