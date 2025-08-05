
import os
import json
import argparse
from typing import List

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("file-server")
BASE_DIR = None  # Will be set in __main__

def _resolve_path(user_path: str) -> str:
    if BASE_DIR is None:
        raise RuntimeError("BASE_DIR is not configured")
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
        return f"Error listing files: {e}"

@mcp.tool()
async def read_file(file_path: str) -> str:
    try:
        file = _resolve_path(file_path)
        if not os.path.isfile(file):
            return f"Error: Not a file or doesn't exist: {file_path}"
        with open(file, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

@mcp.tool()
async def write_file(file_path: str, content: str) -> str:
    try:
        file = _resolve_path(file_path)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file '{file_path}': {e}"

@mcp.tool()
async def delete_file(file_path: str) -> str:
    try:
        file = _resolve_path(file_path)
        if not os.path.exists(file):
            return f"Error: Path doesn't exist: {file_path}"
        if os.path.isdir(file):
            os.rmdir(file)
            return f"Deleted directory: {file_path}"
        os.remove(file)
        return f"Deleted file: {file_path}"
    except Exception as e:
        return f"Error deleting '{file_path}': {e}"

@mcp.tool()
async def search_files(keyword: str, path: str = "") -> str:
    try:
        target_dir = _resolve_path(path)
        matches = []
        for root, _, files in os.walk(target_dir):
            for name in files:
                if keyword.lower() in name.lower():
                    matches.append(os.path.relpath(os.path.join(root, name), BASE_DIR))
        return json.dumps(matches, indent=2)
    except Exception as e:
        return f"Error searching for '{keyword}': {e}"

@mcp.tool()
async def allowed_directories() -> List[str]:
    return [BASE_DIR]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start MCP file server.")
    parser.add_argument("--base-dir", required=True, help="Base directory for file access")
    args = parser.parse_args()

    if not os.path.isdir(args.base_dir):
        raise RuntimeError(f"--base-dir is not a valid directory: {args.base_dir}")

    BASE_DIR = os.path.normpath(args.base_dir)
    mcp.run(transport="stdio")

