#!/usr/bin/env python3
"""
Script to fix all pickle file operations to use binary mode.
"""

import re
import sys

def fix_pickle_binary_mode(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for i, line in enumerate(lines):
        new_line = line

        # Check if this line opens a file in text mode ('r' or 'w')
        if 'file' in line and 'open(' in line and ("'r'" in line or "'w'" in line):
            # Check if next few lines use pickle
            next_few_lines = ''.join(lines[i:min(i+5, len(lines))])
            if 'pickle.load' in next_few_lines or 'pickle.dump' in next_few_lines:
                # Replace 'r' with 'rb' and 'w' with 'wb'
                new_line = line.replace("'r'", "'rb'").replace("'w'", "'wb'")
                if new_line != line:
                    modified = True
                    print(f"  Line {i+1}: Fixed pickle file operation to binary mode")

        new_lines.append(new_line)

    if modified:
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Fixed {filename}")
        return True
    else:
        print(f"No changes needed in {filename}")
        return False

if __name__ == "__main__":
    files_to_fix = [
        'Magic_v1.0.py',
        'Magic_200520.py'
    ]

    for filename in files_to_fix:
        try:
            fix_pickle_binary_mode(filename)
        except Exception as e:
            print(f"Error processing {filename}: {e}")