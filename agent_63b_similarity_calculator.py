"""
Agent 63-B: Similarity Calculator
Specialized agent for calculating semantic similarity between texts

Responsibility: Compare original vs back-translated text
Part of the Back-Translation Validation pipeline
"""

from typing import Dict

class Agent_63B_Similarity_Calculator:
    """
    Calculates semantic similarity between two texts using Jaccard similarity
    Part of the quality validation system
    """
    
    @staticmethod
    def calculate(text1: str, text2: str) -> Dict:
        """
        Calculate semantic similarity between two texts
        
        Uses Jaccard similarity: intersection / union of word sets
        Score ranges from 0.0 (no similarity) to 1.0 (identical)
        
        Args:
            text1: First text (original source)
            text2: Second text (back-translation)
            
        Returns:
            {
                'similarity_score': 0.0-1.0,
                'word_overlap': number of common words,
                'total_unique_words': total unique words in both texts
            }
        """
        # Normalize texts to lowercase
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        similarity_score = intersection / union if union > 0 else 0.0
        
        return {
            'similarity_score': similarity_score,
            'word_overlap': intersection,
            'total_unique_words': union,
            'words_text1': len(words1),
            'words_text2': len(words2)
        }
    
    @staticmethod
    def calculate_character_similarity(text1: str, text2: str) -> float:
        """
        Alternative: Calculate character-level similarity (for Japanese)
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        chars1 = set(text1)
        chars2 = set(text2)
        
        intersection = len(chars1 & chars2)
        union = len(chars1 | chars2)
        
        return intersection / union if union > 0 else 0.0
