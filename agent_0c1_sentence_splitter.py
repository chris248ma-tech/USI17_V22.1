"""
Agent 0C-1: Sentence Splitter
Specialized agent for splitting complex compound sentences into simpler ones

Responsibility: Convert complex multi-clause sentences into simple single-clause sentences
Rules: 10 rules focused on sentence structure
"""

import re
from typing import Dict, List

class Agent_0C1_Sentence_Splitter:
    """
    Splits complex compound sentences into simpler structures
    Part of the Controlled Language preprocessing pipeline
    """
    
    RULES = [
        # RULE 1: Split であり、かつ constructions
        {
            'name': 'SPLIT_であり_かつ',
            'pattern': r'(.+?)であり、かつ(.+?)([。、])',
            'replacement': r'\1です。\2\3',
            'description': 'Split compound "であり、かつ" into separate sentences'
        },
        
        # RULE 2: Split でありながら constructions
        {
            'name': 'SPLIT_でありながら',
            'pattern': r'(.+?)でありながら(.+?)([。、])',
            'replacement': r'\1です。しかし、\2\3',
            'description': 'Split compound "でありながら" with contrast marker'
        },
        
        # RULE 3: Split であるため causal constructions
        {
            'name': 'SPLIT_であるため',
            'pattern': r'(.+?)であるため、?(.+?)([。、])',
            'replacement': r'\1です。そのため、\2\3',
            'description': 'Split causal "であるため" into separate sentences'
        },
        
        # RULE 4: Simplify において constructions
        {
            'name': 'SIMPLIFY_において',
            'pattern': r'(.+?)において(.+?)([。、])',
            'replacement': r'\1では\2\3',
            'description': 'Simplify "において" to simpler "では"'
        },
        
        # RULE 5: Simplify に関して constructions
        {
            'name': 'SIMPLIFY_に関して',
            'pattern': r'(.+?)に関して(.+?)([。、])',
            'replacement': r'\1について\2\3',
            'description': 'Simplify "に関して" to simpler "について"'
        },
        
        # RULE 6: Split at また connector
        {
            'name': 'CONNECTOR_また',
            'pattern': r'、また、',
            'replacement': r'。また、',
            'description': 'Split sentences at "また" connector'
        },
        
        # RULE 7: Split at さらに connector
        {
            'name': 'CONNECTOR_さらに',
            'pattern': r'、さらに、',
            'replacement': r'。さらに、',
            'description': 'Split sentences at "さらに" connector'
        },
        
        # RULE 8: Split at そして connector
        {
            'name': 'CONNECTOR_そして',
            'pattern': r'、そして、',
            'replacement': r'。そして、',
            'description': 'Split sentences at "そして" connector'
        },
        
        # RULE 9: Split at なお connector
        {
            'name': 'CONNECTOR_なお',
            'pattern': r'、なお、',
            'replacement': r'。なお、',
            'description': 'Split sentences at "なお" connector'
        },
        
        # RULE 10: Split at ただし connector
        {
            'name': 'CONNECTOR_ただし',
            'pattern': r'、ただし、',
            'replacement': r'。ただし、',
            'description': 'Split sentences at "ただし" connector'
        }
    ]
    
    @classmethod
    def process(cls, text: str) -> Dict:
        """
        Process text through sentence splitting rules
        
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
