# Corvus Master Windows Installer (Multi-Version Selector)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Corvus Programming Language Master Windows Installer   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "[ERROR] Python 3 is required but was not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/ or 'winget install Python.Python.3.11'" -ForegroundColor Yellow
    Exit 1
}

Write-Host "`nSelect Corvus Version to Install:" -ForegroundColor Yellow
Write-Host "  [1] Version 4.1 (Latest Super Optimizer Engine) [DEFAULT]"
Write-Host "  [2] Version 4.0 (Native StdLib Expansion & REPL)"
Write-Host "  [3] Version 3.1 (Enterprise Error Resilience)"
Write-Host "  [4] Version 3.0 (Self-Hosted Compiler & Concurrency)"
Write-Host "  [5] Version 2.0 (Multi-Platform Native Assembly)"
Write-Host "  [6] Version 1.1 (AST Visitor Interpreter)"

$choice = Read-Host "`nEnter selection (1-6) [Default: 1]"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

$verFolder = switch ($choice) {
    "1" { "Version_4.1" }
    "2" { "Version_4.0" }
    "3" { "Version_3.1" }
    "4" { "Version_3.0" }
    "5" { "Version_2.0" }
    "6" { "Version_1.1" }
    default { "Version_4.1" }
}

$scriptDir = $PSScriptRoot
$targetInstaller = Join-Path $scriptDir "$verFolder\install_windows.ps1"

if (Test-Path $targetInstaller) {
    Write-Host "`n[EXECUTING] Launching installer for $verFolder..." -ForegroundColor Green
    & $targetInstaller
} else {
    Write-Host "[ERROR] Could not locate installer script at $targetInstaller" -ForegroundColor Red
}
