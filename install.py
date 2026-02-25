#!/usr/bin/env python3
"""Set up personal-mcp-starter and register it with the Claude Code CLI."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
SERVER_PATH = SCRIPT_DIR / "server.py"
VENV_DIR = SCRIPT_DIR / ".venv"
MCP_NAME = "personal-mcp"
MIN_VERSION = (3, 11)

OS = platform.system()  # "Linux", "Darwin", "Windows"


# ── helpers ──────────────────────────────────────────────────────────────────

def run(cmd, **kwargs):
    return subprocess.run(cmd, **kwargs)


def banner(text):
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print(f"{'─' * 50}")


def ask(prompt, default="n"):
    suffix = " [y/N] " if default == "n" else " [Y/n] "
    answer = input(prompt + suffix).strip().lower()
    if not answer:
        return default == "y"
    return answer == "y"


# ── python discovery ─────────────────────────────────────────────────────────

def probe_version(executable):
    """Return (major, minor) for the given executable, or None."""
    try:
        result = run(
            [executable, "-c", "import sys; v=sys.version_info; print(v.major,v.minor)"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            major, minor = map(int, result.stdout.strip().split())
            return (major, minor)
    except Exception:
        pass
    return None


def find_pythons():
    """Return a list of (path, version_tuple) for all Python 3.11+ on PATH."""
    seen = set()
    found = []

    # Try the Windows py launcher first
    if OS == "Windows":
        py = shutil.which("py")
        if py:
            for minor in range(13, 10, -1):
                tag = f"-3.{minor}"
                ver = probe_version_with_args(py, [tag])
                if ver and ver >= MIN_VERSION and py not in seen:
                    seen.add(py + tag)
                    found.append((f"py {tag}", ver, [py, tag]))

    candidates = [f"python3.{m}" for m in range(13, 10, -1)] + ["python3", "python"]
    for name in candidates:
        path = shutil.which(name)
        if not path or path in seen:
            continue
        seen.add(path)
        ver = probe_version(path)
        if ver and ver >= MIN_VERSION:
            found.append((path, ver, [path]))

    return found  # list of (display_path, version_tuple, argv_prefix)


def probe_version_with_args(exe, args):
    try:
        result = run(
            [exe] + args + ["-c", "import sys; v=sys.version_info; print(v.major,v.minor)"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            major, minor = map(int, result.stdout.strip().split())
            return (major, minor)
    except Exception:
        pass
    return None


def select_python(pythons):
    if len(pythons) == 1:
        path, ver, argv = pythons[0]
        print(f"  Found Python {ver[0]}.{ver[1]}  →  {path}")
        return argv
    print("  Multiple compatible Python versions found:\n")
    for i, (path, ver, _) in enumerate(pythons, 1):
        print(f"    [{i}] Python {ver[0]}.{ver[1]}  —  {path}")
    print()
    while True:
        choice = input(f"  Select [1–{len(pythons)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(pythons):
            _, ver, argv = pythons[int(choice) - 1]
            print(f"  Using Python {ver[0]}.{ver[1]}")
            return argv
        print("  Invalid choice, try again.")


# ── virtual environment ──────────────────────────────────────────────────────

def setup_venv(python_argv):
    if VENV_DIR.exists():
        if not ask(f"  Existing .venv found. Recreate it?", default="n"):
            print("  Keeping existing .venv.")
            return
        import shutil as sh
        sh.rmtree(VENV_DIR)
        print("  Removed old .venv.")

    print("  Creating virtual environment...")
    run(python_argv + ["-m", "venv", str(VENV_DIR)], check=True)

    pip = venv_python() + ["-m", "pip", "install", "--quiet", "--upgrade", "pip", "fastmcp"]
    print("  Installing fastmcp...")
    run(pip, check=True)
    print("  Dependencies installed.")


def venv_python():
    if OS == "Windows":
        return [str(VENV_DIR / "Scripts" / "python.exe")]
    return [str(VENV_DIR / "bin" / "python")]


# ── claude mcp registration ──────────────────────────────────────────────────

def check_claude_cli():
    if shutil.which("claude") is None:
        print("\n  ERROR: Claude Code CLI not found.")
        print("  Install it from: https://docs.anthropic.com/claude-code\n")
        sys.exit(1)


def is_registered():
    result = run(["claude", "mcp", "list"], capture_output=True, text=True)
    return MCP_NAME in result.stdout


def register():
    python_bin = venv_python()[0]
    if is_registered():
        print(f"\n  '{MCP_NAME}' is already registered with Claude Code.")
        if not ask("  Update it with the current settings?", default="y"):
            print("  Skipped.")
            return
        run(["claude", "mcp", "remove", MCP_NAME], capture_output=True)

    print(f"  Registering '{MCP_NAME}'...")
    run(
        ["claude", "mcp", "add", MCP_NAME, python_bin, str(SERVER_PATH)],
        check=True,
    )
    print(f"  Registered: {MCP_NAME}")
    print(f"    python  → {python_bin}")
    print(f"    server  → {SERVER_PATH}")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    banner(f"personal-mcp-starter  /  {OS}")

    print("\nSearching for Python 3.11+ ...\n")
    pythons = find_pythons()
    if not pythons:
        print("  ERROR: No Python 3.11+ found.")
        print("  Download from: https://python.org/downloads\n")
        sys.exit(1)

    python_argv = select_python(pythons)

    banner("Virtual environment")
    setup_venv(python_argv)

    banner("Claude Code CLI")
    check_claude_cli()
    register()

    banner("All done!")
    print("  Run 'claude mcp list' to verify the registration.")
    print("  Restart Claude Code for changes to take effect.\n")


if __name__ == "__main__":
    main()
