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
        """
        Initialize V22.2 translator with complete system
        
        Args:
            grok_api_key: Grok API key (primary - 2M context)
            gemini_api_key: Gemini API key (backup - 1M context)
            claude_api_key: Claude API key (backup - 200K context)
            max_budget: Maximum budget in Japanese Yen
            V22_2_master_path: Path to USI17_V22_2_MASTER.txt file
        """
        # Initialize API clients
        self.grok_client = OpenAI(
            api_key=grok_api_key,
            base_url="https://api.x.ai/v1"
        ) if grok_api_key else None
        
        self.gemini_api_key = gemini_api_key
        self.claude_api_key = claude_api_key
        
        # Cache monitoring
        self.cache_stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cached_tokens': 0,
            'total_uncached_tokens': 0,
            'cache_savings_jpy': 0.0
        }
        self.cache_log_file = 'cache_monitoring.log'
        
        # Load V22.2 Master system
        self.V22_2_system = self._load_V22_2_master(V22_2_master_path)
        
        # Budget tracking
        self.max_budget = max_budget
        self.total_cost = 0.0
        self.translation_count = 0
        
        # Translation Memory
        self.tm = TranslationMemory()
        
        # Cost tracking per model
        self.model_costs = {
            'grok': 0.0,
            'gemini': 0.0,
            'claude': 0.0
        }
        
        # Pricing (per 1M tokens in USD)
        self.pricing = {
            'grok-4.1-fast': {
                'input': 0.20,
                'input_cached': 0.02,
                'output': 0.50
            },
            'gemini-3-flash': {
                'input': 0.50,
                'input_cached': 0.125,
                'output': 3.00
            },
            'claude-sonnet-4-5': {
                'input': 3.00,
                'input_cached': 0.30,
                'output': 15.00
            }
        }
        
        # Exchange rate USD to JPY
        self.usd_to_jpy = 152.0
        
        # RTF processor for TAG preservation
        self.rtf_processor = RTFProcessor()
        
        # Agent 0C: Controlled Language Simplifier
        self.agent_0c = Agent_0C_Controlled_Language()
        print("✅ Agent 0C: Controlled Language Simplifier loaded (6 agents)")
        
        # Agent 63: Back-Translation Validator
        self.agent_63 = Agent_63_Back_Translation_Validator(self)
        print("✅ Agent 63: Back-Translation Validator loaded (5 agents)")
        
        print(f"✅ Total specialized agents: 11 (2 coordinators + 9 specialized)")
    
    def _load_V22_2_master(self, path: str) -> str:
        """
        Load complete V22.2 Master file (47,805 lines)
        CSV Protocol: Zero truncation, mechanical extraction
        
        Returns:
            Complete V22.2 system as string
        """
        if not path or not os.path.exists(path):
            raise ValueError(f"V22.2 Master file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            system = f.read()
        
        # Verify integrity
        lines = len(system.split('\n'))
        if lines < 47000:
            raise ValueError(f"V22.2 Master appears truncated! Expected 47.8K lines, got {lines}")
        
        # Verify critical components
        required_components = [
            'AGENT_0:',
            'AGENT_46:',
            'AGENT_47:',
            'LAW_13:',
            'LAW_14:',
            'TERM_510:',  # New in V22.2
            'TERM_540:',  # New in V22.2
            'ショックキラー',
            'shock absorber'  # Fixed in V22.2 (not "shock killer")
        ]
        
        for component in required_components:
            if component not in system:
                raise ValueError(f"V22.2 Master missing critical component: {component}")
        
        print(f"✅ V22.2 Master loaded: {lines:,} lines, {len(system):,} characters")
        return system
    
    def translate(self, source_text: str, source_lang: str = 'ja', target_langs: List[str] = None,
                  input_format: str = 'text', preserve_tags: bool = True, 
                  english_first: bool = True) -> Dict:
        """
        Translate using complete V22.2 system - ANY language to MULTIPLE languages
        
        Args:
            source_text: Text to translate
            source_lang: Source language code (ja, en, de, fr, es, etc.)
            target_langs: List of target language codes (e.g., ['en', 'de', 'fr'])
            input_format: 'text', 'rtf', 'docx'
            preserve_tags: If True, preserves TAGs in output
            english_first: If True and 'en' in targets, put English first in output
        
        Returns:
            Complete translation result dictionary
        """
        # Default to English if no targets specified
        if target_langs is None or len(target_langs) == 0:
            target_langs = ['en']
        
        # Remove source language from targets
        target_langs = [t for t in target_langs if t != source_lang]
        
        if len(target_langs) == 0:
            raise ValueError("No valid target languages specified")
        
        # Apply English priority if requested
        if english_first and 'en' in target_langs:
            target_langs = ['en'] + [t for t in target_langs if t != 'en']
        
        # AGENT 0C: Simplify source text
        original_source = source_text
        simplification_result = {'rules_applied': [], 'complexity_reduction': 0.0}
        
        if source_lang == 'ja':
            simplification_result = self.agent_0c.simplify(source_text, source_lang)
            source_text = simplification_result['simplified']
            
            if simplification_result['rules_applied']:
                print(f"✅ Agent 0C: Applied {len(simplification_result['rules_applied'])} rules")
        
        # Check budget
        if self.total_cost >= self.max_budget:
            raise Exception(f"Budget limit reached: ¥{self.total_cost:,.0f} / ¥{self.max_budget:,.0f}")
        
        # Check Translation Memory
        translations = {}
        tm_hits = 0
        remaining_targets = []
        
        for target_lang in target_langs:
            tm_result = self.tm.get(source_text, target_lang)
            if tm_result:
                translations[target_lang] = tm_result['translation']
                tm_hits += 1
                print(f"✅ TM HIT for {target_lang.upper()}")
            else:
                remaining_targets.append(target_lang)
        
        # If all targets found in TM, return immediately
        if len(remaining_targets) == 0:
            return self._build_multi_language_result(
                source_text, source_lang, target_langs, translations,
                model='TM', cost_jpy=0.0, tokens_input=0, tokens_output=0,
                tm_hits=tm_hits, simplification_result=simplification_result
            )
        
        # Build V22.2 prompt for remaining targets
        prompt = self._build_V22_2_multi_prompt(
            source_text, source_lang, remaining_targets, 
            input_format, preserve_tags
        )
        
        # Translate with Gemini (primary), fallback to Grok/Claude
        try:
            result = self._translate_with_gemini(prompt, source_text, remaining_targets)
            model_used = 'gemini'
        except Exception as e:
            print(f"⚠️  Gemini failed: {e}, trying Grok...")
            try:
                result = self._translate_with_grok(prompt, source_text, remaining_targets)
                model_used = 'grok'
            except Exception as e2:
                print(f"⚠️  Grok failed: {e2}, trying Claude...")
                result = self._translate_with_claude(prompt, source_text, remaining_targets)
                model_used = 'claude'
        
        # Parse and merge results
        new_translations = result['translations']
        cost_jpy = result['cost_jpy']
        translations.update(new_translations)
        
        # Store new translations in TM
        for target_lang, translation in new_translations.items():
            self.tm.set(source_text, target_lang, translation, model_used)
        
        # Update tracking
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
        """Build complete V22.2 translation prompt for MULTIPLE target languages"""
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
You are USI17 V22.2 - Complete professional translation system with 276 agents.

TASK: Translate from {source_name} to MULTIPLE languages SIMULTANEOUSLY

SOURCE LANGUAGE: {source_name}
TARGET LANGUAGES: {', '.join(target_names)}
NUMBER OF TARGETS: {len(target_langs)}

SOURCE TEXT:
{source_text}

INSTRUCTIONS:
1. Use ALL 276 agents from V22.2 system
2. Enforce ALL 14 Laws
3. Apply 535-term glossary (LOCKED: ショックキラー = "shock absorber" NEVER "shock killer")
4. Preserve TAGs if present
5. Output TAB-delimited format

OUTPUT FORMAT:
{source_name}[TAB]{target_names[0]}[TAB]{target_names[1] if len(target_names) > 1 else ''}...

CRITICAL TERMS (V22.2 GLOSSARY):
- ショックキラー = "shock absorber"
- 体系表 = "System Chart"
- ストレート取付 = "Inline Mount"
- 折返し取付 = "Reverse Parallel Mount" (EN) / "Parallel Mount" (others)

Begin translation:
"""
        return prompt
    
    def _build_multi_language_result(self, source_text: str, source_lang: str,
                                     target_langs: List[str], translations: Dict[str, str],
                                     model: str, cost_jpy: float, tokens_input: int,
                                     tokens_output: int, tm_hits: int,
                                     simplification_result: Dict = None) -> Dict:
        """Build multi-language result dictionary"""
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
        
        # AGENT 63: Back-Translation Validation
        back_translation_scores = {}
        for target_lang in target_langs:
            try:
                validation = self.validate_with_back_translation(
                    source_text=source_text,
                    translation=translations[target_lang],
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                back_translation_scores[target_lang] = validation
                
                if validation['flag_for_review']:
                    print(f"⚠️  Agent 63: Low confidence for {target_lang}")
            except Exception as e:
                back_translation_scores[target_lang] = {
                    'similarity_score': 0.0,
                    'confidence': 'error',
                    'flag_for_review': True,
                    'error': str(e)
                }
        
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
            'tm_hit_rate': (tm_hits / len(target_langs) * 100) if len(target_langs) > 0 else 0,
            'back_translation': back_translation_scores,
            'agent_0c_applied': simplification_result['rules_applied'] if simplification_result else []
        }
    
    def validate_with_back_translation(self, source_text: str, translation: str,
                                      source_lang: str, target_lang: str) -> Dict:
        """AGENT 63: Back-Translation Validator"""
        return self.agent_63.validate(source_text, translation, source_lang, target_lang)
    
    def translate_rtf_file(self, rtf_content: str, source_lang: str = 'ja', 
                           target_langs: List[str] = None, english_first: bool = True) -> Dict:
        """Translate RTF file with TAG preservation"""
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
        """Translate using Grok 4.1 Fast"""
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
        
        # Calculate cost with caching
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
        """Translate using Gemini 3 Flash"""
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
        """Translate using Claude Sonnet 4.5"""
        raise Exception("Claude not implemented - V22.2 exceeds context window")
    
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
        """Get translation statistics"""
        return {
            'total_cost': self.total_cost,
            'budget_remaining': self.max_budget - self.total_cost,
            'budget_used_pct': (self.total_cost / self.max_budget * 100) if self.max_budget > 0 else 0,
            'translations_completed': self.translation_count,
            'tm_hit_rate': self.tm.get_hit_rate(),
            'costs_by_model': self.model_costs
        }


class TranslationMemory:
    """Persistent translation memory"""
    
    def __init__(self, filepath: str = r'E:\USI17\translation_memory.json'):
        self.filepath = filepath
        self.memory = {}
        self.hits = 0
        self.misses = 0
        
        # Create directory if needed
        tm_dir = os.path.dirname(filepath)
        if tm_dir and not os.path.exists(tm_dir):
            try:
                os.makedirs(tm_dir)
            except:
                self.filepath = 'translation_memory.json'
        
        self.load()
    
    def load(self):
        """Load TM from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                print(f"✅ Loaded {len(self.memory):,} TM entries")
            except:
                self.memory = {}
    
    def save(self):
        """Save TM to file"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_key(self, source_text: str, target_lang: str) -> str:
        """Generate hash key"""
        content = f"{source_text}_{target_lang}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, source_text: str, target_lang: str) -> Optional[Dict]:
        """Retrieve from TM"""
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
        """Calculate TM hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0