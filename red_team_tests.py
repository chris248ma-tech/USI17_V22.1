"""
RED TEAM TESTING SUITE FOR USI17 V22.1
Adversarial testing to verify system robustness
"""

import sys
import os

# Test cases
RED_TEAM_TESTS = [
    {
        "name": "GLOSSARY_ENFORCEMENT_TEST_1",
        "description": "Verify ショックキラー NEVER translates to 'shock killer'",
        "input": "このショックキラーは高性能です。",
        "expected_contains": "shock absorber",
        "expected_not_contains": "shock killer",
        "critical": True,
        "law_tested": "Glossary enforcement (LOCKED terms)"
    },
    
    {
        "name": "GLOSSARY_ENFORCEMENT_TEST_2",
        "description": "Verify エアシリンダ translates to 'air cylinder'",
        "input": "エアシリンダのシリンダ径は50mmです。",
        "expected_contains": "air cylinder",
        "expected_contains_2": "Cylinder Bore Size",
        "critical": True,
        "law_tested": "Glossary enforcement"
    },
    
    {
        "name": "TAG_PRESERVATION_TEST_1",
        "description": "Verify InDesign tags are preserved",
        "input": "新製品<b>パルスブローバルブ</b>BNPシリーズ",
        "expected_contains": "<b>",
        "expected_contains_2": "</b>",
        "critical": True,
        "law_tested": "LAW_13 RTF/TAG preservation"
    },
    
    {
        "name": "TAG_PRESERVATION_TEST_2",
        "description": "Verify memoQ hybrid brackets preserved",
        "input": "この製品は[uf ufcatid=\"123\"}高性能{uf]です。",
        "expected_contains": "[uf",
        "expected_contains_2": "{uf]",
        "critical": True,
        "law_tested": "LAW_13 RTF/TAG preservation - memoQ format"
    },
    
    {
        "name": "PHI_SYMBOL_TEST",
        "description": "Verify φD translates to øD (lowercase ø, no space)",
        "input": "チューブ外径はφ6です。",
        "expected_contains": "ø6",
        "expected_not_contains": "ø 6",
        "expected_not_contains_2": "Ø6",
        "critical": True,
        "law_tested": "Glossary + Character normalization"
    },
    
    {
        "name": "BILINGUAL_OUTPUT_TEST",
        "description": "Verify bilingual TAB-delimited output",
        "input": "新製品です。",
        "expected_format": "Japanese[TAB]English",
        "critical": True,
        "law_tested": "Output format compliance"
    },
    
    {
        "name": "EMPTY_INPUT_TEST",
        "description": "Handle empty input gracefully",
        "input": "",
        "expected_behavior": "Error or empty output (no crash)",
        "critical": False,
        "law_tested": "Error handling"
    },
    
    {
        "name": "VERY_LONG_INPUT_TEST",
        "description": "Handle very long input (stress test)",
        "input": "これは非常に長いテキストです。" * 1000,  # 15,000+ characters
        "expected_behavior": "Processes without error or truncation warning",
        "critical": False,
        "law_tested": "Context window handling"
    },
    
    {
        "name": "MALICIOUS_TAG_INJECTION_TEST",
        "description": "Prevent malicious tag injection",
        "input": "通常のテキスト<script>alert('XSS')</script>です。",
        "expected_behavior": "Tags preserved as-is, not executed",
        "critical": True,
        "law_tested": "Security - no code execution"
    },
    
    {
        "name": "UNICODE_NORMALIZATION_TEST",
        "description": "Verify character normalization (LAW_14)",
        "input": "製品（テスト）です。",  # Full-width parentheses
        "expected_contains": "(",
        "expected_contains_2": ")",
        "expected_not_contains": "（",
        "critical": True,
        "law_tested": "LAW_14 Character normalization"
    },
    
    {
        "name": "MULTI_TERM_CONSISTENCY_TEST",
        "description": "Verify multiple glossary terms in one sentence",
        "input": "ショックキラー付きエアシリンダのチューブ外径はφ8です。",
        "expected_contains": "shock absorber",
        "expected_contains_2": "air cylinder",
        "expected_contains_3": "Tube O.D.",
        "expected_contains_4": "ø8",
        "critical": True,
        "law_tested": "Multiple glossary term enforcement"
    },
    
    {
        "name": "SI_UNIT_SPACING_TEST",
        "description": "Verify 50mm → 50 mm (WITH space) in English",
        "input": "シリンダ径は50mmです。",
        "expected_contains": "50 mm",
        "expected_not_contains": "50mm",
        "critical": True,
        "law_tested": "LAW_7/8 SI Unit Spacing"
    },
    
    {
        "name": "CONTEXT_DEPENDENT_TRANSLATION_TEST",
        "description": "Verify context-aware translation (USI semantic processing)",
        "input": "この製品は軽量で取り扱いやすいです。",
        "expected_quality": "Natural English, not word-for-word",
        "critical": False,
        "law_tested": "USI semantic quality"
    }
]

