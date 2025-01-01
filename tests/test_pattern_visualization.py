"""Tests for pattern visualization functionality"""

import pytest
import plotly.graph_objects as go
from tools.common.visualization.pattern_viz import PatternVisualizer

@pytest.fixture
def config():
    return {
        "visualization": {
            "color_scheme": "viridis",
            "interactive": True
        }
    }

@pytest.fixture
def visualizer(config):
    return PatternVisualizer(config)

@pytest.fixture
def sample_hierarchy():
    return {
        "root": "concepts",
        "children": {
            "usability": {
                "checkout": ["errors", "validation", "flow"],
                "navigation": ["menu", "search", "filters"]
            },
            "performance": {
                "speed": ["loading", "response"],
                "reliability": ["uptime", "errors"]
            }
        }
    }

def test_concept_map_creation(visualizer, sample_hierarchy):
    """Test concept map visualization"""
    fig = visualizer.create_concept_map(sample_hierarchy)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # Edges and nodes
    
    # Check node trace
    node_trace = fig.data[1]
    assert node_trace.mode == "markers+text"
    assert len(node_trace.x) > 0
    assert len(node_trace.y) > 0

def test_semantic_chain_visualization(visualizer, sample_chains):
    """Test semantic chain visualization"""
    fig = visualizer.create_semantic_chain_visualization(sample_chains)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0
    
    # Check chain traces
    chain_traces = [t for t in fig.data if t.mode == "markers+text"]
    assert len(chain_traces) == len(sample_chains)

def test_topic_cluster_visualization(visualizer, sample_topics):
    """Test topic cluster visualization"""
    fig = visualizer.create_topic_cluster_visualization(sample_topics)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert isinstance(fig.data[0], go.Sunburst) 