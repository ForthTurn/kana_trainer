#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析 JMdict 数据结构
"""

import json
import os

def analyze_term_bank(file_path, max_samples=5):
    """分析词条文件的数据结构"""
    print(f"分析文件: {file_path}")
    print("=" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        terms_data = json.load(f)
    
    print(f"总词条数: {len(terms_data)}")
    print()
    
    for i in range(min(max_samples, len(terms_data))):
        term_info = terms_data[i]
        print(f"词条 {i+1}:")
        print(f"  长度: {len(term_info)}")
        
        for j, field in enumerate(term_info):
            field_type = type(field).__name__
            if isinstance(field, str) and len(field) > 50:
                field_preview = field[:50] + "..."
            elif isinstance(field, (list, dict)):
                field_preview = str(field)[:100] + "..." if len(str(field)) > 100 else str(field)
            else:
                field_preview = str(field)
            
            print(f"    [{j}] {field_type}: {field_preview}")
        
        print()

if __name__ == "__main__":
    # 分析第一个词条文件
    term_bank_file = "JMdict_english_with_examples/term_bank_1.json"
    if os.path.exists(term_bank_file):
        analyze_term_bank(term_bank_file, max_samples=3)
    else:
        print(f"文件不存在: {term_bank_file}")
