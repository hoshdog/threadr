#!/usr/bin/env python3
"""Validate TOML syntax before deployment"""

import sys
import tomli

def validate_toml(filepath):
    """Validate TOML file syntax"""
    print(f"🔍 Validating {filepath}...")
    
    try:
        with open(filepath, 'rb') as f:
            data = tomli.load(f)
        
        print("✅ TOML syntax is valid!")
        print("\n📋 Configuration summary:")
        
        # Check providers
        if 'providers' in data:
            print(f"   Providers: {data['providers']}")
        
        # Check phases
        for phase in ['build', 'setup']:
            if f'phases' in data and phase in data['phases']:
                print(f"   Phase '{phase}': configured")
                if 'workDir' in data['phases'][phase]:
                    print(f"      workDir: {data['phases'][phase]['workDir']}")
        
        # Check start command
        if 'start' in data:
            print(f"   Start command: {data['start'].get('cmd', 'NOT SET')[:60]}...")
            
        return True
        
    except tomli.TOMLDecodeError as e:
        print(f"❌ TOML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    import os
    
    # First check if tomli is installed
    try:
        import tomli
    except ImportError:
        print("Installing tomli for TOML validation...")
        os.system(f"{sys.executable} -m pip install tomli")
        import tomli
    
    # Validate nixpacks.toml
    if validate_toml("nixpacks.toml"):
        print("\n✅ nixpacks.toml is ready for deployment!")
    else:
        print("\n❌ Fix the errors above before deploying!")