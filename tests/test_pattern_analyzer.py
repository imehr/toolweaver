"""Tests for pattern analysis functionality"""

import pytest
from datetime import datetime, timedelta
import numpy as np
from tools.modules.ux_research.pattern_analyzer import PatternAnalyzer
from tools.common.validation.quality_metrics import QualityMetrics

@pytest.fixture
def config():
    return {
        "analysis": {
            "similarity_threshold": 0.3,
            "min_group_size": 2,
            "min_frequency": 2
        },
        "validation": {
            "quality_metrics": {
                "min_confidence": 0.7,
                "min_support": 0.3
            }
        }
    }

@pytest.fixture
def pattern_analyzer(config):
    return PatternAnalyzer(config)

@pytest.fixture
def quality_metrics(config):
    return QualityMetrics(config)

@pytest.fixture
def sample_insights():
    base_date = datetime.now()
    return [
        {
            "id": "1",
            "text": "Users consistently struggle with the checkout process",
            "timestamp": (base_date - timedelta(days=5)).isoformat(),
            "sentiment": {"polarity": -0.6},
            "score": 0.8,
            "source": "usability_test",
            "entities": [
                {"text": "checkout process", "label": "feature"}
            ]
        },
        {
            "id": "2",
            "text": "Payment validation errors cause frustration",
            "timestamp": (base_date - timedelta(days=3)).isoformat(),
            "sentiment": {"polarity": -0.7},
            "score": 0.9,
            "source": "user_interview",
            "entities": [
                {"text": "payment validation", "label": "feature"}
            ]
        }
    ]

def test_temporal_pattern_detection(pattern_analyzer, sample_insights):
    """Test temporal pattern detection"""
    result = pattern_analyzer.analyze_temporal_patterns(sample_insights)
    
    assert "patterns" in result
    assert "seasonality" in result
    assert "trends" in result
    assert "confidence" in result
    
    # Check trend detection
    trends = [p for p in result["patterns"] if p["type"] == "trend"]
    assert len(trends) > 0
    assert all("direction" in t for t in trends)
    assert all("strength" in t for t in trends)

def test_relationship_pattern_detection(pattern_analyzer, sample_insights):
    """Test relationship pattern detection"""
    result = pattern_analyzer.analyze_relationship_patterns(sample_insights)
    
    assert "communities" in result
    assert "central_insights" in result
    assert "bridge_insights" in result
    assert isinstance(result["density"], float)
    assert isinstance(result["modularity"], float)

def test_semantic_pattern_detection(pattern_analyzer, sample_insights):
    """Test semantic pattern detection"""
    result = pattern_analyzer.analyze_semantic_patterns(sample_insights)
    
    assert "topic_clusters" in result
    assert "key_phrases" in result
    assert "semantic_chains" in result
    assert "concept_hierarchy" in result

def test_quality_metrics(quality_metrics, sample_insights):
    """Test quality metrics calculation"""
    for insight in sample_insights:
        metrics = quality_metrics.calculate_insight_metrics(insight)
        
        assert "clarity" in metrics
        assert "specificity" in metrics
        assert "actionability" in metrics
        assert "evidence_strength" in metrics
        assert "novelty" in metrics
        assert "impact" in metrics
        
        assert all(0 <= score <= 1 for score in metrics.values()) 