"""Memory migration utilities"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .manager import memory_manager

class MemoryMigrator:
    """Handles memory migrations and upgrades"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("memory_migrator")
        
    async def migrate_memory(self, 
                           source_version: str, 
                           target_version: str) -> bool:
        """Migrate memory from one version to another"""
        try:
            migration_path = self._get_migration_path(
                source_version, 
                target_version
            )
            
            for step in migration_path:
                await self._execute_migration_step(step)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            return False
            
    async def _execute_migration_step(self, step: Dict) -> None:
        """Execute a single migration step"""
        self.logger.info(f"Executing migration step: {step['name']}")
        
        # Get affected memories
        memories = await memory_manager.query(step["query"])
        
        for memory in memories:
            try:
                # Transform memory
                transformed = self._transform_memory(memory, step["transforms"])
                
                # Validate transformed memory
                if self._validate_transformed_memory(transformed, step["validation"]):
                    # Update memory
                    await memory_manager.update(memory["id"], transformed)
                else:
                    self.logger.warning(
                        f"Validation failed for memory {memory['id']}"
                    )
                    
            except Exception as e:
                self.logger.error(
                    f"Failed to migrate memory {memory['id']}: {str(e)}"
                )
                
    def _transform_memory(self, memory: Dict, transforms: List[Dict]) -> Dict:
        """Apply transformations to memory"""
        result = memory.copy()
        
        for transform in transforms:
            if transform["type"] == "rename_field":
                result[transform["new_name"]] = result.pop(transform["old_name"])
            elif transform["type"] == "add_field":
                result[transform["name"]] = transform["value"]
            elif transform["type"] == "remove_field":
                result.pop(transform["name"], None)
            elif transform["type"] == "modify_field":
                result[transform["name"]] = transform["modifier"](
                    result[transform["name"]]
                )
                
        return result 