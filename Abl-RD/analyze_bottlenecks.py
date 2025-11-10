#!/usr/bin/env python
"""
Analyze Magic_v1.0.py to identify potential bottlenecks
"""
import re
import ast

def analyze_code():
    """Analyze the Magic code for optimization opportunities"""

    with open('../Magic_v1.0.py', 'r') as f:
        code = f.read()

    print("="*80)
    print("ANALYSIS OF MAGIC_V1.0.PY FOR OPTIMIZATION OPPORTUNITIES")
    print("="*80)

    # 1. Find nested loops
    print("\n1. NESTED LOOPS (potential O(N^2) or worse complexity):")
    print("-"*40)
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        if 'for ' in line:
            indent = len(line) - len(line.lstrip())
            # Check next 10 lines for another for loop at deeper indent
            for j in range(i, min(i+10, len(lines))):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                if 'for ' in next_line and next_indent > indent:
                    print(f"Line {i}: {line.strip()[:60]}...")
                    print(f"  -> Line {j+1}: {next_line.strip()[:60]}...")
                    break

    # 2. Find list operations that could be vectorized
    print("\n2. LIST OPERATIONS THAT COULD BE VECTORIZED:")
    print("-"*40)
    for i, line in enumerate(lines, 1):
        if 'append(' in line and 'for ' in lines[max(0, i-3):i]:
            print(f"Line {i}: {line.strip()[:70]}...")

    # 3. Find repeated computations
    print("\n3. REPEATED COMPUTATIONS IN LOOPS:")
    print("-"*40)
    for i, line in enumerate(lines, 1):
        if 'for ' in line:
            # Check next 20 lines for repeated calculations
            for j in range(i+1, min(i+20, len(lines))):
                if 'float(' in lines[j] or 'int(' in lines[j] or '.split()' in lines[j]:
                    if lines[j].count('(') > 2:  # Multiple function calls
                        print(f"Line {j+1}: {lines[j].strip()[:70]}...")
                        break

    # 4. Find file I/O in loops
    print("\n4. FILE I/O IN LOOPS (potential bottleneck):")
    print("-"*40)
    for i, line in enumerate(lines, 1):
        if 'open(' in line:
            # Check if it's inside a loop (by checking indentation)
            if len(line) - len(line.lstrip()) > 0:
                print(f"Line {i}: {line.strip()[:70]}...")

    # 5. Find matrix operations that could be optimized
    print("\n5. MATRIX OPERATIONS:")
    print("-"*40)
    for i, line in enumerate(lines, 1):
        if 'matrix' in line.lower() and ('=' in line or '[' in line):
            if '[:,index' in line or '[index' in line or 'np.zeros' in line:
                print(f"Line {i}: {line.strip()[:70]}...")

    # 6. Find potential caching opportunities
    print("\n6. FUNCTIONS CALLED MULTIPLE TIMES (caching candidates):")
    print("-"*40)
    function_calls = {}
    for i, line in enumerate(lines, 1):
        # Find function calls
        matches = re.findall(r'(\w+)\(', line)
        for func in matches:
            if func not in ['print', 'range', 'len', 'int', 'float', 'str', 'open', 'if', 'for', 'while']:
                if func not in function_calls:
                    function_calls[func] = []
                function_calls[func].append(i)

    for func, line_nums in sorted(function_calls.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        if len(line_nums) > 5:
            print(f"Function '{func}' called {len(line_nums)} times")

    # 7. String operations
    print("\n7. STRING OPERATIONS IN HOT PATHS:")
    print("-"*40)
    for i, line in enumerate(lines, 1):
        if '.split()' in line or 'strip()' in line:
            # Check if in a loop
            indent = len(line) - len(line.lstrip())
            if indent > 0:  # Likely in a loop or function
                print(f"Line {i}: {line.strip()[:70]}...")

    # 8. Look for algorithmic improvements
    print("\n8. POTENTIAL ALGORITHMIC IMPROVEMENTS:")
    print("-"*40)

    # Check for sorting operations
    for i, line in enumerate(lines, 1):
        if 'sort(' in line or 'sorted(' in line:
            print(f"Line {i} - Sorting: {line.strip()[:70]}...")

    # Check for distance calculations
    for i, line in enumerate(lines, 1):
        if 'distance' in line.lower() or 'dist' in line.lower():
            print(f"Line {i} - Distance calc: {line.strip()[:70]}...")

    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("""
1. VECTORIZE LOOPS: Replace Python loops with NumPy operations where possible
2. CACHE RESULTS: Use @lru_cache for pure functions called repeatedly
3. PRECOMPUTE: Move invariant calculations outside loops
4. USE NUMPY: Replace list operations with NumPy arrays
5. BATCH I/O: Combine multiple file operations
6. ALGORITHM: Consider better algorithms for distance/similarity calculations
7. PARALLEL: Use multiprocessing.Pool for independent computations
8. JIT: Consider Numba for numerical hot loops
""")

if __name__ == "__main__":
    analyze_code()