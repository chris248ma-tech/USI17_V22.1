"""
RTF File Processor for USI17 V22.1
Handles RTF parsing, TAG extraction, and preservation
Implements Agent 46 (InDesign_Tag_Masker) and Agent 47 (Adaptive_Tag_Learner)
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TaggedSegment:
    """Represents a text segment with its extracted TAGs"""
    original_text: str
    text_with_placeholders: str
    tags: List[Dict[str, str]]  # [{id: 'TAG_001', original: '<b>', position: 0}, ...]
    
class RTFProcessor:
    """
    RTF file processing with TAG preservation
    Implements V22.1 Agent 46 and 47 functionality
    """
    
    # TAG patterns to detect and preserve
    TAG_PATTERNS = {
        'indesign_standard': r'<[^>]+>',  # <tag>
        'indesign_closing': r'</[^>]+>',  # </tag>
        'memoq_hybrid_open': r'\[uf[^\]]*\}',  # [uf ufcatid="..."}
        'memoq_hybrid_close': r'\{uf\]',  # {uf]
        'wordfast_tag': r'\{[0-9]+\}',  # {1}, {2}, etc.
        'trados_tag': r'<[a-z]+[0-9]*\s*/?>',  # <g1>, <x1/>, etc.
        'placeholder': r'⟦TAG_\d+⟧',  # Our own placeholders
    }
    
    def __init__(self):
        self.tag_counter = 0
        
    def extract_text_from_rtf(self, rtf_content: str) -> str:
        """
        Extract plain text from RTF, preserving TAGs
        
        Args:
            rtf_content: Raw RTF file content
            
        Returns:
            Plain text with TAGs preserved
        """
        # Simple RTF to text conversion
        # Remove RTF control words (\\keyword)
        text = re.sub(r'\\[a-z]+\d*\s?', '', rtf_content)
        
        # Remove RTF groups ({ })
        text = re.sub(r'[{}]', '', text)
        
        # Decode common RTF special characters
        text = text.replace('\\\'e9', 'é')
        text = text.replace('\\\'e8', 'è')
        text = text.replace('\\\'ea', 'ê')
        text = text.replace('\\\'a0', ' ')
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def detect_tags(self, text: str) -> List[Dict[str, any]]:
        """
        Detect all TAGs in text using V22.1 patterns
        
        Returns:
            List of detected tags with positions
        """
        detected_tags = []
        
        for pattern_name, pattern in self.TAG_PATTERNS.items():
            for match in re.finditer(pattern, text):
                detected_tags.append({
                    'type': pattern_name,
                    'original': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'length': len(match.group(0))
                })
        
        # Sort by position
        detected_tags.sort(key=lambda x: x['start'])
        
        return detected_tags
    
    def extract_tags_with_placeholders(self, text: str) -> TaggedSegment:
        """
        Extract TAGs and replace with numbered placeholders
        Implements Agent 46: InDesign_Tag_Masker
        
        Process:
        1. Detect all TAGs
        2. Replace each with unique placeholder: ⟦TAG_001⟧, ⟦TAG_002⟧, etc.
        3. Store mapping for restoration
        
        Args:
            text: Original text with TAGs
            
        Returns:
            TaggedSegment with text_with_placeholders and tag mapping
        """
        detected_tags = self.detect_tags(text)
        
        if not detected_tags:
            # No TAGs found
            return TaggedSegment(
                original_text=text,
                text_with_placeholders=text,
                tags=[]
            )
        
        # Replace TAGs with placeholders (in reverse order to preserve positions)
        text_with_placeholders = text
        tag_mappings = []
        
        for i, tag in enumerate(reversed(detected_tags)):
            placeholder_id = f"TAG_{self.tag_counter:03d}"
            self.tag_counter += 1
            
            placeholder = f"⟦{placeholder_id}⟧"
            
            # Replace this specific occurrence
            before = text_with_placeholders[:tag['start']]
            after = text_with_placeholders[tag['end']:]
            text_with_placeholders = before + placeholder + after
            
            # Store mapping
            tag_mappings.insert(0, {
                'id': placeholder_id,
                'placeholder': placeholder,
                'original': tag['original'],
                'type': tag['type'],
                'position_in_source': tag['start']
            })
        
        return TaggedSegment(
            original_text=text,
            text_with_placeholders=text_with_placeholders,
            tags=tag_mappings
        )
    
    def restore_tags(self, translated_text: str, tag_mappings: List[Dict]) -> str:
        """
        Restore original TAGs in translated text
        Implements Agent 46: Tag restoration
        
        Process:
        1. Find each placeholder ⟦TAG_XXX⟧ in translated text
        2. Replace with original TAG
        3. Validate all TAGs restored
        
        Args:
            translated_text: Text with placeholders
            tag_mappings: List of tag mappings from extraction
            
        Returns:
            Translated text with original TAGs restored
        """
        result = translated_text
        
        for tag in tag_mappings:
            placeholder = tag['placeholder']
            original_tag = tag['original']
            
            # Replace placeholder with original TAG
            result = result.replace(placeholder, original_tag)
        
        # Verify all placeholders replaced
        remaining = re.findall(r'⟦TAG_\d+⟧', result)
        if remaining:
            print(f"⚠️ Warning: {len(remaining)} placeholders not restored: {remaining}")
        
        return result
    
    def validate_rtf_structure(self, source_rtf: str, target_rtf: str) -> bool:
        """
        Validate RTF structure preservation (LAW_13)
        
        Checks:
        - TAG count matches
        - TAG types match
        - TAG order preserved
        
        Args:
            source_rtf: Original RTF text with TAGs
            target_rtf: Translated RTF text with TAGs
            
        Returns:
            True if structure preserved, False otherwise
        """
        source_tags = self.detect_tags(source_rtf)
        target_tags = self.detect_tags(target_rtf)
        
        # Check 1: TAG count
        if len(source_tags) != len(target_tags):
            print(f"❌ LAW_13 VIOLATION: TAG count mismatch! Source: {len(source_tags)}, Target: {len(target_tags)}")
            return False
        
        # Check 2: TAG types match
        source_types = [t['type'] for t in source_tags]
        target_types = [t['type'] for t in target_tags]
        
        if source_types != target_types:
            print(f"❌ LAW_13 VIOLATION: TAG types mismatch!")
            print(f"   Source: {source_types}")
            print(f"   Target: {target_types}")
            return False
        
        # Check 3: TAG originals match (for simple TAGs like <b>, </b>)
        for i, (src, tgt) in enumerate(zip(source_tags, target_tags)):
            if src['original'] != tgt['original']:
                # Allow some flexibility for content-bearing TAGs
                if src['type'] not in ['memoq_hybrid_open', 'trados_tag']:
                    print(f"❌ LAW_13 VIOLATION: TAG content mismatch at position {i}!")
                    print(f"   Source TAG: {src['original']}")
                    print(f"   Target TAG: {tgt['original']}")
                    return False
        
        print("✅ LAW_13 PASSED: RTF structure preserved")
        return True
    
    def process_rtf_file(self, rtf_content: str) -> Dict:
        """
        Complete RTF file processing workflow
        
        Args:
            rtf_content: Raw RTF file content
            
        Returns:
            {
                'plain_text': extracted text,
                'text_with_placeholders': text ready for translation,
                'tag_mappings': tag restoration data,
                'original_text_with_tags': original with TAGs,
                'tag_count': number of TAGs detected
            }
        """
        # Extract text from RTF
        plain_text = self.extract_text_from_rtf(rtf_content)
        
        # Extract TAGs with placeholders
        tagged = self.extract_tags_with_placeholders(plain_text)
        
        return {
            'plain_text': plain_text,
            'text_with_placeholders': tagged.text_with_placeholders,
            'tag_mappings': tagged.tags,
            'original_text_with_tags': tagged.original_text,
            'tag_count': len(tagged.tags)
        }
    
    def create_bilingual_output(self, source_text: str, target_text: str, 
                                source_lang: str, target_lang: str) -> str:
        """
        Create bilingual TAB-delimited output
        
        Format:
        SourceLang[TAB]TargetLang
        Source text with TAGs[TAB]Translation with TAGs
        
        Args:
            source_text: Source with TAGs
            target_text: Translation with TAGs
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            TAB-delimited bilingual output
        """
        lang_names = {
            'ja': 'Japanese', 'en': 'English', 'de': 'German', 'fr': 'French',
            'es': 'Spanish', 'em': 'Spanish (MX)', 'pt': 'Portuguese',
            'it': 'Italian', 'cz': 'Czech', 'pl': 'Polish', 'tk': 'Turkish',
            'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian',
            'ko': 'Korean', 'cn': 'Chinese (CN)', 'tw': 'Chinese (TW)'
        }
        
        source_name = lang_names.get(source_lang, source_lang.upper())
        target_name = lang_names.get(target_lang, target_lang.upper())
        
        header = f"{source_name}\t{target_name}"
        data = f"{source_text}\t{target_text}"
        
        return f"{header}\n{data}"


# Example usage
if __name__ == "__main__":
    processor = RTFProcessor()
    
    # Test with InDesign TAGs
    test_text = "この<b>ショックキラー</b>は高性能です。シリンダ径は<i>50mm</i>です。"
    
    print("Original text:")
    print(test_text)
    print()
    
    # Extract TAGs
    tagged = processor.extract_tags_with_placeholders(test_text)
    
    print("Text with placeholders:")
    print(tagged.text_with_placeholders)
    print()
    
    print("TAG mappings:")
    for tag in tagged.tags:
        print(f"  {tag['placeholder']} → {tag['original']}")
    print()
    
    # Simulate translation
    translated = "This ⟦TAG_000⟧shock absorber⟦TAG_001⟧ is high performance. Cylinder Bore Size is ⟦TAG_002⟧50 mm⟦TAG_003⟧."
    
    print("Translated (with placeholders):")
    print(translated)
    print()
    
    # Restore TAGs
    restored = processor.restore_tags(translated, tagged.tags)
    
    print("Final (TAGs restored):")
    print(restored)
    print()
    
    # Validate structure
    processor.validate_rtf_structure(test_text, restored)
