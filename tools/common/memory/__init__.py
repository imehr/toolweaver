"""
ToolWeaver Memory System
Provides shared memory capabilities for tools with short-term, working, and long-term memory.
"""

from typing import Any, Dict, List, Optional, Union, Pattern, Callable, Tuple
import json
import os
import time
from pathlib import Path
import asyncio
import shutil
import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from difflib import SequenceMatcher
from .compression import MemoryCompressor
from .migration import MemoryMigration
from concurrent.futures import ThreadPoolExecutor
from functools import partial

@dataclass
class MemorySearchResult:
    """Search result from memory"""
    key: str
    data: Any
    memory_type: str
    timestamp: float
    score: float = 0.0

class MemoryType(Enum):
    """Types of memory for searching"""
    SHORT_TERM = "short_term"
    WORKING = "working"
    LONG_TERM = "long_term"
    ALL = "all"

class MemorySystem:
    """Central memory management system for ToolWeaver"""
    
    def __init__(self, base_path: str = "tools/data/memory"):
        self.base_path = Path(base_path)
        self.stm_path = self.base_path / "short_term"
        self.wm_path = self.base_path / "working"
        self.ltm_path = self.base_path / "long_term"
        
        # Initialize memory storage
        self._init_storage()
        
        # Start cleanup task
        asyncio.create_task(self._periodic_cleanup())
        
        self.compressor = MemoryCompressor()
        self.migration = MemoryMigration(self.base_path)
        self.search_executor = ThreadPoolExecutor(max_workers=3)  # One per memory type
        
    def _init_storage(self):
        """Initialize memory storage directories"""
        for path in [self.stm_path, self.wm_path, self.ltm_path]:
            path.mkdir(parents=True, exist_ok=True)
            
    async def _periodic_cleanup(self):
        """Periodically clean up expired data"""
        while True:
            await self._cleanup_stm()
            await self._cleanup_wm()
            await asyncio.sleep(3600)  # Run every hour
            
    async def _cleanup_stm(self):
        """Clean up expired short-term memory items"""
        current_time = time.time()
        for item in self.stm_path.glob("*.json"):
            if current_time - item.stat().st_mtime > 3600:  # 1 hour
                item.unlink()
                
    async def _cleanup_wm(self):
        """Clean up expired working memory items"""
        current_time = time.time()
        for item in self.wm_path.glob("*.json"):
            if current_time - item.stat().st_mtime > 86400:  # 24 hours
                item.unlink()

    async def search(self, 
                    query: Union[str, Pattern, Dict],
                    memory_type: MemoryType = MemoryType.ALL,
                    limit: int = 10) -> List[MemorySearchResult]:
        """
        Search across memory types
        Args:
            query: Search string, regex pattern, or dict of criteria
            memory_type: Type of memory to search
            limit: Max results to return
        """
        results = []
        
        if memory_type in [MemoryType.SHORT_TERM, MemoryType.ALL]:
            results.extend(await self._search_stm(query))
            
        if memory_type in [MemoryType.WORKING, MemoryType.ALL]:
            results.extend(await self._search_wm(query))
            
        if memory_type in [MemoryType.LONG_TERM, MemoryType.ALL]:
            results.extend(await self._search_ltm(query))
            
        # Sort by score and timestamp
        results.sort(key=lambda x: (-x.score, -x.timestamp))
        return results[:limit]
    
    async def optimize(self):
        """Optimize memory storage and indexing"""
        # Compact STM
        await self._compact_stm()
        
        # Optimize WM
        await self._optimize_wm()
        
        # Reindex LTM
        await self._reindex_ltm()
    
    async def _compact_stm(self):
        """Compact short-term memory by removing duplicates"""
        seen = set()
        for item in self.stm_path.glob("*.json"):
            with open(item, 'r') as f:
                data = json.load(f)
                key = json.dumps(data['data'], sort_keys=True)
                if key in seen:
                    item.unlink()  # Remove duplicate
                else:
                    seen.add(key)
    
    async def _optimize_wm(self):
        """Optimize working memory"""
        # Group related items
        groups = {}
        for item in self.wm_path.glob("*.json"):
            with open(item, 'r') as f:
                data = json.load(f)
                session_id = data.get('session_id', 'default')
                if session_id not in groups:
                    groups[session_id] = []
                groups[session_id].append((item, data))
        
        # Merge related items
        for session_id, items in groups.items():
            if len(items) > 1:
                merged_data = self._merge_related_items(items)
                merged_path = self.wm_path / f"merged_{session_id}.json"
                with open(merged_path, 'w') as f:
                    json.dump(merged_data, f)
                
                # Remove original files
                for item, _ in items:
                    item.unlink()
    
    async def _reindex_ltm(self):
        """Reindex long-term memory"""
        index = {}
        for item in self.ltm_path.glob("*.json"):
            if item.name != "index.json":
                with open(item, 'r') as f:
                    data = json.load(f)
                    key = item.stem
                    index[key] = {
                        'path': str(item),
                        'timestamp': data.get('timestamp', 0),
                        'type': data.get('metadata', {}).get('type', 'unknown'),
                        'keywords': self._extract_keywords(data['data'])
                    }
        
        # Save new index
        index_path = self.ltm_path / "index.json"
        with open(index_path, 'w') as f:
            json.dump(index, f)
    
    def _extract_keywords(self, data: Any) -> List[str]:
        """Extract searchable keywords from data"""
        keywords = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                keywords.add(key)
                keywords.update(self._extract_keywords(value))
        elif isinstance(data, list):
            for item in data:
                keywords.update(self._extract_keywords(item))
        elif isinstance(data, str):
            # Add basic string tokenization
            keywords.update(data.split())
        
        return list(keywords)
    
    def _merge_related_items(self, items: List[tuple]) -> Dict:
        """Merge related memory items"""
        merged = {
            'data': {},
            'timestamp': max(data['timestamp'] for _, data in items),
            'session_id': items[0][1].get('session_id', 'default'),
            'merged': True,
            'sources': len(items)
        }
        
        for _, data in items:
            if isinstance(data['data'], dict):
                merged['data'].update(data['data'])
            elif isinstance(data['data'], list):
                if 'data' not in merged:
                    merged['data'] = []
                merged['data'].extend(data['data'])
            else:
                merged['data'] = data['data']
        
        return merged

    async def _search_stm(self, query: Union[str, Pattern, Dict]) -> List[MemorySearchResult]:
        """Search short-term memory"""
        results = []
        
        for item in self.stm_path.glob("*.json"):
            with open(item, 'r') as f:
                data = json.load(f)
                score = self._calculate_match_score(query, data['data'])
                if score > 0:
                    results.append(MemorySearchResult(
                        key=item.stem,
                        data=data['data'],
                        memory_type="short_term",
                        timestamp=data['timestamp'],
                        score=score
                    ))
        return results

    async def _search_wm(self, query: Union[str, Pattern, Dict]) -> List[MemorySearchResult]:
        """Search working memory"""
        results = []
        
        for item in self.wm_path.glob("*.json"):
            with open(item, 'r') as f:
                data = json.load(f)
                score = self._calculate_match_score(query, data['data'])
                if score > 0:
                    results.append(MemorySearchResult(
                        key=item.stem,
                        data=data['data'],
                        memory_type="working",
                        timestamp=data['timestamp'],
                        score=score
                    ))
        return results

    async def _search_ltm(self, query: Union[str, Pattern, Dict]) -> List[MemorySearchResult]:
        """Search long-term memory using index"""
        results = []
        
        # Use index for efficient search
        for key, meta in self.ltm.index.items():
            file_path = Path(meta['path'])
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    score = self._calculate_match_score(query, data['data'])
                    if score > 0:
                        results.append(MemorySearchResult(
                            key=key,
                            data=data['data'],
                            memory_type="long_term",
                            timestamp=data['timestamp'],
                            score=score
                        ))
        return results

    def _calculate_match_score(self, query: Union[str, Pattern, Dict], data: Any) -> float:
        """Calculate how well data matches the query"""
        if isinstance(query, str):
            return self._fuzzy_text_match(query, data)
        elif isinstance(query, Pattern):
            return self._pattern_match(query, data)
        elif isinstance(query, dict):
            return self._dict_match(query, data)
        return 0.0

    def _fuzzy_text_match(self, query: str, data: Any) -> float:
        """Perform fuzzy text matching"""
        if isinstance(data, str):
            return SequenceMatcher(None, query.lower(), data.lower()).ratio()
        elif isinstance(data, dict):
            # Search in dict values
            max_score = 0.0
            for value in data.values():
                score = self._fuzzy_text_match(query, value)
                max_score = max(max_score, score)
            return max_score
        elif isinstance(data, list):
            # Search in list items
            max_score = 0.0
            for item in data:
                score = self._fuzzy_text_match(query, item)
                max_score = max(max_score, score)
            return max_score
        return 0.0

    def _pattern_match(self, pattern: Pattern, data: Any) -> float:
        """Match using regex pattern"""
        if isinstance(data, str):
            return 1.0 if pattern.search(data) else 0.0
        elif isinstance(data, dict):
            # Search in dict values
            for value in data.values():
                if self._pattern_match(pattern, value) > 0:
                    return 1.0
        elif isinstance(data, list):
            # Search in list items
            for item in data:
                if self._pattern_match(pattern, item) > 0:
                    return 1.0
        return 0.0

    def _dict_match(self, query: Dict, data: Any) -> float:
        """Match using dictionary criteria"""
        if not isinstance(data, dict):
            return 0.0
            
        matches = 0
        total = len(query)
        
        for key, value in query.items():
            if key in data:
                if isinstance(value, (str, Pattern)):
                    if isinstance(value, str):
                        score = self._fuzzy_text_match(value, data[key])
                    else:
                        score = self._pattern_match(value, data[key])
                    if score > 0.7:  # Threshold for considering a match
                        matches += 1
                elif data[key] == value:
                    matches += 1
                    
        return matches / total if total > 0 else 0.0

    async def store_compressed(self, memory_type: MemoryType, key: str, data: Any):
        """Store compressed data in specified memory"""
        compressed_data = self.compressor.compress(data)
        
        if memory_type == MemoryType.SHORT_TERM:
            await self.stm.store(key, compressed_data)
        elif memory_type == MemoryType.WORKING:
            await self.wm.store(key, compressed_data)
        elif memory_type == MemoryType.LONG_TERM:
            await self.ltm.store(key, compressed_data)
    
    async def retrieve_compressed(self, memory_type: MemoryType, key: str) -> Optional[Any]:
        """Retrieve and decompress data from specified memory"""
        if memory_type == MemoryType.SHORT_TERM:
            data = await self.stm.retrieve(key)
        elif memory_type == MemoryType.WORKING:
            data = await self.wm.retrieve(key)
        elif memory_type == MemoryType.LONG_TERM:
            data = await self.ltm.retrieve(key)
        else:
            return None
            
        if data and isinstance(data, dict) and data.get('compressed'):
            return self.compressor.decompress(data)
        return data
    
    async def migrate_version(self, old_version: str, new_version: str):
        """Migrate memory system to new version"""
        try:
            await self.migration.migrate_schema(old_version, new_version)
            return True
        except Exception as e:
            print(f"Migration failed: {e}")
            return False

    async def parallel_search(self, 
                            query: Union[str, Pattern, Dict],
                            memory_type: MemoryType = MemoryType.ALL,
                            limit: int = 10,
                            min_score: float = 0.5) -> List[MemorySearchResult]:
        """
        Perform parallel search across memory types
        Args:
            query: Search string, regex pattern, or dict of criteria
            memory_type: Type of memory to search
            limit: Max results to return
            min_score: Minimum score threshold
        """
        search_tasks = []
        loop = asyncio.get_running_loop()
        
        if memory_type in [MemoryType.SHORT_TERM, MemoryType.ALL]:
            task = loop.run_in_executor(
                self.search_executor,
                partial(self._search_memory_files, 
                       self.stm_path, 
                       query,
                       "short_term",
                       min_score)
            )
            search_tasks.append(task)
            
        if memory_type in [MemoryType.WORKING, MemoryType.ALL]:
            task = loop.run_in_executor(
                self.search_executor,
                partial(self._search_memory_files, 
                       self.wm_path, 
                       query,
                       "working",
                       min_score)
            )
            search_tasks.append(task)
            
        if memory_type in [MemoryType.LONG_TERM, MemoryType.ALL]:
            task = loop.run_in_executor(
                self.search_executor,
                partial(self._search_memory_files, 
                       self.ltm_path, 
                       query,
                       "long_term",
                       min_score)
            )
            search_tasks.append(task)
        
        # Wait for all search tasks to complete
        results = []
        for completed_task in await asyncio.gather(*search_tasks):
            results.extend(completed_task)
            
        # Sort and filter results
        results.sort(key=lambda x: (-x.score, -x.timestamp))
        return results[:limit]
    
    def _search_memory_files(self, 
                           path: Path, 
                           query: Union[str, Pattern, Dict],
                           memory_type: str,
                           min_score: float) -> List[MemorySearchResult]:
        """Search files in a memory directory"""
        results = []
        
        for item in path.glob("*.json"):
            try:
                with open(item, 'r') as f:
                    data = json.load(f)
                    
                # Skip index file in LTM
                if memory_type == "long_term" and item.name == "index.json":
                    continue
                    
                score = self._calculate_match_score(query, data['data'])
                if score >= min_score:
                    results.append(MemorySearchResult(
                        key=item.stem,
                        data=data['data'],
                        memory_type=memory_type,
                        timestamp=data.get('timestamp', 0),
                        score=score
                    ))
            except Exception as e:
                print(f"Error searching {item}: {e}")
                continue
                
        return results
    
    async def search_with_callback(self,
                                 query: Union[str, Pattern, Dict],
                                 callback: Callable[[MemorySearchResult], None],
                                 memory_type: MemoryType = MemoryType.ALL,
                                 min_score: float = 0.5):
        """
        Stream search results through a callback as they're found
        Args:
            query: Search query
            callback: Function to call with each result
            memory_type: Type of memory to search
            min_score: Minimum score threshold
        """
        async def process_results(future):
            results = await future
            for result in results:
                await callback(result)
        
        search_future = self.parallel_search(query, memory_type, limit=None, min_score=min_score)
        await process_results(search_future)
    
    def _batch_search_files(self, 
                          files: List[Path], 
                          query: Union[str, Pattern, Dict],
                          memory_type: str,
                          min_score: float) -> List[MemorySearchResult]:
        """Search a batch of files"""
        results = []
        
        for file in files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                score = self._calculate_match_score(query, data['data'])
                if score >= min_score:
                    results.append(MemorySearchResult(
                        key=file.stem,
                        data=data['data'],
                        memory_type=memory_type,
                        timestamp=data.get('timestamp', 0),
                        score=score
                    ))
            except Exception as e:
                print(f"Error searching {file}: {e}")
                continue
                
        return results

