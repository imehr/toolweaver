"""Data quality validation for insights"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime, timedelta
from collections import Counter

class QualityChecker:
    """Checks data quality of insights and synthesis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.content_rules = config["validation"]["content_rules"]
        self.quality_metrics = config["validation"]["quality_metrics"]
    
    def check_insight_quality(self, insight: Dict) -> Dict[str, Any]:
        """Check quality of a single insight"""
        quality_scores = {
            "content": self._check_content_quality(insight),
            "completeness": self._check_completeness(insight),
            "consistency": self._check_consistency(insight),
            "timeliness": self._check_timeliness(insight)
        }
        
        return {
            "scores": quality_scores,
            "overall": sum(quality_scores.values()) / len(quality_scores),
            "issues": self._identify_quality_issues(insight, quality_scores)
        }
    
    def check_synthesis_quality(self, synthesis: Dict) -> Dict[str, Any]:
        """Check quality of synthesis results"""
        return {
            "structure": self._check_synthesis_structure(synthesis),
            "content": self._check_synthesis_content(synthesis),
            "relationships": self._check_insight_relationships(synthesis),
            "metrics": self._check_quality_metrics(synthesis)
        }
    
    def _check_content_quality(self, insight: Dict) -> float:
        """Check content quality against rules"""
        text = insight.get("text", "")
        word_count = len(text.split())
        
        # Check word count
        if not (self.content_rules["min_word_count"] <= 
                word_count <= 
                self.content_rules["max_word_count"]):
            return 0.5
        
        # Check required patterns
        pattern_scores = []
        for pattern in self.content_rules["required_patterns"]:
            if re.search(pattern["regex"], text, re.IGNORECASE):
                pattern_scores.append(1.0)
            else:
                pattern_scores.append(0.0)
        
        return sum(pattern_scores) / len(pattern_scores)
    
    def _check_completeness(self, insight: Dict) -> float:
        """Check insight completeness"""
        required_fields = {
            "text": 1.0,
            "score": 1.0,
            "timestamp": 0.8,
            "source": 0.8,
            "entities": 0.6,
            "keywords": 0.6
        }
        
        score = 0.0
        total_weight = 0.0
        
        for field, weight in required_fields.items():
            if field in insight and insight[field]:
                score += weight
            total_weight += weight
        
        return score / total_weight
    
    def _check_consistency(self, insight: Dict) -> float:
        """Check internal consistency of insight"""
        consistency_checks = [
            self._check_sentiment_consistency(insight),
            self._check_entity_consistency(insight),
            self._check_theme_consistency(insight)
        ]
        
        return sum(check for check in consistency_checks if check is not None) / len(consistency_checks)
    
    def _check_timeliness(self, insight: Dict) -> float:
        """Check insight timeliness"""
        if "timestamp" not in insight:
            return 0.5
            
        timestamp = datetime.fromisoformat(insight["timestamp"])
        age = datetime.now() - timestamp
        
        # Score decreases with age
        if age <= timedelta(days=7):
            return 1.0
        elif age <= timedelta(days=30):
            return 0.8
        elif age <= timedelta(days=90):
            return 0.6
        elif age <= timedelta(days=180):
            return 0.4
        else:
            return 0.2 