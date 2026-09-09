# Corvus Master Windows Installer (Multi-Version Selector)
Write-Host ========================================================== -ForegroundColor Cyan
Write-Host  Corvus Programming Language Master Windows Installer  -ForegroundColor Cyan
Write-Host ========================================================== -ForegroundColor Cyan

 = Get-Command python -ErrorAction SilentlyContinue
if (-not ) {
    Write-Host [ERROR] Python 3 is required but was not found in PATH. -ForegroundColor Red
    Write-Host Please install Python 3.8+ from https://www.python.org/ or 'winget install Python.Python.3.11' -ForegroundColor Yellow
    Exit 1
}

Write-Host 
Select Corvus Version to Install: -ForegroundColor Yellow
Write-Host  [1] Version 4.3 (Latest AI/ML Stack, 30+ StdLib Modules & Rust Diagnostics) [DEFAULT]
Write-Host  [2] Version 4.2 (Desktop 2D Graphics & Murder of Crows Concurrency)
Write-Host  [3] Version 4.1 (Super Optimizer Engine & Assembly Peephole)
Write-Host  [4] Version 4.0 (Native StdLib Expansion & REPL)
Write-Host  [5] Version 3.1 (Enterprise Error Resilience)
Write-Host  [6] Version 3.0 (Self-Hosted Compiler & Concurrency)
Write-Host  [7] Version 2.0 (Multi-Platform Native Assembly)
Write-Host  [8] Version 1.1 (AST Visitor Interpreter)

 = Read-Host 
Enter selection (1-8) [Default: 1]
if ([string]::IsNullOrWhiteSpace()) {  = 1 }

 = switch () {
    1 { Version_4.3 }
    2 { Version_4.2 }
    3 { Version_4.1 }
    4 { Version_4.0 }
    5 { Version_3.1 }
    6 { Version_3.0 }
    7 { Version_2.0 }
    8 { Version_1.1 }
    default { Version_4.3 }
}

 = 
 = Join-Path  \install_windows.ps1

if (Test-Path ) {
    Write-Host 
[EXECUTING] Launching installer for ... -ForegroundColor Green
    & 
} else {
    Write-Host [ERROR] Could not locate installer script at  -ForegroundColor Red
}
