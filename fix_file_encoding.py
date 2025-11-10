#!/usr/bin/env python3
"""
Script to add encoding='utf-8' to all file open() calls that don't have it.
For binary files (pickle), it will ensure they use 'rb' or 'wb' mode.
"""

import re
import sys

def fix_file_encoding(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pattern for text file operations that need encoding
    # Matches open() calls with 'r' or 'w' mode but without encoding parameter
    text_pattern = r"open\(([^,)]+),\s*['\"]([rwa])['\"](?![^)]*encoding)\)"

    # Replace with encoding='utf-8' for text files
    def replace_text(match):
        filepath = match.group(1)
        mode = match.group(2)
        return f"open({filepath}, '{mode}', encoding='utf-8')"

    content = re.sub(text_pattern, replace_text, content)

    # Pattern for pickle file operations - ensure they use binary mode
    # Matches file operations that use pickle.dump or pickle.load
    pickle_write_pattern = r"file\s*=\s*open\(([^,)]+),\s*['\"]w['\"]\)([^#\n]*pickle\.dump)"
    pickle_read_pattern = r"file\s*=\s*open\(([^,)]+),\s*['\"]r['\"]\)([^#\n]*pickle\.load)"

    # Replace pickle write operations to use 'wb'
    def replace_pickle_write(match):
        filepath = match.group(1)
        rest = match.group(2)
        return f"file = open({filepath}, 'wb'){rest}"

    # Replace pickle read operations to use 'rb'
    def replace_pickle_read(match):
        filepath = match.group(1)
        rest = match.group(2)
        return f"file = open({filepath}, 'rb'){rest}"

    content = re.sub(pickle_write_pattern, replace_pickle_write, content)
    content = re.sub(pickle_read_pattern, replace_pickle_read, content)

    # Also fix lines that already have 'wb' or 'rb' but might have incorrect encoding
    content = re.sub(r"open\(([^,)]+),\s*['\"]([rw])b['\"],\s*encoding=['\"]utf-8['\"]\)",
                    r"open(\1, '\2b')", content)

    if content != original_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed encoding in {filename}")
        return True
    else:
        print(f"No changes needed in {filename}")
        return False

if __name__ == "__main__":
    files_to_fix = [
        'Magic_v1.0.py',
        'Magic_200520.py',
        'generate.py',
        'generate_new.py',
        'MAGIC_Net.py'
    ]

    for filename in files_to_fix:
        try:
            fix_file_encoding(filename)
        except Exception as e:
            print(f"Error processing {filename}: {e}")