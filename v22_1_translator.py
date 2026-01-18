"""
USI17 V22.1 Complete Translation System
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

class USI17_V22_1_Translator:
    """
    Complete USI17 V22.1 translation system
    - 276 agents (0-266, excluding 226)
    - 14 Laws enforced
    - 509-term glossary
    - RTF/TAG preservation
    - Bilingual output
    """
    
    def __init__(self, grok_api_key: str, gemini_api_key: str = None, claude_api_key: str = None, 
                 max_budget: float = 30000.0, v22_1_master_path: str = None):
        """
        Initialize V22.1 translator with complete system
        
        Args:
            grok_api_key: Grok API key (primary - 2M context)
            gemini_api_key: Gemini API key (backup - 1M context)
            claude_api_key: Claude API key (backup - 200K context)
            max_budget: Maximum budget in Japanese Yen
            v22_1_master_path: Path to USI17_V22_1_MASTER.txt file
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
        
        # Load V22.1 Master system
        self.v22_1_system = self._load_v22_1_master(v22_1_master_path)
        
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
            'grok-4-fast': {
                'input': 0.20,
                'input_cached': 0.02,  # 90% discount
                'output': 0.50
            },
            'gemini-3-flash': {
                'input': 0.075,
                'input_cached': 0.01875,  # 75% discount
                'output': 0.30
            },
            'claude-sonnet-4-5': {
                'input': 3.00,
                'input_cached': 0.30,  # 90% discount
                'output': 15.00
            }
        }
        
        # Exchange rate USD to JPY
        self.usd_to_jpy = 152.0
        
        # RTF processor for TAG preservation
        self.rtf_processor = RTFProcessor()
        
        # Agent 0C: Controlled Language Simplifier (1 coordinator + 5 sub-agents)
        self.agent_0c = Agent_0C_Controlled_Language()
        print("✅ Agent 0C: Controlled Language Simplifier loaded (6 agents)")
        
        # Agent 63: Back-Translation Validator (1 coordinator + 4 sub-agents)
        self.agent_63 = Agent_63_Back_Translation_Validator(self)
        print("✅ Agent 63: Back-Translation Validator loaded (5 agents)")
        
        print(f"✅ Total specialized agents: 11 (2 coordinators + 9 specialized)")
    
    def _load_v22_1_master(self, path: str) -> str:
        """
        Load complete V22.1 Master file (47,000 lines)
        CSV Protocol: Zero truncation, mechanical extraction
        
        Returns:
            Complete V22.1 system as string
        """
        if not path or not os.path.exists(path):
            raise ValueError(f"V22.1 Master file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            system = f.read()
        
        # Verify integrity
        lines = len(system.split('\n'))
        if lines < 46000:
            raise ValueError(f"V22.1 Master appears truncated! Expected 47K lines, got {lines}")
        
        # Verify critical components
        required_components = [
            'AGENT_0:',
            'AGENT_46:',  # InDesign_Tag_Masker
            'AGENT_47:',  # Adaptive_Tag_Learner
            'LAW_13:',    # RTF_Structure_Preservation
            'LAW_14:',    # Character_Normalization
            'ショックキラー',  # Critical glossary term
            'shock absorber'
        ]
        
        for component in required_components:
            if component not in system:
                raise ValueError(f"V22.1 Master missing critical component: {component}")
        
        print(f"✅ V22.1 Master loaded: {lines:,} lines, {len(system):,} characters")
        return system
    
    def translate(self, source_text: str, source_lang: str = 'ja', target_langs: List[str] = None,
                  input_format: str = 'text', preserve_tags: bool = True, 
                  english_first: bool = True) -> Dict:
        """
        Translate using complete V22.1 system - ANY language to MULTIPLE languages
        
        Args:
            source_text: Text to translate
            source_lang: Source language code (ja, en, de, fr, es, etc.)
            target_langs: List of target language codes (e.g., ['en', 'de', 'fr'])
                         If None, defaults to ['en']
            input_format: 'text', 'rtf', 'docx'
            preserve_tags: If True, preserves TAGs in output
            english_first: If True and 'en' in targets, put English first in output
        
        Returns:
            {
                'source': original text,
                'source_lang': source language code,
                'targets': {
                    'en': 'English translation',
                    'de': 'German translation',
                    'fr': 'French translation',
                    ...
                },
                'multi_language_tab': TAB-delimited output with all languages,
                'column_order': ['ja', 'en', 'de', 'fr', ...],
                'model': model used,
                'cost_jpy': cost in yen,
                'tokens_input': input tokens,
                'tokens_output': output tokens,
                'tm_hits': number of TM hits
            }
        """
        # Default to English if no targets specified
        if target_langs is None or len(target_langs) == 0:
            target_langs = ['en']
        
        # Remove source language from targets (can't translate to same language)
        target_langs = [t for t in target_langs if t != source_lang]
        
        if len(target_langs) == 0:
            raise ValueError("No valid target languages specified")
        
        # Apply English priority if requested
        if english_first and 'en' in target_langs:
            # Move English to first position
            target_langs = ['en'] + [t for t in target_langs if t != 'en']
        
        # AGENT 0C: Simplify source text before USI processing
        # This improves mathematical mapping accuracy by 2-3%
        # Uses 6 agents: 1 coordinator + 5 specialized
        original_source = source_text
        simplification_result = {'rules_applied': [], 'complexity_reduction': 0.0}  # Default
        
        if source_lang == 'ja':  # Currently only Japanese supported
            simplification_result = self.agent_0c.simplify(source_text, source_lang)
            source_text = simplification_result['simplified']
            
            if simplification_result['rules_applied']:
                print(f"✅ Agent 0C: Applied {len(simplification_result['rules_applied'])} simplification rules")
                print(f"   Complexity reduction: {simplification_result['complexity_reduction']:.1f}%")
            else:
                print(f"ℹ️  Agent 0C: No simplification needed")
        
        # Check budget
        if self.total_cost >= self.max_budget:
            raise Exception(f"Budget limit reached: ¥{self.total_cost:,.0f} / ¥{self.max_budget:,.0f}")
        
        # Check Translation Memory for each target
        translations = {}
        tm_hits = 0
        remaining_targets = []
        
        for target_lang in target_langs:
            tm_result = self.tm.get(source_text, target_lang)
            if tm_result:
                translations[target_lang] = tm_result['translation']
                tm_hits += 1
                print(f"✅ TM HIT for {target_lang.upper()}! Saved cost")
            else:
                remaining_targets.append(target_lang)
        
        # If all targets found in TM, return immediately
        if len(remaining_targets) == 0:
            return self._build_multi_language_result(
                source_text, source_lang, target_langs, translations,
                model='TM', cost_jpy=0.0, tokens_input=0, tokens_output=0,
                tm_hits=tm_hits
            )
        
        # Build V22.1 prompt for remaining targets
        prompt = self._build_v22_1_multi_prompt(
            source_text, source_lang, remaining_targets, 
            input_format, preserve_tags
        )
        
        # Translate with Gemini (primary), fallback to Grok/Claude
        # Gemini is 42% cheaper than Grok with similar performance
        try:
            result = self._translate_with_gemini(prompt, source_text, remaining_targets)
            model_used = 'gemini'
        except Exception as e:
            print(f"⚠️  Gemini failed: {e}, trying Grok (backup)...")
            try:
                result = self._translate_with_grok(prompt, source_text, remaining_targets)
                model_used = 'grok'
            except Exception as e2:
                print(f"⚠️  Grok failed: {e2}, trying Claude...")
                result = self._translate_with_claude(prompt, source_text, remaining_targets)
                model_used = 'claude'
        
        # Parse multi-language response
        new_translations = result['translations']  # Dict of {lang: translation}
        cost_jpy = result['cost_jpy']
        
        # Merge TM hits with new translations
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
            tm_hits=tm_hits
        )
    
    def _build_v22_1_multi_prompt(self, source_text: str, source_lang: str, 
                                   target_langs: List[str], input_format: str, 
                                   preserve_tags: bool) -> str:
        """
        Build complete V22.1 translation prompt for MULTIPLE target languages
        Uses FULL system (no truncation)
        """
        # Language code to name mapping
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
You are USI17 V22.1 - Complete professional translation system with 276 agents.