class ShortTermMemory:
    """Handles immediate context and temporary data"""
    
    def __init__(self, memory_system: MemorySystem):
        self.memory_system = memory_system
        self.context: Dict[str, Any] = {}
        
    async def store(self, key: str, data: Any):
        """Store data in short-term memory"""
        file_path = self.memory_system.stm_path / f"{key}.json"
        async with asyncio.Lock():
            with open(file_path, 'w') as f:
                json.dump({
                    'data': data,
                    'timestamp': time.time()
                }, f)
        self.context[key] = data
        
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from short-term memory"""
        if key in self.context:
            return self.context[key]
            
        file_path = self.memory_system.stm_path / f"{key}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.context[key] = data['data']
                return data['data']
        return None

class WorkingMemory:
    """Manages active session data and ongoing processes"""
    
    def __init__(self, memory_system: MemorySystem):
        self.memory_system = memory_system
        self.active_session: Dict[str, Any] = {}
        
    async def store(self, key: str, data: Any):
        """Store data in working memory"""
        file_path = self.memory_system.wm_path / f"{key}.json"
        async with asyncio.Lock():
            with open(file_path, 'w') as f:
                json.dump({
                    'data': data,
                    'timestamp': time.time(),
                    'session_id': id(self)
                }, f)
        self.active_session[key] = data
        
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from working memory"""
        if key in self.active_session:
            return self.active_session[key]
            
        file_path = self.memory_system.wm_path / f"{key}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.active_session[key] = data['data']
                return data['data']
        return None

