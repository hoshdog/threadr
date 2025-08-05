#!/usr/bin/env python3
"""Force Railway rebuild through various methods"""

import subprocess
import os
import sys
from datetime import datetime

def run_command(cmd, description):
    """Run a shell command and report results"""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Force Railway rebuild using multiple methods"""
    print("=" * 60)
    print("🚀 Railway Force Rebuild Tool")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if we're in the right directory
    if not os.path.exists("nixpacks.toml"):
        print("❌ Error: Not in Threadr root directory!")
        print("   Please run from: C:\\Users\\HoshitoPowell\\Desktop\\Threadr")
        return
    
    print("\nChoose rebuild method:")
    print("1. Add timestamp to nixpacks.toml (Recommended)")
    print("2. Create FORCE_DEPLOY file")
    print("3. Modify backend file directly")
    print("4. All of the above (Nuclear option)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1" or choice == "4":
        # Method 1: Update nixpacks.toml
        print("\n📝 Method 1: Updating nixpacks.toml...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read current content
        with open("nixpacks.toml", "r") as f:
            content = f.read()
        
        # Add timestamp comment
        if "# Last forced rebuild:" in content:
            # Update existing timestamp
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "# Last forced rebuild:" in line:
                    lines[i] = f"# Last forced rebuild: {timestamp}"
                    break
            content = "\n".join(lines)
        else:
            # Add new timestamp at the top
            content = f"# Last forced rebuild: {timestamp}\n{content}"
        
        # Write back
        with open("nixpacks.toml", "w") as f:
            f.write(content)
        print("   ✅ Updated nixpacks.toml with timestamp")
    
    if choice == "2" or choice == "4":
        # Method 2: Create force deploy file
        print("\n📝 Method 2: Creating FORCE_DEPLOY file...")
        with open("FORCE_DEPLOY.txt", "w") as f:
            f.write(f"Forcing Railway deployment at {datetime.now().isoformat()}\n")
            f.write("This file can be deleted after deployment succeeds.\n")
        print("   ✅ Created FORCE_DEPLOY.txt")
    
    if choice == "3" or choice == "4":
        # Method 3: Touch backend file
        print("\n📝 Method 3: Updating backend file timestamp...")
        backend_file = "backend/src/main_minimal.py"
        if os.path.exists(backend_file):
            # Add a comment with timestamp
            with open(backend_file, "r") as f:
                content = f.read()
            
            # Update or add deployment timestamp
            timestamp_comment = f'# Deployment forced at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            if "# Deployment forced at:" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "# Deployment forced at:" in line:
                        lines[i] = timestamp_comment
                        break
                content = "\n".join(lines)
            else:
                # Add after the docstring
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if '"""' in line and i > 0:  # End of docstring
                        lines.insert(i + 1, timestamp_comment)
                        break
                content = "\n".join(lines)
            
            with open(backend_file, "w") as f:
                f.write(content)
            print("   ✅ Updated main_minimal.py")
    
    # Git operations
    print("\n🔄 Committing changes...")
    
    commands = [
        ("git add -A", "Staging changes"),
        (f'git commit -m "Force Railway rebuild - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"', "Creating commit"),
        ("git push origin main", "Pushing to GitHub")
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
            break
    
    if success:
        print("\n✅ SUCCESS! Changes pushed to GitHub")
        print("\n📋 Next steps:")
        print("1. Check Railway dashboard for new deployment")
        print("2. Monitor build logs for 'main_minimal.py'")
        print("3. Run: python scripts/verify_railway_cache_clear.py")
        print("\n⏱️ Deployment usually takes 2-3 minutes")
    else:
        print("\n❌ Failed to push changes")
        print("Check git status and try manually")
    
    # Offer to monitor
    monitor = input("\nMonitor deployment? (y/n): ").strip().lower()
    if monitor == "y":
        print("\nStarting deployment monitor...")
        os.system("python scripts/verify_railway_cache_clear.py --monitor")

if __name__ == "__main__":
    main()