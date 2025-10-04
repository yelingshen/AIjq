# 构建 Windows exe 的辅助脚本（PowerShell）
# 用法：在仓库根目录运行：
#   .\build_windows.ps1
# 可选参数：-OneDir 将使用 --onedir 模式以便调试
param(
    [switch]$OneDir
)

$venvPath = ".venv"

Write-Host "创建虚拟环境..."
python -m venv $venvPath

Write-Host "激活虚拟环境（PowerShell）..."
$activate = Join-Path $venvPath 'Scripts\Activate.ps1'
if (Test-Path $activate) {
    # dot-source the activation script so the current process gets the venv environment
    . $activate
} else {
    Write-Host "无法找到激活脚本: $activate" -ForegroundColor Red
    Write-Host "请手动激活虚拟环境然后重试，例如: .\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "安装运行时依赖和 PyInstaller..."
python -m pip install --upgrade pip

# Install requirements but skip netifaces on Windows because it requires
# a C compiler (Visual C++ Build Tools). Project code handles netifaces
# being absent at runtime with graceful errors.
$buildDir = Join-Path (Get-Location) 'build'
if (!(Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}
$reqs = Get-Content -Path "multi_tool\requirements.txt" | Where-Object { $_ -and ($_ -notmatch '^\s*#') -and ($_ -notmatch 'netifaces') }
$tmpReq = Join-Path $buildDir 'requirements_no_netifaces.txt'
$reqs | Out-File -FilePath $tmpReq -Encoding utf8
python -m pip install -r $tmpReq
python -m pip install pyinstaller

# 可选：将需要的 hidden imports 在此列出
$hiddenImports = @(
    # 如果遇到缺失模块错误，可在此添加，例如： 'tkinter'
)
$hiddenArgs = ""
foreach ($h in $hiddenImports) { $hiddenArgs += " --hidden-import $h" }

# 选择 onefile 或 onedir
if ($OneDir) {
    Write-Host "使用 --onedir 模式（调试模式）"
    pyinstaller --name multi_tool_launcher --distpath dist --workpath build --specpath build launcher.py $hiddenArgs
} else {
    Write-Host "使用 --onefile 模式（单文件输出）"
    pyinstaller --onefile --name multi_tool --distpath dist --workpath build --specpath build launcher.py $hiddenArgs
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "打包失败，查看 PyInstaller 输出日志（build 目录）" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "打包完成，产物位于 dist\" -ForegroundColor Green
Write-Host "测试运行 exe：dist\\multi_tool.exe --help" -ForegroundColor Yellow

# 取消激活：PowerShell 会在脚本结束后恢复到父进程的环境
