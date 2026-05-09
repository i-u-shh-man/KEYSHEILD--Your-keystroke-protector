# KeyShield

KeyShield is a Windows-focused proof-of-concept for behavioral keylogger detection and demonstration. It combines a small C++ command-line demo, a Tkinter process-monitoring dashboard, and a local test keylogger used to generate keyboard-hook activity for controlled testing.

> Use this project only on systems you own or have explicit permission to test. The hook and test logger components intentionally capture keystrokes for demonstration purposes.

## Components

- `KeyShield.exe`: C++ demo application built from `main.cpp`, `Analyst.cpp`, and `keyboard_hook.cpp`.
- `Dashboard.py`: Tkinter GUI that scans running Windows processes with PowerShell and assigns simple heuristic threat scores.
- `keylogger.py`: local test logger that records key presses to `keylog_output.txt` using `pynput` when available, with `keyboard` as a fallback.
- `KeyShield_Launcher.bat`: starts the packaged dashboard, packaged test logger, and selected C++ mode.
- `KeySheildDriver.c`: KMDF driver stub for future work; it is not part of the current CMake build.

## C++ Demo Modes

```text
KeyShield.exe analyze   Run seeded process threat scoring
KeyShield.exe hook      Install a low-level keyboard hook and log key names
KeyShield.exe help      Show command help
```

If no command is provided, `analyze` runs by default.

## Prerequisites

- Windows
- CMake 3.20 or newer
- A C++17 compiler, such as Visual Studio Build Tools or MinGW-w64
- Python 3, if running or packaging the Python components
- Python packages for the test logger/package build: `pynput`, `keyboard`, and `pyinstaller`

The `build_all.ps1` helper can install missing CMake/compiler tooling through `winget` and installs Python package dependencies into `.venv`.

## Build the C++ Application

From PowerShell in the repository root:

```powershell
.\build.ps1
```

Run the built executable from whichever path CMake produced:

```powershell
.\build\Release\KeyShield.exe analyze
.\build\Release\KeyShield.exe hook
```

Some generators place the executable at:

```powershell
.\build\KeyShield.exe
```

## Manual CMake Build

```powershell
cmake -S . -B .\build
cmake --build .\build --config Release
.\build\Release\KeyShield.exe analyze
```

## Run the Python Components

Create and activate a virtual environment, then install the logger dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pynput keyboard pyinstaller
```

Run the dashboard:

```powershell
python Dashboard.py
```

Run the test keylogger:

```powershell
python keylogger.py
```

The logger writes to `keylog_output.txt`. Press `Esc` or `Ctrl+C` in the logger console to stop it.

## Package Everything

To build the C++ executable and package the Python scripts as standalone executables:

```powershell
.\build_all.ps1
```

Expected packaged outputs:

- `build\KeyShield.exe` or `build\Release\KeyShield.exe`
- `dist\Dashboard.exe`
- `dist\keylogger.exe`

Then launch the packaged demo:

```bat
KeyShield_Launcher.bat
```

The launcher checks for required executables, starts the dashboard, starts the test logger, and prompts for the C++ `analyze` or `hook` mode.

## Installer

After all executables are built, create the Windows installer with Inno Setup:

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" KeyShield_Installer.iss
```

The installer output is written to `installer\KeyShield_Installer.exe`.

## Notes and Limitations

- Detection is heuristic and demo-oriented; it is not a production keylogger detector.
- The C++ `analyze` mode uses seeded sample processes rather than live process telemetry.
- The C++ `hook` mode writes `keylog_output.txt` beside the built executable.
- The Python dashboard computes process scores from process name/path signals and marks high-scoring processes as isolated in the UI only.
- Build outputs, packaged executables, virtual environments, and runtime logs should stay out of version control.
