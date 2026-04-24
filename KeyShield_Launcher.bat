@echo off
echo ========================================
echo    KeyShield Application Launcher
echo ========================================
echo.
echo This will launch all KeyShield components:
echo 1. KeyShield C++ Analyzer/Hook
echo 2. Dashboard GUI
echo 3. Keylogger (for testing)
echo.
echo Note: C++ executable must be built first
echo.

set "SCRIPT_DIR=%~dp0"

echo Checking for executables...

if exist "%SCRIPT_DIR%build\KeyShield.exe" (
    echo [+] KeyShield.exe found
) else if exist "%SCRIPT_DIR%build\Release\KeyShield.exe" (
    echo [+] KeyShield.exe found in Release folder
) else (
    echo [-] KeyShield.exe not found. Please build the C++ project first.
    echo Run: .\build.ps1
    pause
    exit /b 1
)

if exist "%SCRIPT_DIR%dist\Dashboard.exe" (
    echo [+] Dashboard.exe found
) else (
    echo [-] Dashboard.exe not found. Please package Python scripts first.
    pause
    exit /b 1
)

if exist "%SCRIPT_DIR%dist\keylogger.exe" (
    echo [+] keylogger.exe found
) else (
    echo [-] keylogger.exe not found. Please package Python scripts first.
    pause
    exit /b 1
)

echo.
echo Starting KeyShield components...
echo.

echo Starting Dashboard GUI...
start "" "%SCRIPT_DIR%dist\Dashboard.exe"

timeout /t 2 /nobreak > nul

echo Starting Keylogger (press ESC in console to stop)...
start "" "%SCRIPT_DIR%dist\keylogger.exe"

timeout /t 2 /nobreak > nul

echo.
echo Choose KeyShield mode:
echo 1. Analyze mode (threat detection demo)
echo 2. Hook mode (keyboard monitoring demo)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Starting KeyShield in Analyze mode...
    if exist "%SCRIPT_DIR%build\KeyShield.exe" (
        "%SCRIPT_DIR%build\KeyShield.exe" analyze
    ) else (
        "%SCRIPT_DIR%build\Release\KeyShield.exe" analyze
    )
) else if "%choice%"=="2" (
    echo Starting KeyShield in Hook mode...
    if exist "%SCRIPT_DIR%build\KeyShield.exe" (
        "%SCRIPT_DIR%build\KeyShield.exe" hook
    ) else (
        "%SCRIPT_DIR%build\Release\KeyShield.exe" hook
    )
) else (
    echo Invalid choice. Starting in Analyze mode by default...
    if exist "%SCRIPT_DIR%build\KeyShield.exe" (
        "%SCRIPT_DIR%build\KeyShield.exe" analyze
    ) else (
        "%SCRIPT_DIR%build\Release\KeyShield.exe" analyze
    )
)

echo.
echo KeyShield application finished.
pause