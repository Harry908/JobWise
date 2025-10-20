#!/usr/bin/env python3
"""Script to properly fix Pydantic Config to ConfigDict syntax errors."""

import os
import re

def fix_pydantic_config_syntax():
    """Fix syntax errors in DTO files."""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all DTO files
    dto_files = []
    for root, dirs, files in os.walk(os.path.join(backend_dir, 'app', 'application', 'dtos')):
        for file in files:
            if file.endswith('_dtos.py'):
                dto_files.append(os.path.join(root, file))
    
    for file_path in dto_files:
        print(f"Fixing {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the malformed ConfigDict syntax
        # Pattern: model_config = ConfigDict(\n    json_schema_extra = {\n        ... \n    )\n)        }
        pattern = r'model_config = ConfigDict\(\n\s*json_schema_extra\s*=\s*\{([^}]+)\}\n\s*\)\s*\}'
        
        def fix_config(match):
            inner_content = match.group(1)
            return f'model_config = ConfigDict(\n        json_schema_extra={{{inner_content}}}\n    )'
        
        content = re.sub(pattern, fix_config, content, flags=re.DOTALL)
        
        # Also fix cases where the json_schema_extra is not properly nested
        content = re.sub(
            r'model_config = ConfigDict\(\n([^}]+)\n\s*\)\s*\}',
            r'model_config = ConfigDict(\n\1\n    )',
            content,
            flags=re.DOTALL
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_pydantic_config_syntax()
    print("All syntax errors fixed!")