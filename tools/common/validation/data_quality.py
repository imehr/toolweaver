"""Data quality validation utilities"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import Counter
import re

class DataQualityChecker:
    """Advanced data quality validation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.quality_rules = config["validation"]["data_quality"]
    
    def check_data_quality(self, data: Dict) -> Dict[str, Any]:
        """Comprehensive data quality check"""
        checks = {
            "completeness": self._check_completeness(data),
            "consistency": self._check_consistency(data),
            "timeliness": self._check_timeliness(data),
            "validity": self._check_validity(data),
            "uniqueness": self._check_uniqueness(data),
            "integrity": self._check_integrity(data)
        }
        
        return {
            "checks": checks,
            "score": self._calculate_quality_score(checks),
            "issues": self._identify_quality_issues(checks),
            "recommendations": self._generate_quality_recommendations(checks)
        }
    
    def _check_validity(self, data: Dict) -> Dict[str, Any]:
        """Check data validity"""
        validity_checks = {
            "format": self._check_format_validity(data),
            "range": self._check_range_validity(data),
            "logic": self._check_logical_validity(data),
            "dependencies": self._check_dependency_validity(data)
        }
        
        return {
            "checks": validity_checks,
            "score": np.mean(list(validity_checks.values())),
            "issues": [k for k, v in validity_checks.items() if v < 0.8]
        }
    
    def _check_integrity(self, data: Dict) -> Dict[str, Any]:
        """Check data integrity"""
        return {
            "referential": self._check_referential_integrity(data),
            "structural": self._check_structural_integrity(data),
            "semantic": self._check_semantic_integrity(data)
        }
    
    def _generate_quality_recommendations(self, checks: Dict) -> List[Dict]:
        """Generate recommendations for improving data quality"""
        recommendations = []
        
        for check_type, results in checks.items():
            if isinstance(results, dict) and results.get("score", 1.0) < 0.8:
                recommendations.extend(
                    self._get_recommendations_for_check(check_type, results)
                )
        
        return sorted(
            recommendations,
            key=lambda x: (-x["priority"], -x["impact"])
        ) 