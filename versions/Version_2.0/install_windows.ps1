# Corvus v2.0 Automated Windows Installer
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Installing Corvus Programming Language v2.0  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "[ERROR] Python 3 is required but was not found in PATH." -ForegroundColor Red
    Exit 1
}

$scriptDir = $PSScriptRoot
$batInterpreter = Join-Path $scriptDir "corvus.bat"
$batCompiler = Join-Path $scriptDir "corvusc.bat"

# Interpreter Wrapper
Set-Content -Path $batInterpreter -Value "@echo off`npython `"$scriptDir\Interpreter\Corvus.py`" %*"
# Compiler Wrapper
Set-Content -Path $batCompiler -Value "@echo off`npython `"$scriptDir\Compiler\CorvusC.py`" %*"

Write-Host "[SUCCESS] Created Corvus Interpreter CLI wrapper: $batInterpreter" -ForegroundColor Green
Write-Host "[SUCCESS] Created Corvus Compiler CLI wrapper: $batCompiler" -ForegroundColor Green

# Add to User PATH
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$scriptDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$scriptDir", "User")
    Write-Host "[SUCCESS] Added '$scriptDir' to User PATH." -ForegroundColor Green
}

Write-Host "`n[INSTALL COMPLETE] Corvus v2.0 installed!" -ForegroundColor Green
Write-Host "Commands: 'corvus <file.crv>' (Interpreter) or 'corvusc <file.crv>' (Compiler)" -ForegroundColor Cyan
