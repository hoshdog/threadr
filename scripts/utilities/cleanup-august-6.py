#!/usr/bin/env python3
"""
Threadr Project Cleanup Script - August 6, 2025
Archives redundant code and prepares for production
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

def create_archive_structure():
    """Create archive directory structure"""
    archive_dir = PROJECT_ROOT / "archive"
    
    # Create subdirectories
    dirs_to_create = [
        archive_dir / "frontend-alpine-legacy",
        archive_dir / "railway-configs",
        archive_dir / "old-env-files",
        archive_dir / "duplicate-docs",
        archive_dir / "old-backend-versions"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {dir_path.relative_to(PROJECT_ROOT)}")
    
    return archive_dir

def archive_alpine_frontend():
    """Archive the Alpine.js frontend"""
    source = PROJECT_ROOT / "frontend"
    dest = PROJECT_ROOT / "archive" / "frontend-alpine-legacy"
    
    if source.exists():
        # Keep a README in the original location
        readme_content = """# Frontend Directory - ARCHIVED

The Alpine.js frontend has been archived to `/archive/frontend-alpine-legacy/`

## Current Production Frontend
- **Technology**: Next.js
- **Location**: `/threadr-nextjs/`
- **URL**: https://threadr-plum.vercel.app

## Why Archived?
- Alpine.js version hit architectural limits (260KB file)
- Next.js provides better scalability and performance
- Migration completed August 2025

See `/archive/frontend-alpine-legacy/` for the original code.
"""
        
        # Write README before moving
        readme_path = source / "README_ARCHIVED.md"
        readme_path.write_text(readme_content)
        
        print(f"[ARCHIVE] Archiving Alpine.js frontend...")
        # Don't move, just note it needs manual action
        print(f"   ACTION REQUIRED: Manually move frontend/ to archive/frontend-alpine-legacy/")
        return True
    else:
        print("[WARNING] Frontend directory not found")
        return False

def cleanup_railway_configs():
    """Remove Railway-specific configuration files"""
    railway_files = [
        PROJECT_ROOT / "nixpacks.toml",
        PROJECT_ROOT / "railway.json",
        PROJECT_ROOT / "railway.toml",
        PROJECT_ROOT / "Procfile",
        PROJECT_ROOT / "backend" / "nixpacks.toml",
        PROJECT_ROOT / "backend" / "railway.json"
    ]
    
    archive_dir = PROJECT_ROOT / "archive" / "railway-configs"
    
    for file_path in railway_files:
        if file_path.exists():
            dest = archive_dir / file_path.name
            print(f"[ARCHIVE] Archiving: {file_path.name} -> archive/railway-configs/")
            # Note action needed
            print(f"   ACTION: Move {file_path.relative_to(PROJECT_ROOT)} to {dest.relative_to(PROJECT_ROOT)}")

def identify_env_files():
    """Identify environment files with old URLs"""
    env_files = list(PROJECT_ROOT.glob("**/.env*"))
    
    print("\n[SCAN] Environment Files Found:")
    for env_file in env_files:
        if env_file.is_file():
            content = env_file.read_text()
            if "railway" in content.lower():
                print(f"   [WARNING] {env_file.relative_to(PROJECT_ROOT)} - Contains Railway references")
            else:
                print(f"   [OK] {env_file.relative_to(PROJECT_ROOT)}")

def check_security_issues():
    """Check for exposed API keys"""
    print("\n[SECURITY] Security Audit:")
    
    # Check for exposed keys in tracked files
    sensitive_files = [
        PROJECT_ROOT / "backend" / ".env.production",
        PROJECT_ROOT / "frontend" / "public" / "config.js"
    ]
    
    for file_path in sensitive_files:
        if file_path.exists():
            content = file_path.read_text()
            if "sk-proj-" in content or "sk_live_" in content:
                print(f"   [CRITICAL] Real API key found in {file_path.relative_to(PROJECT_ROOT)}")
            elif "your-api-key-here" in content:
                print(f"   [WARNING] Placeholder found in {file_path.relative_to(PROJECT_ROOT)}")
            else:
                print(f"   [OK] {file_path.relative_to(PROJECT_ROOT)} appears safe")

def generate_cleanup_report():
    """Generate a cleanup report"""
    report = f"""
# Cleanup Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Actions Required

### 1. Security (IMMEDIATE)
- [ ] Rotate OpenAI API key in OpenAI dashboard
- [ ] Remove backend/.env.production from Git
- [ ] Update .gitignore to exclude .env.production

### 2. Manual Archiving
- [ ] Move `frontend/` -> `archive/frontend-alpine-legacy/`
- [ ] Move Railway configs -> `archive/railway-configs/`
- [ ] Delete old .env files with Railway URLs

### 3. Service Shutdown
- [ ] Cancel Railway subscription
- [ ] Delete Railway project
- [ ] Remove Railway Redis instance

### 4. Git Cleanup
```bash
# Remove sensitive files from Git history
git filter-branch --force --index-filter \\
  "git rm --cached --ignore-unmatch backend/.env.production" \\
  --prune-empty --tag-name-filter cat -- --all

# Force push (CAREFUL!)
git push origin --force --all
```

## Current Production URLs
- Frontend: https://threadr-plum.vercel.app
- Backend: https://threadr-pw0s.onrender.com

## Next Steps
1. Complete manual archiving
2. Update environment variables on Render
3. Deploy full backend (main.py instead of main_minimal.py)
4. Begin Phase 2 development

---
Generated by cleanup-august-6.py
"""
    
    report_path = PROJECT_ROOT / "CLEANUP_REPORT_AUGUST_6.md"
    report_path.write_text(report)
    print(f"\n[REPORT] Report saved to: {report_path.name}")

def main():
    print("[CLEANUP] Threadr Project Cleanup Script")
    print("=" * 50)
    
    # Create archive structure
    print("\n[SETUP] Creating Archive Structure:")
    create_archive_structure()
    
    # Check Alpine frontend
    print("\n[FRONTEND] Frontend Status:")
    archive_alpine_frontend()
    
    # Check Railway configs
    print("\n[RAILWAY] Railway Configurations:")
    cleanup_railway_configs()
    
    # Check environment files
    identify_env_files()
    
    # Security audit
    check_security_issues()
    
    # Generate report
    print("\n[REPORT] Generating Cleanup Report...")
    generate_cleanup_report()
    
    print("\n[COMPLETE] Cleanup analysis complete!")
    print("   See CLEANUP_REPORT_AUGUST_6.md for action items")

if __name__ == "__main__":
    main()