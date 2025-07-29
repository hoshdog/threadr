#!/usr/bin/env python3
"""
Threadr Deployment Helper Script
This script helps automate some deployment preparation steps.
"""

import os
import shutil
import sys
import json
import re

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*50)
    print(f" {text}")
    print("="*50 + "\n")

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def prepare_backend():
    """Prepare backend for deployment"""
    print_header("Preparing Backend")
    
    # Copy production main.py
    if check_file_exists("backend/main_production.py"):
        shutil.copy2("backend/main_production.py", "backend/main.py")
        print("✓ Copied main_production.py to main.py")
    else:
        print("✗ main_production.py not found!")
        return False
    
    # Remove sensitive files
    sensitive_files = ["openaiKey.key", "backend/.openai_key", ".env"]
    for file in sensitive_files:
        if check_file_exists(file):
            os.remove(file)
            print(f"✓ Removed {file}")
    
    return True

def update_frontend_config(backend_url=None):
    """Update frontend configuration"""
    print_header("Updating Frontend Configuration")
    
    config_path = "frontend/config.js"
    if not check_file_exists(config_path):
        print("✗ frontend/config.js not found!")
        return False
    
    if backend_url:
        # Read the config file
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update the URL
        pattern = r"'https://YOUR-APP-NAME\.up\.railway\.app'"
        replacement = f"'{backend_url}'"
        new_content = re.sub(pattern, replacement, content)
        
        # Write back
        with open(config_path, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Updated API URL to: {backend_url}")
    else:
        print("! No backend URL provided. Remember to update frontend/config.js manually!")
    
    return True

def check_requirements():
    """Check if all required files exist"""
    print_header("Checking Requirements")
    
    required_files = [
        "backend/main.py",
        "backend/requirements.txt",
        "frontend/index.html",
        "frontend/config.js",
        ".gitignore",
        "railway.json",
        "Procfile"
    ]
    
    all_good = True
    for file in required_files:
        if check_file_exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING!")
            all_good = False
    
    return all_good

def create_env_template():
    """Create an environment variable template"""
    print_header("Creating Environment Template")
    
    env_template = """# Threadr Environment Variables
# Copy this to Railway's environment variables

OPENAI_API_KEY=your-openai-api-key-here
"""
    
    with open(".env.example", "w") as f:
        f.write(env_template)
    
    print("✓ Created .env.example template")
    return True

def main():
    """Main deployment preparation function"""
    print("\n🚀 Threadr Deployment Preparation Script")
    print("This script will help prepare your application for deployment.\n")
    
    # Step 1: Prepare backend
    if not prepare_backend():
        print("\n❌ Backend preparation failed!")
        sys.exit(1)
    
    # Step 2: Get backend URL if available
    backend_url = input("\nEnter your Railway backend URL (or press Enter to skip): ").strip()
    if backend_url and not backend_url.startswith("https://"):
        backend_url = f"https://{backend_url}"
    
    # Step 3: Update frontend config
    if not update_frontend_config(backend_url):
        print("\n❌ Frontend configuration update failed!")
        sys.exit(1)
    
    # Step 4: Create env template
    create_env_template()
    
    # Step 5: Check all requirements
    if not check_requirements():
        print("\n❌ Some required files are missing!")
        sys.exit(1)
    
    # Success!
    print_header("Deployment Preparation Complete!")
    print("Next steps:")
    print("1. Review and commit your changes")
    print("2. Push to GitHub")
    print("3. Deploy to Railway and Vercel")
    print("4. Follow the DEPLOYMENT_CHECKLIST.md")
    print("\nGood luck with your deployment! 🎉")

if __name__ == "__main__":
    main()