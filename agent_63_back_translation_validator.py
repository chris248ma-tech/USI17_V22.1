"""
Agent 63: Back-Translation Validator (Master Coordinator)
Coordinates 4 specialized sub-agents for translation quality validation

Sub-agents:
- Agent 63-A: Back-Translator (reverse translation)
- Agent 63-B: Similarity Calculator (Jaccard similarity)
- Agent 63-C: Confidence Assessor (confidence levels)
- Agent 63-D: Review Flagger (review decisions)

Total: 5 agents (1 coordinator + 4 specialized)
Expected accuracy gain: 2-3%
"""

from typing import Dict
from agent_63a_back_translator import Agent_63A_Back_Translator
from agent_63b_similarity_calculator import Agent_63B_Similarity_Calculator
from agent_63c_confidence_assessor import Agent_63C_Confidence_Assessor
from agent_63d_review_flagger import Agent_63D_Review_Flagger

class Agent_63_Back_Translation_Validator:
    """
    Master coordinator for back-translation validation
    
    Architecture: 1 coordinator + 4 specialized sub-agents
    Philosophy: Many specialized agents > One monolithic agent
    
    Validation pipeline:
    1. Agent 63-A: Back-translate target → source
    2. Agent 63-B: Calculate similarity (original vs back-translation)
    3. Agent 63-C: Assess confidence level
    4. Agent 63-D: Flag for review if needed
    """
    
    def __init__(self, translator_instance):
        """
        Initialize master validator with translator reference
        
        Args:
            translator_instance: Instance of USI17_V22_1_Translator
        """
        # Initialize sub-agents
        self.agent_63a = Agent_63A_Back_Translator(translator_instance)
        self.agent_63b = Agent_63B_Similarity_Calculator()
        self.agent_63c = Agent_63C_Confidence_Assessor()
        self.agent_63d = Agent_63D_Review_Flagger()
        
        self.sub_agents = [
            ('63-A', 'Back-Translator'),
            ('63-B', 'Similarity Calculator'),
            ('63-C', 'Confidence Assessor'),
            ('63-D', 'Review Flagger')
        ]
    
    def validate(self, source_text: str, translation: str, 
                 source_lang: str, target_lang: str) -> Dict:
        """
        Validate translation quality using 4-phase specialized agent pipeline
        
        Args:
            source_text: Original source text
            translation: Translation to validate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            {
                'back_translation': back-translated text,
                'similarity_score': 0.0-1.0,
                'confidence': 'high' | 'medium' | 'low',
                'flag_for_review': True/False,
                'agent_breakdown': per-agent statistics,
                'recommended_action': suggested next step
            }
        """
        print(f"🔄 Agent 63: Validating {target_lang} → {source_lang}...")
        
        agent_breakdown = {}
        
        # PHASE 1: Agent 63-A - Back-Translation
        print(f"  ✓ Agent 63-A: Back-translating...")
        back_result = self.agent_63a.back_translate(translation, target_lang, source_lang)
        
        if not back_result['success']:
            # Back-translation failed
            return {
                'back_translation': '',
                'similarity_score': 0.0,
                'confidence': 'error',
                'flag_for_review': True,
                'error': back_result.get('error', 'Unknown error'),
                'agent_breakdown': {'63-A': {'status': 'failed', 'error': back_result.get('error')}}
            }
        
        back_translation = back_result['back_translation']
        agent_breakdown['63-A'] = {'status': 'success', 'back_translation_length': len(back_translation)}
        
        # PHASE 2: Agent 63-B - Similarity Calculation
        print(f"  ✓ Agent 63-B: Calculating similarity...")
        similarity_result = self.agent_63b.calculate(source_text, back_translation)
        similarity_score = similarity_result['similarity_score']
        agent_breakdown['63-B'] = {
            'status': 'success',
            'similarity_score': similarity_score,
            'word_overlap': similarity_result['word_overlap'],
            'total_unique_words': similarity_result['total_unique_words']
        }
        
        # PHASE 3: Agent 63-C - Confidence Assessment
        print(f"  ✓ Agent 63-C: Assessing confidence...")
        confidence_result = self.agent_63c.assess(similarity_score)
        confidence = confidence_result['confidence']
        agent_breakdown['63-C'] = {
            'status': 'success',
            'confidence': confidence,
            'confidence_percentage': confidence_result['confidence_percentage'],
            'quality_assessment': confidence_result['quality_assessment']
        }
        
        # PHASE 4: Agent 63-D - Review Flagging
        print(f"  ✓ Agent 63-D: Determining review necessity...")
        flag_result = self.agent_63d.should_flag(confidence, similarity_score)
        flag_for_review = flag_result['flag_for_review']
        agent_breakdown['63-D'] = {
            'status': 'success',
            'flag_for_review': flag_for_review,
            'priority': flag_result['priority'],
            'reason': flag_result['reason']
        }
        
        # Final status
        if flag_for_review:
            print(f"⚠️  Agent 63: LOW CONFIDENCE ({similarity_score:.2f}) - Flagged for review [{flag_result['priority']} priority]")
        else:
            print(f"✅ Agent 63: HIGH CONFIDENCE ({similarity_score:.2f}) - No review needed")
        
        return {
            'back_translation': back_translation,
            'similarity_score': similarity_score,
            'confidence': confidence,
            'confidence_percentage': confidence_result['confidence_percentage'],
            'quality_assessment': confidence_result['quality_assessment'],
            'flag_for_review': flag_for_review,
            'priority': flag_result['priority'],
            'reason': flag_result['reason'],
            'recommended_action': flag_result['recommended_action'],
            'agent_breakdown': agent_breakdown
        }
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the agent system
        
        Returns:
            {
                'total_agents': 5 (1 coordinator + 4 specialized),
                'agents': [...agent details...]
            }
        """
        return {
            'total_agents': 5,  # 1 coordinator + 4 sub-agents
            'coordinator': 'Agent 63',
            'sub_agents': [
                {'id': '63-A', 'name': 'Back-Translator', 'function': 'Reverse translation'},
                {'id': '63-B', 'name': 'Similarity Calculator', 'function': 'Jaccard similarity'},
                {'id': '63-C', 'name': 'Confidence Assessor', 'function': 'Confidence levels'},
                {'id': '63-D', 'name': 'Review Flagger', 'function': 'Review decisions'}
            ],
            'thresholds': {
                'high_confidence': Agent_63C_Confidence_Assessor.HIGH_CONFIDENCE_THRESHOLD,
                'medium_confidence': Agent_63C_Confidence_Assessor.MEDIUM_CONFIDENCE_THRESHOLD,
                'review_threshold': Agent_63D_Review_Flagger.REVIEW_THRESHOLD
            }
        }
