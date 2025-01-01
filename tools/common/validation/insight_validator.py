"""Validation utilities for insights"""

from typing import Dict, List, Any
from datetime import datetime
import re

class InsightValidator:
    """Validates insight data and structures"""
    
    @staticmethod
    def validate_insight(insight: Dict) -> bool:
        """Validate single insight structure"""
        required_fields = {"text", "score"}
        if not all(field in insight for field in required_fields):
            return False
            
        if not isinstance(insight["text"], str) or not insight["text"].strip():
            return False
            
        if not isinstance(insight["score"], (int, float)) or not 0 <= insight["score"] <= 1:
            return False
            
        return True
    
    @staticmethod
    def validate_synthesis(synthesis: Dict) -> List[str]:
        """Validate synthesis structure and content"""
        errors = []
        
        # Check required sections
        required_sections = {
            "key_findings",
            "recommendations",
            "priority_areas",
            "confidence_scores"
        }
        
        missing_sections = required_sections - set(synthesis.keys())
        if missing_sections:
            errors.append(f"Missing required sections: {missing_sections}")
        
        # Validate timestamps
        if not InsightValidator._validate_timestamp(synthesis.get("timestamp")):
            errors.append("Invalid timestamp format")
        
        # Validate scores
        if not InsightValidator._validate_confidence_scores(
            synthesis.get("confidence_scores", {})
        ):
            errors.append("Invalid confidence scores")
        
        # Validate findings
        findings_errors = InsightValidator._validate_findings(
            synthesis.get("key_findings", [])
        )
        errors.extend(findings_errors)
        
        return errors
    
    @staticmethod
    def _validate_timestamp(timestamp: str) -> bool:
        """Validate timestamp format"""
        try:
            datetime.fromisoformat(timestamp)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _validate_confidence_scores(scores: Dict) -> bool:
        """Validate confidence score structure"""
        required_scores = {"overall", "findings", "recommendations", "priorities"}
        
        if not all(score in scores for score in required_scores):
            return False
            
        return all(
            isinstance(score, (int, float)) and 0 <= score <= 1
            for score in scores.values()
        )
    
    @staticmethod
    def _validate_findings(findings: List[Dict]) -> List[str]:
        """Validate findings structure and content"""
        errors = []
        
        for i, finding in enumerate(findings):
            if not isinstance(finding.get("text"), str):
                errors.append(f"Finding {i}: Invalid text format")
                
            if not isinstance(finding.get("theme"), str):
                errors.append(f"Finding {i}: Invalid theme format")
                
            if not isinstance(finding.get("frequency"), int):
                errors.append(f"Finding {i}: Invalid frequency format")
                
            if not isinstance(finding.get("confidence"), (int, float)):
                errors.append(f"Finding {i}: Invalid confidence format")
        
        return errors 