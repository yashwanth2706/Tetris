import os
import sys
import subprocess
from pathlib import Path
import platform

print("\nAuto-detecting raylib installation...")

given = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\raylib")
given = given.resolve()

def find_raylib_root(start: Path) -> Path | None:
    p = start
    while p != p.parent:
        raylib_h = p / "raylib" / "src" / "raylib.h"
        if raylib_h.exists():
            return p
        p = p.parent
    return None

# Locate raylib root automatically
raylib_root = None

if given.is_file() and given.name.lower() == "raylib.h":
    raylib_root = find_raylib_root(given.parent.parent)
else:
    raylib_root = find_raylib_root(given)

if not raylib_root:
    print("\nERROR: Could not find raylib.")
    print("Expected structure: <root>/raylib/src/raylib.h\n")
    sys.exit(1)

raylib_src = raylib_root / "raylib" / "src"

# Detect OS
system = platform.system().lower()

project = Path.cwd()
output = project.name
sources = sorted(project.glob("*.cpp"))
sources = [str(s) for s in sources]

if not sources:
    print("ERROR: No .cpp files found.")
    sys.exit(1)

external = project / "external"

print(f"\n[OK] raylib root: {raylib_root}")
print(f"[OK] include/lib path: {raylib_src}")
print(f"[OK] platform detected: {system}")

# ---------------------------
# WINDOWS BUILD
# ---------------------------
if "windows" in system:
    compiler_bin = raylib_root / "w64devkit" / "bin"
    gpp = compiler_bin / "g++.exe"

    if not gpp.exists():
        print("ERROR: g++ not found. Ensure you downloaded raylib Windows pack.")
        sys.exit(1)

    output += ".exe"

    cflags = [
        "-Wall", "-std=c++17", "-DPLATFORM_DESKTOP",
        f"-I{raylib_src}"
    ]
    if external.exists():
        cflags.append(f"-I{external}")

    ldflags = [
        f"-L{raylib_src}",
        "-lraylib",
        "-lopengl32", "-lgdi32", "-lwinmm"
    ]

    cmd = [str(gpp), "-o", output] + sources + cflags + ldflags

    env = os.environ.copy()
    env["PATH"] = str(compiler_bin) + os.pathsep + env["PATH"]

# ---------------------------
# LINUX BUILD
# ---------------------------
else:
    # Try pkg-config first (preferred)
    try:
        subprocess.check_call(["pkg-config", "--exists", "raylib"])
        use_pkg = True
    except:
        use_pkg = False

    if use_pkg:
        print("[OK] Using pkg-config for raylib")
        cmd = ["g++", "-o", output] + sources + [
            "-Wall", "-std=c++17", "-DPLATFORM_DESKTOP"
        ]
        if external.exists():
            cmd.append(f"-I{external}")
        cmd += subprocess.check_output(["pkg-config", "--cflags", "--libs", "raylib"]).decode().split()
        env = os.environ.copy()
    else:
        print("[!] pkg-config not found or no raylib package. Linking manually.")
        # Expect: libraylib.a exists in raylib_src
        lib_file = raylib_src / "libraylib.a"
        if not lib_file.exists():
            print("ERROR: libraylib.a not found. Build raylib first:")
            print("  cd raylib/src && make PLATFORM=PLATFORM_DESKTOP")
            sys.exit(1)

        cflags = [
            "-Wall", "-std=c++17", "-DPLATFORM_DESKTOP",
            f"-I{raylib_src}",
        ]
        if external.exists():
            cflags.append(f"-I{external}")

        ldflags = [
            f"{lib_file}",
            "-lGL", "-lm", "-lpthread", "-ldl", "-lrt", "-lX11"
        ]

        cmd = ["g++", "-o", output] + sources + cflags + ldflags
        env = os.environ.copy()

# ---------------------------
# BUILD
# ---------------------------

print("\nCompiling...\n")
if Path(output).exists():
    Path(output).unlink()

result = subprocess.run(cmd, env=env)

if result.returncode != 0:
    print("\nBuild failed.")
    sys.exit(result.returncode)

print(f"\nBuild succeeded: {output}")
print("\nRunning...\n")
subprocess.run([f"./{output}"] if "linux" in system else [output], shell=("windows" in system))