class LongTermMemory:
    """Stores persistent data and learned patterns"""
    
    def __init__(self, memory_system: MemorySystem):
        self.memory_system = memory_system
        self._load_index()
        
    def _load_index(self):
        """Load or create the LTM index"""
        index_path = self.memory_system.ltm_path / "index.json"
        if index_path.exists():
            with open(index_path, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
            self._save_index()
            
    def _save_index(self):
        """Save the LTM index"""
        index_path = self.memory_system.ltm_path / "index.json"
        with open(index_path, 'w') as f:
            json.dump(self.index, f)
        
    async def store(self, key: str, data: Any):
        """Store data in long-term memory"""
        file_path = self.memory_system.ltm_path / f"{key}.json"
        async with asyncio.Lock():
            with open(file_path, 'w') as f:
                json.dump({
                    'data': data,
                    'timestamp': time.time(),
                    'metadata': {
                        'version': 1,
                        'type': str(type(data).__name__)
                    }
                }, f)
            self.index[key] = {
                'path': str(file_path),
                'timestamp': time.time()
            }
            self._save_index()
        
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from long-term memory"""
        if key not in self.index:
            return None
            
        file_path = Path(self.index[key]['path'])
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data['data']
        return None

# Initialize global memory system
memory_system = MemorySystem() 