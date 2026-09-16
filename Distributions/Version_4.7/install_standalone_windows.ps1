# install_standalone_windows.ps1
# One-click Windows installer for Corvus v4.7 Standalone Native Binaries

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Corvus v4.7 Standalone Native Binaries Installer (Windows)  " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$ScriptDir = $PSScriptRoot
$StandaloneDir = Join-Path $ScriptDir "standalone"

if (-not (Test-Path (Join-Path $StandaloneDir "corvus.exe"))) {
    Write-Host "[ERROR] Could not find corvus.exe in $StandaloneDir" -ForegroundColor Red
    Exit 1
}

$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$StandaloneDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$StandaloneDir", "User")
    Write-Host "[SUCCESS] Added '$StandaloneDir' to User PATH." -ForegroundColor Green
} else {
    Write-Host "[INFO] '$StandaloneDir' is already configured in User PATH." -ForegroundColor Yellow
}

Write-Host "`n[INSTALL COMPLETE] Corvus v4.7 Standalone Binaries Installed!" -ForegroundColor Green
Write-Host "You can now open a new terminal window and run:" -ForegroundColor Cyan
Write-Host "  corvus --help" -ForegroundColor White
Write-Host "  corvus ai ask <question>" -ForegroundColor White
Write-Host "  corvus ai explain <file.crv>" -ForegroundColor White
Write-Host "  corvus ai fix <code_or_file>" -ForegroundColor White
Write-Host "  corvus ai translate <file.py>" -ForegroundColor White
Write-Host "  corvus ai chat" -ForegroundColor White
Write-Host "  corvus <file.crv>" -ForegroundColor White
Write-Host "  corvus compile <file.crv> [-o file.crvc]" -ForegroundColor White
Write-Host "  corvus --vm <file.crvc>" -ForegroundColor White
Write-Host "  corvusc <file.crv> -o <binary.exe> --run" -ForegroundColor White
Write-Host "No Python installation required!" -ForegroundColor Green
