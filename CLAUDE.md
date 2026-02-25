# personal-mcp-starter

A local MCP server template built with FastMCP. All tools run over STDIO — no network exposure.

## Project layout

| File | Purpose |
|------|---------|
| `server.py` | All 6 MCP tools live here |
| `pyproject.toml` | Dependencies (`fastmcp>=2.0`) |
| `config/` | Example client configs |

## Adding a tool

1. Define a function in `server.py` and decorate it with `@mcp.tool`.
2. Add a clear docstring — FastMCP uses it as the tool description exposed to the model.
3. For any file or path operation, validate with `_safe_path()` before touching the filesystem.

## Running locally

```bash
uv run python server.py
# or
python server.py
```

## Security rules

- All file access is restricted to `~` via `_safe_path()`.
- `read_file` enforces a 10 KB cap.
- `search_files` and `list_files` cap results at 50 entries.
- `write_note` writes only to `~/notes/mcp-notes.txt`.
- No shell commands, no network calls, no root operations.
