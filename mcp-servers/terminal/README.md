# Terminal MCP Server

A minimal Python MCP server that exposes a single tool for running shell commands.

## Tool

- `run_command(command)`

## Resource

- `file:///downloads/f35-brochure.pdf` (application/pdf)

The resource reads from `DOWNLOADS_DIR` when set, otherwise it falls back to the current user's `Downloads` folder.

## Docker

Build the image from the repository root:

```bash
docker build -f mcp-servers/terminal/Dockerfile -t mcp-terminal:dev .
```

Run it with the host Downloads folder mounted read-only into the container:

```bash
docker run -i --rm --init \
	-e DOWNLOADS_DIR=/data/downloads \
	-v "$HOME/Downloads:/data/downloads:ro" \
	mcp-terminal:dev
```

For Claude Desktop, point the server command at `docker` and pass the same arguments.

## Run

```bash
/Users/armaansidhu/Documents/Projects/GenAI/MCP/environ/bin/python /Users/armaansidhu/Documents/Projects/GenAI/MCP/mcp-servers/terminal/server.py
```
