"""
Agent 0C: Controlled Language Simplifier (Master Coordinator)
Coordinates 5 specialized sub-agents for text simplification

Sub-agents:
- Agent 0C-1: Sentence Splitter (10 rules)
- Agent 0C-2: Voice Converter (5 rules)
- Agent 0C-3: Technical Standardizer (15 rules)
- Agent 0C-4: Redundancy Remover (15 rules)
- Agent 0C-5: Formatter (5 rules)

Total: 50 rules across 5 specialized agents
Expected accuracy gain: 2-3%
"""

from typing import Dict, List
from agent_0c1_sentence_splitter import Agent_0C1_Sentence_Splitter
from agent_0c2_voice_converter import Agent_0C2_Voice_Converter
from agent_0c3_technical_standardizer import Agent_0C3_Technical_Standardizer
from agent_0c4_redundancy_remover import Agent_0C4_Redundancy_Remover
from agent_0c5_formatter import Agent_0C5_Formatter

class Agent_0C_Controlled_Language:
    """
    Master coordinator for controlled language simplification
    
    Architecture: 1 coordinator + 5 specialized sub-agents
    Philosophy: Many specialized agents > One monolithic agent
    
    Processing pipeline:
    1. Agent 0C-1: Split compound sentences
    2. Agent 0C-2: Convert passive to active voice
    3. Agent 0C-3: Standardize technical phrasing
    4. Agent 0C-4: Remove redundancy
    5. Agent 0C-5: Format and cleanup
    """
    
    def __init__(self):
        """Initialize master coordinator"""
        self.sub_agents = [
            ('0C-1', Agent_0C1_Sentence_Splitter, 'Sentence Splitter'),
            ('0C-2', Agent_0C2_Voice_Converter, 'Voice Converter'),
            ('0C-3', Agent_0C3_Technical_Standardizer, 'Technical Standardizer'),
            ('0C-4', Agent_0C4_Redundancy_Remover, 'Redundancy Remover'),
            ('0C-5', Agent_0C5_Formatter, 'Formatter')
        ]
    
    def simplify(self, text: str, source_lang: str = 'ja') -> Dict:
        """
        Simplify text using 5-phase specialized agent pipeline
        
        Args:
            text: Source text to simplify
            source_lang: Source language code
            
        Returns:
            {
                'original': original text,
                'simplified': simplified text,
                'rules_applied': list of all rules applied,
                'complexity_reduction': percentage reduction,
                'agent_breakdown': per-agent statistics
            }
        """
        if source_lang != 'ja':
            # Only Japanese simplification implemented for now
            return {
                'original': text,
                'simplified': text,
                'rules_applied': [],
                'complexity_reduction': 0.0,
                'agent_breakdown': {}
            }
        
        original = text
        result = text
        all_rules_applied = []
        agent_breakdown = {}
        
        # Process through 5-phase pipeline
        for agent_id, agent_class, agent_name in self.sub_agents:
            phase_result = agent_class.process(result)
            result = phase_result['text']
            rules = phase_result['rules_applied']
            
            # Track per-agent statistics
            agent_breakdown[agent_id] = {
                'name': agent_name,
                'rules_applied': rules,
                'rule_count': len(rules)
            }
            
            # Accumulate all rules
            all_rules_applied.extend(rules)
            
            # Log progress
            if rules:
                print(f"  ✓ Agent {agent_id} ({agent_name}): {len(rules)} rules applied")
        
        # Calculate complexity reduction
        complexity_reduction = self._calculate_complexity_reduction(original, result)
        
        return {
            'original': original,
            'simplified': result,
            'rules_applied': all_rules_applied,
            'complexity_reduction': complexity_reduction,
            'agent_breakdown': agent_breakdown
        }
    
    def _calculate_complexity_reduction(self, original: str, simplified: str) -> float:
        """
        Calculate complexity reduction percentage
        
        Metrics:
        - Sentence count change (more sentences = simpler)
        - Character count change (fewer chars = simpler)
        - Average sentence length change
        """
        original_sentences = len([s for s in original.split('。') if s.strip()])
        simplified_sentences = len([s for s in simplified.split('。') if s.strip()])
        
        original_length = len(original)
        simplified_length = len(simplified)
        
        # More sentences = more simplification (splitting compound sentences)
        sentence_factor = (simplified_sentences - original_sentences) / max(original_sentences, 1)
        
        # Shorter text = more simplification (removing unnecessary words)
        length_factor = (original_length - simplified_length) / max(original_length, 1)
        
        # Combined complexity reduction score
        reduction = (sentence_factor * 0.5 + length_factor * 0.5) * 100
        
        return max(0.0, min(100.0, reduction))
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the agent system
        
        Returns:
            {
                'total_agents': 6 (1 coordinator + 5 specialized),
                'total_rules': 50,
                'agents': [...agent details...]
            }
        """
        return {
            'total_agents': 6,  # 1 coordinator + 5 sub-agents
            'total_rules': 50,
            'coordinator': 'Agent 0C',
            'sub_agents': [
                {'id': '0C-1', 'name': 'Sentence Splitter', 'rules': 10},
                {'id': '0C-2', 'name': 'Voice Converter', 'rules': 5},
                {'id': '0C-3', 'name': 'Technical Standardizer', 'rules': 15},
                {'id': '0C-4', 'name': 'Redundancy Remover', 'rules': 15},
                {'id': '0C-5', 'name': 'Formatter', 'rules': 5}
            ]
        }


# Example usage
if __name__ == "__main__":
    agent_0c = Agent_0C_Controlled_Language()
    
    test_texts = [
        "このショックキラーは高性能であり、かつ耐久性に優れている。",
        "圧力が調整される際において、安全性が確保される。",
        "優れた性能を有する製品である。",
        "非常に高い品質を備える部品となる。"
    ]
    
    print("=" * 70)
    print("Agent 0C: Controlled Language Simplifier - Modular Architecture Test")
    print("=" * 70)
    print()
    
    for i, text in enumerate(test_texts, 1):
        result = agent_0c.simplify(text)
        
        print(f"Test {i}:")
        print(f"  Original:   {result['original']}")
        print(f"  Simplified: {result['simplified']}")
        print(f"  Total rules: {len(result['rules_applied'])}")
        print(f"  Reduction:   {result['complexity_reduction']:.1f}%")
        print()
        
        # Show per-agent breakdown
        for agent_id, stats in result['agent_breakdown'].items():
            if stats['rule_count'] > 0:
                print(f"    {agent_id} - {stats['name']}: {stats['rule_count']} rules")
        print()
    
    # Show system statistics
    stats = agent_0c.get_statistics()
    print(f"System: {stats['total_agents']} agents, {stats['total_rules']} rules")
