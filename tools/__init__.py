"""
Tools Framework
==============

This module provides a unified interface to all available tools in the framework.
Tools are organized in modules/ directory, each in its own self-contained package.

Usage:
------
from tools import process_sales_data, get_weather, generate_component

result = process_sales_data('data.xlsx')
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

# Tool registry to store loaded tools
_tools: Dict[str, Any] = {}

def _load_tool_config(tool_dir: Path) -> Dict[str, Any]:
    """Load tool configuration from config.json"""
    config_path = tool_dir / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def _discover_tools() -> None:
    """Discover and load all available tools"""
    modules_dir = Path(__file__).parent / 'modules'
    if not modules_dir.exists():
        return

    for tool_dir in modules_dir.iterdir():
        if not tool_dir.is_dir():
            continue

        config = _load_tool_config(tool_dir)
        if not config:
            continue

        # Import based on language
        language = config.get('language', 'python')
        if language == 'python':
            module_path = f"tools.modules.{tool_dir.name}"
            try:
                module = __import__(module_path, fromlist=['*'])
                for attr in getattr(module, '__all__', []):
                    _tools[attr] = getattr(module, attr)
            except ImportError:
                print(f"Warning: Failed to import {module_path}")
        elif language == 'typescript':
            # TypeScript tools are imported through their Python interface
            module_path = f"tools.modules.{tool_dir.name}.interface"
            try:
                module = __import__(module_path, fromlist=['*'])
                for attr in getattr(module, '__all__', []):
                    _tools[attr] = getattr(module, attr)
            except ImportError:
                print(f"Warning: Failed to import {module_path}")

def get_available_tools() -> List[str]:
    """Return list of available tool names"""
    return list(_tools.keys())

# Load all tools on module import
_discover_tools()

# Export all discovered tools
__all__ = list(_tools.keys())

# Add tools to module namespace
globals().update(_tools) 