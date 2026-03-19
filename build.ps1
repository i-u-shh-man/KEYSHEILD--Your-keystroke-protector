Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-Command([string]$Name) {
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Command "cmake")) {
  Write-Host "CMake not found. Install CMake and ensure `cmake` is on PATH." -ForegroundColor Red
  exit 1
}

$buildDir = Join-Path $root "build"
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

$generatorArgs = @()
if (Test-Command "cl") {
  # Let CMake pick the default Visual Studio generator for the installed toolset.
  $generatorArgs = @()
} elseif (Test-Command "g++") {
  # MinGW generator works when cmake is the MinGW build.
  $generatorArgs = @("-G", "MinGW Makefiles")
} else {
  Write-Host "No C++ compiler found on PATH (cl or g++)." -ForegroundColor Red
  Write-Host "Install Visual Studio Build Tools (Desktop development with C++) or MinGW-w64." -ForegroundColor Yellow
  exit 1
}

cmake -S $root -B $buildDir @generatorArgs
cmake --build $buildDir --config Release

$exe = Join-Path $buildDir "keyboard_hook.exe"
if (-not (Test-Path $exe)) {
  $exe = Join-Path $buildDir "Release\keyboard_hook.exe"
}
if (Test-Path $exe) {
  Write-Host "Built: $exe" -ForegroundColor Green
  Write-Host "Run:  `"$exe`""
} else {
  Write-Host "Build finished but keyboard_hook.exe was not found in expected locations." -ForegroundColor Yellow
}
