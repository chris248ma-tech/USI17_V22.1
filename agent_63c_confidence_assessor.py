"""
Agent 63-C: Confidence Assessor
Specialized agent for assessing translation confidence based on similarity

Responsibility: Map similarity scores to confidence levels
Part of the Back-Translation Validation pipeline
"""

from typing import Dict

class Agent_63C_Confidence_Assessor:
    """
    Assesses translation confidence based on back-translation similarity
    Part of the quality validation system
    """
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.90
    MEDIUM_CONFIDENCE_THRESHOLD = 0.85
    
    @classmethod
    def assess(cls, similarity_score: float) -> Dict:
        """
        Assess confidence level based on similarity score
        
        Thresholds:
        - 0.90-1.0: HIGH confidence
        - 0.85-0.89: MEDIUM confidence
        - 0.00-0.84: LOW confidence
        
        Args:
            similarity_score: Similarity score from Agent 63-B
            
        Returns:
            {
                'confidence': 'high' | 'medium' | 'low',
                'confidence_percentage': 0-100,
                'quality_assessment': descriptive text
            }
        """
        if similarity_score >= cls.HIGH_CONFIDENCE_THRESHOLD:
            confidence = 'high'
            quality = 'Excellent translation quality'
        elif similarity_score >= cls.MEDIUM_CONFIDENCE_THRESHOLD:
            confidence = 'medium'
            quality = 'Good translation quality with minor variations'
        else:
            confidence = 'low'
            quality = 'Translation may have significant semantic drift'
        
        confidence_percentage = similarity_score * 100
        
        return {
            'confidence': confidence,
            'confidence_percentage': confidence_percentage,
            'quality_assessment': quality,
            'similarity_score': similarity_score
        }
    
    @classmethod
    def get_thresholds(cls) -> Dict:
        """
        Get confidence threshold configuration
        
        Returns:
            Threshold values
        """
        return {
            'high': cls.HIGH_CONFIDENCE_THRESHOLD,
            'medium': cls.MEDIUM_CONFIDENCE_THRESHOLD,
            'low': 0.0
        }
