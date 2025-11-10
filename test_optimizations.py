#!/usr/bin/env python
"""
Test the optimized Magic version and compare performance
"""

import time
import subprocess
import os
import sys
import psutil
from datetime import datetime

def test_optimization(config_file='Abl-RD/start_MG.txt'):
    """Test both versions and compare performance"""

    print("=" * 70)
    print("MAGIC OPTIMIZATION PERFORMANCE TEST")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Config file: {config_file}")
    print(f"System Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"Available Memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    print("=" * 70)

    results = {}

    # Test original version
    print("\n1. Testing ORIGINAL Magic_v1.0.py...")
    print("-" * 40)

    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, 'Magic_v1.0.py', config_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        original_time = time.perf_counter() - start_time

        if result.returncode == 0:
            print(f"✓ Original version completed successfully")
            print(f"  Execution time: {original_time:.2f} seconds")
            results['original'] = {
                'time': original_time,
                'status': 'success',
                'output_lines': len(result.stdout.split('\n'))
            }
        else:
            print(f"✗ Original version failed with error:")
            print(f"  {result.stderr[:200]}")
            results['original'] = {
                'time': original_time,
                'status': 'failed',
                'error': result.stderr[:500]
            }
    except subprocess.TimeoutExpired:
        print(f"✗ Original version timed out after 120 seconds")
        results['original'] = {
            'time': 120,
            'status': 'timeout'
        }
    except Exception as e:
        print(f"✗ Error running original version: {e}")
        results['original'] = {
            'status': 'error',
            'error': str(e)
        }

    # Test optimized version
    print("\n2. Testing OPTIMIZED Magic_v1_optimized.py...")
    print("-" * 40)

    if os.path.exists('Magic_v1_optimized.py'):
        start_time = time.perf_counter()
        try:
            result = subprocess.run(
                [sys.executable, 'Magic_v1_optimized.py', config_file],
                capture_output=True,
                text=True,
                timeout=120
            )
            optimized_time = time.perf_counter() - start_time

            if result.returncode == 0:
                print(f"✓ Optimized version completed successfully")
                print(f"  Execution time: {optimized_time:.2f} seconds")
                results['optimized'] = {
                    'time': optimized_time,
                    'status': 'success',
                    'output_lines': len(result.stdout.split('\n'))
                }
            else:
                print(f"✗ Optimized version failed with error:")
                print(f"  {result.stderr[:200]}")
                results['optimized'] = {
                    'time': optimized_time,
                    'status': 'failed',
                    'error': result.stderr[:500]
                }
        except subprocess.TimeoutExpired:
            print(f"✗ Optimized version timed out after 120 seconds")
            results['optimized'] = {
                'time': 120,
                'status': 'timeout'
            }
        except Exception as e:
            print(f"✗ Error running optimized version: {e}")
            results['optimized'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        print("✗ Optimized version not found. Run apply_optimizations.py first.")
        results['optimized'] = {'status': 'not_found'}

    # Compare results
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON")
    print("=" * 70)

    if 'original' in results and 'optimized' in results:
        if results['original'].get('status') == 'success' and results['optimized'].get('status') == 'success':
            orig_time = results['original']['time']
            opt_time = results['optimized']['time']

            speedup = orig_time / opt_time
            improvement = (orig_time - opt_time) / orig_time * 100

            print(f"Original time:    {orig_time:.2f} seconds")
            print(f"Optimized time:   {opt_time:.2f} seconds")
            print("-" * 40)

            if opt_time < orig_time:
                print(f"🎉 PERFORMANCE IMPROVED!")
                print(f"   Speedup:      {speedup:.2f}x faster")
                print(f"   Improvement:  {improvement:.1f}%")
                print(f"   Time saved:   {orig_time - opt_time:.2f} seconds")
            elif opt_time > orig_time:
                print(f"⚠️  PERFORMANCE DEGRADED")
                print(f"   Slowdown:     {opt_time/orig_time:.2f}x slower")
                print(f"   Degradation:  {-improvement:.1f}%")
                print(f"   Extra time:   {opt_time - orig_time:.2f} seconds")
            else:
                print(f"↔️  PERFORMANCE UNCHANGED")
        else:
            print("⚠️  Cannot compare - one or both versions failed to run successfully")
            if results['original'].get('status') != 'success':
                print(f"   Original: {results['original'].get('status')}")
            if results['optimized'].get('status') != 'success':
                print(f"   Optimized: {results['optimized'].get('status')}")

    # Additional optimization suggestions
    print("\n" + "=" * 70)
    print("ADDITIONAL OPTIMIZATION OPPORTUNITIES")
    print("=" * 70)
    print("""
Based on the bottleneck analysis, here are the top remaining optimizations:

1. NUMPY VECTORIZATION (Est. 30-50% improvement)
   - Replace 80+ nested loops with NumPy operations
   - Vectorize distance calculations and matrix operations
   - Use NumPy broadcasting for peak neighbor finding

2. CACHING STRATEGY (Est. 10-20% improvement)
   - Add @lru_cache to pure functions called repeatedly
   - Cache expensive calculations (distances, scores)
   - Implement result memoization for recursive calls

3. PARALLEL PROCESSING (Est. 2-4x speedup on multi-core)
   - Use multiprocessing.Pool for independent calculations
   - Parallelize peak assignment scoring
   - Implement concurrent matrix operations

4. ALGORITHM IMPROVEMENTS (Est. 20-40% improvement)
   - Replace O(N²) searches with hash tables or trees
   - Use KD-tree for spatial queries (already partially done)
   - Implement early termination for convergence

5. I/O OPTIMIZATION (Est. 5-10% improvement)
   - Batch file operations
   - Use memory-mapped files for large datasets
   - Implement async I/O for logging

To apply these optimizations:
1. Start with NumPy vectorization (biggest impact)
2. Add caching for quick wins
3. Profile after each change
4. Test with all dataset sizes
""")

    # Save detailed report
    report_file = f"optimization_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("MAGIC OPTIMIZATION TEST REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Config: {config_file}\n")
        f.write("\nResults:\n")
        for version, data in results.items():
            f.write(f"\n{version.upper()}:\n")
            for key, value in data.items():
                f.write(f"  {key}: {value}\n")

    print(f"\nDetailed report saved to: {report_file}")

    return results

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists('Magic_v1.0.py'):
        print("Error: Magic_v1.0.py not found in current directory")
        print("Please run this script from the MAGIC directory")
        sys.exit(1)

    # Run the test
    test_optimization()