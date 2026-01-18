"""
Agent 0C-4: Redundancy Remover
Specialized agent for removing unnecessary modifiers and redundant expressions

Responsibility: Eliminate wordiness and redundancy
Rules: 15 rules focused on conciseness
"""

import re
from typing import Dict, List

class Agent_0C4_Redundancy_Remover:
    """
    Removes unnecessary words and redundant expressions
    Part of the Controlled Language preprocessing pipeline
    """
    
    RULES = [
        # RULES 1-5: Remove unnecessary modifiers
        {
            'name': 'REMOVE_非常に',
            'pattern': r'非常に',
            'replacement': r'',
            'description': 'Remove unnecessary intensifier "非常に"'
        },
        {
            'name': 'REMOVE_極めて',
            'pattern': r'極めて',
            'replacement': r'',
            'description': 'Remove unnecessary intensifier "極めて"'
        },
        {
            'name': 'REMOVE_大変',
            'pattern': r'大変',
            'replacement': r'',
            'description': 'Remove unnecessary intensifier "大変"'
        },
        {
            'name': 'REMOVE_かなり',
            'pattern': r'かなり',
            'replacement': r'',
            'description': 'Remove unnecessary intensifier "かなり"'
        },
        {
            'name': 'REMOVE_とても',
            'pattern': r'とても',
            'replacement': r'',
            'description': 'Remove unnecessary intensifier "とても"'
        },
        
        # RULES 6-10: Simplify verbose expressions
        {
            'name': 'SIMPLIFY_することができる',
            'pattern': r'することができる',
            'replacement': r'できます',
            'description': 'Simplify "することができる" to "できます"'
        },
        {
            'name': 'SIMPLIFY_することが可能',
            'pattern': r'することが可能',
            'replacement': r'できます',
            'description': 'Simplify "することが可能" to "できます"'
        },
        {
            'name': 'SIMPLIFY_という',
            'pattern': r'という([特徴|性質|性能])',
            'replacement': r'の\1',
            'description': 'Simplify "という" to "の"'
        },
        {
            'name': 'SIMPLIFY_といった',
            'pattern': r'といった',
            'replacement': r'のような',
            'description': 'Simplify "といった" to "のような"'
        },
        {
            'name': 'SIMPLIFY_によって',
            'pattern': r'によって',
            'replacement': r'で',
            'description': 'Simplify "によって" to "で"'
        },
        
        # RULES 11-15: Remove redundant verbalizations
        {
            'name': 'REDUNDANT_することで',
            'pattern': r'することで',
            'replacement': r'すると',
            'description': 'Simplify "することで" to "すると"'
        },
        {
            'name': 'REDUNDANT_した場合',
            'pattern': r'した場合',
            'replacement': r'すると',
            'description': 'Simplify "した場合" to "すると"'
        },
        {
            'name': 'REDUNDANT_する際',
            'pattern': r'する際',
            'replacement': r'する時',
            'description': 'Simplify "する際" to "する時"'
        },
        {
            'name': 'REDUNDANT_行った',
            'pattern': r'行った',
            'replacement': r'した',
            'description': 'Simplify "行った" to "した"'
        },
        {
            'name': 'REDUNDANT_実施する',
            'pattern': r'実施する',
            'replacement': r'する',
            'description': 'Simplify "実施する" to "する"'
        }
    ]
    
    @classmethod
    def process(cls, text: str) -> Dict:
        """
        Process text through redundancy removal rules
        
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
