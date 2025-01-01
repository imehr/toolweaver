"""Memory compression utilities"""

from typing import Any, Dict, Optional
import zlib
import json
import pickle
from datetime import datetime
import base64

class MemoryCompressor:
    """Handles compression of memory objects"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.compression_level = config.get("compression_level", 6)
        self.min_size = config.get("min_compression_size", 1024)  # 1KB
        
    def compress(self, data: Any) -> Dict[str, Any]:
        """Compress data for storage"""
        serialized = self._serialize(data)
        
        if len(serialized) < self.min_size:
            return {
                "compressed": False,
                "data": serialized,
                "original_size": len(serialized),
                "timestamp": datetime.now().isoformat()
            }
            
        compressed = zlib.compress(serialized, self.compression_level)
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        return {
            "compressed": True,
            "data": encoded,
            "original_size": len(serialized),
            "compressed_size": len(compressed),
            "timestamp": datetime.now().isoformat()
        }
        
    def decompress(self, compressed_data: Dict) -> Any:
        """Decompress stored data"""
        if not compressed_data.get("compressed", False):
            return self._deserialize(compressed_data["data"])
            
        decoded = base64.b64decode(compressed_data["data"])
        decompressed = zlib.decompress(decoded)
        return self._deserialize(decompressed)
        
    def _serialize(self, data: Any) -> bytes:
        """Serialize data to bytes"""
        try:
            # Try JSON serialization first
            return json.dumps(data).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(data)
            
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from bytes"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data) 