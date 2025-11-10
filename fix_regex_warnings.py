#!/usr/bin/env python3
"""
Script to fix regex patterns with invalid escape sequences.
Converts regex patterns to raw strings (r'...').
"""

import re

def fix_regex_warnings(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Patterns to fix (from the warnings)
    patterns_to_fix = [
        (r"re\.search\('\\w\(\\d\+\)\\w'", r"re.search(r'\\w(\\d+)\\w'"),
        (r"re\.search\('\(\\d\+\)\\w'", r"re.search(r'(\\d+)\\w'"),
        (r"re\.search\('\[0-9\]\+\(\\w\+\)'", r"re.search(r'[0-9]+(\\w+)'"),
        (r"re\.search\('\\w\(\\d\+\)'", r"re.search(r'\\w(\\d+)'"),
    ]

    for old_pattern, new_pattern in patterns_to_fix:
        content = re.sub(old_pattern, new_pattern, content)

    if content != original_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed regex warnings in {filename}")
        return True
    else:
        print(f"No regex warnings to fix in {filename}")
        return False

if __name__ == "__main__":
    files_to_fix = [
        'Magic_v1.0.py',
        'Magic_200520.py'
    ]

    for filename in files_to_fix:
        try:
            fix_regex_warnings(filename)
        except Exception as e:
            print(f"Error processing {filename}: {e}")