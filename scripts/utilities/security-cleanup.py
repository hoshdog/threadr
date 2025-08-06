#!/usr/bin/env python3
"""
Security Cleanup Script - Remove exposed API keys from documentation
This script replaces exposed API keys with secure placeholders
"""

import os
import re
from pathlib import Path

# Exposed keys to replace
EXPOSED_KEYS = {
    # API Keys
    "your-api-key-here": "your-api-key-here",
    "your-secondary-api-key-here": "your-secondary-api-key-here",
    
    # OpenAI keys pattern
    r"sk-proj-YOUR-OPENAI-API-KEY-HERE": "sk-proj-YOUR-OPENAI-API-KEY-HERE",
    r"sk-YOUR-OPENAI-API-KEY-HERE": "sk-YOUR-OPENAI-API-KEY-HERE",
    
    # Redis URLs with passwords
    r"redis://default:YOUR-REDIS-PASSWORD@redis.railway.internal:6379": "redis://default:YOUR-REDIS-PASSWORD@redis.railway.internal:6379",
}

# File extensions to process
EXTENSIONS = ['.md', '.txt', '.html', '.js', '.py', '.json', '.yml', '.yaml']

def replace_exposed_keys(file_path):
    """Replace exposed keys in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements = 0
        
        # Replace exact matches
        for exposed_key, replacement in EXPOSED_KEYS.items():
            if exposed_key.startswith('r"') or exposed_key.startswith('r\''):
                # Regex pattern
                pattern = exposed_key[2:-1]  # Remove r" or r'
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    replacements += len(matches)
            else:
                # Exact string
                if exposed_key in content:
                    count = content.count(exposed_key)
                    content = content.replace(exposed_key, replacement)
                    replacements += count
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[CLEANED] {file_path.name}: {replacements} keys replaced")
            return replacements
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Processing {file_path}: {e}")
        return 0

def main():
    """Main cleanup function"""
    print("Security Cleanup Script - Removing Exposed API Keys")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    total_files = 0
    total_replacements = 0
    cleaned_files = []
    
    # Process all files
    for ext in EXTENSIONS:
        for file_path in project_root.rglob(f"*{ext}"):
            # Skip .git and node_modules
            if '.git' in file_path.parts or 'node_modules' in file_path.parts:
                continue
            
            # Skip .env files (they should not be in git anyway)
            if file_path.name.startswith('.env') and not file_path.name.endswith('.example'):
                continue
            
            total_files += 1
            replacements = replace_exposed_keys(file_path)
            if replacements > 0:
                total_replacements += replacements
                cleaned_files.append(str(file_path.relative_to(project_root)))
    
    # Summary
    print("\n" + "=" * 60)
    print("SECURITY CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Total files scanned: {total_files}")
    print(f"Files cleaned: {len(cleaned_files)}")
    print(f"Total keys replaced: {total_replacements}")
    
    if cleaned_files:
        print("\nFiles cleaned:")
        for file in sorted(cleaned_files):
            print(f"  - {file}")
    
    print("\nIMPORTANT NEXT STEPS:")
    print("1. Rotate your OpenAI API key immediately in the OpenAI dashboard")
    print("2. Generate new API keys for your application")
    print("3. Update Railway/Vercel environment variables with new keys")
    print("4. Commit these changes to prevent re-exposure")
    print("\nSecurity cleanup complete!")

if __name__ == "__main__":
    main()