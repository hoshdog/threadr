#!/usr/bin/env python3
"""Simple TOML validation by parsing"""

import sys

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def validate_toml_simple(filepath):
    """Basic TOML validation"""
    print(f"🔍 Checking {filepath} structure...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for common TOML syntax issues
    issues = []
    
    # Check if providers is an array
    if '[providers]' in content and 'python = ' in content:
        issues.append("❌ [providers] should not be a table section")
    elif 'providers = [' in content:
        print("✅ providers is correctly defined as an array")
    
    # Check for proper quotes
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if '=' in line and not line.strip().startswith('#'):
            # Check for unquoted strings that need quotes
            if 'true' not in line and 'false' not in line and '[' not in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    value = parts[1].strip()
                    if value and not (value.startswith('"') or value.startswith("'") or value.isdigit()):
                        if not value.startswith('['):
                            issues.append(f"Line {i}: Possible unquoted string: {line.strip()}")
    
    # Check brackets balance
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    if open_brackets != close_brackets:
        issues.append(f"❌ Bracket mismatch: {open_brackets} [ vs {close_brackets} ]")
    
    if not issues:
        print("✅ Basic TOML structure looks valid!")
        
        # Show key configurations
        print("\n📋 Key configurations found:")
        if 'providers = ["python"]' in content:
            print("   ✅ Python provider configured")
        if 'workDir = "backend"' in content:
            print("   ✅ Working directory set to backend")
        if 'main_minimal' in content:
            print("   ✅ main_minimal.py referenced")
        
        return True
    else:
        print("\n❌ Found potential issues:")
        for issue in issues:
            print(f"   {issue}")
        return False

if __name__ == "__main__":
    if validate_toml_simple("nixpacks.toml"):
        print("\n✅ nixpacks.toml appears valid!")
        print("\n📌 Next step: Commit and push to trigger Railway deployment")
    else:
        print("\n❌ Fix the issues above before deploying!")