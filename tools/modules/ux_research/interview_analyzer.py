"""Tool for analyzing user interview transcripts"""

from typing import Dict, List, Any
from tools.common.base_tool import BaseTool, ValidationError
import re
from textblob import TextBlob
import spacy
from collections import Counter

class InterviewAnalyzer(BaseTool):
    def __init__(self):
        super().__init__("interview_analyzer")
        self.nlp = spacy.load("en_core_web_sm")
        
    async def execute(self, transcript: str) -> Dict[str, Any]:
        """Execute interview analysis"""
        try:
            if not self._validate_input({"transcript": transcript}):
                raise ValidationError("Invalid transcript format")
                
            return await self.analyze_transcript(transcript)
            
        except Exception as e:
            raise ValidationError(f"Analysis failed: {str(e)}")
    
    async def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """Analyze interview transcript and extract insights"""
        
        # Get historical patterns from memory
        context = await self.get_context()
        known_patterns = context.get('historical', {}).get('patterns', [])
        
        # Process transcript
        doc = self.nlp(transcript)
        
        # Analyze transcript
        insights = self._extract_insights(doc, known_patterns)
        sentiment = self._analyze_sentiment(transcript)
        themes = self._identify_themes(doc)
        
        result = {
            "type": "interview_analysis",
            "insights": insights,
            "sentiment": sentiment,
            "themes": themes,
            "source": "interview_transcript",
            "metadata": {
                "word_count": len(doc),
                "sentence_count": len(list(doc.sents))
            }
        }
        
        # Store results in memory
        await self.store_result(result)
        
        return result
    
    def _extract_insights(self, doc: spacy.tokens.Doc, known_patterns: List[str]) -> List[Dict]:
        """Extract insights from processed text"""
        insights = []
        
        # Extract key sentences based on patterns
        for sent in doc.sents:
            score = self._calculate_insight_score(sent, known_patterns)
            if score > self.config.config["validation"]["confidence_threshold"]:
                insights.append({
                    "text": sent.text,
                    "score": score,
                    "entities": self._extract_entities(sent),
                    "keywords": self._extract_keywords(sent)
                })
                
        return insights
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
            "assessment": self._get_sentiment_label(blob.sentiment.polarity)
        }
    
    def _identify_themes(self, doc: spacy.tokens.Doc) -> List[str]:
        """Identify themes using NLP"""
        # Extract noun phrases and named entities
        phrases = [chunk.text for chunk in doc.noun_chunks]
        entities = [ent.text for ent in doc.ents]
        
        # Count frequencies
        phrase_counter = Counter(phrases)
        entity_counter = Counter(entities)
        
        # Combine and get top themes
        themes = []
        for item, count in (phrase_counter + entity_counter).most_common(10):
            if count >= 2:  # Minimum frequency threshold
                themes.append(item)
                
        return themes
    
    def _calculate_insight_score(self, sent: spacy.tokens.Span, patterns: List[str]) -> float:
        """Calculate insight relevance score"""
        # Implement scoring logic
        return 0.8
    
    def _extract_entities(self, sent: spacy.tokens.Span) -> List[Dict]:
        """Extract named entities from sentence"""
        return [{"text": ent.text, "label": ent.label_} for ent in sent.ents]
    
    def _extract_keywords(self, sent: spacy.tokens.Span) -> List[str]:
        """Extract keywords from sentence"""
        return [token.text for token in sent 
                if not token.is_stop and token.is_alpha]
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert sentiment polarity to label"""
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        return "neutral" 