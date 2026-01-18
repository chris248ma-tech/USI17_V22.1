"""
Agent 63-D: Review Flagger
Specialized agent for determining which translations require human review

Responsibility: Flag low-confidence translations for review
Part of the Back-Translation Validation pipeline
"""

from typing import Dict

class Agent_63D_Review_Flagger:
    """
    Determines which translations require human review based on confidence
    Part of the quality validation system
    """
    
    # Review threshold (flag if below this)
    REVIEW_THRESHOLD = 0.85
    
    @classmethod
    def should_flag(cls, confidence_level: str, similarity_score: float) -> Dict:
        """
        Determine if translation should be flagged for review
        
        Flagging criteria:
        - Confidence is 'low'
        - Similarity score < 0.85
        
        Args:
            confidence_level: Confidence level from Agent 63-C
            similarity_score: Similarity score from Agent 63-B
            
        Returns:
            {
                'flag_for_review': True/False,
                'reason': explanation why flagged,
                'priority': 'high' | 'medium' | 'low',
                'recommended_action': suggested next step
            }
        """
        flag = similarity_score < cls.REVIEW_THRESHOLD
        
        if flag:
            # Determine priority based on how low the score is
            if similarity_score < 0.70:
                priority = 'high'
                reason = f"Very low similarity ({similarity_score:.2f}) - significant semantic drift detected"
                action = "IMMEDIATE REVIEW REQUIRED: Manual review and retranslation recommended"
            elif similarity_score < 0.80:
                priority = 'medium'
                reason = f"Low similarity ({similarity_score:.2f}) - potential semantic issues"
                action = "Review recommended: Check for accuracy and completeness"
            else:
                priority = 'low'
                reason = f"Below threshold similarity ({similarity_score:.2f}) - minor variations detected"
                action = "Optional review: Translation likely acceptable but verify key terms"
        else:
            priority = 'none'
            reason = f"Similarity within acceptable range ({similarity_score:.2f})"
            action = "No review needed: Translation has high confidence"
        
        return {
            'flag_for_review': flag,
            'reason': reason,
            'priority': priority,
            'recommended_action': action
        }
    
    @classmethod
    def get_threshold(cls) -> float:
        """Get the review threshold value"""
        return cls.REVIEW_THRESHOLD
