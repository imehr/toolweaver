"""Memory management system"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
from .compression import MemoryCompressor
from ..monitoring import tool_monitor

class MemoryManager:
    """Manages tool memory operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.compressor = MemoryCompressor(config.get("compression", {}))
        self._initialize_storage()
        
    def _initialize_storage(self):
        """Initialize memory storage"""
        self.working_memory = {}
        self.long_term_memory = {}
        self.context_memory = {}
        
    async def store(self, 
                   memory_type: str,
                   key: str,
                   data: Any,
                   metadata: Optional[Dict] = None) -> bool:
        """Store data in memory"""
        try:
            compressed = self.compressor.compress(data)
            
            memory_entry = {
                "data": compressed,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "access_count": 0
            }
            
            if memory_type == "working":
                self.working_memory[key] = memory_entry
            elif memory_type == "long_term":
                self.long_term_memory[key] = memory_entry
            elif memory_type == "context":
                self.context_memory[key] = memory_entry
                
            await tool_monitor.log_memory_operation(
                "store",
                memory_type,
                key,
                len(compressed["data"])
            )
            
            return True
            
        except Exception as e:
            await tool_monitor.log_error(
                "memory_store",
                str(e),
                {"memory_type": memory_type, "key": key}
            )
            return False
            
    async def retrieve(self,
                      memory_type: str,
                      key: str) -> Optional[Any]:
        """Retrieve data from memory"""
        try:
            if memory_type == "working":
                memory = self.working_memory.get(key)
            elif memory_type == "long_term":
                memory = self.long_term_memory.get(key)
            elif memory_type == "context":
                memory = self.context_memory.get(key)
            else:
                return None
                
            if memory:
                memory["access_count"] += 1
                data = self.compressor.decompress(memory["data"])
                
                await tool_monitor.log_memory_operation(
                    "retrieve",
                    memory_type,
                    key,
                    len(memory["data"]["data"])
                )
                
                return data
                
            return None
            
        except Exception as e:
            await tool_monitor.log_error(
                "memory_retrieve",
                str(e),
                {"memory_type": memory_type, "key": key}
            )
            return None 