
import os
import json
from typing import List

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("file-server")

# Base directory
BASE_DIR = os.path.normpath("D:\\Git\\Nexee")

def _resolve_path(user_path: str) -> str:
    """Resolve and validate a user-supplied path relative to BASE_DIR."""
    target = os.path.normpath(os.path.join(BASE_DIR, user_path))
    if not target.startswith(BASE_DIR):
        raise ValueError(f"Access denied: '{user_path}' resolves outside of base directory.")
    return target

@mcp.tool()
async def list_files(path: str = "") -> str:
    try:
        target_dir = _resolve_path(path)
        entries = []
        for name in os.listdir(target_dir):
            full = os.path.join(target_dir, name)
            entries.append({
                "name": name,
                "type": "Directory" if os.path.isdir(full) else "File",
                "size": os.path.getsize(full) if os.path.isfile(full) else "-"
            })
        return json.dumps(entries, indent=2)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
async def read_file(file_path: str) -> str:
    try:
        file = _resolve_path(file_path)
        if not os.path.isfile(file):
            return f"Error: Not a file or doesn't exist: {file_path}"
        with open(file, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

@mcp.tool()
async def write_file(file_path: str, content: str) -> str:
    try:
        file = _resolve_path(file_path)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"

@mcp.tool()
async def delete_file(file_path: str) -> str:
    try:
        file = _resolve_path(file_path)
        if not os.path.exists(file):
            return f"Error: Path doesn't exist: {file_path}"
        if os.path.isdir(file):
            os.rmdir(file)
            return f"Deleted directory: {file_path}"
        else:
            os.remove(file)
            return f"Deleted file: {file_path}"
    except Exception as e:
        return f"Error deleting '{file_path}': {str(e)}"

@mcp.tool()
async def search_files(keyword: str, path: str = "") -> str:
    try:
        target_dir = _resolve_path(path)
        matches = []
        for root, _, files in os.walk(target_dir):
            for name in files:
                if keyword.lower() in name.lower():
                    rel = os.path.relpath(os.path.join(root, name), BASE_DIR)
                    matches.append(rel)
        return json.dumps(matches, indent=2)
    except Exception as e:
        return f"Error searching for '{keyword}': {str(e)}"

@mcp.tool()
async def allowed_directories() -> List[str]:
    return [BASE_DIR]

if __name__ == "__main__":
    mcp.run(transport="stdio")

