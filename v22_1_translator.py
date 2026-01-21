"""
USI17 V22.2 Complete Translation System
Full 276-agent architecture with all Laws and glossary terms
Uses Grok 4 Fast for 2M token context window
"""

import os
import json
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from openai import OpenAI
from rtf_processor import RTFProcessor
from agent_0c_controlled_language import Agent_0C_Controlled_Language
from agent_63_back_translation_validator import Agent_63_Back_Translation_Validator

class USI17_V22_2_Translator:
    """
    Complete USI17 V22.2 translation system
    - 276 agents (0-266, excluding 226)
    - 14 Laws enforced
    - 535-term glossary (updated from 509 in V22.1)
    - RTF/TAG preservation
    - Bilingual output
    """
    
    def __init__(self, grok_api_key: str, gemini_api_key: str = None, claude_api_key: str = None, 
                 max_budget: float = 30000.0, V22_2_master_path: str = None):
        """Initialize V22.2 translator"""
        self.grok_client = OpenAI(
            api_key=grok_api_key,
            base_url="https://api.x.ai/v1"
        ) if grok_api_key else None
        
        self.gemini_api_key = gemini_api_key
        self.claude_api_key = claude_api_key
        
        self.cache_stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cached_tokens': 0,
            'total_uncached_tokens': 0,
            'cache_savings_jpy': 0.0
        }
        self.cache_log_file = 'cache_monitoring.log'
        
        self.V22_2_system = self._load_V22_2_master(V22_2_master_path)
        
        self.max_budget = max_budget
        self.total_cost = 0.0
        self.translation_count = 0
        
        self.tm = TranslationMemory()
        
        self.model_costs = {'grok': 0.0, 'gemini': 0.0, 'claude': 0.0}
        
        self.pricing = {
            'grok-4.1-fast': {'input': 0.20, 'input_cached': 0.02, 'output': 0.50},
            'gemini-3-flash': {'input': 0.50, 'input_cached': 0.125, 'output': 3.00},
            'claude-sonnet-4-5': {'input': 3.00, 'input_cached': 0.30, 'output': 15.00}
        }
        
        self.usd_to_jpy = 152.0
        self.rtf_processor = RTFProcessor()
        
        self.agent_0c = Agent_0C_Controlled_Language()
        print("✅ Agent 0C loaded")
        
        self.agent_63 = Agent_63_Back_Translation_Validator(self)
        print("✅ Agent 63 loaded")
    
    def _load_V22_2_master(self, path: str) -> str:
        """Load V22.2 Master file"""
        if not path or not os.path.exists(path):
            raise ValueError(f"V22.2 Master file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            system = f.read()
        
        lines = len(system.split('\n'))
        if lines < 47000:
            raise ValueError(f"V22.2 Master truncated! Expected 47.8K lines, got {lines}")
        
        print(f"✅ V22.2 Master loaded: {lines:,} lines")
        return system
    
    def translate(self, source_text: str, source_lang: str = 'ja', target_langs: List[str] = None,
                  input_format: str = 'text', preserve_tags: bool = True, 
                  english_first: bool = True) -> Dict:
        """Translate using V22.2 system"""
        if target_langs is None or len(target_langs) == 0:
            target_langs = ['en']
        
        target_langs = [t for t in target_langs if t != source_lang]
        
        if len(target_langs) == 0:
            raise ValueError("No valid target languages")
        
        if english_first and 'en' in target_langs:
            target_langs = ['en'] + [t for t in target_langs if t != 'en']
        
        # AGENT 0C: Simplify
        original_source = source_text
        simplification_result = {'rules_applied': [], 'complexity_reduction': 0.0}
        
        if source_lang == 'ja':
            simplification_result = self.agent_0c.simplify(source_text, source_lang)
            source_text = simplification_result['simplified']
        
        if self.total_cost >= self.max_budget:
            raise Exception(f"Budget limit reached: ¥{self.total_cost:,.0f}")
        
        # Check TM
        translations = {}
        tm_hits = 0
        remaining_targets = []
        
        for target_lang in target_langs:
            tm_result = self.tm.get(source_text, target_lang)
            if tm_result:
                translations[target_lang] = tm_result['translation']
                tm_hits += 1
            else:
                remaining_targets.append(target_lang)
        
        if len(remaining_targets) == 0:
            return self._build_multi_language_result(
                source_text, source_lang, target_langs, translations,
                model='TM', cost_jpy=0.0, tokens_input=0, tokens_output=0,
                tm_hits=tm_hits, simplification_result=simplification_result
            )
        
        prompt = self._build_V22_2_multi_prompt(
            source_text, source_lang, remaining_targets, input_format, preserve_tags
        )
        
        try:
            result = self._translate_with_gemini(prompt, source_text, remaining_targets)
            model_used = 'gemini'
        except Exception as e:
            try:
                result = self._translate_with_grok(prompt, source_text, remaining_targets)
                model_used = 'grok'
            except Exception as e2:
                result = self._translate_with_claude(prompt, source_text, remaining_targets)
                model_used = 'claude'
        
        new_translations = result['translations']
        cost_jpy = result['cost_jpy']
        translations.update(new_translations)
        
        for target_lang, translation in new_translations.items():
            self.tm.set(source_text, target_lang, translation, model_used)
        
        self.total_cost += cost_jpy
        self.model_costs[model_used] += cost_jpy
        self.translation_count += len(remaining_targets)
        
        return self._build_multi_language_result(
            source_text, source_lang, target_langs, translations,
            model=result['model'], cost_jpy=cost_jpy,
            tokens_input=result['tokens_input'],
            tokens_output=result['tokens_output'],
            tm_hits=tm_hits, simplification_result=simplification_result
        )
    
    def _build_V22_2_multi_prompt(self, source_text: str, source_lang: str, 
                                   target_langs: List[str], input_format: str, 
                                   preserve_tags: bool) -> str:
        """Build V22.2 prompt"""
        lang_names = {
            'ja': 'Japanese', 'en': 'English', 'de': 'German', 'fr': 'French',
            'es': 'Spanish', 'em': 'Spanish (MX)', 'pt': 'Portuguese', 
            'it': 'Italian', 'cz': 'Czech', 'pl': 'Polish', 'tk': 'Turkish',
            'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian', 
            'ko': 'Korean', 'cn': 'Chinese (CN)', 'tw': 'Chinese (TW)'
        }
        
        source_name = lang_names.get(source_lang, source_lang.upper())
        target_names = [lang_names.get(t, t.upper()) for t in target_langs]
        
        prompt = f"""
You are USI17 V22.2 with 276 agents.

Translate from {source_name} to: {', '.join(target_names)}

SOURCE TEXT:
{source_text}

INSTRUCTIONS:
1. Use V22.2 system (535 terms)
2. CRITICAL: ショックキラー = "shock absorber" NEVER "shock killer"
3. Output TAB-delimited

OUTPUT FORMAT:
Source[TAB]Target1[TAB]Target2[TAB]...

Begin:
"""
        return prompt
    
    def _build_multi_language_result(self, source_text: str, source_lang: str,
                                     target_langs: List[str], translations: Dict[str, str],
                                     model: str, cost_jpy: float, tokens_input: int,
                                     tokens_output: int, tm_hits: int,
                                     simplification_result: Dict = None) -> Dict:
        """Build result - FIXED: Added simplification_result parameter"""
        column_order = [source_lang] + target_langs
        tab_values = [source_text] + [translations.get(t, '') for t in target_langs]
        multi_language_tab = '\t'.join(tab_values)
        
        lang_names = {
            'ja': 'Japanese', 'en': 'English', 'de': 'German', 'fr': 'French',
            'es': 'Spanish', 'em': 'Spanish (MX)', 'pt': 'Portuguese',
            'it': 'Italian', 'cz': 'Czech', 'pl': 'Polish', 'tk': 'Turkish',
            'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian',
            'ko': 'Korean', 'cn': 'Chinese (CN)', 'tw': 'Chinese (TW)'
        }
        header_names = [lang_names.get(lang, lang.upper()) for lang in column_order]
        header_row = '\t'.join(header_names)
        
        # AGENT 63: Back-translation
        back_translation_scores = {}
        for target_lang in target_langs:
            try:
                validation = self.validate_with_back_translation(
                    source_text, translations[target_lang], source_lang, target_lang
                )
                back_translation_scores[target_lang] = validation
            except:
                back_translation_scores[target_lang] = {'error': True}
        
        return {
            'source': source_text,
            'source_lang': source_lang,
            'targets': translations,
            'target_langs': target_langs,
            'multi_language_tab': multi_language_tab,
            'with_header': f"{header_row}\n{multi_language_tab}",
            'column_order': column_order,
            'model': model,
            'cost_jpy': cost_jpy,
            'tokens_input': tokens_input,
            'tokens_output': tokens_output,
            'tm_hits': tm_hits,
            'tm_hit_rate': (tm_hits / len(target_langs) * 100) if target_langs else 0,
            'back_translation': back_translation_scores,
            'agent_0c_applied': simplification_result['rules_applied'] if simplification_result else []
        }
    
    def validate_with_back_translation(self, source_text: str, translation: str,
                                      source_lang: str, target_lang: str) -> Dict:
        """AGENT 63"""
        return self.agent_63.validate(source_text, translation, source_lang, target_lang)
    
    def translate_rtf_file(self, rtf_content: str, source_lang: str = 'ja', 
                           target_langs: List[str] = None, english_first: bool = True) -> Dict:
        """RTF translation"""
        if target_langs is None:
            target_langs = ['en']
        
        rtf_data = self.rtf_processor.process_rtf_file(rtf_content)
        
        translation_result = self.translate(
            source_text=rtf_data['text_with_placeholders'],
            source_lang=source_lang,
            target_langs=target_langs,
            input_format='text',
            preserve_tags=True,
            english_first=english_first
        )
        
        targets_with_tags = {}
        bilingual_outputs = {}
        law_13_results = {}
        
        for target_lang in target_langs:
            translation_with_tags = self.rtf_processor.restore_tags(
                translation_result['targets'][target_lang],
                rtf_data['tag_mappings']
            )
            targets_with_tags[target_lang] = translation_with_tags
            
            bilingual = self.rtf_processor.create_bilingual_output(
                rtf_data['original_text_with_tags'],
                translation_with_tags,
                source_lang,
                target_lang
            )
            bilingual_outputs[target_lang] = bilingual
            
            law_13_passed = self.rtf_processor.validate_rtf_structure(
                rtf_data['original_text_with_tags'],
                translation_with_tags
            )
            law_13_results[target_lang] = law_13_passed
        
        return {
            'source_with_tags': rtf_data['original_text_with_tags'],
            'targets_with_tags': targets_with_tags,
            'bilingual_outputs': bilingual_outputs,
            'tag_count': rtf_data['tag_count'],
            'law_13_passed': all(law_13_results.values()),
            'law_13_results': law_13_results,
            'model': translation_result['model'],
            'cost_jpy': translation_result['cost_jpy'],
            'tokens_input': translation_result['tokens_input'],
            'tokens_output': translation_result['tokens_output'],
            'tm_hits': translation_result['tm_hits']
        }
    
    def _translate_with_grok(self, prompt: str, source_text: str, target_langs: List[str] = None) -> Dict:
        """Translate with Grok"""
        if not self.grok_client:
            raise Exception("Grok API key not configured")
        
        if target_langs is None:
            target_langs = ['en']
        
        response = self.grok_client.chat.completions.create(
            model="grok-4.1-fast",
            messages=[
                {"role": "system", "content": self.V22_2_system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content.strip()
        translations = self._parse_multi_language_response(response_text, target_langs)
        
        tokens_input = response.usage.prompt_tokens
        tokens_output = response.usage.completion_tokens
        
        cached_tokens = 0
        if hasattr(response.usage, 'prompt_tokens_details'):
            details = response.usage.prompt_tokens_details
            if hasattr(details, 'cached_tokens'):
                cached_tokens = details.cached_tokens
        
        uncached_tokens = tokens_input - cached_tokens
        cost_usd = (cached_tokens / 1_000_000 * 0.02) + (uncached_tokens / 1_000_000 * 0.20) + (tokens_output / 1_000_000 * 0.50)
        cost_jpy = cost_usd * self.usd_to_jpy
        
        return {
            'translations': translations,
            'model': 'grok-4.1-fast',
            'cost_jpy': cost_jpy,
            'tokens_input': tokens_input,
            'tokens_output': tokens_output
        }
    
    def _translate_with_gemini(self, prompt: str, source_text: str, target_langs: List[str] = None) -> Dict:
        """Translate with Gemini"""
        if not self.gemini_api_key:
            raise Exception("Gemini API key not configured")
        
        if target_langs is None:
            target_langs = ['en']
        
        import google.generativeai as genai
        
        genai.configure(api_key=self.gemini_api_key)
        
        model = genai.GenerativeModel(
            'gemini-3-flash-preview',
            system_instruction=self.V22_2_system
        )
        
        response = model.generate_content(
            prompt,
            generation_config={'temperature': 0.1, 'candidate_count': 1}
        )
        
        response_text = response.text.strip()
        translations = self._parse_multi_language_response(response_text, target_langs)
        
        usage = response.usage_metadata
        tokens_input = usage.prompt_token_count
        tokens_output = usage.candidates_token_count
        cached_tokens = usage.cached_content_token_count if hasattr(usage, 'cached_content_token_count') else 0
        uncached_tokens = tokens_input - cached_tokens
        
        cost_usd = (cached_tokens / 1_000_000 * 0.125) + (uncached_tokens / 1_000_000 * 0.50) + (tokens_output / 1_000_000 * 3.00)
        cost_jpy = cost_usd * self.usd_to_jpy
        
        return {
            'translations': translations,
            'model': 'gemini-3-flash',
            'cost_jpy': cost_jpy,
            'tokens_input': tokens_input,
            'tokens_output': tokens_output
        }
    
    def _translate_with_claude(self, prompt: str, source_text: str, target_langs: List[str] = None) -> Dict:
        """Translate with Claude"""
        raise Exception("Claude not implemented")
    
    def _parse_multi_language_response(self, response_text: str, target_langs: List[str]) -> Dict[str, str]:
        """Parse TAB-delimited response"""
        parts = response_text.split('\t')
        translations_list = parts[1:] if len(parts) > 1 else parts
        
        translations = {}
        for i, lang in enumerate(target_langs):
            if i < len(translations_list):
                translations[lang] = translations_list[i].strip()
            else:
                translations[lang] = ""
        
        return translations
    
    def get_stats(self) -> Dict:
        """Get stats"""
        return {
            'total_cost': self.total_cost,
            'budget_remaining': self.max_budget - self.total_cost,
            'budget_used_pct': (self.total_cost / self.max_budget * 100) if self.max_budget > 0 else 0,
            'translations_completed': self.translation_count,
            'tm_hit_rate': self.tm.get_hit_rate(),
            'costs_by_model': self.model_costs
        }


class TranslationMemory:
    """Translation Memory"""
    
    def __init__(self, filepath: str = r'E:\USI17\translation_memory.json'):
        self.filepath = filepath
        self.memory = {}
        self.hits = 0
        self.misses = 0
        
        tm_dir = os.path.dirname(filepath)
        if tm_dir and not os.path.exists(tm_dir):
            try:
                os.makedirs(tm_dir)
            except:
                self.filepath = 'translation_memory.json'
        
        self.load()
    
    def load(self):
        """Load TM"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                print(f"✅ Loaded {len(self.memory):,} TM entries")
            except:
                self.memory = {}
    
    def save(self):
        """Save TM"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_key(self, source_text: str, target_lang: str) -> str:
        """Generate hash"""
        content = f"{source_text}_{target_lang}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, source_text: str, target_lang: str) -> Optional[Dict]:
        """Get from TM"""
        key = self.get_key(source_text, target_lang)
        if key in self.memory:
            self.hits += 1
            entry = self.memory[key]
            entry['last_used'] = datetime.now().isoformat()
            entry['use_count'] += 1
            self.save()
            return entry
        self.misses += 1
        return None
    
    def set(self, source_text: str, target_lang: str, translation: str, model: str):
        """Store in TM"""
        key = self.get_key(source_text, target_lang)
        
        self.memory[key] = {
            'source': source_text[:100],
            'translation': translation,
            'target_lang': target_lang,
            'model': model,
            'created': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'use_count': 1
        }
        
        self.save()
    
    def get_hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
