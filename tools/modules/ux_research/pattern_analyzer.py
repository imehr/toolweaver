"""Pattern analysis utilities for insights"""

from typing import Dict, List, Any, Optional
import numpy as np
from scipy import stats
from datetime import datetime
import networkx as nx
from collections import defaultdict

class PatternAnalyzer:
    """Analyzes patterns in insight data"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.similarity_threshold = config["analysis"]["similarity_threshold"]
        
    def analyze_temporal_patterns(self, insights: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in insights"""
        timestamps = []
        values = defaultdict(list)
        
        for insight in insights:
            if "timestamp" in insight:
                ts = datetime.fromisoformat(insight["timestamp"])
                timestamps.append(ts)
                
                # Track different metrics
                values["sentiment"].append(
                    insight.get("sentiment", {}).get("polarity", 0)
                )
                values["confidence"].append(insight.get("score", 0))
                values["impact"].append(
                    self._calculate_impact_score(insight)
                )
        
        if not timestamps:
            return {"patterns": [], "confidence": 0.0}
            
        return {
            "patterns": self._identify_temporal_patterns(timestamps, values),
            "seasonality": self._analyze_seasonality(timestamps, values),
            "trends": self._analyze_trends(timestamps, values),
            "confidence": self._calculate_pattern_confidence(timestamps, values)
        }
    
    def analyze_relationship_patterns(self, insights: List[Dict]) -> Dict[str, Any]:
        """Analyze relationships between insights"""
        # Build relationship graph
        graph = self._build_relationship_graph(insights)
        
        # Analyze graph structure
        communities = self._detect_communities(graph)
        central_nodes = self._identify_central_nodes(graph)
        bridges = self._find_bridge_insights(graph)
        
        return {
            "communities": communities,
            "central_insights": central_nodes,
            "bridge_insights": bridges,
            "density": nx.density(graph),
            "modularity": self._calculate_modularity(graph, communities)
        }
    
    def analyze_semantic_patterns(self, insights: List[Dict]) -> Dict[str, Any]:
        """Analyze semantic patterns in insights"""
        # Extract text content
        texts = [insight.get("text", "") for insight in insights]
        
        return {
            "topic_clusters": self._identify_topic_clusters(texts),
            "key_phrases": self._extract_key_phrases(texts),
            "semantic_chains": self._find_semantic_chains(insights),
            "concept_hierarchy": self._build_concept_hierarchy(insights)
        }
    
    def _identify_temporal_patterns(self, 
                                  timestamps: List[datetime],
                                  values: Dict[str, List[float]]) -> List[Dict]:
        """Identify patterns in temporal data"""
        patterns = []
        
        # Analyze each metric
        for metric, metric_values in values.items():
            # Check for trends
            trend = self._detect_trend(metric_values)
            if trend["strength"] > 0.6:
                patterns.append({
                    "type": "trend",
                    "metric": metric,
                    "direction": trend["direction"],
                    "strength": trend["strength"]
                })
            
            # Check for cycles
            cycles = self._detect_cycles(timestamps, metric_values)
            patterns.extend(cycles)
            
            # Check for anomalies
            anomalies = self._detect_anomalies(metric_values)
            patterns.extend(anomalies)
        
        return patterns
    
    def _build_relationship_graph(self, insights: List[Dict]) -> nx.Graph:
        """Build graph of insight relationships"""
        graph = nx.Graph()
        
        # Add nodes
        for insight in insights:
            graph.add_node(insight["id"], **insight)
        
        # Add edges based on similarity
        for i, insight1 in enumerate(insights):
            for insight2 in insights[i+1:]:
                similarity = self._calculate_similarity(insight1, insight2)
                if similarity > self.similarity_threshold:
                    graph.add_edge(
                        insight1["id"],
                        insight2["id"],
                        weight=similarity
                    )
        
        return graph
    
    def _detect_communities(self, graph: nx.Graph) -> List[Dict]:
        """Detect communities in insight graph"""
        communities = nx.community.greedy_modularity_communities(graph)
        
        return [
            {
                "id": i,
                "insights": list(community),
                "size": len(community),
                "density": nx.density(graph.subgraph(community)),
                "central_node": self._find_community_center(
                    graph.subgraph(community)
                )
            }
            for i, community in enumerate(communities)
        ]
    
    def _calculate_modularity(self, graph: nx.Graph, communities: List[Dict]) -> float:
        """Calculate modularity of community structure"""
        community_sets = [set(c["insights"]) for c in communities]
        return nx.community.modularity(graph, community_sets) 
    
    def _identify_topic_clusters(self, texts: List[str]) -> List[Dict]:
        """Identify clusters of related topics"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import DBSCAN
        
        # Vectorize texts
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english'
        )
        vectors = vectorizer.fit_transform(texts)
        
        # Cluster vectors
        clustering = DBSCAN(
            eps=0.3,
            min_samples=2,
            metric='cosine'
        ).fit(vectors)
        
        # Extract topics for each cluster
        topics = []
        for label in set(clustering.labels_):
            if label == -1:  # Skip noise
                continue
            
            cluster_indices = [i for i, l in enumerate(clustering.labels_) if l == label]
            cluster_vectors = vectors[cluster_indices]
            
            # Get top terms for cluster
            importance = cluster_vectors.mean(axis=0).A1
            top_terms = [
                vectorizer.get_feature_names_out()[i]
                for i in importance.argsort()[-5:][::-1]
            ]
            
            topics.append({
                "id": label,
                "terms": top_terms,
                "size": len(cluster_indices),
                "coherence": self._calculate_topic_coherence(cluster_vectors)
            })
        
        return topics
    
    def _find_semantic_chains(self, insights: List[Dict]) -> List[Dict]:
        """Find chains of semantically related insights"""
        chains = []
        used = set()
        
        for i, start_insight in enumerate(insights):
            if i in used:
                continue
            
            chain = [start_insight]
            used.add(i)
            
            # Find connected insights
            current = start_insight
            while True:
                next_insight = self._find_next_in_chain(current, insights, used)
                if not next_insight:
                    break
                
                chain.append(next_insight["insight"])
                used.add(next_insight["index"])
                current = next_insight["insight"]
            
            if len(chain) > 1:
                chains.append({
                    "insights": chain,
                    "strength": self._calculate_chain_strength(chain),
                    "theme": self._identify_chain_theme(chain)
                })
        
        return chains
    
    def _build_concept_hierarchy(self, insights: List[Dict]) -> Dict[str, Any]:
        """Build hierarchical representation of concepts"""
        # Extract entities and relationships
        entities = self._extract_all_entities(insights)
        relationships = self._extract_relationships(insights)
        
        # Build hierarchy
        hierarchy = {
            "root": "concepts",
            "children": self._organize_concepts(entities, relationships)
        }
        
        return hierarchy
    
    def _calculate_pattern_significance(self, pattern: Dict) -> float:
        """Calculate statistical significance of pattern"""
        if pattern["type"] == "trend":
            return self._calculate_trend_significance(
                pattern["values"],
                pattern["timestamps"]
            )
        elif pattern["type"] == "cycle":
            return self._calculate_cycle_significance(
                pattern["values"],
                pattern["period"]
            )
        elif pattern["type"] == "anomaly":
            return self._calculate_anomaly_significance(
                pattern["value"],
                pattern["baseline"]
            )
        
        return 0.0
    
    def _detect_trend(self, values: List[float]) -> Dict[str, Any]:
        """Detect trend in time series data"""
        # Calculate slope using linear regression
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Determine trend direction and strength
        direction = "increasing" if slope > 0 else "decreasing"
        strength = abs(r_value)
        
        return {
            "direction": direction,
            "strength": strength,
            "slope": slope,
            "p_value": p_value,
            "confidence": 1 - p_value
        }
    
    def _detect_cycles(self, timestamps: List[datetime], values: List[float]) -> List[Dict]:
        """Detect cyclical patterns"""
        from scipy.fft import fft
        
        # Convert to numpy array
        values_array = np.array(values)
        
        # Perform FFT
        fft_result = fft(values_array)
        frequencies = np.fft.fftfreq(len(values_array))
        
        # Find significant frequencies
        threshold = 0.1 * np.max(np.abs(fft_result))
        significant_freq = frequencies[np.abs(fft_result) > threshold]
        
        cycles = []
        for freq in significant_freq:
            if freq > 0:  # Only positive frequencies
                period = 1 / freq
                cycles.append({
                    "type": "cycle",
                    "period": period,
                    "strength": float(np.abs(fft_result[frequencies == freq])[0]),
                    "phase": float(np.angle(fft_result[frequencies == freq])[0])
                })
        
        return cycles 