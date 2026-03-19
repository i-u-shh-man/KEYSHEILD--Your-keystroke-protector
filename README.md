# KeyShield: Conceptual Framework for Keylogger Detection

### KeyShield is a research-based project focused on the theoretical design and architectural planning of a behavioral-based keylogging detection tool. This project explores the transition from traditional signature-based security to a more robust, behavioral monitoring model.

# 📖 Overview

In the current cybersecurity landscape, custom-written keyloggers can easily bypass standard antivirus software. KeyShield aims to provide a conceptual framework for a tool that monitors system-level interactions to identify unauthorized keyboard hooking and polling patterns.

# 🏗️ Proposed Architecture

The project is designed around a Conceptual Dual-Layer Model:

Kernel Layer (Proposed): A design for a Windows Driver (KMDF) intended to observe I/O Request Packets (IRPs) at the lowest possible level, ensuring system-wide visibility.

User Layer (Planned): A monitoring service that analyzes process activities for specific Windows API calls, such as SetWindowsHookEx and GetAsyncKeyState, which are common markers of keylogging behavior.

# 🧪 Methodology & Research Focus

The project focuses on the following theoretical pillars:

Hooking Logic Analysis: Researching how malicious scripts insert themselves into the Windows message chain.

Behavioral Pattern Mapping: Defining the difference between legitimate software (e.g., gaming overlays) and malicious loggers based on their API calling frequency.

Mitigation Strategy: Designing the logic required to "unhook" malicious functions and terminate suspicious process threads.

# 🛠️ Planned Tech Stack

Research IDE: Visual Studio / Cursor

Core Concepts: Windows Driver Kit (WDK), Win32 API Internals

Documentation: Technical Specifications and Architectural Diagrams

# 📅 Current Progress & Roadmap

Phase 1 (Completed): Literature review and problem background analysis.

Phase 2 (Current): Architectural design and API interaction research.

Phase 3 (Next): Development of a basic proof-of-concept for user-mode hook detection.

Phase 4: Performance optimization and final report documentation.

# 📝 Project Status

This repository serves as the primary documentation for the Minor Project First Review (Feb 25, 2026). The current focus is on the theoretical validation of the proposed detection engine.

## Standalone PoC: Global keyboard hook (console)

This repo also includes a small standalone Windows console program, `keyboard_hook.cpp`, that installs a global low-level keyboard hook (`SetWindowsHookEx` with `WH_KEYBOARD_LL`) and prints virtual-key codes in real time while it runs a standard Windows message loop (`GetMessage` / `DispatchMessage`).

### Quick build (recommended)

From **PowerShell** in the repo root:

```powershell
.\build.ps1
```

Then run the printed `keyboard_hook.exe` path (usually `.\build\keyboard_hook.exe` or `.\build\Release\keyboard_hook.exe`).

### Build (CMake manual)

```powershell
cmake -S . -B .\build
cmake --build .\build --config Release
.\build\Release\keyboard_hook.exe
```

### Build (MSVC Developer Command Prompt, no CMake)

```bat
cl /EHsc /W4 keyboard_hook.cpp user32.lib
```

### Build (MinGW-w64 g++, no CMake)

```bat
g++ -std=c++17 -O2 -Wall -Wextra -pedantic keyboard_hook.cpp -o keyboard_hook.exe -luser32
```

### Run

```bat
keyboard_hook.exe
```
