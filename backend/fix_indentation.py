#!/usr/bin/env python3
"""Fix indentation issue in main.py"""

def fix_indentation():
    with open('src/main.py', 'r') as f:
        lines = f.readlines()
    
    # Find the problematic line
    for i, line in enumerate(lines):
        if i >= 1155 and 'except HTTPException:' in line:
            print(f"Found 'except HTTPException:' at line {i+1}")
            print(f"Current line: {repr(line)}")
            
            # The except should be at the same level as try (4 spaces)
            # Currently it has 8 spaces (4 from line 1155 + 4 from except line)
            # We need to remove the extra indentation from line 1155
            if i > 0 and lines[i-1].strip() == '':
                lines[i-1] = '\n'  # Remove extra spaces from blank line
                print(f"Fixed blank line at {i}")
            
            break
    
    # Write the fixed file
    with open('src/main.py', 'w') as f:
        f.writelines(lines)
    
    print("Fixed indentation issue!")

if __name__ == '__main__':
    fix_indentation()