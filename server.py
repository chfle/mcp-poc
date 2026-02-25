import os
import platform
import datetime
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("personal-mcp-starter")

HOME = Path.home()
MAX_FILE_SIZE = 10 * 1024  # 10 KB


def _safe_path(rel: str = "") -> Path:
    resolved = (HOME / rel).resolve() if rel else HOME.resolve()
    if not resolved.is_relative_to(HOME):
        raise ValueError("Path must be inside your home directory.")
    return resolved


@mcp.tool
def greet(name: str = "World") -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}! Your personal MCP server is up and running."


@mcp.tool
def list_files(subdir: str = "") -> list[str]:
    """List non-hidden files in your home directory or a subdirectory of it."""
    path = _safe_path(subdir)
    if not path.is_dir():
        return [f"Not a directory: {path}"]
    return [f.name for f in sorted(path.iterdir()) if not f.name.startswith(".")][:50]


@mcp.tool
def read_file(filepath: str) -> str:
    """Read a text file located inside your home directory (max 10 KB)."""
    path = _safe_path(filepath)
    if not path.is_file():
        return f"Not a file: {path}"
    if path.stat().st_size > MAX_FILE_SIZE:
        return f"File too large (max {MAX_FILE_SIZE // 1024} KB)."
    return path.read_text(errors="replace")


@mcp.tool
def get_system_info() -> dict:
    """Return basic, non-sensitive system information."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "hostname": platform.node(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "home": str(HOME),
    }


@mcp.tool
def search_files(pattern: str, subdir: str = "") -> list[str]:
    """Search for files matching a glob pattern inside your home directory.

    Example patterns: '*.py', '*.md', 'notes*'
    Results are capped at 50 and hidden directories are skipped.
    """
    path = _safe_path(subdir)
    results = [
        str(p.relative_to(HOME))
        for p in path.rglob(pattern)
        if p.is_file() and not any(part.startswith(".") for part in p.parts)
    ]
    return results[:50]


@mcp.tool
def write_note(note: str) -> str:
    """Append a timestamped note to ~/notes/mcp-notes.txt."""
    notes_file = HOME / "notes" / "mcp-notes.txt"
    notes_file.parent.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    with notes_file.open("a") as f:
        f.write(f"[{timestamp}] {note}\n")
    return f"Note saved to {notes_file}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
