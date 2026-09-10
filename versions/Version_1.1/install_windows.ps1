# Corvus v1.1 Automated Windows Installer
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Installing Corvus Programming Language v1.1  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Verify Python Installation
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "[ERROR] Python 3 is required but was not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ or 'winget install Python.Python.3.11'" -ForegroundColor Yellow
    Exit 1
}

$scriptDir = $PSScriptRoot
$batPath = Join-Path $scriptDir "corvus.bat"

# 2. Create corvus.bat wrapper
$batContent = @"
@echo off
python "$scriptDir\Interpreter\Corvus.py" %*
"@

Set-Content -Path $batPath -Value $batContent
Write-Host "[SUCCESS] Created Corvus CLI wrapper: $batPath" -ForegroundColor Green

# 3. Add to User PATH Environment Variable
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$scriptDir*") {
    $newPath = "$userPath;$scriptDir"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "[SUCCESS] Added '$scriptDir' to User PATH environment variable." -ForegroundColor Green
} else {
    Write-Host "[INFO] '$scriptDir' is already present in User PATH." -ForegroundColor Yellow
}

Write-Host "`n[INSTALL COMPLETE] Corvus v1.1 installed successfully!" -ForegroundColor Green
Write-Host "Restart your terminal and type 'corvus <file.crv>' to run Corvus scripts!" -ForegroundColor Cyan
