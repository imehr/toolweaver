"""Quality metrics for insight analysis"""

from typing import Dict, List, Any, Optional
import numpy as np
from scipy import stats
from datetime import datetime
import re
from collections import Counter

class QualityMetrics:
    """Metrics for measuring insight and pattern quality"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quality_thresholds = config["validation"]["quality_metrics"]
    
    def calculate_insight_metrics(self, insight: Dict) -> Dict[str, float]:
        """Calculate quality metrics for a single insight"""
        return {
            "clarity": self._measure_clarity(insight),
            "specificity": self._measure_specificity(insight),
            "actionability": self._measure_actionability(insight),
            "evidence_strength": self._measure_evidence_strength(insight),
            "novelty": self._measure_novelty(insight),
            "impact": self._measure_potential_impact(insight)
        }
    
    def calculate_pattern_metrics(self, pattern: Dict) -> Dict[str, float]:
        """Calculate quality metrics for a pattern"""
        return {
            "reliability": self._measure_pattern_reliability(pattern),
            "significance": self._measure_statistical_significance(pattern),
            "consistency": self._measure_pattern_consistency(pattern),
            "coverage": self._measure_pattern_coverage(pattern),
            "distinctiveness": self._measure_pattern_distinctiveness(pattern)
        }
    
    def _measure_clarity(self, insight: Dict) -> float:
        """Measure clarity of insight text"""
        text = insight.get("text", "")
        
        # Check sentence structure
        sentences = text.split(".")
        sentence_scores = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # Check length
            words = sentence.split()
            if not (5 <= len(words) <= 25):
                sentence_scores.append(0.5)
                continue
            
            # Check readability
            score = self._calculate_readability_score(sentence)
            sentence_scores.append(score)
        
        return np.mean(sentence_scores) if sentence_scores else 0.0
    
    def _measure_specificity(self, insight: Dict) -> float:
        """Measure how specific and concrete the insight is"""
        text = insight.get("text", "")
        
        # Check for specific details
        specificity_markers = [
            r"\b\d+(?:\.\d+)?%?\b",  # Numbers and percentages
            r"\b(increased|decreased|improved|reduced) by\b",  # Quantified changes
            r"\b(specifically|particularly|notably)\b",  # Specific indicators
            r"\b(in|during|on) [A-Z][a-z]+ \d{4}\b"  # Dates
        ]
        
        marker_scores = []
        for marker in specificity_markers:
            matches = len(re.findall(marker, text))
            marker_scores.append(min(matches / 2, 1.0))
        
        return np.mean(marker_scores) if marker_scores else 0.0
    
    def _measure_evidence_strength(self, insight: Dict) -> float:
        """Measure strength of supporting evidence"""
        # Check data sources
        sources = insight.get("sources", [])
        if not sources:
            return 0.0
            
        source_scores = []
        for source in sources:
            score = 0.0
            
            # Check source type
            if source.get("type") == "primary_research":
                score += 0.4
            elif source.get("type") == "secondary_research":
                score += 0.2
                
            # Check sample size
            sample_size = source.get("sample_size", 0)
            if sample_size > 100:
                score += 0.3
            elif sample_size > 30:
                score += 0.2
            elif sample_size > 10:
                score += 0.1
                
            # Check methodology
            if source.get("methodology"):
                score += 0.3
                
            source_scores.append(score)
        
        return np.mean(source_scores) 