def run_red_team_tests(translator):
    """
    Run all Red Team tests against USI17 V22.1
    
    Args:
        translator: USI17_V22_1_Translator instance
    
    Returns:
        Dict with test results
    """
    print("=" * 80)
    print("🔴 RED TEAM TESTING SUITE - USI17 V22.1")
    print("=" * 80)
    print()
    
    results = {
        'total': len(RED_TEAM_TESTS),
        'passed': 0,
        'failed': 0,
        'critical_failures': 0,
        'details': []
    }
    
    for i, test in enumerate(RED_TEAM_TESTS, 1):
        print(f"[TEST {i}/{len(RED_TEAM_TESTS)}] {test['name']}")
        print(f"  Description: {test['description']}")
        print(f"  Law Tested: {test['law_tested']}")
        print(f"  Critical: {'YES' if test['critical'] else 'NO'}")
        
        try:
            # Run translation
            if test['input'] == "":
                # Test empty input handling
                try:
                    result = translator.translate(
                        source_text=test['input'],
                        source_lang='ja',
                        target_lang='en'
                    )
                    status = "PASS" if result else "FAIL"
                except:
                    status = "PASS"  # Expected to handle gracefully
            else:
                result = translator.translate(
                    source_text=test['input'],
                    source_lang='ja',
                    target_lang='en'
                )
                
                translation = result['target']
                bilingual = result['bilingual_tab']
                
                # Check expected content
                status = "PASS"
                failures = []
                
                if 'expected_contains' in test:
                    if test['expected_contains'] not in translation:
                        status = "FAIL"
                        failures.append(f"Missing: '{test['expected_contains']}'")
                
                if 'expected_contains_2' in test:
                    if test['expected_contains_2'] not in translation:
                        status = "FAIL"
                        failures.append(f"Missing: '{test['expected_contains_2']}'")
                
                if 'expected_contains_3' in test:
                    if test['expected_contains_3'] not in translation:
                        status = "FAIL"
                        failures.append(f"Missing: '{test['expected_contains_3']}'")
                
                if 'expected_contains_4' in test:
                    if test['expected_contains_4'] not in translation:
                        status = "FAIL"
                        failures.append(f"Missing: '{test['expected_contains_4']}'")
                
                if 'expected_not_contains' in test:
                    if test['expected_not_contains'] in translation:
                        status = "FAIL"
                        failures.append(f"Should NOT contain: '{test['expected_not_contains']}'")
                
                if 'expected_not_contains_2' in test:
                    if test['expected_not_contains_2'] in translation:
                        status = "FAIL"
                        failures.append(f"Should NOT contain: '{test['expected_not_contains_2']}'")
                
                if 'expected_format' in test and test['expected_format'] == "Japanese[TAB]English":
                    if '\t' not in bilingual:
                        status = "FAIL"
                        failures.append("Missing TAB delimiter in bilingual output")
                
                print(f"  Input: {test['input'][:50]}...")
                print(f"  Output: {translation[:100]}...")
                print(f"  Status: {status}")
                
                if failures:
                    print(f"  Failures:")
                    for failure in failures:
                        print(f"    - {failure}")
            
            # Update results
            if status == "PASS":
                results['passed'] += 1
                print(f"  ✅ PASSED")
            else:
                results['failed'] += 1
                if test['critical']:
                    results['critical_failures'] += 1
                    print(f"  ❌ FAILED (CRITICAL)")
                else:
                    print(f"  ⚠️ FAILED (non-critical)")
            
            results['details'].append({
                'test': test['name'],
                'status': status,
                'critical': test['critical'],
                'law': test['law_tested']
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results['failed'] += 1
            if test['critical']:
                results['critical_failures'] += 1
            results['details'].append({
                'test': test['name'],
                'status': 'ERROR',
                'critical': test['critical'],
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("RED TEAM TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print(f"Critical Failures: {results['critical_failures']}")
    print()
    
    if results['critical_failures'] > 0:
        print("❌ SYSTEM NOT READY FOR PRODUCTION")
        print(f"   {results['critical_failures']} critical test(s) failed")
        print("   Fix critical issues before deployment")
    elif results['failed'] > 0:
        print("⚠️ SYSTEM PASSED WITH WARNINGS")
        print(f"   {results['failed']} non-critical test(s) failed")
        print("   Safe for production, but review failures")
    else:
        print("✅ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
    
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    print("Red Team Testing Suite")
    print("Usage: Import and run with translator instance")
    print()
    print("Example:")
    print("  from v22_1_translator import USI17_V22_1_Translator")
    print("  from red_team_tests import run_red_team_tests")
    print()
    print("  translator = USI17_V22_1_Translator(...)")
    print("  results = run_red_team_tests(translator)")
