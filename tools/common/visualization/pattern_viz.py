"""
Pattern Visualization for ToolWeaver

Provides visualization capabilities for:
- Memory usage patterns
- Tool execution flows
- Data relationships
- Performance metrics
"""

from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import json

class PatternVisualizer:
    """Visualizes patterns and relationships in tool data"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.style = self.config.get("style", "default")
        plt.style.use(self.style)
        
    def visualize_memory_usage(self, 
                             memory_data: Dict[str, Dict],
                             output_path: Optional[str] = None):
        """Visualize memory usage patterns"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        memory_types = list(memory_data.keys())
        usage_values = [d["size"] for d in memory_data.values()]
        
        ax.bar(memory_types, usage_values)
        ax.set_title("Memory Usage by Type")
        ax.set_ylabel("Size (bytes)")
        
        if output_path:
            plt.savefig(output_path)
        else:
            plt.show()
            
    def visualize_tool_flow(self,
                           flow_data: List[Dict],
                           output_path: Optional[str] = None):
        """Visualize tool execution flow"""
        G = nx.DiGraph()
        
        # Add nodes and edges
        for step in flow_data:
            G.add_node(step["tool_id"], **step.get("attributes", {}))
            if step.get("next_tools"):
                for next_tool in step["next_tools"]:
                    G.add_edge(step["tool_id"], next_tool)
                    
        # Create layout
        pos = nx.spring_layout(G)
        
        # Draw graph
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos,
                with_labels=True,
                node_color='lightblue',
                node_size=2000,
                arrowsize=20)
                
        if output_path:
            plt.savefig(output_path)
        else:
            plt.show()
            
    def visualize_performance(self,
                            metrics: Dict[str, List],
                            output_path: Optional[str] = None):
        """Visualize performance metrics"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for metric_name, values in metrics.items():
            timestamps = range(len(values))
            ax.plot(timestamps, values, label=metric_name)
            
        ax.set_title("Performance Metrics Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
        
        if output_path:
            plt.savefig(output_path)
        else:
            plt.show()
            
    def export_visualization_data(self,
                                data: Dict[str, Any],
                                output_path: str):
        """Export visualization data as JSON"""
        with open(output_path, 'w') as f:
            json.dump({
                "data": data,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }, f, indent=2) 