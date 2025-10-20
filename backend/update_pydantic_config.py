#!/usr/bin/env python3
"""Script to update Pydantic V1 Config to V2 ConfigDict."""

import os
import re
import sys

def update_pydantic_config(file_path):
    """Update a single file from Config class to ConfigDict."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add ConfigDict import if not present
    if 'from pydantic import' in content and 'ConfigDict' not in content:
        content = re.sub(
            r'from pydantic import ([^)]+)',
            r'from pydantic import \1, ConfigDict',
            content
        )
    
    # Replace class Config with model_config = ConfigDict
    # This regex handles multiline Config classes
    config_pattern = r'    class Config:\s*\n((?:        [^\n]*\n)*)'
    
    def replace_config(match):
        config_content = match.group(1)
        # Extract the content inside the Config class
        config_dict_content = config_content.replace('        ', '    ')
        return f'    model_config = ConfigDict(\n{config_dict_content}    )'
    
    content = re.sub(config_pattern, replace_config, content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file_path}")

def main():
    # Get the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all DTO files
    dto_files = []
    for root, dirs, files in os.walk(os.path.join(backend_dir, 'app', 'application', 'dtos')):
        for file in files:
            if file.endswith('_dtos.py'):
                dto_files.append(os.path.join(root, file))
    
    print(f"Found {len(dto_files)} DTO files to update:")
    for file_path in dto_files:
        update_pydantic_config(file_path)
    
    print("All DTO files updated!")

if __name__ == "__main__":
    main()