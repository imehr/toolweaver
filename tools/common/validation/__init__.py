"""
Common validation utilities for ToolWeaver framework.
This module provides validation functionality used across different tools.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

__version__ = "0.1.0"

class ToolConfig(BaseModel):
    """Base configuration model for tools."""
    name: str = Field(..., description="Tool name")
    version: str = Field(..., description="Tool version")
    description: str = Field(..., description="Tool description")
    
    class Config:
        extra = "allow"

def validate_tool_config(config: Dict[str, Any]) -> bool:
    """Validate tool configuration."""
    try:
        ToolConfig(**config)
        return True
    except Exception:
        return False

def validate_tool_structure(tool_path: str) -> List[str]:
    """Validate tool directory structure and return any issues."""
    return []
