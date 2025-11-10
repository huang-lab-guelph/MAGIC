#!/usr/bin/env python3
"""
Compare outputs from optimized and non-optimized versions of Magic_v1.0.py
This script checks if the results are semantically identical, ignoring dictionary ordering.
"""

import sys
import re
from collections import Counter

def parse_line(line):
    """Parse a line and extract the key assignment information, normalizing dictionary content"""
    if line.startswith('Assignment') or not line.strip():
        return line  # Header or empty line

    parts = line.split('\t')
    if len(parts) < 3:
        return line

    # Extract assignment name, w1, w2, and note fields
    assignment = parts[0]
    w1 = parts[1]

    # The rest contains w2, scores, and dictionary
    rest = parts[2] if len(parts) > 2 else ""

    # Extract the dictionary part (between curly braces)
    dict_match = re.search(r'\{[^}]+\}', rest)
    if dict_match:
        dict_str = dict_match.group(0)
        # Normalize dictionary by sorting the key-value pairs
        dict_items = re.findall(r"'([^']+)':\s*([^,}]+)", dict_str)
        sorted_dict = sorted(dict_items)
        normalized_dict = '{' + ', '.join([f"'{k}': {v}" for k, v in sorted_dict]) + '}'

        # Replace the dictionary in the rest of the line
        rest_without_dict = rest[:dict_match.start()] + normalized_dict + rest[dict_match.end():]
    else:
        rest_without_dict = rest

    return f"{assignment}\t{w1}\t{rest_without_dict}"

def compare_files(file1, file2):
    """Compare two output files, ignoring dictionary ordering"""
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = [parse_line(line.rstrip()) for line in f1]
        lines2 = [parse_line(line.rstrip()) for line in f2]

    if len(lines1) != len(lines2):
        print(f"❌ Different number of lines: {len(lines1)} vs {len(lines2)}")
        return False

    differences = []
    for i, (line1, line2) in enumerate(zip(lines1, lines2), 1):
        if line1 != line2:
            differences.append((i, line1, line2))

    if differences:
        print(f"❌ Found {len(differences)} differences:")
        for line_num, l1, l2 in differences[:5]:  # Show first 5 differences
            print(f"\nLine {line_num}:")
            print(f"  Original : {l1}")
            print(f"  Optimized: {l2}")
        if len(differences) > 5:
            print(f"\n... and {len(differences) - 5} more differences")
        return False

    return True

def main():
    base_dir = "/Users/felipe/Documents/MAGIC/Abl-RD"
    original_dir = f"{base_dir}/2025-11-09 22:00:49/Output"
    optimized_dir = f"{base_dir}/2025-11-09 23:56:41/Output"

    files_to_compare = [
        'hmqc.list',
        'cch.list',
        'hmqc_iso.list',
        'cch_iso.list',
        'mapping.pml',
        'mapping_iso.pml'
    ]

    print("=" * 70)
    print("Comparing outputs between optimized and non-optimized versions")
    print("=" * 70)

    all_identical = True
    for filename in files_to_compare:
        print(f"\n📄 Comparing {filename}...")
        file1 = f"{original_dir}/{filename}"
        file2 = f"{optimized_dir}/{filename}"

        try:
            if compare_files(file1, file2):
                print(f"✅ {filename}: IDENTICAL (ignoring dict ordering)")
            else:
                print(f"❌ {filename}: DIFFERENCES FOUND")
                all_identical = False
        except Exception as e:
            print(f"⚠️  Error comparing {filename}: {e}")
            all_identical = False

    print("\n" + "=" * 70)
    if all_identical:
        print("✅ ALL OUTPUT FILES ARE SEMANTICALLY IDENTICAL!")
        print("   (Only dictionary key ordering differs, which is expected)")
    else:
        print("❌ SOME DIFFERENCES FOUND - Review above for details")
    print("=" * 70)

    return 0 if all_identical else 1

if __name__ == '__main__':
    sys.exit(main())
