"""Monitoring utilities for tools"""

import logging
from typing import Dict, Any
import time
from datetime import datetime
import asyncio
from pathlib import Path

class ToolMonitor:
    """Monitors tool execution and performance"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool_monitor")
        self._setup_logging()
        self.metrics = {}
        
    def _setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler("logs/tool_execution.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    async def monitor_execution(self, tool_id: str, func, *args, **kwargs):
        """Monitor tool execution"""
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self._update_metrics(tool_id, {
                "last_execution": datetime.now(),
                "execution_time": execution_time,
                "status": "success"
            })
            
            self.logger.info(
                f"Tool {tool_id} executed successfully in {execution_time:.2f}s"
            )
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(tool_id, {
                "last_execution": datetime.now(),
                "execution_time": execution_time,
                "status": "error",
                "error": str(e)
            })
            
            self.logger.error(
                f"Tool {tool_id} failed after {execution_time:.2f}s: {str(e)}"
            )
            raise
            
    def _update_metrics(self, tool_id: str, data: Dict[str, Any]):
        """Update tool metrics"""
        if tool_id not in self.metrics:
            self.metrics[tool_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0
            }
            
        metrics = self.metrics[tool_id]
        metrics["total_executions"] += 1
        
        if data["status"] == "success":
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1
            
        # Update average execution time
        n = metrics["total_executions"]
        old_avg = metrics["average_execution_time"]
        new_time = data["execution_time"]
        metrics["average_execution_time"] = (old_avg * (n-1) + new_time) / n
        
        # Store latest execution data
        metrics.update(data)

# Initialize global monitor
tool_monitor = ToolMonitor() 