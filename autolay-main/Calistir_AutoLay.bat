@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Calistir_AutoLay.ps1"
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo AutoLay calistirma hatasi. Cikis kodu: %EXITCODE%
)

echo.
pause
exit /b %EXITCODE%
