"""Pattern visualization utilities"""

from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
from datetime import datetime

class PatternVisualizer:
    """Visualizes patterns in insight data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.color_scheme = config.get("visualization", {}).get(
            "color_scheme", "viridis"
        )
    
    def create_temporal_visualization(self, 
                                   timestamps: List[datetime],
                                   values: Dict[str, List[float]],
                                   patterns: List[Dict]) -> go.Figure:
        """Create temporal pattern visualization"""
        fig = go.Figure()
        
        # Add time series
        for metric, metric_values in values.items():
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=metric_values,
                name=metric,
                mode='lines+markers'
            ))
        
        # Highlight patterns
        self._add_pattern_highlights(fig, timestamps, patterns)
        
        # Add annotations
        self._add_pattern_annotations(fig, patterns)
        
        return fig
    
    def create_relationship_visualization(self,
                                       graph: nx.Graph,
                                       communities: List[Dict]) -> go.Figure:
        """Create relationship graph visualization"""
        # Calculate layout
        pos = nx.spring_layout(graph)
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        edge_x, edge_y = self._get_edge_coordinates(graph, pos)
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        for community in communities:
            node_x, node_y = self._get_community_coordinates(
                community["insights"],
                pos
            )
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=[graph.nodes[node]["text"] for node in community["insights"]],
                marker=dict(
                    size=10,
                    line_width=2
                )
            ))
        
        return fig
    
    def create_pattern_summary(self, patterns: List[Dict]) -> go.Figure:
        """Create pattern summary visualization"""
        # Convert patterns to DataFrame
        df = pd.DataFrame(patterns)
        
        # Create summary visualization
        fig = px.scatter(
            df,
            x='strength',
            y='confidence',
            color='type',
            size='impact',
            hover_data=['description']
        )
        
        return fig 
    
    def create_concept_map(self, hierarchy: Dict[str, Any]) -> go.Figure:
        """Create interactive concept map visualization"""
        def _process_node(node, parent=""):
            nodes = []
            edges = []
            
            if isinstance(node, dict):
                for key, value in node.items():
                    nodes.append({"id": key, "label": key})
                    if parent:
                        edges.append({"from": parent, "to": key})
                    child_nodes, child_edges = _process_node(value, key)
                    nodes.extend(child_nodes)
                    edges.extend(child_edges)
            
            return nodes, edges
        
        nodes, edges = _process_node(hierarchy)
        
        # Create network graph
        G = nx.Graph()
        for node in nodes:
            G.add_node(node["id"], label=node["label"])
        for edge in edges:
            G.add_edge(edge["from"], edge["to"])
        
        # Calculate layout
        pos = nx.spring_layout(G)
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[G.nodes[node]["label"] for node in G.nodes()],
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                size=20,
                color=list(range(len(G.nodes()))),
                colorscale=self.color_scheme,
                line_width=2
            )
        ))
        
        return fig
    
    def create_semantic_chain_visualization(self, chains: List[Dict]) -> go.Figure:
        """Create visualization of semantic chains"""
        fig = go.Figure()
        
        for i, chain in enumerate(chains):
            # Create nodes for insights
            x = list(range(len(chain["insights"])))
            y = [i] * len(chain["insights"])
            
            # Add connections
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                line=dict(
                    width=2,
                    color=f'rgba(100,100,100,{chain["strength"]})'
                ),
                hoverinfo='none'
            ))
            
            # Add insight nodes
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='markers+text',
                text=[insight["text"][:50] + "..." for insight in chain["insights"]],
                textposition="top center",
                marker=dict(
                    size=15,
                    color=i,
                    colorscale=self.color_scheme
                ),
                name=f'Chain {i+1}: {chain["theme"]}'
            ))
        
        return fig
    
    def create_topic_cluster_visualization(self, topics: List[Dict]) -> go.Figure:
        """Create topic cluster visualization"""
        # Create sunburst chart
        labels = []
        parents = []
        values = []
        
        # Add root
        labels.append("Topics")
        parents.append("")
        values.append(sum(topic["size"] for topic in topics))
        
        # Add topics
        for topic in topics:
            # Add topic node
            topic_id = f"Topic {topic['id']}"
            labels.append(topic_id)
            parents.append("Topics")
            values.append(topic["size"])
            
            # Add terms
            for term in topic["terms"]:
                labels.append(term)
                parents.append(topic_id)
                values.append(1)
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total"
        ))
        
        return fig 