# KeyShield

KeyShield is a Windows-focused proof-of-concept repository for behavioral keylogger detection. The repository is now aligned around one runnable C++ entry point, `KeyShield.exe`, with two demo modes exposed through that single executable.

## What runs now

- `analyze`: scores demo processes using simple behavioral heuristics
- `hook`: installs a low-level keyboard hook, prints virtual-key codes, and appends keys to `keylog_output.txt`

## Project layout

- `main.cpp`: primary application entry point
- `Analyst.cpp` / `Analyst.h`: process threat scoring demo logic
- `keyboard_hook.cpp` / `keyboard_hook.h`: low-level keyboard hook demo
- `Dashboard.py`: optional mock GUI for presentation/demo purposes
- `KeySheildDriver.c`: KMDF driver stub for future work, not part of the current build

## Quick build

From PowerShell in the repository root:

```powershell
.\build.ps1
```

If the build succeeds, run one of these:

```powershell
.\build\Release\KeyShield.exe analyze
.\build\Release\KeyShield.exe hook
```

Depending on your generator, the executable may also be placed at `.\build\KeyShield.exe`.

## Manual build with CMake

```powershell
cmake -S . -B .\build
cmake --build .\build --config Release
.\build\Release\KeyShield.exe analyze
```

## Manual build with MSVC

```bat
cl /EHsc /W4 main.cpp Analyst.cpp keyboard_hook.cpp user32.lib /Fe:KeyShield.exe
```

## Commands

```text
KeyShield.exe analyze
KeyShield.exe hook
KeyShield.exe help
```

## Complete Application Packaging

The application has been packaged into standalone executables:

### Python Components (Already Built)
- `dist\Dashboard.exe` - GUI dashboard for threat monitoring
- `dist\keylogger.exe` - Test keylogger application

### C++ Component
- `build\KeyShield.exe` - Main C++ executable (requires building)

### Running the Complete Application

1. **Build the C++ component:**
   ```powershell
   .\build_all.ps1
   ```

2. **Run all components together:**
   ```bat
   KeyShield_Launcher.bat
   ```

   This launcher will:
   - Check for all required executables
   - Start the Dashboard GUI
   - Start the keylogger
   - Prompt for KeyShield mode (analyze/hook)
   - Run the selected mode

### Creating an Installer

To create a complete Windows installer:

1. Ensure all components are built
2. Run the Inno Setup compiler:
   ```bat
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" KeyShield_Installer.iss
   ```

This creates `installer\KeyShield_Installer.exe` which can be distributed and installed on any Windows system.

## Notes

- The analysis mode is a seeded demo, not a live detector yet.
- The hook mode is a standalone Win32 proof of concept for local testing.
- The Python dashboard and KMDF driver stub are intentionally outside the primary build so the repo has one clear executable path.
