"""Tool for recognizing patterns across multiple research artifacts"""

from typing import Dict, List, Any, Optional
from tools.common.base_tool import BaseTool, ValidationError
from tools.common.memory import MemoryType
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np
from collections import defaultdict

class PatternRecognizer(BaseTool):
    def __init__(self):
        super().__init__("pattern_recognizer")
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        
    async def execute(self, data_type: str) -> List[Dict]:
        """Execute pattern recognition"""
        if not self._validate_input({"data_type": data_type}):
            raise ValidationError("Invalid data type")
            
        return await self.find_patterns(data_type)
        
    async def find_patterns(self, data_type: str) -> List[Dict]:
        """Find patterns in research data"""
        
        # Search for relevant data
        results = await self.memory.parallel_search(
            query={"type": data_type},
            memory_type=MemoryType.ALL,
            min_score=0.7
        )
        
        if not results:
            return []
            
        # Extract text content for analysis
        texts = []
        metadata = []
        for result in results:
            text, meta = self._extract_text_and_metadata(result.data)
            texts.append(text)
            metadata.append(meta)
            
        # Vectorize and cluster
        vectors = self.vectorizer.fit_transform(texts)
        clusters = self._cluster_texts(vectors)
        
        # Analyze patterns
        patterns = self._analyze_patterns(texts, clusters, metadata)
        
        result = {
            "type": "pattern_analysis",
            "patterns": patterns,
            "source_type": data_type,
            "confidence": self._calculate_confidence(patterns)
        }
        
        # Store results
        await self.store_result(result)
        
        if result["confidence"] > 0.8:
            await self.memory.memory_system.store_compressed(
                MemoryType.LONG_TERM,
                f"patterns_{data_type}",
                result
            )
        
        return patterns
        
    def _extract_text_and_metadata(self, data: Dict) -> tuple:
        """Extract text and metadata from data"""
        text = ""
        metadata = {}
        
        if "insights" in data:
            text = " ".join(i["text"] for i in data["insights"])
            metadata["insight_count"] = len(data["insights"])
            
        if "themes" in data:
            metadata["themes"] = data["themes"]
            
        if "sentiment" in data:
            metadata["sentiment"] = data["sentiment"]
            
        return text, metadata
        
    def _cluster_texts(self, vectors) -> np.ndarray:
        """Cluster text vectors using DBSCAN"""
        clustering = DBSCAN(
            eps=0.3,
            min_samples=2,
            metric='cosine'
        )
        return clustering.fit_predict(vectors.toarray())
        
    def _analyze_patterns(self, 
                         texts: List[str],
                         clusters: np.ndarray,
                         metadata: List[Dict]) -> List[Dict]:
        """Analyze patterns in clustered texts"""
        patterns = []
        cluster_data = defaultdict(list)
        
        # Group by cluster
        for text, cluster_id, meta in zip(texts, clusters, metadata):
            if cluster_id != -1:  # Skip noise
                cluster_data[cluster_id].append((text, meta))
                
        # Analyze each cluster
        for cluster_id, items in cluster_data.items():
            pattern = self._analyze_cluster(items)
            if pattern:
                patterns.append(pattern)
                
        return patterns
        
    def _analyze_cluster(self, items: List[tuple]) -> Optional[Dict]:
        """Analyze a single cluster"""
        texts, metadata = zip(*items)
        
        # Get common themes
        themes = set()
        for meta in metadata:
            themes.update(meta.get("themes", []))
            
        # Analyze sentiments
        sentiments = [
            meta.get("sentiment", {}).get("assessment")
            for meta in metadata
            if "sentiment" in meta
        ]
        
        if not themes or not sentiments:
            return None
            
        return {
            "themes": list(themes),
            "sentiment_distribution": self._count_sentiments(sentiments),
            "frequency": len(items),
            "confidence": self._calculate_cluster_confidence(items)
        }
        
    def _count_sentiments(self, sentiments: List[str]) -> Dict[str, float]:
        """Calculate sentiment distribution"""
        total = len(sentiments)
        counts = defaultdict(int)
        for sentiment in sentiments:
            counts[sentiment] += 1
            
        return {
            sentiment: count/total
            for sentiment, count in counts.items()
        }
        
    def _calculate_cluster_confidence(self, items: List[tuple]) -> float:
        """Calculate confidence score for a cluster"""
        # Implementation of confidence calculation
        return 0.8
        
    def _calculate_confidence(self, patterns: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not patterns:
            return 0.0
            
        return sum(p.get("confidence", 0) for p in patterns) / len(patterns) 