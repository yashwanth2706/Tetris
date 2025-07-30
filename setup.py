import os
import platform
import subprocess
import zipfile
import urllib.request
from pathlib import Path
import sys

LOG_FILE = "compileandrun.log"
RAYLIB_REPO_ZIP = "https://github.com/raysan5/raylib/archive/refs/heads/master.zip"

def log(message):
    with open(LOG_FILE, "a") as logf:
        logf.write(message + "\n")
    print(message)

def clear_log():
    with open(LOG_FILE, "w") as logf:
        logf.write("")

def is_raylib_present(path):
    return (path / "src" / "raylib.h").exists()

def scan_home_for_raylib(precompiled):
    system = platform.system()

    search_dirs = []

    if system == "Windows":
        if precompiled:
            log("User input [Pre-Compiled for Windows] running compiled file")
            subprocess.run(["TetrisGame.exe"])
            exit()
        search_dirs = [Path("C:/"), Path("D:/"), Path("E:/"), Path("F:/"), Path.home()]
    elif system == "Linux":
        if precompiled:
            log("User input [Pre-Compiled for Linux] running compiled file")
            subprocess.run(["./TetrisGame"])
            exit()
        search_dirs = [Path.home(), Path("/usr/local"), Path("/opt")]
    elif system == "Darwin":
        if precompiled:
            log("User input [Pre-Compiled for MacOS] Option Not Support for MacOS")
            exit()
        search_dirs = [Path.home(), Path("/usr/local"), Path("/opt")]
    else:
        log(f"Unknown OS: {system}. Scanning only home directory.")
        search_dirs = [Path.home()]
    log("Scanning for raylib/src/raylib.h ...")

    for dir in search_dirs:
        if not dir.exists():
            continue
        log(f"Scanning {dir} for raylib/src/raylib.h ...")
        for path in dir.rglob("raylib.h"):
            candidate = path.parent.parent
            if is_raylib_present(candidate):
                log(f"Found raylib at {candidate.resolve()}")
                return candidate.resolve()

    log("raylib not found in scanned directories.")
    return None

def download_and_extract_raylib(dest_dir):
    zip_path = dest_dir / "raylib.zip"
    log(f"Downloading raylib from {RAYLIB_REPO_ZIP}...")
    urllib.request.urlretrieve(RAYLIB_REPO_ZIP, zip_path)
    log("Download complete. Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
    extracted = next(dest_dir.glob("raylib-*/"))
    log(f"raylib extracted to {extracted}")
    return extracted.resolve()

def build_raylib_linux(raylib_path):
    # No cmake, plain make if available
    src_dir = raylib_path / "src"
    os.chdir(src_dir)
    try:
        subprocess.run(["make"], check=True)
        log("raylib compiled using plain `make` in src directory.")
        subprocess.run(["sudo", "make", "install"], check=True)
        log("raylib built on Linux.")
    except subprocess.CalledProcessError as e:
        log(f"Error building raylib on Linux: {e}")
        sys.exit(1)

def compile_game_linux(raylib_path):
    source_dir = Path(__file__).parent.resolve()
    source_files = ["main.cpp", "game.cpp", "grid.cpp", "position.cpp", "colors.cpp", "block.cpp", "blocks.cpp"]
    compile_cmd = ["g++"] + [str(source_dir / f) for f in source_files] + [
        "-o", "TetrisGame", "-I" + str(raylib_path / "src"), "-L" + str(raylib_path / "src"),
        "-lraylib", "-lGL", "-lm", "-lpthread", "-ldl", "-lrt", "-lX11"
    ]
    try:
        subprocess.run(compile_cmd, check=True)
        log("TetrisGame compiled successfully.")
        subprocess.run(["./TetrisGame"])
        log("Game executed successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Compilation or execution failed: {e}")

def compile_game_windows(raylib_path):
    compiler_path = next(raylib_path.glob("**/w64devkit/bin"), None)
    if not compiler_path:
        # Try searching common locations
        search_dirs = [Path("C:/"), Path("C:/Downloads")]
        for dir in search_dirs:
            found = next(dir.rglob("w64devkit/bin"), None)
            if found:
                compiler_path = found
                break

    if not compiler_path:
        user_search = input("w64devkit not found. Search other partitions (D:, E:, F:)? (y|n): ").strip().lower()
        if user_search == 'y':
            for part in ["D:/", "E:/", "F:/"]:
                part_path = Path(part)
                if part_path.exists():
                    found = next(part_path.rglob("w64devkit/bin"), None)
                    if found:
                        compiler_path = found
                        break

    if not compiler_path:
        user_download = input("w64devkit not found. Download? (y/n): ").strip().lower()
        if user_download == 'y':
            w64_url = "https://github.com/skeeto/w64devkit/releases/latest/download/w64devkit.zip"
            dest_dir = Path.home() / "w64devkit"
            zip_path = dest_dir / "w64devkit.zip"
            dest_dir.mkdir(parents=True, exist_ok=True)
            log(f"Downloading w64devkit from {w64_url}...")
            urllib.request.urlretrieve(w64_url, zip_path)
            log("Download complete. Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
            compiler_path = next(dest_dir.glob("**/w64devkit/bin"), None)
            log(f"w64devkit extracted to {compiler_path}")

    if not compiler_path:
        log("Compiler path not found in raylib or system. Exiting.")
        return

    os.environ["PATH"] = str(compiler_path) + os.pathsep + os.environ["PATH"]
    os.environ["CC"] = "g++"
    os.environ["CFLAGS"] = f"-Wall -I{raylib_path / 'src'} -DPLATFORM_DESKTOP"
    os.environ["LDFLAGS"] = "-lraylib -lopengl32 -lgdi32 -lwinmm"

    source_files = ["main.cpp", "grid.cpp", "colors.cpp", "position.cpp", "blocks.cpp", "block.cpp", "game.cpp"]
    output_name = "TetrisGame.exe"
    compile_cmd = ["g++"] + source_files + ["-o", output_name] + os.environ["CFLAGS"].split() + os.environ["LDFLAGS"].split()

    try:
        subprocess.run(compile_cmd, check=True)
        log(f"{output_name} compiled successfully.")
        subprocess.run([output_name])
        log("Game executed successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Compilation or execution failed: {e}")

def main():
    clear_log()
    log("==== RAYLIB BUILD AUTOMATION SCRIPT START ====")

    system = platform.system()
    raylib_path = None

    input_path = input("Select an option:\n 1: Auto scan for Raylib?\n 2: Enter full raylib path:\n[WINDOWS] Example: C:/raylib/src/raylib.h\n[LINUX] Example: home/user/raylib/src/raylib.h\n 3: Select if precompiled\n")
    if input_path == "1":
        scan_home_for_raylib(False)
    elif input_path == "2":
        input_path = input()
        raylib_path = Path(input_path)
        if not is_raylib_present(raylib_path):
            log("Checking for raylib")
            raylib_path = None
        if not raylib_path:
            raylib_path = scan_home_for_raylib(False)
        if not raylib_path:
            log("raylib not found. Downloading...")
            raylib_path = download_and_extract_raylib(Path.cwd())
    elif input_path == "3":
        scan_home_for_raylib(True)
    else:
        log("Input Invalid\n")
        
    if not input_path == "3":

        log(f"Using raylib at {raylib_path}")

        if system == "Linux":
            build_raylib_linux(raylib_path)
            compile_game_linux(raylib_path)
        elif system == "Windows":
            compile_game_windows(raylib_path)
        else:
            log("Unsupported operating system.")
            
    def exit():
        exit(0)

    log("==== SCRIPT END ====")

if __name__ == "__main__":
    main()
