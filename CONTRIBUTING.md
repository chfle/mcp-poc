# Contributing

## Adding your own tool

Open `server.py` and add a decorated function anywhere before `mcp.run()`:

```python
@mcp.tool
def my_tool(param: str) -> str:
    """One-sentence description — this becomes the tool's description in Claude."""
    return f"Result: {param}"
```

That's it. FastMCP picks it up automatically on next start.

## Guidelines

- **Type-hint every parameter and return value.** FastMCP uses these to generate the JSON schema shown to the model.
- **Write a clear docstring.** The model reads it to decide when and how to call your tool.
- **Validate file paths with `_safe_path()`.** Never pass user input directly to `open()`, `os.listdir()`, or `subprocess`.
- **Never add network calls or shell execution** — the whole point of this server is that it is safe and local.
- **Cap unbounded results.** If your tool returns a list, slice it (e.g. `[:50]`) so the model's context window doesn't get flooded.

## Testing a new tool manually

```bash
# Start the server and hit it with the MCP inspector (optional)
uv run python server.py

# Or just import and call the function directly in a Python REPL
python -c "from server import my_tool; print(my_tool('hello'))"
```
