import os
from fastmcp import FastMCP

mcp = FastMCP("Lehnert-PoC")  # dein Name im Claude


@mcp.tool
def secure_hello(name: str = "Lehnert") -> str:
    """Sichere Begrüßung – nur dein privater Server"""
    return f"Hallo {name}! 👋\nDas ist dein persönlicher, sicherer MCP-Server auf Debian.\nNiemand sonst kann ihn benutzen – er läuft nur lokal über Claude Desktop."


@mcp.tool
def safe_list_home_files(subdir: str = "") -> list[str]:
    """Sicheres Auflisten von Dateien in deinem Home-Ordner (z.B. projects)"""
    home = os.path.expanduser("~")
    path = os.path.join(home, subdir) if subdir else home

    # Sicherheits-Check: nur innerhalb von ~
    if not os.path.abspath(path).startswith(home):
        return ["FEHLER: Nur Dateien in deinem Home-Verzeichnis erlaubt!"]

    try:
        files = [f for f in os.listdir(path) if not f.startswith(".")][:20]
        return files
    except Exception as e:
        return [f"Fehler: {str(e)}"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
