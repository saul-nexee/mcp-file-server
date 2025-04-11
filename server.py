import os
from pathlib import Path
import json
from typing import Dict, Any, List, Optional

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("file-server")

# Set the base directory where we'll read and write files
BASE_DIR = "/data"  # This will be mapped to your local directory in Docker

@mcp.tool()
async def list_files(path: str = "") -> str:
    """List all files in the specified directory.
    
    Args:
        path: Optional subdirectory path relative to the base directory
    """
    target_dir = os.path.normpath(os.path.join(BASE_DIR, path))
    
    # Security check to prevent directory traversal
    if not target_dir.startswith(BASE_DIR):
        return f"Error: Cannot access directories outside of the base directory."
    
    try:
        files = os.listdir(target_dir)
        file_info = []
        
        for file in files:
            full_path = os.path.join(target_dir, file)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else "-"
            file_type = "Directory" if is_dir else "File"
            
            file_info.append({
                "name": file,
                "type": file_type,
                "size": size
            })
        
        return json.dumps(file_info, indent=2)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
async def read_file(file_path: str) -> str:
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file relative to the base directory
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))
    
    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return f"Error: Cannot access files outside of the base directory."
    
    try:
        if not os.path.isfile(target_file):
            return f"Error: File does not exist or is not a file: {file_path}"
        
        with open(target_file, 'r') as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def write_file(file_path: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        file_path: Path to the file relative to the base directory
        content: Content to write to the file
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))
    
    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return f"Error: Cannot access files outside of the base directory."
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        with open(target_file, 'w') as f:
            f.write(content)
        
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
async def delete_file(file_path: str) -> str:
    """Delete a file.
    
    Args:
        file_path: Path to the file relative to the base directory
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))
    
    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return f"Error: Cannot access files outside of the base directory."
    
    try:
        if not os.path.exists(target_file):
            return f"Error: File does not exist: {file_path}"
        
        if os.path.isdir(target_file):
            os.rmdir(target_file)
            return f"Successfully deleted directory: {file_path}"
        else:
            os.remove(target_file)
            return f"Successfully deleted file: {file_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server with stdio transport
    mcp.run(transport='stdio')