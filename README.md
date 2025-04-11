# MCP File Server

An MCP server for reading and writing files from a local directory.

## Features

- List files in directories
- Read file contents
- Write content to files
- Delete files and directories

## Usage

This server is designed to be run in Docker, with a volume mount to access your local files.

```bash
docker build -t mcp-file-server .
docker run -v /your/local/path:/data mcp-file-server
```

This MCP server can be connected to Claude for Desktop or any other MCP client to provide file system access.
