"""Base tool class with memory integration"""

from typing import Any, Dict, Optional
from .memory import memory_manager, MemoryType
from .config.tool_config import ToolConfig
from .validation import SchemaValidator
from .monitoring import tool_monitor
import asyncio
from abc import ABC, abstractmethod

class ToolError(Exception):
    """Base class for tool errors"""
    pass

class ValidationError(ToolError):
    """Error for validation failures"""
    pass

class MemoryError(ToolError):
    """Error for memory operations"""
    pass

class BaseTool(ABC):
    """Base class for tools with memory capabilities"""
    
    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.memory = memory_manager
        self.config = ToolConfig(tool_id)
        self.validator = SchemaValidator()
        
    async def __call__(self, *args, **kwargs):
        """Make tools callable with monitoring"""
        return await tool_monitor.monitor_execution(
            self.tool_id,
            self.execute,
            *args,
            **kwargs
        )
        
    async def store_result(self, result: Any):
        """Store tool execution result with validation"""
        validation_result = self.validator.validate_data(
            result,
            self.config.config["validation"]["output_schema"]
        )
        
        if not validation_result.is_valid:
            raise ValidationError(
                f"Invalid output format for {self.tool_id}: {validation_result.errors}"
            )
            
        await self.memory.store_tool_result(self.tool_id, result)
        
    async def get_context(self) -> Dict[str, Any]:
        """Get tool context from memory with error handling"""
        try:
            return await self.memory.get_context(self.tool_id)
        except Exception as e:
            raise MemoryError(f"Failed to get context: {str(e)}")
            
    def _validate_input(self, input_data: Any) -> bool:
        """Validate input data against schema"""
        validation_result = self.validator.validate_data(
            input_data,
            self.config.config["validation"]["input_schema"]
        )
        return validation_result.is_valid
        
    def _validate_output(self, output_data: Any) -> bool:
        """Validate output data against schema"""
        schema = self.config.config["validation"]["output_schema"]
        # Implement validation logic
        return True
        
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute tool functionality"""
        pass 