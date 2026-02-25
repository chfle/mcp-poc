# personal-mcp-starter

A minimal, secure, personal MCP server you can run locally and connect to Claude. Clone it, add your own tools, and extend Claude with capabilities that only you can use.

Everything runs over **STDIO** — no port, no network exposure, no server to manage.

---

## What is MCP?

MCP (Model Context Protocol) is a way to give Claude access to tools that run on your own machine. Without MCP, Claude can only work with text you paste into the chat. With MCP, Claude can actually *do things* — read files, search your home directory, check your system info, save notes — all by calling small Python functions you define and control.

Think of it like giving Claude a set of safe, approved actions it can take on your behalf. You decide what those actions are. Claude decides when to use them based on your conversation.

**How it works in practice:**

```
You: "What Python files do I have in my projects folder?"

Claude: [calls search_files("*.py", "projects") on your machine]
        → "I found 12 Python files in ~/projects: main.py, utils.py, ..."
```

The tool runs locally on your computer. Nothing is sent to a third party. Claude sees the result and uses it to answer you.

---

## Prerequisites

- Python 3.11 or newer — [download here](https://python.org/downloads)
- [Claude Code CLI](https://docs.anthropic.com/claude-code) **or** [Claude Desktop](https://claude.ai/download)
- Git

---

## Quick start

```bash
git clone https://github.com/chfle/mcp-poc.git
cd mcp-poc
python install.py
```

The installer will:
1. Find all Python 3.11+ versions on your system — if there are multiple, you pick one
2. Create a `.venv` and install `fastmcp`
3. Check if this MCP server is already registered — if so, ask whether to update it
4. Register the server with `claude mcp add`

Restart Claude Code after the installer finishes and your tools will be available.

> **Prefer to do it manually?** See the [manual setup](#manual-setup) section below.

---

## Using your tools

Once the server is registered and Claude Code is restarted, just talk to Claude naturally. You don't need to mention tool names — Claude figures out when to use them.

**Some example prompts to try:**

| What you type | What Claude does |
|---------------|-----------------|
| `Say hello from my MCP server` | calls `greet` |
| `What files are in my home directory?` | calls `list_files` |
| `Show me what's in ~/projects` | calls `list_files("projects")` |
| `Read the file notes/todo.txt` | calls `read_file("notes/todo.txt")` |
| `What OS am I running?` | calls `get_system_info` |
| `Find all Python files under my projects folder` | calls `search_files("*.py", "projects")` |
| `Save a note: fix the login bug tomorrow` | calls `write_note(...)` |
| `What notes have I saved?` | calls `read_file("notes/mcp-notes.txt")` |

**In Claude Desktop**, look for the hammer icon (🔨) in the chat input bar — that confirms your tools are connected. Click it to see the full list.

**In Claude Code**, type `claude mcp list` in your terminal to verify the server is registered, then start a new session.

### Copy-paste prompts

Use these exactly as written — just paste into Claude:

| Tool | Paste this |
|------|-----------|
| `greet` | `Use the greet tool and say hello to me` |
| `list_files` | `Use list_files to show what's in my home directory` |
| `list_files` (subdir) | `Use list_files to show what's inside my Documents folder` |
| `read_file` | `Use read_file to read notes/mcp-notes.txt` |
| `get_system_info` | `Use get_system_info and tell me about my machine` |
| `search_files` | `Use search_files to find all .py files in my home directory` |
| `write_note` | `Use write_note to save this: "my MCP server is working"` |

---

## Available tools

| Tool | What it does |
|------|-------------|
| `greet` | Returns a friendly greeting — useful for testing the connection |
| `list_files` | Lists non-hidden files in your home directory or a subdirectory |
| `read_file` | Reads a text file inside your home directory (max 10 KB) |
| `get_system_info` | Returns OS, hostname, Python version, CPU count |
| `search_files` | Searches for files matching a glob pattern (e.g. `*.py`, `*.md`) |
| `write_note` | Appends a timestamped note to `~/notes/mcp-notes.txt` |

All file operations are restricted to your home directory. No tool makes network requests or runs shell commands.

---

## Manual setup

### Claude Code CLI

```bash
# From inside the mcp-poc directory:
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install fastmcp

claude mcp add personal-mcp .venv/bin/python /absolute/path/to/server.py
claude mcp list                  # verify it appears
```

### Claude Desktop

Find your config file:

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Open it (create it if it doesn't exist) and add:

**macOS / Linux**
```json
{
  "mcpServers": {
    "personal-mcp": {
      "command": "/absolute/path/to/mcp-poc/.venv/bin/python",
      "args": ["/absolute/path/to/mcp-poc/server.py"]
    }
  }
}
```

**Windows**
```json
{
  "mcpServers": {
    "personal-mcp": {
      "command": "C:\\Users\\YOU\\mcp-poc\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YOU\\mcp-poc\\server.py"]
    }
  }
}
```

Restart Claude Desktop. The hammer icon in the chat bar confirms the connection.

---

## Adding your own tool

See [CONTRIBUTING.md](CONTRIBUTING.md) for a full guide. The short version — add a decorated function to `server.py`:

```python
@mcp.tool
def my_tool(param: str) -> str:
    """One clear sentence describing what this tool does."""
    return f"Result: {param}"
```

Restart your client and the tool is live.

---

## Project structure

```
.
├── server.py                        # All MCP tools
├── install.py                       # Installer — run this first
├── pyproject.toml                   # Dependencies
├── CONTRIBUTING.md                  # How to add your own tools
├── CLAUDE.md                        # Context file for Claude Code
├── config/
│   └── claude_desktop.example.json  # Config reference for Claude Desktop
└── .python-version                  # Pinned Python version
```

---

## Troubleshooting

**The hammer icon doesn't appear / Claude doesn't see my tools**
- Make sure you used the absolute path to the `.venv` Python, not the system Python.
- Run `python server.py` manually to check for import errors.
- Restart the client fully after any config change — a regular reload is not enough.

**`ModuleNotFoundError: fastmcp`**
- The config is pointing at the system Python instead of the `.venv` Python. Run `install.py` again to fix it.

**`claude: command not found`**
- The Claude Code CLI is not installed or not on your PATH. Follow the [installation guide](https://docs.anthropic.com/claude-code).

**Permission denied on macOS/Linux**
- `chmod 644 server.py`

---

## License

MIT — see [LICENSE](LICENSE).
