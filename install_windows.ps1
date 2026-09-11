# Corvus Master Windows Installer (Multi-Version Selector)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Corvus Programming Language Master Windows Installer     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

Write-Host "`nSelect Corvus Installation Package:" -ForegroundColor Yellow
Write-Host "  [0] Standalone Native Binaries v4.6 (Zero Python Required) [RECOMMENDED]" -ForegroundColor Green
Write-Host "  [1] Version 4.6 (Security Hardened, Bytecode VM & .crvc Compiler) [DEFAULT]"
Write-Host "  [2] Version 4.5 (Corvus Bytecode VM & .crvc Compiler)"
Write-Host "  [3] Version 4.4 (Universal Dual Syntax & Smart Type Inference)"
Write-Host "  [4] Version 4.3 (AI/ML Stack, 30+ StdLib Modules & Rust Diagnostics)"
Write-Host "  [5] Version 4.2 (Desktop 2D Graphics & Murder of Crows Concurrency)"
Write-Host "  [6] Version 4.1 (Super Optimizer Engine & Assembly Peephole)"
Write-Host "  [7] Version 4.0 (Native StdLib Expansion & REPL)"
Write-Host "  [8] Version 3.1 (Enterprise Error Resilience)"
Write-Host "  [9] Version 3.0 (Self-Hosted Compiler & Concurrency)"
Write-Host " [10] Version 2.0 (Multi-Platform Native Assembly)"
Write-Host " [11] Version 1.1 (AST Visitor Interpreter)"

$choice = Read-Host "`nEnter selection (0-11) [Default: 0]"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "0" }

if ($choice -eq "0") {
    $installer = Join-Path $PSScriptRoot "Distributions\Version_4.6\install_standalone_windows.ps1"
    if (Test-Path $installer) {
        Write-Host "`n[EXECUTING] Launching Standalone Native Binaries Installer..." -ForegroundColor Green
        & $installer
        Exit 0
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3 is required for source installations but was not found in PATH." -ForegroundColor Red
    Write-Host "Tip: Choose option [0] to install Standalone Native Binaries with zero Python required!" -ForegroundColor Yellow
    Exit 1
}

$verFolder = switch ($choice) {
    "1" { "Version_4.6" }
    "2" { "Version_4.5" }
    "3" { "Version_4.4" }
    "4" { "Version_4.3" }
    "5" { "Version_4.2" }
    "6" { "Version_4.1" }
    "7" { "Version_4.0" }
    "8" { "Version_3.1" }
    "9" { "Version_3.0" }
    "10" { "Version_2.0" }
    "11" { "Version_1.1" }
    default { "Version_4.6" }
}

$targetInstaller = Join-Path $PSScriptRoot "versions\$verFolder\install_windows.ps1"

if (Test-Path $targetInstaller) {
    Write-Host "`n[EXECUTING] Launching installer for $verFolder..." -ForegroundColor Green
    & $targetInstaller
} else {
    Write-Host "[ERROR] Could not locate installer script at $targetInstaller" -ForegroundColor Red
}
