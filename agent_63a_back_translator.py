"""
Agent 63-A: Back-Translator
Specialized agent for performing reverse translation (target → source)

Responsibility: Execute back-translation only
Part of the Back-Translation Validation pipeline
"""

from typing import Dict, Any

class Agent_63A_Back_Translator:
    """
    Performs back-translation from target language to source language
    Part of the quality validation system
    """
    
    def __init__(self, translator_instance):
        """
        Initialize with reference to main translator
        
        Args:
            translator_instance: Instance of USI17_V22_1_Translator
        """
        self.translator = translator_instance
    
    def back_translate(self, translation: str, target_lang: str, source_lang: str) -> Dict:
        """
        Back-translate from target language to source language
        
        Args:
            translation: Translation to validate
            target_lang: Target language code (e.g., 'en')
            source_lang: Source language code (e.g., 'ja')
            
        Returns:
            {
                'back_translation': back-translated text,
                'success': True/False,
                'error': error message if failed
            }
        """
        try:
            # Perform reverse translation
            result = self.translator.translate(
                source_text=translation,
                source_lang=target_lang,
                target_langs=[source_lang],
                input_format='text',
                preserve_tags=False,
                english_first=False
            )
            
            back_translated_text = result['targets'][source_lang]
            
            return {
                'back_translation': back_translated_text,
                'success': True
            }
            
        except Exception as e:
            return {
                'back_translation': '',
                'success': False,
                'error': str(e)
            }
