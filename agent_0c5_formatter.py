"""
Agent 0C-5: Formatter
Specialized agent for final text formatting and cleanup

Responsibility: Clean up spaces, punctuation, and formatting artifacts
Rules: 5 rules focused on text cleanup
"""

import re
from typing import Dict, List

class Agent_0C5_Formatter:
    """
    Performs final formatting and cleanup
    Part of the Controlled Language preprocessing pipeline
    """
    
    RULES = [
        # RULE 1: Remove double spaces
        {
            'name': 'CLEANUP_DOUBLE_SPACE',
            'pattern': r'  +',
            'replacement': r' ',
            'description': 'Remove double spaces'
        },
        
        # RULE 2: Remove space before punctuation
        {
            'name': 'CLEANUP_SPACE_BEFORE_PUNCT',
            'pattern': r' ([。、])',
            'replacement': r'\1',
            'description': 'Remove space before Japanese punctuation'
        },
        
        # RULE 3: Remove double periods
        {
            'name': 'CLEANUP_DOUBLE_PERIOD',
            'pattern': r'。。+',
            'replacement': r'。',
            'description': 'Remove duplicate periods'
        },
        
        # RULE 4: Fix comma before period
        {
            'name': 'CLEANUP_COMMA_PERIOD',
            'pattern': r'、。',
            'replacement': r'。',
            'description': 'Fix comma before period error'
        },
        
        # RULE 5: Remove trailing spaces
        {
            'name': 'CLEANUP_TRAILING_SPACE',
            'pattern': r' +$',
            'replacement': r'',
            'description': 'Remove trailing spaces'
        }
    ]
    
    @classmethod
    def process(cls, text: str) -> Dict:
        """
        Process text through formatting rules
        
        Args:
            text: Input text
            
        Returns:
            {
                'text': processed text,
                'rules_applied': list of rule names applied
            }
        """
        result = text
        rules_applied = []
        
        for rule in cls.RULES:
            before = result
            result = re.sub(rule['pattern'], rule['replacement'], result, flags=re.MULTILINE)
            if result != before:
                rules_applied.append(rule['name'])
        
        return {
            'text': result,
            'rules_applied': rules_applied
        }
