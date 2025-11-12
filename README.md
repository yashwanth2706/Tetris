Tetris (raylib)
=================

Install raylib from:
https://www.raylib.com/


This is a Tetris game implemented in C++ using raylib. The repository includes a convenience `setup.py` script that helps find your raylib installation and builds the project on both Windows and Linux.

This README documents how to build and run the game on Windows and Linux using the provided `setup.py` and also shows manual build steps and common troubleshooting tips.

Contents
--------
- Source files: .cpp/.h files in the repository root
- Build helper: `setup.py` (auto-detects raylib and runs g++)
- Shell helpers: `compileTetris.sh`, `dependencies.sh` (Linux helper scripts)

Prerequisites
-------------
- Python 3 (to run `setup.py`)
- A C++17-capable compiler (g++)
- raylib (see below platform sections for details)

Note: `setup.py` prints guidance and detects the platform. It supports two modes:
- Windows: expects a raylib root (default: `C:\raylib`) and a Windows raylib pack containing `w64devkit` and `raylib/src/raylib.h`.
- Linux: prefers `pkg-config` + system raylib; if not found it can attempt to run `dependencies.sh` and `compileTetris.sh` to build raylib automatically (Debian-based distributions).

Windows setup
-------------
What you need

- raylib Windows package installed somewhere (recommended: `C:\raylib`). The package should include:
	- `raylib/src/raylib.h`
	- `w64devkit/bin/g++.exe` (or another bundled MinGW toolchain)
- Python 3

Steps

1. If you haven't already, install a Windows raylib package from https://www.raylib.com/ and extract it to `C:\raylib` (or another drive/folder).
2. Open PowerShell in this project folder (`d:\Tetris`).
3. Run the setup script. You can provide the raylib root folder or a direct path to `raylib.h`:

```powershell
# Use default C:\raylib
python setup.py

# Or provide the raylib root folder
python setup.py C:/raylib

# Or provide the full path to raylib.h
python setup.py C:/raylib/raylib/src/raylib.h
```

What `setup.py` does on Windows

- It looks for `raylib/src/raylib.h` under the given path (or `C:\raylib` by default).
- It looks for `w64devkit/bin/g++.exe` inside the raylib root and uses it to compile all `.cpp` files in the repository to `Tetris.exe` (project folder name + `.exe`).
- If compilation succeeds, it runs the produced executable.

Manual compile (if you prefer)

If you want to compile manually using your own MinGW/toolchain, run a g++ command similar to:

```powershell
g++ -Wall -std=c++17 -DPLATFORM_DESKTOP -I C:/path/to/raylib/src -o Tetris.exe *.cpp -L C:/path/to/raylib/src -lraylib -lopengl32 -lgdi32 -lwinmm
```

Then run the game with:

```powershell
.\Tetris.exe
```

(Recommended): Notepad++ quick-build using `script.txt` (Windows only)
-------------------------------------------------------------
There is a ready-to-use script in this repository: `script.txt`. On Windows you can use Notepad++ together with the NppExec plugin to compile and run the game with a single keypress.

Important editor note
---------------------
Raylib's Windows installer typically ships a customized editor called "Notepad++ for Raylib" (a Notepad++ build preconfigured for raylib). Use that shipped "Notepad++ for Raylib" when following the steps below to avoid missing plugins or environment presets. If you prefer to use a standalone Notepad++ installation instead, make sure NppExec is installed and that you configure the plugin and environment variables (compiler and raylib paths) as described below — otherwise the provided script may not work out of the box.

What the script does (summary):
- Saves the current file, sets up environment variables (paths to raylib and the compiler), runs g++ with the project sources and flags, then executes the built `.exe` if compilation succeeds.

How to use it

