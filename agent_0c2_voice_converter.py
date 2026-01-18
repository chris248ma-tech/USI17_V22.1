"""
Agent 0C-2: Voice Converter
Specialized agent for converting passive voice to active voice

Responsibility: Convert passive constructions to active for clearer meaning
Rules: 5 rules focused on voice conversion
"""

import re
from typing import Dict, List

class Agent_0C2_Voice_Converter:
    """
    Converts passive voice to active voice in Japanese technical text
    Part of the Controlled Language preprocessing pipeline
    """
    
    RULES = [
        # RULE 1: 調整される → 調整します
        {
            'name': 'ACTIVE_調整される',
            'pattern': r'(.+?)が調整される',
            'replacement': r'\1を調整します',
            'description': 'Convert passive "調整される" to active "調整します"'
        },
        
        # RULE 2: 使用される → 使用します
        {
            'name': 'ACTIVE_使用される',
            'pattern': r'(.+?)が使用される',
            'replacement': r'\1を使用します',
            'description': 'Convert passive "使用される" to active "使用します"'
        },
        
        # RULE 3: 設定される → 設定します
        {
            'name': 'ACTIVE_設定される',
            'pattern': r'(.+?)が設定される',
            'replacement': r'\1を設定します',
            'description': 'Convert passive "設定される" to active "設定します"'
        },
        
        # RULE 4: 選択される → 選択します
        {
            'name': 'ACTIVE_選択される',
            'pattern': r'(.+?)が選択される',
            'replacement': r'\1を選択します',
            'description': 'Convert passive "選択される" to active "選択します"'
        },
        
        # RULE 5: 推奨される → 推奨します
        {
            'name': 'ACTIVE_推奨される',
            'pattern': r'(.+?)が推奨される',
            'replacement': r'\1を推奨します',
            'description': 'Convert passive "推奨される" to active "推奨します"'
        }
    ]
    
    @classmethod
    def process(cls, text: str) -> Dict:
        """
        Process text through voice conversion rules
        
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
