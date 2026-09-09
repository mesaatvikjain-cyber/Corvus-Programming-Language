# Corvus v4.0 Automated Windows Installer (Native StdLib, REPL & VS Code Extension)
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Installing Corvus Programming Language v4.0  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "[ERROR] Python 3 is required but was not found in PATH." -ForegroundColor Red
    Exit 1
}

$scriptDir = $PSScriptRoot
$batInterpreter = Join-Path $scriptDir "corvus.bat"
$batCompiler = Join-Path $scriptDir "corvusc.bat"

Set-Content -Path $batInterpreter -Value "@echo off`npython `"$scriptDir\Interpreter\Corvus.py`" %*"
Set-Content -Path $batCompiler -Value "@echo off`npython `"$scriptDir\Compiler_Windows\CorvusC_win64.py`" %*"

Write-Host "[SUCCESS] Created Corvus Interpreter CLI wrapper: $batInterpreter" -ForegroundColor Green
Write-Host "[SUCCESS] Created Corvus Compiler CLI wrapper: $batCompiler" -ForegroundColor Green

$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$scriptDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$scriptDir", "User")
    Write-Host "[SUCCESS] Added '$scriptDir' to User PATH." -ForegroundColor Green
}

Write-Host "`n[INSTALL COMPLETE] Corvus v4.0 installed!" -ForegroundColor Green
Write-Host "Commands: 'corvus <file.crv>', 'corvus --repl', or 'corvusc <file.crv>'" -ForegroundColor Cyan
