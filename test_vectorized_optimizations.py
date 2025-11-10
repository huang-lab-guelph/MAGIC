#!/usr/bin/env python
"""
Test script to compare performance of different optimization levels
Tests on Abl-RD dataset with progressive optimizations
"""

import time
import subprocess
import os
import sys
import psutil
from datetime import datetime

def run_test(script_name, config_file, description):
    """Run a single test and return timing information"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*60}")

    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            [sys.executable, script_name, config_file],
            capture_output=True,
            text=True,
            timeout=180  # 3 minute timeout
        )

        elapsed_time = time.perf_counter() - start_time

        if result.returncode == 0:
            # Count progress lines to ensure it completed
            progress_lines = [line for line in result.stderr.split('\n')
                            if 'Tc=' in line or 'Assignment complete' in line]

            if 'Assignment complete' in result.stderr or len(progress_lines) > 10:
                print(f"✓ Completed successfully in {elapsed_time:.2f} seconds")
                return {'status': 'success', 'time': elapsed_time, 'output': result.stderr}
            else:
                print(f"⚠ May not have completed fully")
                return {'status': 'partial', 'time': elapsed_time}
        else:
            print(f"✗ Failed with return code {result.returncode}")
            print(f"Error: {result.stderr[:500]}")
            return {'status': 'failed', 'time': elapsed_time}

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout after 180 seconds")
        return {'status': 'timeout', 'time': 180}
    except Exception as e:
        print(f"✗ Error: {e}")
        return {'status': 'error', 'time': None}


def main():
    """Run comprehensive performance tests"""

    print("=" * 80)
    print("MAGIC OPTIMIZATION PERFORMANCE TEST - Abl-RD Dataset")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"CPU cores: {psutil.cpu_count()}")
    print(f"Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")

    # Change to Abl-RD directory for testing
    original_dir = os.getcwd()
    os.chdir('Abl-RD')

    tests = [
        ('Magic_v1.0.py', 'Original version (baseline)'),
        ('Magic_v1_optimized.py', 'Initial optimizations (8% improvement)'),
        ('Magic_v1_fully_optimized.py', 'With vectorization + caching')
    ]

    results = {}

    for script, description in tests:
        script_path = f'../{script}'
        if os.path.exists(script_path):
            result = run_test(script_path, 'start_MG.txt', description)
            results[script] = result
        else:
            print(f"\n⚠ Skipping {script} - file not found")
            results[script] = {'status': 'not_found', 'time': None}

    # Return to original directory
    os.chdir(original_dir)

    # Print summary
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON SUMMARY")
    print("=" * 80)

    baseline_time = None
    for script, result in results.items():
        if result['status'] == 'success':
            time_str = f"{result['time']:.2f}s"

            if 'v1.0.py' in script and baseline_time is None:
                baseline_time = result['time']
                speedup_str = "(baseline)"
            elif baseline_time:
                speedup = baseline_time / result['time']
                improvement = (baseline_time - result['time']) / baseline_time * 100
                speedup_str = f"({speedup:.2f}x faster, {improvement:.1f}% improvement)"
            else:
                speedup_str = ""

            print(f"{script:30s}: {time_str:10s} {speedup_str}")
        else:
            print(f"{script:30s}: {result['status']}")

    print("\n" + "=" * 80)
    print("OPTIMIZATION BREAKDOWN")
    print("=" * 80)

    if all(results[s]['status'] == 'success' for s in ['Magic_v1.0.py', 'Magic_v1_fully_optimized.py']):
        baseline = results['Magic_v1.0.py']['time']
        optimized = results['Magic_v1_fully_optimized.py']['time']

        print(f"Baseline time:                 {baseline:.2f} seconds")
        print(f"Fully optimized time:          {optimized:.2f} seconds")
        print(f"Time saved:                    {baseline - optimized:.2f} seconds")
        print(f"Overall speedup:               {baseline/optimized:.2f}x")
        print(f"Performance improvement:       {(baseline - optimized)/baseline * 100:.1f}%")

        print("\n" + "=" * 80)
        print("EXPECTED CONTRIBUTIONS")
        print("=" * 80)
        print("• Dictionary lookups (O(1)):    ~5-10% improvement")
        print("• Pre-compiled regex:           ~2-5% improvement")
        print("• Cached float conversions:     ~5-10% improvement")
        print("• Vectorized operations:        ~20-40% improvement")
        print("• Smart caching:                ~10-20% improvement")
        print("• Total expected:               ~40-70% improvement")

    # Save detailed report
    report_file = f"optimization_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("MAGIC OPTIMIZATION TEST REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: Abl-RD\n\n")

        for script, result in results.items():
            f.write(f"\n{script}:\n")
            f.write(f"  Status: {result['status']}\n")
            if result['time']:
                f.write(f"  Time: {result['time']:.2f} seconds\n")

    print(f"\nDetailed report saved to: {report_file}")

    # Print cache statistics if available
    try:
        from caching_optimizations import cached_float_conversion, cached_split_and_convert
        print("\n" + "=" * 80)
        print("CACHE STATISTICS (if available)")
        print("=" * 80)
        if hasattr(cached_float_conversion, 'cache_info'):
            print(f"Float conversion cache: {cached_float_conversion.cache_info()}")
        if hasattr(cached_split_and_convert, 'cache_info'):
            print(f"Split/convert cache: {cached_split_and_convert.cache_info()}")
    except:
        pass


if __name__ == "__main__":
    main()