"""Tool configuration management"""

from typing import Dict, Any, Optional
import json
from pathlib import Path
import yaml

class ToolConfig:
    """Manages tool configuration and validation"""
    
    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.config_path = Path(f"tools/config/tools/{tool_id}.yaml")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load tool configuration"""
        if not self.config_path.exists():
            return self._create_default_config()
            
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default tool configuration"""
        config = {
            "tool_id": self.tool_id,
            "version": "1.0.0",
            "memory": {
                "storage_rules": {
                    "working_memory": True,
                    "long_term": False
                },
                "retention": {
                    "working_memory": "24h",
                    "long_term": "permanent"
                }
            },
            "validation": {
                "input_schema": {},
                "output_schema": {},
                "confidence_threshold": 0.7
            }
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f)
            
        return config 