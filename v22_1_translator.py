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
            'grok-4-fast': {'input': 0.20, 'output': 0.50},
            'gemini-3-flash': {'input': 0.075, 'output': 0.30},
            'claude-sonnet-4-5': {'input': 3.00, 'output': 15.00}
        }
        
        # Exchange rate USD to JPY
        self.usd_to_jpy = 152.0
        
        # RTF processor for TAG preservation
        self.rtf_processor = RTFProcessor()
    
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
        
        # Translate with Grok (primary), fallback to Gemini/Claude
        try:
            result = self._translate_with_grok(prompt, source_text, remaining_targets)
            model_used = 'grok'
        except Exception as e:
            print(f"⚠️ Grok failed: {e}, trying Gemini...")
            try:
                result = self._translate_with_gemini(prompt, source_text, remaining_targets)
                model_used = 'gemini'
            except Exception as e2:
                print(f"⚠️ Gemini failed: {e2}, trying Claude...")
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
            'tm_hit_rate': (tm_hits / len(target_langs) * 100) if len(target_langs) > 0 else 0
        }
    
    def _build_v22_1_prompt(self, source_text: str, source_lang: str, target_lang: str,
                            input_format: str, preserve_tags: bool) -> str:
        """
        Build complete V22.1 translation prompt (single target - for backwards compatibility)
        """
        return self._build_v22_1_multi_prompt(source_text, source_lang, [target_lang], 
                                              input_format, preserve_tags)
    
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
            
            # Calculate cost
            tokens_input = response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else len(self.v22_1_system.split()) + len(prompt.split())
            tokens_output = response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else len(response_text.split())
            
            cost_usd = (tokens_input / 1_000_000 * self.pricing['grok-4-fast']['input'] +
                       tokens_output / 1_000_000 * self.pricing['grok-4-fast']['output'])
            cost_jpy = cost_usd * self.usd_to_jpy
            
            return {
                'translations': translations,  # Dict of {lang: translation}
                'model': 'grok-4-fast',
                'cost_jpy': cost_jpy,
                'tokens_input': tokens_input,
                'tokens_output': tokens_output
            }
            
        except Exception as e:
            raise Exception(f"Grok translation failed: {str(e)}")
    
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
        """Translate using Gemini 3 Flash (backup) - supports multiple targets"""
        raise Exception("Gemini not implemented yet - V22.1 exceeds Gemini's practical limit")
    
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
            'costs_by_model': self.model_costs
        }


class TranslationMemory:
    """Simple translation memory with MD5 hashing"""
    
    def __init__(self):
        self.memory = {}
        self.hits = 0
        self.misses = 0
    
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
            return entry
        self.misses += 1
        return None
    
    def set(self, source_text: str, target_lang: str, translation: str, model: str):
        """Store in TM"""
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
    
    def get_hit_rate(self) -> float:
        """Calculate TM hit rate"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
