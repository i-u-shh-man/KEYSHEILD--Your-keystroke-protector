# KeyShield Complete Build Script
# This script builds all components of the KeyShield application

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "    KeyShield Complete Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$cmakePath = "C:\Program Files\CMake\bin\cmake.exe"
if (-not (Test-Path $cmakePath)) {
    Write-Host "CMake not found. Installing..." -ForegroundColor Red
    winget install --id Kitware.CMake --source winget
}

# Try to find a C++ compiler
$hasCompiler = $false
if (Get-Command cl -ErrorAction SilentlyContinue) {
    Write-Host "MSVC compiler found" -ForegroundColor Green
    $hasCompiler = $true
    $generator = ""
} elseif (Get-Command g++ -ErrorAction SilentlyContinue) {
    Write-Host "MinGW g++ found" -ForegroundColor Green
    $hasCompiler = $true
    $generator = "-G", "MinGW Makefiles"
} else {
    Write-Host "No C++ compiler found. Installing LLVM MinGW..." -ForegroundColor Red
    winget install --id "LLVM.LLVM" --source winget
    if (Get-Command clang++ -ErrorAction SilentlyContinue) {
        Write-Host "Clang found" -ForegroundColor Green
        $hasCompiler = $true
        $generator = "-G", "Unix Makefiles"
        $env:CC = "clang"
        $env:CXX = "clang++"
    } else {
        Write-Host "Could not install compiler. C++ build will be skipped." -ForegroundColor Red
    }
}

# Build C++ component
if ($hasCompiler) {
    Write-Host "`nBuilding C++ KeyShield executable..." -ForegroundColor Yellow

    $root = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $root

    $buildDir = Join-Path $root "build"
    if (Test-Path $buildDir) {
        Remove-Item -Recurse -Force $buildDir
    }
    New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

    & $cmakePath -S $root -B $buildDir @generator
    if ($LASTEXITCODE -eq 0) {
        & $cmakePath --build $buildDir --config Release
        if ($LASTEXITCODE -eq 0) {
            $exe = Join-Path $buildDir "KeyShield.exe"
            if (-not (Test-Path $exe)) {
                $exe = Join-Path $buildDir "Release\KeyShield.exe"
            }
            if (Test-Path $exe) {
                Write-Host "C++ build successful: $exe" -ForegroundColor Green
            } else {
                Write-Host "C++ build completed but executable not found" -ForegroundColor Yellow
            }
        } else {
            Write-Host "C++ build failed" -ForegroundColor Red
        }
    } else {
        Write-Host "CMake configuration failed" -ForegroundColor Red
    }
} else {
    Write-Host "`nSkipping C++ build - no compiler available" -ForegroundColor Yellow
}

# Build Python executables
Write-Host "`nBuilding Python executables..." -ForegroundColor Yellow

$venvPath = Join-Path $root ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"
$pyinstallerExe = Join-Path $venvPath "Scripts\pyinstaller.exe"

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    & python -m venv .venv
}

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& $pipExe install pyinstaller pynput keyboard

# Build executables
Write-Host "Building Dashboard.exe..." -ForegroundColor Yellow
& $pyinstallerExe --onefile --windowed Dashboard.py

Write-Host "Building keylogger.exe..." -ForegroundColor Yellow
& $pyinstallerExe --onefile keylogger.py

# Check results
Write-Host "`nBuild Results:" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan

$cppExe = Join-Path $buildDir "KeyShield.exe"
if (-not (Test-Path $cppExe)) {
    $cppExe = Join-Path $buildDir "Release\KeyShield.exe"
}

if (Test-Path $cppExe) {
    Write-Host "[+] KeyShield.exe (C++)" -ForegroundColor Green
} else {
    Write-Host "[-] KeyShield.exe (C++) - Build failed or skipped" -ForegroundColor Red
}

if (Test-Path "dist\Dashboard.exe") {
    Write-Host "[+] Dashboard.exe (Python)" -ForegroundColor Green
} else {
    Write-Host "[-] Dashboard.exe (Python) - Build failed" -ForegroundColor Red
}

if (Test-Path "dist\keylogger.exe") {
    Write-Host "[+] keylogger.exe (Python)" -ForegroundColor Green
} else {
    Write-Host "[-] keylogger.exe (Python) - Build failed" -ForegroundColor Red
}

Write-Host "`nTo create installer, run:" -ForegroundColor Yellow
Write-Host "ISCC KeyShield_Installer.iss" -ForegroundColor White

Write-Host "`nTo run the application:" -ForegroundColor Yellow
Write-Host ".\KeyShield_Launcher.bat" -ForegroundColor White

Write-Host "`nBuild complete!" -ForegroundColor Green