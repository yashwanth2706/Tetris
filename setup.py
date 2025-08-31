import os
import platform
import subprocess
import zipfile
import urllib.request
from pathlib import Path
import sys
import shutil

LOG_FILE = "compileandrun.log"
RAYLIB_REPO_ZIP = "https://github.com/raysan5/raylib/archive/refs/heads/master.zip"
BUILD_DIR = Path("build") if platform.system() in ["Windows", "Darwin"] else Path("bin")

# ---------------- Logging ----------------
def log(message: str):
    with open(LOG_FILE, "a") as logf:
        logf.write(message + "\n")
    print(message)

def clear_log():
    Path(LOG_FILE).write_text("")

# ---------------- Helpers ----------------
def is_raylib_present(path: Path) -> bool:
    return (path / "src" / "raylib.h").exists()

def run_command(cmd, cwd=None, check=True):
    log(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=check)
    except subprocess.CalledProcessError as e:
        log(f"Error running command: {e}")
        sys.exit(1)

def download_and_extract(url: str, dest_dir: Path, name: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / f"{name}.zip"
    log(f"Downloading {name} from {url}...")
    urllib.request.urlretrieve(url, zip_path)
    log("Download complete. Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
    extracted = next(dest_dir.glob(f"{name}-*/"))
    log(f"{name} extracted to {extracted}")
    return extracted.resolve()

# ---------------- Raylib Search ----------------
def scan_for_raylib(precompiled=False):
    system = platform.system()
    search_dirs = {
        "Windows": [Path("C:/"), Path("D:/"), Path("E:/"), Path("F:/"), Path.home()],
        "Linux": [Path.home(), Path("/usr/local"), Path("/opt")],
        "Darwin": [Path.home(), Path("/usr/local"), Path("/opt")]
    }.get(system, [Path.home()])

    if precompiled:
        if system == "Windows":
            log("Running precompiled Windows binary...")
            run_command([str(BUILD_DIR / "TetrisGame.exe")])
        elif system == "Linux":
            log("Running precompiled Linux binary...")
            run_command([str(BUILD_DIR / "TetrisGame")])
        elif system == "Darwin":
            log("Precompiled option not supported for macOS.")
        sys.exit(0)

    log("Scanning for raylib/src/raylib.h ...")
    for dir in search_dirs:
        if not dir.exists():
            continue
        log(f"Scanning {dir} ...")
        for path in dir.rglob("raylib.h"):
            candidate = path.parent.parent
            if is_raylib_present(candidate):
                log(f"Found raylib at {candidate.resolve()}")
                return candidate.resolve()
    log("raylib not found.")
    return None

# ---------------- Build Functions ----------------
def build_raylib_linux(raylib_path: Path):
    src_dir = raylib_path / "src"
    run_command(["make"], cwd=src_dir)
    log("raylib compiled with `make`.")
    choice = input("Install globally with `sudo make install`? (y/n): ").strip().lower()
    if choice == "y":
        run_command(["sudo", "make", "install"], cwd=src_dir)
        log("raylib installed globally.")

def build_game(raylib_path: Path):
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    source_dir = Path(__file__).parent.resolve()
    source_files = ["main.cpp", "game.cpp", "grid.cpp", "position.cpp", "colors.cpp", "block.cpp", "blocks.cpp"]
    system = platform.system()

    if system == "Linux":
        output = BUILD_DIR / "TetrisGame"
        compile_cmd = [
            "g++", *map(str, [source_dir / f for f in source_files]),
            "-o", str(output),
            f"-I{raylib_path/'src'}", f"-L{raylib_path/'src'}",
            "-lraylib", "-lGL", "-lm", "-lpthread", "-ldl", "-lrt", "-lX11"
        ]
        run_command(compile_cmd)
        run_command([str(output)])

    elif system == "Windows":
        # Try existing compilers first
        compiler = shutil.which("g++")
        if not compiler:
            compiler_path = next(raylib_path.glob("**/w64devkit/bin"), None)
            if compiler_path:
                os.environ["PATH"] = str(compiler_path) + os.pathsep + os.environ["PATH"]
                compiler = shutil.which("g++")
        if not compiler:
            url = "https://github.com/skeeto/w64devkit/releases/latest/download/w64devkit.zip"
            compiler_path = download_and_extract(url, Path.home() / "w64devkit", "w64devkit")
            os.environ["PATH"] = str(compiler_path / "w64devkit/bin") + os.pathsep + os.environ["PATH"]
            compiler = shutil.which("g++")

        output = BUILD_DIR / "TetrisGame.exe"
        compile_cmd = [
            compiler, *map(str, [source_dir / f for f in source_files]),
            "-o", str(output),
            f"-I{raylib_path/'src'}", "-DPLATFORM_DESKTOP",
            "-lraylib", "-lopengl32", "-lgdi32", "-lwinmm"
        ]
        run_command(compile_cmd)
        run_command([str(output)])

    elif system == "Darwin":
        output = BUILD_DIR / "TetrisGame"
        compile_cmd = [
            "clang++", *map(str, [source_dir / f for f in source_files]),
            "-o", str(output),
            f"-I{raylib_path/'src'}", f"-L{raylib_path/'src'}",
            "-lraylib", "-framework", "OpenGL", "-framework", "Cocoa", "-framework", "IOKit"
        ]
        run_command(compile_cmd)
        run_command([str(output)])

    else:
        log(f"Unsupported OS: {system}")
        sys.exit(1)

# ---------------- Main ----------------
def main():
    clear_log()
    log("==== RAYLIB BUILD AUTOMATION SCRIPT START ====")
    system = platform.system()
    raylib_path = None

    choice = input("Select option:\n"
                   "1: Auto scan for Raylib\n"
                   "2: Enter full raylib path\n"
                   "3: Precompiled\n")
    if choice == "1":
        raylib_path = scan_for_raylib(False)
    elif choice == "2":
        input_path = Path(input("Enter path to raylib root (not raylib.h): ").strip())
        if is_raylib_present(input_path):
            raylib_path = input_path
        else:
            log("Invalid path. Scanning home directories...")
            raylib_path = scan_for_raylib(False)
    elif choice == "3":
        scan_for_raylib(True)
    else:
        log("Invalid choice.")
        sys.exit(1)

    if not raylib_path:
        log("raylib not found. Downloading...")
        raylib_path = download_and_extract(RAYLIB_REPO_ZIP, Path.cwd(), "raylib")

    log(f"Using raylib at {raylib_path}")
    if system == "Linux":
        build_raylib_linux(raylib_path)
    build_game(raylib_path)

    log("==== SCRIPT END ====")

if __name__ == "__main__":
    main()
