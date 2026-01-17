#!/usr/bin/env python3
"""
Extract USI17 V22.1 Glossary to CSV
Converts 509 terms from V22.1 Master to editable CSV format
"""

import csv
import re

def extract_glossary(v22_1_path, output_csv):
    """Extract all 509 glossary terms to CSV"""
    
    with open(v22_1_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all TERM entries
    term_pattern = r'TERM_(\d+):(.*?)(?=TERM_\d+:|$)'
    terms = re.findall(term_pattern, content, re.DOTALL)
    
    glossary_data = []
    
    for term_id, term_content in terms:
        # Extract fields
        ja = re.search(r'JA:\s*(.+)', term_content)
        en = re.search(r'EN:\s*(.+)', term_content)
        de = re.search(r'DE:\s*(.+)', term_content)
        fr = re.search(r'FR:\s*(.+)', term_content)
        es = re.search(r'ES:\s*(.+)', term_content)
        pt = re.search(r'PT:\s*(.+)', term_content)
        it = re.search(r'IT:\s*(.+)', term_content)
        cz = re.search(r'CZ:\s*(.+)', term_content)
        pl = re.search(r'PL:\s*(.+)', term_content)
        tk = re.search(r'TK:\s*(.+)', term_content)
        vi = re.search(r'VI:\s*(.+)', term_content)
        th = re.search(r'TH:\s*(.+)', term_content)
        id_lang = re.search(r'ID:\s*(.+)', term_content)
        ko = re.search(r'KO:\s*(.+)', term_content)
        cn = re.search(r'CN:\s*(.+)', term_content)
        tw = re.search(r'TW:\s*(.+)', term_content)
        mx = re.search(r'MX:\s*(.+)', term_content)
        
        domain = re.search(r'DOMAIN:\s*(.+)', term_content)
        locked = re.search(r'LOCKED:\s*(.+)', term_content)
        
        if ja and en:  # Minimum requirement
            glossary_data.append({
                'term_id': f'TERM_{term_id.zfill(3)}',
                'japanese': ja.group(1).strip(),
                'english': en.group(1).strip() if en else '',
                'german': de.group(1).strip() if de else '',
                'french': fr.group(1).strip() if fr else '',
                'spanish': es.group(1).strip() if es else '',
                'portuguese': pt.group(1).strip() if pt else '',
                'italian': it.group(1).strip() if it else '',
                'czech': cz.group(1).strip() if cz else '',
                'polish': pl.group(1).strip() if pl else '',
                'turkish': tk.group(1).strip() if tk else '',
                'vietnamese': vi.group(1).strip() if vi else '',
                'thai': th.group(1).strip() if th else '',
                'indonesian': id_lang.group(1).strip() if id_lang else '',
                'korean': ko.group(1).strip() if ko else '',
                'chinese_simplified': cn.group(1).strip() if cn else '',
                'chinese_traditional': tw.group(1).strip() if tw else '',
                'mexican_spanish': mx.group(1).strip() if mx else '',
                'domain': domain.group(1).strip() if domain else '',
                'locked': locked.group(1).strip() if locked else 'true',
            })
    
    # Write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['term_id', 'japanese', 'english', 'german', 'french', 
                     'spanish', 'portuguese', 'italian', 'czech', 'polish',
                     'turkish', 'vietnamese', 'thai', 'indonesian', 'korean',
                     'chinese_simplified', 'chinese_traditional', 'mexican_spanish',
                     'domain', 'locked']
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(glossary_data)
    
    print(f"✅ Extracted {len(glossary_data)} terms to {output_csv}")
    return len(glossary_data)

if __name__ == "__main__":
    count = extract_glossary(
        'USI17_V22_1_MASTER.txt',
        'USI17_GLOSSARY_509_TERMS.csv'
    )
    print(f"📊 Total terms: {count}")
