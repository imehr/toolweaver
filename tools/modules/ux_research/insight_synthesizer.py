"""Tool for synthesizing insights from multiple sources"""

from typing import Dict, List, Any, Optional
from tools.common.base_tool import BaseTool, ValidationError
from tools.common.memory import MemoryType
import asyncio
from collections import defaultdict
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

class InsightSynthesizer(BaseTool):
    def __init__(self):
        super().__init__("insight_synthesizer")
        self.insights = []
        
    async def execute(self, min_confidence: float = 0.8) -> Dict[str, Any]:
        """Execute insight synthesis"""
        if not self._validate_input({"min_confidence": min_confidence}):
            raise ValidationError("Invalid input parameters")
            
        return await self.synthesize(min_confidence)
        
    async def synthesize(self, min_confidence: float = 0.8) -> Dict[str, Any]:
        """Synthesize insights from all available sources"""
        
        # Collect insights using callback
        async def search_callback(result):
            if result.score > min_confidence:
                self.insights.append(result.data)
        
        self.insights = []
        await self.memory.search_with_callback(
            query={"type": "insight"},
            callback=search_callback,
            min_score=min_confidence
        )
        
        if not self.insights:
            return self._create_empty_synthesis()
        
        # Process and synthesize insights
        synthesis = {
            "type": "insight_synthesis",
            "timestamp": datetime.now().isoformat(),
            "key_findings": await self._extract_key_findings(),
            "recommendations": self._generate_recommendations(),
            "priority_areas": self._identify_priority_areas(),
            "confidence_scores": self._calculate_confidence_scores(),
            "metadata": {
                "source_count": len(self.insights),
                "insight_count": self._count_total_insights()
            }
        }
        
        # Store synthesis in working memory
        await self.store_result(synthesis)
        
        # If synthesis is comprehensive, store in long-term memory
        if len(synthesis["key_findings"]) >= 5:
            await self.memory.memory_system.store_compressed(
                MemoryType.LONG_TERM,
                f"synthesis_{self.tool_id}_{datetime.now().strftime('%Y%m%d')}",
                synthesis
            )
        
        return synthesis
    
    async def _extract_key_findings(self) -> List[Dict]:
        """Extract and consolidate key findings"""
        findings = []
        themes = defaultdict(list)
        
        # Group insights by theme
        for insight_data in self.insights:
            for insight in insight_data.get("insights", []):
                for theme in insight_data.get("themes", []):
                    themes[theme].append(insight)
        
        # Process each theme
        for theme, theme_insights in themes.items():
            # Group similar insights
            grouped_insights = self._group_similar_insights(theme_insights)
            
            # Create consolidated findings
            for group in grouped_insights:
                finding = self._consolidate_insight_group(group, theme)
                if finding:
                    findings.append(finding)
        
        # Sort by confidence and relevance
        findings.sort(key=lambda x: (-x["confidence"], -x["relevance"]))
        return findings
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze patterns and trends
        patterns = self._analyze_insight_patterns()
        
        for pattern in patterns:
            if pattern["strength"] > 0.7:  # Strong patterns only
                recommendation = {
                    "title": self._generate_recommendation_title(pattern),
                    "description": self._generate_recommendation_description(pattern),
                    "priority": self._calculate_priority(pattern),
                    "impact": self._estimate_impact(pattern),
                    "effort": self._estimate_effort(pattern),
                    "supporting_insights": pattern["supporting_insights"]
                }
                recommendations.append(recommendation)
        
        # Sort by priority and impact
        recommendations.sort(key=lambda x: (-x["priority"], -x["impact"]))
        return recommendations
    
    def _identify_priority_areas(self) -> List[Dict]:
        """Identify high-priority areas for attention"""
        areas = defaultdict(lambda: {
            "mentions": 0,
            "sentiment_sum": 0,
            "insights": [],
            "urgency": 0
        })
        
        # Analyze insights for priority areas
        for insight_data in self.insights:
            for insight in insight_data.get("insights", []):
                area = self._determine_area(insight)
                if area:
                    areas[area]["mentions"] += 1
                    areas[area]["sentiment_sum"] += self._get_sentiment_score(insight)
                    areas[area]["insights"].append(insight)
                    areas[area]["urgency"] = max(
                        areas[area]["urgency"],
                        self._calculate_urgency(insight)
                    )
        
        # Convert to list and calculate scores
        priority_areas = []
        for area_name, data in areas.items():
            if data["mentions"] >= 2:  # Minimum mention threshold
                priority_areas.append({
                    "name": area_name,
                    "score": self._calculate_area_score(data),
                    "sentiment": data["sentiment_sum"] / data["mentions"],
                    "urgency": data["urgency"],
                    "insight_count": data["mentions"],
                    "key_insights": self._select_key_insights(data["insights"])
                })
        
        # Sort by score and urgency
        priority_areas.sort(key=lambda x: (-x["score"], -x["urgency"]))
        return priority_areas
    
    def _calculate_confidence_scores(self) -> Dict[str, float]:
        """Calculate confidence scores for different aspects"""
        return {
            "overall": self._calculate_overall_confidence(),
            "findings": self._calculate_findings_confidence(),
            "recommendations": self._calculate_recommendations_confidence(),
            "priorities": self._calculate_priorities_confidence()
        }
    
    def _group_similar_insights(self, insights: List[Dict]) -> List[List[Dict]]:
        """Group similar insights together"""
        groups = []
        used = set()
        
        for i, insight in enumerate(insights):
            if i in used:
                continue
                
            group = [insight]
            used.add(i)
            
            # Compare with remaining insights
            for j, other in enumerate(insights[i+1:], i+1):
                if j not in used and self._are_insights_similar(insight, other):
                    group.append(other)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_insights_similar(self, insight1: Dict, insight2: Dict) -> bool:
        """Check if two insights are similar"""
        text1 = insight1.get("text", "")
        text2 = insight2.get("text", "")
        
        # Calculate text similarity
        blob1 = TextBlob(text1)
        blob2 = TextBlob(text2)
        
        # Compare word sets
        words1 = set(word.lower() for word in blob1.words)
        words2 = set(word.lower() for word in blob2.words)
        
        # Calculate Jaccard similarity
        similarity = len(words1 & words2) / len(words1 | words2)
        
        return similarity > 0.3
    
    def _consolidate_insight_group(self, group: List[Dict], theme: str) -> Optional[Dict]:
        """Consolidate a group of similar insights"""
        if not group:
            return None
            
        # Get the most representative insight
        main_insight = max(group, key=lambda x: x.get("score", 0))
        
        return {
            "text": main_insight["text"],
            "theme": theme,
            "frequency": len(group),
            "confidence": self._calculate_group_confidence(group),
            "relevance": self._calculate_group_relevance(group),
            "supporting_insights": [i["text"] for i in group if i != main_insight],
            "entities": self._merge_entities([i.get("entities", []) for i in group])
        }
    
    def _create_empty_synthesis(self) -> Dict[str, Any]:
        """Create an empty synthesis result"""
        return {
            "type": "insight_synthesis",
            "timestamp": datetime.now().isoformat(),
            "key_findings": [],
            "recommendations": [],
            "priority_areas": [],
            "confidence_scores": {
                "overall": 0.0,
                "findings": 0.0,
                "recommendations": 0.0,
                "priorities": 0.0
            },
            "metadata": {
                "source_count": 0,
                "insight_count": 0
            }
        }
    
    def _count_total_insights(self) -> int:
        """Count total number of insights"""
        return sum(
            len(data.get("insights", []))
            for data in self.insights
        ) 
    
    def _analyze_insight_patterns(self) -> List[Dict]:
        """Analyze patterns in insights"""
        patterns = []
        
        # Extract key elements
        elements = self._extract_pattern_elements()
        
        # Find co-occurring elements
        co_occurrences = self._find_co_occurrences(elements)
        
        # Identify strong patterns
        for element_type, occurrences in co_occurrences.items():
            for items, data in occurrences.items():
                if data["frequency"] >= self.config.config["analysis"]["min_frequency"]:
                    pattern = {
                        "type": element_type,
                        "elements": items,
                        "frequency": data["frequency"],
                        "strength": self._calculate_pattern_strength(data),
                        "supporting_insights": data["insights"],
                        "sentiment_trend": self._analyze_sentiment_trend(data["insights"])
                    }
                    patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: (-x["strength"], -x["frequency"]))
    
    def _extract_pattern_elements(self) -> Dict[str, List[Dict]]:
        """Extract elements for pattern analysis"""
        elements = {
            "themes": [],
            "entities": [],
            "keywords": [],
            "sentiments": []
        }
        
        for insight_data in self.insights:
            for insight in insight_data.get("insights", []):
                # Add themes
                elements["themes"].extend(
                    {"value": theme, "insight": insight}
                    for theme in insight_data.get("themes", [])
                )
                
                # Add entities
                elements["entities"].extend(
                    {"value": entity["text"], "type": entity["label"], "insight": insight}
                    for entity in insight.get("entities", [])
                )
                
                # Add keywords
                elements["keywords"].extend(
                    {"value": keyword, "insight": insight}
                    for keyword in insight.get("keywords", [])
                )
                
                # Add sentiment
                if "sentiment" in insight_data:
                    elements["sentiments"].append({
                        "value": insight_data["sentiment"]["assessment"],
                        "insight": insight
                    })
        
        return elements
    
    def _find_co_occurrences(self, elements: Dict[str, List[Dict]]) -> Dict:
        """Find co-occurring elements"""
        co_occurrences = defaultdict(lambda: defaultdict(lambda: {
            "frequency": 0,
            "insights": set(),
            "contexts": []
        }))
        
        # Analyze co-occurrences within each element type
        for element_type, items in elements.items():
            for i, item1 in enumerate(items):
                for item2 in items[i+1:]:
                    if self._are_elements_related(item1, item2):
                        key = tuple(sorted([item1["value"], item2["value"]]))
                        co_occurrences[element_type][key]["frequency"] += 1
                        co_occurrences[element_type][key]["insights"].update([
                            item1["insight"]["text"],
                            item2["insight"]["text"]
                        ])
                        co_occurrences[element_type][key]["contexts"].append({
                            "element1": item1,
                            "element2": item2
                        })
        
        return co_occurrences
    
    def _calculate_pattern_strength(self, pattern_data: Dict) -> float:
        """Calculate pattern strength score"""
        # Base strength from frequency
        base_strength = min(pattern_data["frequency"] / 10, 1.0)
        
        # Context consistency
        context_score = self._evaluate_context_consistency(pattern_data["contexts"])
        
        # Support strength
        support_score = len(pattern_data["insights"]) / self._count_total_insights()
        
        # Weighted combination
        return (base_strength * 0.4 + context_score * 0.3 + support_score * 0.3)
    
    def _evaluate_context_consistency(self, contexts: List[Dict]) -> float:
        """Evaluate consistency of pattern contexts"""
        if not contexts:
            return 0.0
        
        # Analyze sentiment consistency
        sentiment_consistency = self._calculate_sentiment_consistency(contexts)
        
        # Analyze temporal consistency
        temporal_consistency = self._calculate_temporal_consistency(contexts)
        
        # Analyze source diversity
        source_diversity = self._calculate_source_diversity(contexts)
        
        return (sentiment_consistency + temporal_consistency + source_diversity) / 3
    
    def _generate_recommendation_title(self, pattern: Dict) -> str:
        """Generate recommendation title from pattern"""
        element_type = pattern["type"]
        elements = pattern["elements"]
        
        if element_type == "themes":
            return f"Address {' and '.join(elements)} improvements"
        elif element_type == "entities":
            return f"Optimize {' & '.join(elements)} integration"
        else:
            return f"Focus on {' - '.join(elements)} enhancement"
    
    def _generate_recommendation_description(self, pattern: Dict) -> str:
        """Generate detailed recommendation description"""
        description = []
        
        # Add context
        description.append(f"Based on analysis of {pattern['frequency']} related insights")
        
        # Add main recommendation
        description.append(self._generate_main_recommendation(pattern))
        
        # Add supporting evidence
        evidence = self._summarize_supporting_evidence(pattern)
        if evidence:
            description.append("\nSupporting evidence:")
            description.extend(f"- {point}" for point in evidence)
        
        return "\n".join(description)
    
    def _calculate_priority(self, pattern: Dict) -> float:
        """Calculate recommendation priority"""
        weights = self.config.config["analysis"]["priority_weights"]
        
        sentiment_score = self._get_sentiment_impact(pattern)
        frequency_score = pattern["frequency"] / self._count_total_insights()
        urgency_score = self._calculate_urgency_score(pattern)
        
        return (
            weights["sentiment"] * sentiment_score +
            weights["frequency"] * frequency_score +
            weights["urgency"] * urgency_score
        )
    
    def _estimate_impact(self, pattern: Dict) -> float:
        """Estimate potential impact of recommendation"""
        # Base impact from pattern strength
        base_impact = pattern["strength"]
        
        # Adjust for scope
        scope_multiplier = self._calculate_scope_multiplier(pattern)
        
        # Adjust for current sentiment
        sentiment_multiplier = self._calculate_sentiment_multiplier(pattern)
        
        return base_impact * scope_multiplier * sentiment_multiplier
    
    def _estimate_effort(self, pattern: Dict) -> float:
        """Estimate implementation effort"""
        # Base effort from complexity
        base_effort = self._calculate_complexity(pattern)
        
        # Adjust for dependencies
        dependency_factor = self._analyze_dependencies(pattern)
        
        # Adjust for scope
        scope_factor = self._calculate_scope_factor(pattern)
        
        return base_effort * dependency_factor * scope_factor
    
    def _merge_entities(self, entity_lists: List[List[Dict]]) -> List[Dict]:
        """Merge entity lists with deduplication"""
        merged = {}
        
        for entities in entity_lists:
            for entity in entities:
                key = (entity["text"].lower(), entity["label"])
                if key not in merged:
                    merged[key] = entity
                else:
                    # Update frequency if tracked
                    merged[key]["frequency"] = merged[key].get("frequency", 1) + 1
        
        return list(merged.values())
    
    def _calculate_group_confidence(self, group: List[Dict]) -> float:
        """Calculate confidence score for insight group"""
        # Base confidence from individual scores
        base_confidence = np.mean([
            insight.get("score", 0.5)
            for insight in group
        ])
        
        # Adjust for group size
        size_factor = min(len(group) / 5, 1.0)
        
        # Adjust for consistency
        consistency = self._calculate_group_consistency(group)
        
        return (base_confidence * 0.4 + size_factor * 0.3 + consistency * 0.3)
    
    def _calculate_group_relevance(self, group: List[Dict]) -> float:
        """Calculate relevance score for insight group"""
        # Consider recency
        recency_score = self._calculate_recency_score(group)
        
        # Consider impact
        impact_score = self._calculate_impact_score(group)
        
        # Consider source quality
        source_score = self._calculate_source_quality(group)
        
        return (recency_score * 0.3 + impact_score * 0.4 + source_score * 0.3) 
    
    def _analyze_sentiment_trend(self, insights: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment trends in insights"""
        timestamps = []
        sentiments = []
        
        for insight in insights:
            if "timestamp" in insight and "sentiment" in insight:
                timestamps.append(datetime.fromisoformat(insight["timestamp"]))
                sentiments.append(insight["sentiment"]["polarity"])
        
        if not timestamps:
            return {"trend": "neutral", "confidence": 0.0}
        
        # Calculate trend
        trend_data = {
            "direction": self._calculate_trend_direction(timestamps, sentiments),
            "volatility": self._calculate_volatility(sentiments),
            "recent_sentiment": self._get_recent_sentiment(timestamps, sentiments),
            "confidence": self._calculate_trend_confidence(timestamps, sentiments)
        }
        
        return trend_data
    
    def _analyze_dependencies(self, pattern: Dict) -> float:
        """Analyze pattern dependencies and complexity"""
        dependencies = set()
        complexity_score = 0.0
        
        # Extract entities and their relationships
        for insight in pattern["supporting_insights"]:
            entities = self._extract_related_entities(insight)
            dependencies.update(entities)
            
            # Calculate relationship complexity
            complexity_score += self._calculate_relationship_complexity(entities)
        
        # Normalize complexity score
        if pattern["supporting_insights"]:
            complexity_score /= len(pattern["supporting_insights"])
        
        return 1.0 + (len(dependencies) * 0.2) + (complexity_score * 0.3)
    
    def _calculate_temporal_consistency(self, contexts: List[Dict]) -> float:
        """Calculate temporal consistency of insights"""
        if not contexts:
            return 0.0
        
        timestamps = []
        for context in contexts:
            for element in [context["element1"], context["element2"]]:
                if "timestamp" in element["insight"]:
                    timestamps.append(
                        datetime.fromisoformat(element["insight"]["timestamp"])
                    )
        
        if not timestamps:
            return 0.5  # Default when no temporal data
        
        # Calculate time span and frequency
        time_span = max(timestamps) - min(timestamps)
        days_span = time_span.days + (time_span.seconds / 86400)
        
        if days_span == 0:
            return 1.0  # All insights from same day
        
        # Calculate distribution evenness
        distribution_score = self._calculate_time_distribution(timestamps)
        
        # Calculate recency weight
        recency_score = self._calculate_recency_weight(timestamps)
        
        return (distribution_score * 0.6 + recency_score * 0.4)
    
    def _calculate_source_diversity(self, contexts: List[Dict]) -> float:
        """Calculate diversity of insight sources"""
        sources = set()
        total_sources = 0
        
        for context in contexts:
            for element in [context["element1"], context["element2"]]:
                source = element["insight"].get("source")
                if source:
                    sources.add(source)
                    total_sources += 1
        
        if total_sources == 0:
            return 0.5  # Default when no source data
        
        # Calculate diversity score
        unique_ratio = len(sources) / total_sources
        
        # Adjust for minimum source requirement
        if len(sources) < 2:
            unique_ratio *= 0.5
        
        return unique_ratio 