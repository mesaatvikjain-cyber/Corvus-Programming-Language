# setup_embedded_python.ps1
# Automates downloading and setting up the official Python 3.11 Embeddable zip
# inside portable-sdk/runtime for 100% offline, zero-dependency usage!

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$PythonZipUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
$ZipFile = Join-Path $ScriptDir "python_embed.zip"
$TargetDir = $ScriptDir

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Corvus Portable SDK: Embedded Python Runtime Setup " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (Test-Path (Join-Path $TargetDir "python.exe")) {
    Write-Host "[INFO] Embedded Python runtime already exists in $TargetDir" -ForegroundColor Green
    Exit 0
}

Write-Host "[1/3] Downloading official Python 3.11 Embeddable package..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $PythonZipUrl -OutFile $ZipFile

Write-Host "[2/3] Extracting Python runtime to $TargetDir..." -ForegroundColor Yellow
Expand-Archive -Path $ZipFile -DestinationPath $TargetDir -Force
Remove-Item -Force $ZipFile

# Enable site-packages support in embeddable python by uncommenting 'import site' in ._pth file
$pthFile = Get-ChildItem -Path $TargetDir -Filter "*._pth" | Select-Object -First 1
if ($pthFile) {
    $content = Get-Content $pthFile.FullName
    $updated = $content -replace "#import site", "import site"
    Set-Content -Path $pthFile.FullName -Value $updated
}

Write-Host "[3/3] Testing embedded Python runtime..." -ForegroundColor Yellow
& (Join-Path $TargetDir "python.exe") --version

Write-Host "`n[SUCCESS] Corvus Portable Embedded Runtime is ready!" -ForegroundColor Green
Write-Host "You can now run 'bin\corvus.bat' or 'bin\corvusc.bat' completely offline without host Python!" -ForegroundColor Cyan
