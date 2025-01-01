"""
ToolWeaver modules package.
This package contains all the tool modules created by the framework.
"""

from typing import Dict, List, Optional
import os
import json
from pathlib import Path

__version__ = "0.1.0"

def get_available_tools() -> List[str]:
    """Get list of available tools."""
    tools_dir = Path(__file__).parent
    return [d.name for d in tools_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]

def get_tool_info(tool_name: str) -> Optional[Dict]:
    """Get information about a specific tool."""
    tool_dir = Path(__file__).parent / tool_name
    config_file = tool_dir / 'config.json'
    
    if not config_file.exists():
        return None
        
    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception:
        return None 