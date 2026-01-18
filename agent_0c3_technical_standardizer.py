"""
Agent 0C-3: Technical Standardizer
Specialized agent for standardizing technical terminology and phrasing

Responsibility: Ensure consistent technical expression patterns
Rules: 15 rules focused on technical standardization
"""

import re
from typing import Dict, List

class Agent_0C3_Technical_Standardizer:
    """
    Standardizes technical phrasing for consistent translation
    Part of the Controlled Language preprocessing pipeline
    """
    
    RULES = [
        # RULES 1-5: Standardize attribute expressions
        {
            'name': 'STANDARDIZE_優れた性能',
            'pattern': r'優れた(性能|耐久性|品質|精度)',
            'replacement': r'\1に優れています',
            'description': 'Standardize "優れた X" to "X に優れています"'
        },
        {
            'name': 'STANDARDIZE_高い性能',
            'pattern': r'高い(性能|耐久性|品質|精度)',
            'replacement': r'\1が高いです',
            'description': 'Standardize "高い X" to "X が高いです"'
        },
        {
            'name': 'STANDARDIZE_良好な',
            'pattern': r'良好な(状態|品質|性能)',
            'replacement': r'\1が良好です',
            'description': 'Standardize "良好な X" to "X が良好です"'
        },
        {
            'name': 'STANDARDIZE_有する',
            'pattern': r'(.+?)を有する',
            'replacement': r'\1があります',
            'description': 'Simplify "を有する" to "があります"'
        },
        {
            'name': 'STANDARDIZE_備える',
            'pattern': r'(.+?)を備える',
            'replacement': r'\1を持っています',
            'description': 'Simplify "を備える" to "を持っています"'
        },
        
        # RULES 6-10: Standardize verb endings
        {
            'name': 'STANDARDIZE_である',
            'pattern': r'である([。、])',
            'replacement': r'です\1',
            'description': 'Standardize "である" to "です"'
        },
        {
            'name': 'STANDARDIZE_となる',
            'pattern': r'となる([。、])',
            'replacement': r'になります\1',
            'description': 'Standardize "となる" to "になります"'
        },
        {
            'name': 'STANDARDIZE_行う',
            'pattern': r'行う([。、])',
            'replacement': r'します\1',
            'description': 'Standardize "行う" to "します"'
        },
        {
            'name': 'STANDARDIZE_なる',
            'pattern': r'なる([。、])',
            'replacement': r'なります\1',
            'description': 'Standardize "なる" to "なります"'
        },
        {
            'name': 'STANDARDIZE_する',
            'pattern': r'する([。、])',
            'replacement': r'します\1',
            'description': 'Standardize "する" to "します"'
        },
        
        # RULES 11-15: Standardize technical term formats
        {
            'name': 'FORMAT_範囲',
            'pattern': r'(.+?)から(.+?)までの範囲',
            'replacement': r'\1〜\2の範囲',
            'description': 'Standardize range format'
        },
        {
            'name': 'FORMAT_以上以下',
            'pattern': r'(.+?)以上(.+?)以下',
            'replacement': r'\1〜\2',
            'description': 'Standardize "以上〜以下" format'
        },
        {
            'name': 'FORMAT_または',
            'pattern': r'または',
            'replacement': r'か',
            'description': 'Simplify "または" to "か"'
        },
        {
            'name': 'FORMAT_及び',
            'pattern': r'及び',
            'replacement': r'と',
            'description': 'Simplify "及び" to "と"'
        },
        {
            'name': 'FORMAT_並びに',
            'pattern': r'並びに',
            'replacement': r'と',
            'description': 'Simplify "並びに" to "と"'
        }
    ]
    
    @classmethod
    def process(cls, text: str) -> Dict:
        """
        Process text through technical standardization rules
        
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
