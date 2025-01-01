"""
ToolWeaver common utilities and shared components
"""

from .memory import MemorySystem, MemoryManager
from .memory.manager import MemoryManager

# Initialize global memory manager
memory_manager = MemoryManager()

__all__ = ['MemorySystem', 'MemoryManager', 'memory_manager']
