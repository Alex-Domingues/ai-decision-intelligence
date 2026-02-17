#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replace Mid-Market with Corporate in all files"""

import os

files_to_update = [
    'data/processed/saas_financial_snapshot.csv',
    'notebooks/00_data_treatment_financial_snapshot.ipynb',
    'notebooks/01_business_eda_enhanced.ipynb',
    'notebooks/02_decision_engine.ipynb'
]

replacements = [
    ('Mid‑Market', 'Corporate'),  # Non-breaking hyphen
    ('Mid-Market', 'Corporate'),  # Normal hyphen
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        print(f"⚠️  {filepath} not found, skipping")
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            count = original_content.count('Mid‑Market') + original_content.count('Mid-Market')
            print(f"✓ Updated {filepath} ({count} replacements)")
        else:
            print(f"• {filepath} - no changes needed")
    
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

print("\n✅ Replacement complete!")