1. Open `script.txt` and copy its contents (or open it directly in Notepad++ for Raylib).
2. Open Notepad++ for Raylib.
3. Make sure the NppExec plugin is installed (Plugins → Plugins Admin → search for "NppExec"). If it's not installed, install and restart Notepad++.
4. Open any project source file (for example `main.cpp`) so Notepad++ knows the current directory and filename.
5. Open the NppExec Execute dialog: Plugins → NppExec → Execute... (or press F6 by default).
6. Paste the contents of `script.txt` into the Execute dialog (or use the script file if you prefer). Click "Save" in the dialog and give the script a name (for example: "Build Tetris").
7. Optionally assign the script to a keyboard shortcut (for example F5):
	- Plugins → NppExec → Advanced Options → under "Associated script" add your saved script to the menu, then use `Settings → Shortcut Mapper` → `Plugin commands` to bind it to F5.
8. Run the script by pressing F6 → OK, or press your assigned shortcut (F5) to compile & run.

Notes
- The script in `script.txt` uses Notepad++ / NppExec variables such as `$(CURRENT_DIRECTORY)` and `$(NAME_PART)` and commands like `npp_save`. Running the script using the NppExec Execute dialog (or a saved NppExec script) is required — simply pasting the file into the normal Run (F5) dialog will not work unless you map the script to a plugin command/shortcut.
- The method is Windows-only because it relies on the Windows toolchain and paths used by the raylib Windows package.


Linux setup (Debian-based)
--------------------------
What you need

- Python 3
- g++ (C++17)
- raylib development files (recommended via package manager or building from source)
- pkg-config (optional but preferred)

Automated helper (via `setup.py`)

1. Open a terminal in the project folder.
2. Run `python setup.py`.

Behavior on Linux

- `setup.py` first checks `pkg-config --exists raylib`. If present it uses `pkg-config` to add cflags/libs and compiles the project with `g++`.
- If pkg-config or a library package is not found, `setup.py` looks for `libraylib.a` in common locations. If missing, it prompts to run `dependencies.sh` and `compileTetris.sh` to install dependencies and build raylib automatically (this is intended for Debian-based systems). If you confirm, the script runs those shell scripts.

Manual compile (if you prefer)

If pkg-config is available and raylib is installed, compile with:

```bash
g++ -Wall -std=c++17 -DPLATFORM_DESKTOP -o Tetris *.cpp $(pkg-config --cflags --libs raylib)
```

If using a static libray (e.g., `libraylib.a`):

```bash
g++ -Wall -std=c++17 -DPLATFORM_DESKTOP -I /path/to/raylib/src -o Tetris *.cpp /path/to/libraylib.a -lGL -lm -lpthread -ldl -lrt -lX11
```

Run with:

```bash
./Tetris
```

Troubleshooting
---------------
- "Could not find raylib" / "raylib.h not found":
	- On Windows provide the correct raylib root or full path to `raylib.h` when running `setup.py`.
	- On Linux install raylib via your package manager (example on Debian/Ubuntu: `sudo apt-get install libraylib-dev` if available) or let `setup.py` run `dependencies.sh` then `compileTetris.sh` when prompted.

- g++ not found (Windows):
	- Ensure you downloaded the raylib Windows package that bundles `w64devkit` or install a MinGW-w64 toolchain and add `g++` to PATH.

- Linking errors on Linux (missing X11 or GL):
	- Install development packages: `sudo apt-get install build-essential libx11-dev libgl1-mesa-dev` and other dependencies listed in `dependencies.sh`.

Notes for contributors
----------------------
- The `setup.py` script is intentionally simple: it gathers `.cpp` files from the project root and compiles them together. If you add source files in subfolders, update the script or compile manually.
- The project includes helper scripts `compileTetris.sh` and `dependencies.sh` intended for Linux. Inspect them before running.

Files of interest
-----------------
- `setup.py` — Python build helper (Windows + Linux logic)
- `compileTetris.sh`, `dependencies.sh` — Linux helper scripts referenced by `setup.py`
- `*.cpp`, `*.h` — game source code

Quick start (summary)
---------------------
- Windows (recommended):
	1. Install raylib Windows package (recommended at `C:\raylib`).
	2. In PowerShell run: `python setup.py C:/raylib` or simply `python setup.py`.

- Linux (Debian-based):
	1. Ensure Python 3 and g++ are installed. Install raylib via package manager or run `python setup.py` and allow it to run `dependencies.sh`/`compileTetris.sh` when prompted.
