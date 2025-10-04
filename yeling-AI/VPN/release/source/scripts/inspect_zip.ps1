$f = 'C:\Users\WJ\Desktop\VPN\VPN\multi_tool_release.zip'
if (Test-Path $f) {
    $s = (Get-Item $f).Length
    Write-Host "ZIP_PATH: $f"
    Write-Host "SIZE_BYTES: $s"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $z = [System.IO.Compression.ZipFile]::OpenRead($f)
    $i = 0
    foreach ($e in $z.Entries) {
        if ($i -ge 20) { break }
        Write-Host $e.FullName
        $i++
    }
    $z.Dispose()
} else {
    Write-Host 'ZIP_MISSING'
}