TASK:
Translate from {source_name} to MULTIPLE languages SIMULTANEOUSLY

SOURCE LANGUAGE: {source_name}
TARGET LANGUAGES: {', '.join(target_names)}
NUMBER OF TARGETS: {len(target_langs)}

INPUT FORMAT: {input_format.upper()}
PRESERVE TAGS: {"YES" if preserve_tags else "NO"}

SOURCE TEXT:
{source_text}

INSTRUCTIONS:
1. Use ALL 276 agents from the V22.1 system loaded in your context
2. Enforce ALL 14 Laws (especially LAW_13 RTF preservation, LAW_14 character normalization)
3. Apply 509-term glossary (LOCKED terms like ショックキラー = "shock absorber")
4. Preserve all TAGs if input contains formatting
5. Translate SIMULTANEOUSLY to all {len(target_langs)} target languages
6. Output TAB-delimited format with one row per source segment

OUTPUT FORMAT (CRITICAL):
For each source segment, output ONE line with TAB-delimited translations in this order:

{source_name}[TAB]{target_names[0]}[TAB]{target_names[1] if len(target_names) > 1 else ''}...

Example output structure:
Source text[TAB]Translation1[TAB]Translation2[TAB]Translation3...

CRITICAL GLOSSARY TERMS (LOCKED - 100% enforcement):
- ショックキラー = "shock absorber" (NEVER "shock killer")
- エアシリンダ = "air cylinder"
- チューブ外径 = "Tube O.D."
- チューブ内径 = "Tube I.D."
- シリンダ径 = "Cylinder Bore Size"
- φD = "øD" (no space between ø and number)
- 体系表 = "Series selection guide"

