@echo off
echo Starting DexterOptiClean...

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
) else (
    echo Standard user privileges detected.
)

:: Start the application
python app.py %*
pause