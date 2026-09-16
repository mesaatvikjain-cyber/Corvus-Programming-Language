@echo off
setlocal enabledelayedexpansion

:: Resolve root directory of portable-sdk
set "PORTABLE_DIR=%~dp0.."
set "EMBED_PYTHON=%PORTABLE_DIR%\runtime\python.exe"

:: 1. Check if bundled portable python exists in runtime/
if exist "%EMBED_PYTHON%" (
    "%EMBED_PYTHON%" "%PORTABLE_DIR%\Interpreter\Corvus.py" %*
    exit /b %ERRORLEVEL%
)

:: 2. Check if Python is available on system PATH
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "%PORTABLE_DIR%\Interpreter\Corvus.py" %*
    exit /b %ERRORLEVEL%
)

:: 3. Fallback warning with auto-bootstrap guidance
echo [ERROR] No Python runtime found!
echo Corvus Portable SDK can run with system Python or an embedded runtime.
echo To bootstrap the zero-dependency embedded Python automatically, run:
echo   powershell -ExecutionPolicy Bypass -File "%PORTABLE_DIR%\runtime\setup_embedded_python.ps1"
echo Or install Python 3.8+ from https://www.python.org/
exit /b 1