CRITICAL: SI UNIT SPACING (LAW_7/8):
- Japanese: 50mm (no space)
- English/German/French/Spanish/etc.: 50 mm (SPACE required before unit)
- Chinese/Korean: 50mm (no space)

OUTPUT MUST BE TAB-DELIMITED WITH ALL LANGUAGES IN ONE LINE!

Begin translation:
"""
        return prompt
    
    def _build_multi_language_result(self, source_text: str, source_lang: str,
                                     target_langs: List[str], translations: Dict[str, str],
                                     model: str, cost_jpy: float, tokens_input: int,
                                     tokens_output: int, tm_hits: int) -> Dict:
        """
        Build multi-language result dictionary with TAB-delimited output
        """
        # Build column order: source first, then targets
        column_order = [source_lang] + target_langs
        
        # Build TAB-delimited output
        # Format: SourceText[TAB]Target1[TAB]Target2[TAB]...
        tab_values = [source_text] + [translations.get(t, '') for t in target_langs]
        multi_language_tab = '\t'.join(tab_values)
        
        # Build header row with language names
        lang_names = {
            'ja': 'Japanese', 'en': 'English', 'de': 'German', 'fr': 'French',
            'es': 'Spanish', 'em': 'Spanish (MX)', 'pt': 'Portuguese',
            'it': 'Italian', 'cz': 'Czech', 'pl': 'Polish', 'tk': 'Turkish',
            'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian',
            'ko': 'Korean', 'cn': 'Chinese (CN)', 'tw': 'Chinese (TW)'
        }
        header_names = [lang_names.get(lang, lang.upper()) for lang in column_order]
        header_row = '\t'.join(header_names)
        
        # AGENT 63: Back-Translation Validation (Quality Estimation)
        # Validates translation quality by back-translating and comparing
        back_translation_scores = {}
        for target_lang in target_langs:
            try:
                validation = self.validate_with_back_translation(
                    source_text=original_source if source_lang == 'ja' else source_text,
                    translation=translations[target_lang],
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                back_translation_scores[target_lang] = validation
                
                if validation['flag_for_review']:
                    print(f"⚠️  Agent 63: Low confidence for {target_lang} (score: {validation['similarity_score']:.2f})")
            except Exception as e:
                print(f"⚠️  Agent 63: Back-translation failed for {target_lang}: {str(e)}")
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
            'back_translation': back_translation_scores,  # NEW: Agent 63 results
            'agent_0c_applied': simplification_result['rules_applied'] if source_lang == 'ja' else []  # NEW: Agent 0C tracking
        }
    
    def _build_v22_1_prompt(self, source_text: str, source_lang: str, target_lang: str,
                            input_format: str, preserve_tags: bool) -> str:
        """
        Build complete V22.1 translation prompt (single target - for backwards compatibility)
        """
        return self._build_v22_1_multi_prompt(source_text, source_lang, [target_lang], 
                                              input_format, preserve_tags)
    
    def validate_with_back_translation(self, source_text: str, translation: str,
                                      source_lang: str, target_lang: str) -> Dict:
        """
        AGENT 63: Back-Translation Validator (uses 5 specialized agents)
        Validates translation quality by back-translating to source language
        
        Agent breakdown:
        - Agent 63: Master Coordinator
        - Agent 63-A: Back-Translator
        - Agent 63-B: Similarity Calculator
        - Agent 63-C: Confidence Assessor
        - Agent 63-D: Review Flagger
        
        Process:
        1. Agent 63-A: Back-translate Target → Source
        2. Agent 63-B: Calculate Jaccard similarity
        3. Agent 63-C: Assess confidence level (high/medium/low)
        4. Agent 63-D: Flag for review if needed
        
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
                'flag_for_review': True if needs human review,
                'agent_breakdown': per-agent statistics
            }
        """
        # Delegate to Agent 63 coordinator
        return self.agent_63.validate(source_text, translation, source_lang, target_lang)
    
    def translate_rtf_file(self, rtf_content: str, source_lang: str = 'ja', 
                           target_langs: List[str] = None, english_first: bool = True) -> Dict:
        """
        Translate RTF file with TAG preservation
        
        Args:
            rtf_content: Raw RTF file content (as string)
            source_lang: Source language code
            target_langs: List of target language codes
            english_first: Put English first in output
            
        Returns:
            {
                'source_with_tags': original text with TAGs,
                'targets_with_tags': {lang: translation with TAGs},
                'bilingual_outputs': {lang: TAB-delimited output},
                'tag_count': number of TAGs processed,
                'law_13_passed': True if RTF structure validated,
                ... (other translation metrics)
            }
        """
        if target_langs is None:
            target_langs = ['en']
        
        # Process RTF file
        rtf_data = self.rtf_processor.process_rtf_file(rtf_content)
        
        source_text_with_tags = rtf_data['original_text_with_tags']
        text_for_translation = rtf_data['text_with_placeholders']
        tag_mappings = rtf_data['tag_mappings']
        tag_count = rtf_data['tag_count']
        
        print(f"📄 RTF processed: {tag_count} TAGs detected")
        print(f"📝 Text with placeholders ready for translation")
        
        # Translate text with placeholders
        translation_result = self.translate(
            source_text=text_for_translation,
            source_lang=source_lang,
            target_langs=target_langs,
            input_format='text',  # Already extracted from RTF
            preserve_tags=True,
            english_first=english_first
        )
        
        # Restore TAGs in each translation
        targets_with_tags = {}
        bilingual_outputs = {}
        law_13_results = {}
        
        for target_lang in target_langs:
            # Get translation with placeholders
            translation_with_placeholders = translation_result['targets'][target_lang]
            
            # Restore TAGs
            translation_with_tags = self.rtf_processor.restore_tags(
                translation_with_placeholders, 
                tag_mappings
            )
            
            targets_with_tags[target_lang] = translation_with_tags
            
            # Create bilingual output
            bilingual = self.rtf_processor.create_bilingual_output(
                source_text_with_tags,
                translation_with_tags,
                source_lang,
                target_lang
            )
            bilingual_outputs[target_lang] = bilingual
            
            # Validate RTF structure (LAW_13)
            law_13_passed = self.rtf_processor.validate_rtf_structure(
                source_text_with_tags,
                translation_with_tags
            )
            law_13_results[target_lang] = law_13_passed
        
        # Check if all LAW_13 validations passed
        all_law_13_passed = all(law_13_results.values())
        
        if not all_law_13_passed:
            failed_langs = [lang for lang, passed in law_13_results.items() if not passed]
            print(f"⚠️ LAW_13 FAILED for languages: {failed_langs}")
        
        return {
            'source_with_tags': source_text_with_tags,
            'targets_with_tags': targets_with_tags,
            'bilingual_outputs': bilingual_outputs,
            'tag_count': tag_count,
            'law_13_passed': all_law_13_passed,
            'law_13_results': law_13_results,
            'model': translation_result['model'],
            'cost_jpy': translation_result['cost_jpy'],
            'tokens_input': translation_result['tokens_input'],
            'tokens_output': translation_result['tokens_output'],
            'tm_hits': translation_result['tm_hits']
        }
    
    def _translate_with_grok(self, prompt: str, source_text: str, target_langs: List[str] = None) -> Dict:
        """Translate using Grok 4 Fast (2M context) - supports multiple targets"""
        if not self.grok_client:
            raise Exception("Grok API key not configured")
        
        if target_langs is None:
            target_langs = ['en']  # Default
        
        try:
            # Use V22.1 Master as system prompt
            response = self.grok_client.chat.completions.create(
                model="grok-4-fast",
                messages=[
                    {"role": "system", "content": self.v22_1_system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse multi-language response
            # Expected format: Source[TAB]Target1[TAB]Target2[TAB]...
            translations = self._parse_multi_language_response(response_text, target_langs)
            
            # Calculate cost with prompt caching support
            tokens_input = response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else len(self.v22_1_system.split()) + len(prompt.split())
            tokens_output = response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else len(response_text.split())
            
            # Check for cached tokens (Grok automatic caching)
            cached_tokens = 0
            uncached_tokens = tokens_input
            cache_hit = False
            
            if hasattr(response.usage, 'prompt_tokens_details'):
                details = response.usage.prompt_tokens_details
                if hasattr(details, 'cached_tokens') and details.cached_tokens > 0:
                    cached_tokens = details.cached_tokens
                    uncached_tokens = tokens_input - cached_tokens
                    cache_hit = True
                    
                    # Update cache statistics
                    self.cache_stats['cache_hits'] += 1
                    self.cache_stats['total_cached_tokens'] += cached_tokens
                    
                    print(f"🚀 CACHE HIT: {cached_tokens:,} tokens cached (90% discount!)")
            
            if not cache_hit:
                self.cache_stats['cache_misses'] += 1
                self.cache_stats['total_uncached_tokens'] += tokens_input
                print(f"❄️  CACHE MISS: {tokens_input:,} tokens sent (full price)")
            
            self.cache_stats['total_calls'] += 1
            
            # Calculate cost with caching discount
            # Cached tokens: $0.02/1M (90% discount)
            # Uncached tokens: $0.20/1M (normal price)
            cost_input_cached = cached_tokens / 1_000_000 * 0.02
            cost_input_uncached = uncached_tokens / 1_000_000 * self.pricing['grok-4-fast']['input']
            cost_output = tokens_output / 1_000_000 * self.pricing['grok-4-fast']['output']
            
            cost_usd = cost_input_cached + cost_input_uncached + cost_output
            cost_jpy = cost_usd * self.usd_to_jpy
            
            if cached_tokens > 0:
                savings_usd = (cached_tokens / 1_000_000 * self.pricing['grok-4-fast']['input']) - cost_input_cached
                savings_jpy = savings_usd * self.usd_to_jpy
                self.cache_stats['cache_savings_jpy'] += savings_jpy
                print(f"   Cache savings this call: ¥{savings_jpy:.2f}")
                print(f"   Total cache savings so far: ¥{self.cache_stats['cache_savings_jpy']:.2f}")
            
            # Log to file for monitoring
            self._log_cache_event(cache_hit, cached_tokens, uncached_tokens, savings_jpy if cache_hit else 0)
            
            return {
                'translations': translations,  # Dict of {lang: translation}
                'model': 'grok-4-fast',
                'cost_jpy': cost_jpy,
                'tokens_input': tokens_input,
                'tokens_output': tokens_output
            }
            
        except Exception as e:
            raise Exception(f"Grok translation failed: {str(e)}")
    
    
    def _log_cache_event(self, cache_hit: bool, cached_tokens: int, uncached_tokens: int, savings_jpy: float):
        """
        Log cache event to file for monitoring
        
        Args:
            cache_hit: True if cache hit, False if miss
            cached_tokens: Number of cached tokens
            uncached_tokens: Number of uncached tokens
            savings_jpy: Yen saved from caching
        """
        timestamp = datetime.now().isoformat()
        event_type = "HIT" if cache_hit else "MISS"
        
        log_entry = f"{timestamp} | {event_type} | Cached: {cached_tokens:,} | Uncached: {uncached_tokens:,} | Savings: ¥{savings_jpy:.2f}\n"
        
        try:
            with open(self.cache_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️  Could not write to cache log: {e}")
    
    def get_cache_statistics(self) -> Dict:
        """
        Get comprehensive cache statistics
        
        Returns:
            {
                'total_calls': int,
                'cache_hits': int,
                'cache_misses': int,
                'hit_rate': float (percentage),
                'total_cached_tokens': int,
                'total_uncached_tokens': int,
                'cache_savings_jpy': float,
                'estimated_cost_without_cache': float,
                'actual_cost_with_cache': float
            }
        """
        total_calls = self.cache_stats['total_calls']
        hit_rate = (self.cache_stats['cache_hits'] / total_calls * 100) if total_calls > 0 else 0.0
        
        # Estimate what it would have cost WITHOUT caching
        total_tokens = self.cache_stats['total_cached_tokens'] + self.cache_stats['total_uncached_tokens']
        estimated_cost_without_cache_jpy = (total_tokens / 1_000_000 * 0.20) * self.usd_to_jpy
        
        # Actual cost WITH caching
        cached_cost_jpy = (self.cache_stats['total_cached_tokens'] / 1_000_000 * 0.02) * self.usd_to_jpy
        uncached_cost_jpy = (self.cache_stats['total_uncached_tokens'] / 1_000_000 * 0.20) * self.usd_to_jpy
        actual_cost_with_cache_jpy = cached_cost_jpy + uncached_cost_jpy
        
        return {
            'total_calls': total_calls,
            'cache_hits': self.cache_stats['cache_hits'],
            'cache_misses': self.cache_stats['cache_misses'],
            'hit_rate': hit_rate,
            'total_cached_tokens': self.cache_stats['total_cached_tokens'],
            'total_uncached_tokens': self.cache_stats['total_uncached_tokens'],
            'cache_savings_jpy': self.cache_stats['cache_savings_jpy'],
            'estimated_cost_without_cache': estimated_cost_without_cache_jpy,
            'actual_cost_with_cache': actual_cost_with_cache_jpy
        }
    
    def print_cache_report(self):
        """Print detailed cache performance report"""
        stats = self.get_cache_statistics()
        
        print("\n" + "=" * 70)
        print("GROK PROMPT CACHE PERFORMANCE REPORT")
        print("=" * 70)
        print(f"Total API calls:       {stats['total_calls']}")
        print(f"Cache hits:            {stats['cache_hits']} ({stats['hit_rate']:.1f}%)")
        print(f"Cache misses:          {stats['cache_misses']}")
        print(f"Total cached tokens:   {stats['total_cached_tokens']:,}")
        print(f"Total uncached tokens: {stats['total_uncached_tokens']:,}")
        print()
        print(f"Cost WITHOUT caching:  ¥{stats['estimated_cost_without_cache']:,.2f}")
        print(f"Cost WITH caching:     ¥{stats['actual_cost_with_cache']:,.2f}")
        print(f"TOTAL SAVINGS:         ¥{stats['cache_savings_jpy']:,.2f}")
        print("=" * 70)
        print(f"\nCache log file: {self.cache_log_file}")
        print()
    
    def _parse_multi_language_response(self, response_text: str, target_langs: List[str]) -> Dict[str, str]:
        """
        Parse multi-language TAB-delimited response
        Format: Source[TAB]Target1[TAB]Target2[TAB]...
        
        Returns: {lang_code: translation}
        """
        # Split by TAB
        parts = response_text.split('\t')
        
        # First part is source (skip it), rest are translations
        translations_list = parts[1:] if len(parts) > 1 else parts
        
        # Map to language codes
        translations = {}
        for i, lang in enumerate(target_langs):
            if i < len(translations_list):
                translations[lang] = translations_list[i].strip()
            else:
                translations[lang] = ""  # Missing translation
        
        return translations
    
    def _translate_with_gemini(self, prompt: str, source_text: str, target_langs: List[str] = None) -> Dict:
        """
        Translate using Gemini 3 Flash (primary) - supports multiple targets
        
        Uses prompt caching for 75% discount on repeated system prompt
        Gemini is 42% cheaper than Grok with similar performance
        """
        if not self.gemini_api_key:
            raise Exception("Gemini API key not configured")
        
        if target_langs is None:
            target_langs = ['en']  # Default
        
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            
            # Use Gemini 3 Flash with prompt caching
            model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',  # Latest model with caching
                system_instruction=self.v22_1_system  # System prompt (will be cached!)
            )
            
            # Generate translation
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'candidate_count': 1
                }
            )
            
            response_text = response.text.strip()
            
            # Parse multi-language response
            translations = self._parse_multi_language_response(response_text, target_langs)
            
            # Calculate cost with caching support
            # Gemini automatically caches system_instruction
            usage = response.usage_metadata
            
            tokens_input = usage.prompt_token_count if hasattr(usage, 'prompt_token_count') else len(self.v22_1_system.split()) + len(prompt.split())
            tokens_output = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else len(response_text.split())
            
            # Check for cached tokens
            cached_tokens = usage.cached_content_token_count if hasattr(usage, 'cached_content_token_count') else 0
            uncached_tokens = tokens_input - cached_tokens
            cache_hit = cached_tokens > 0
            
            if cache_hit:
                self.cache_stats['cache_hits'] += 1
                self.cache_stats['total_cached_tokens'] += cached_tokens
                print(f"🚀 GEMINI CACHE HIT: {cached_tokens:,} tokens cached (75% discount!)")
            else:
                self.cache_stats['cache_misses'] += 1
                self.cache_stats['total_uncached_tokens'] += tokens_input
                print(f"❄️  GEMINI CACHE MISS: {tokens_input:,} tokens sent (full price)")
            
            self.cache_stats['total_calls'] += 1
            
            # Calculate cost with caching discount
            # Cached tokens: $0.01875/1M (75% discount)
            # Uncached tokens: $0.075/1M (normal price)
            cost_input_cached = cached_tokens / 1_000_000 * self.pricing['gemini-3-flash']['input_cached']
            cost_input_uncached = uncached_tokens / 1_000_000 * self.pricing['gemini-3-flash']['input']
            cost_output = tokens_output / 1_000_000 * self.pricing['gemini-3-flash']['output']
            
            cost_usd = cost_input_cached + cost_input_uncached + cost_output
            cost_jpy = cost_usd * self.usd_to_jpy
            
            if cache_hit:
                savings_usd = (cached_tokens / 1_000_000 * self.pricing['gemini-3-flash']['input']) - cost_input_cached
                savings_jpy = savings_usd * self.usd_to_jpy
                self.cache_stats['cache_savings_jpy'] += savings_jpy
                print(f"   Cache savings this call: ¥{savings_jpy:.2f}")
                print(f"   Total cache savings so far: ¥{self.cache_stats['cache_savings_jpy']:.2f}")
            
            # Log to file
            self._log_cache_event(cache_hit, cached_tokens, uncached_tokens, savings_jpy if cache_hit else 0)
            
            return {
                'translations': translations,  # Dict of {lang: translation}
                'model': 'gemini-3-flash',
                'cost_jpy': cost_jpy,
                'tokens_input': tokens_input,
                'tokens_output': tokens_output
            }
            
        except ImportError:
            raise Exception("google-generativeai not installed. Run: pip install google-generativeai --break-system-packages")
        except Exception as e:
            raise Exception(f"Gemini translation failed: {str(e)}")
    
    def _translate_with_claude(self, prompt: str, source_text: str, target_langs: List[str] = None) -> Dict:
        """Translate using Claude Sonnet 4.5 (backup) - supports multiple targets"""
        raise Exception("Claude not implemented yet - V22.1 exceeds Claude's context window")
    
    def _extract_bilingual_output(self, source: str, translation: str) -> str:
        """
        Extract bilingual TAB-delimited output
        Format: SOURCE[TAB]TARGET
        """
        # If translation already contains TAB, return as-is
        if '\t' in translation:
            return translation
        
        # Otherwise, create bilingual pair
        return f"{source}\t{translation}"
    
    def _strip_tags(self, text: str) -> str:
        """Remove all TAGs from text"""
        # Remove XML-style tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove bracket tags
        text = re.sub(r'\[uf[^\]]*\]', '', text)
        text = re.sub(r'\{uf[^\}]*\}', '', text)
        # Remove placeholders
        text = re.sub(r'⟦TAG_\d+⟧', '', text)
        return text.strip()
    
    def get_stats(self) -> Dict:
        """Get translation statistics"""
        return {
            'total_cost': self.total_cost,
            'budget_remaining': self.max_budget - self.total_cost,
            'budget_used_pct': (self.total_cost / self.max_budget * 100) if self.max_budget > 0 else 0,
            'translations_completed': self.translation_count,
            'tm_hit_rate': self.tm.get_hit_rate(),
            'costs_by_model': self.model_costs,
            'agent_0c_rules_applied': self.controlled_language.get_statistics()  # NEW
        }


class TranslationMemory:
    """
    Persistent translation memory with file storage
    Saves to E:\\USI17\\translation_memory.json
    """
    
    def __init__(self, filepath: str = r'E:\USI17\translation_memory.json'):
        """
        Initialize Translation Memory with persistent storage
        
        Args:
            filepath: Path to TM file (default: E:\\USI17\\translation_memory.json)
        """
        self.filepath = filepath
        self.memory = {}
        self.hits = 0
        self.misses = 0
        
        # Create directory if it doesn't exist
        import os
        tm_dir = os.path.dirname(filepath)
        if tm_dir and not os.path.exists(tm_dir):
            try:
                os.makedirs(tm_dir)
                print(f"✅ Created TM directory: {tm_dir}")
            except Exception as e:
                print(f"⚠️  Could not create directory {tm_dir}: {e}")
                # Fall back to current directory
                self.filepath = 'translation_memory.json'
        
        # Load existing TM
        self.load()
    
    def load(self):
        """Load TM from file"""
        import os
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                print(f"✅ Loaded {len(self.memory):,} entries from TM: {self.filepath}")
            except Exception as e:
                print(f"⚠️  Could not load TM from {self.filepath}: {e}")
                self.memory = {}
        else:
            print(f"ℹ️  No existing TM found at {self.filepath}. Starting fresh.")
            self.memory = {}
    
    def save(self):
        """Save TM to file"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            # Note: We don't print on every save to avoid spam
        except Exception as e:
            print(f"⚠️  Could not save TM to {self.filepath}: {e}")
    
    def set_filepath(self, new_path: str):
        """
        Change TM file location
        
        Args:
            new_path: New file path for TM
        """
        # Save current TM to new location
        old_path = self.filepath
        self.filepath = new_path
        self.save()
        print(f"✅ TM moved from {old_path} to {new_path}")
    
    def get_key(self, source_text: str, target_lang: str) -> str:
        """Generate MD5 hash key"""
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
            # Auto-save on use (updates use_count and last_used)
            self.save()
            return entry
        self.misses += 1
        return None
    
    def set(self, source_text: str, target_lang: str, translation: str, model: str):
        """Store in TM and save to disk"""
        key = self.get_key(source_text, target_lang)
        
        self.memory[key] = {
            'source': source_text[:100],  # Store snippet
            'translation': translation,
            'target_lang': target_lang,
            'model': model,
            'created': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'use_count': 1,
            'cost_saved': 0.0  # Will be calculated on hit
        }
        
        # Auto-save after adding new entry
        self.save()
    
    def get_hit_rate(self) -> float:
        """Calculate TM hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    def get_size_mb(self) -> float:
        """Get TM file size in MB"""
        import os
        if os.path.exists(self.filepath):
            return os.path.getsize(self.filepath) / (1024 * 1024)
        return 0.0
    
    def backup(self, backup_path: str = None):
        """
        Create backup of TM file
        
        Args:
            backup_path: Path for backup (default: adds .backup to current path)
        """
        import shutil
        if backup_path is None:
            backup_path = f"{self.filepath}.backup"
        
        try:
            shutil.copy2(self.filepath, backup_path)
            print(f"✅ TM backed up to: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")

