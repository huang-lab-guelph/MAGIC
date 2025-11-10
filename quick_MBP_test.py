#!/usr/bin/env python
"""
Quick performance comparison test for MBP_diMe dataset
Runs each version for a fixed time and compares progress
"""

import subprocess
import time
import os
import re
from datetime import datetime

def run_timed_test(script_path, duration=120):
    """Run script for fixed duration and capture progress"""

    process = subprocess.Popen(
        ['python', script_path, 'start_MG.txt'],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    start_time = time.time()
    max_tc = 0
    max_percent = 0
    last_line = ""
    line_count = 0

    # Collect output for duration seconds
    while time.time() - start_time < duration:
        try:
            # Check if process has output
            line = process.stderr.readline()
            if line:
                line_count += 1
                last_line = line.strip()

                # Parse Tc values and percentages
                tc_match = re.search(r'Tc=\s*([\d.]+)', line)
                percent_match = re.search(r'(\d+\.?\d*)\s*%', line)

                if tc_match:
                    tc_val = float(tc_match.group(1))
                    if tc_val > max_tc:
                        max_tc = tc_val

                if percent_match:
                    percent = float(percent_match.group(1))
                    if percent > max_percent:
                        max_percent = percent

            # Check if process finished
            if process.poll() is not None:
                break

            time.sleep(0.1)
        except:
            break

    # Terminate process if still running
    if process.poll() is None:
        process.terminate()
        time.sleep(1)
        if process.poll() is None:
            process.kill()

    elapsed = time.time() - start_time

    return {
        'elapsed': elapsed,
        'max_tc': max_tc,
        'max_percent': max_percent,
        'last_line': last_line,
        'lines_processed': line_count,
        'completed': 'Assignment complete' in last_line
    }


def main():
    print("=" * 80)
    print("MAGIC QUICK PERFORMANCE TEST - MBP_diMe Dataset")
    print("=" * 80)
    print(f"Date: {datetime.now()}")
    print(f"Test duration: 120 seconds per version")
    print(f"Dataset: MBP_diMe (119 HMQC peaks, 632 NOE peaks)")
    print("=" * 80)
    print()

    # Change to MBP_diMe directory
    os.chdir('/Users/felipe/Documents/MAGIC/MBP_diMe')

    tests = [
        ('../Magic_v1.0.py', 'Baseline'),
        ('../Magic_v1_optimized.py', 'Optimized'),
        ('../Magic_v1_fast.py', 'Fast+Cache'),
    ]

    results = {}

    for script, name in tests:
        if not os.path.exists(script):
            print(f"⚠ Skipping {name} - file not found")
            continue

        print(f"\nTesting: {name}")
        print("-" * 40)

        result = run_timed_test(script, duration=120)
        results[name] = result

        print(f"Progress after {result['elapsed']:.1f}s:")
        print(f"  Max Tc reached: {result['max_tc']}")
        print(f"  Max completion: {result['max_percent']:.1f}%")
        print(f"  Lines processed: {result['lines_processed']}")
        if result['completed']:
            print(f"  ✓ COMPLETED!")
        else:
            print(f"  Last status: {result['last_line'][:60]}...")

    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)

    # Compare results
    if 'Baseline' in results and 'Optimized' in results:
        baseline = results['Baseline']
        optimized = results['Optimized']

        print(f"\nProgress after 120 seconds:")
        print(f"  Baseline:  {baseline['max_percent']:.1f}% (Tc={baseline['max_tc']})")
        print(f"  Optimized: {optimized['max_percent']:.1f}% (Tc={optimized['max_tc']})")

        if optimized['max_percent'] > baseline['max_percent']:
            improvement = (optimized['max_percent'] - baseline['max_percent']) / baseline['max_percent'] * 100
            print(f"\n✓ Optimized version is {improvement:.1f}% faster in progress")

        # Estimate total runtime based on progress
        if baseline['max_percent'] > 0:
            baseline_est = 120 * 100 / baseline['max_percent']
            print(f"\nEstimated total runtime:")
            print(f"  Baseline:  ~{baseline_est/60:.1f} minutes")

        if optimized['max_percent'] > 0:
            optimized_est = 120 * 100 / optimized['max_percent']
            print(f"  Optimized: ~{optimized_est/60:.1f} minutes")

            if baseline['max_percent'] > 0:
                speedup = baseline_est / optimized_est
                print(f"\nEstimated speedup: {speedup:.2f}x")

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print("""
MBP_diMe is a much larger dataset than Abl-RD:
- 119 HMQC peaks (vs 84 in Abl-RD)
- 632 NOE peaks (vs ~200 in Abl-RD)
- Higher computational complexity

This makes it a good test for optimization scalability.
The optimizations should show more benefit on larger datasets.
""")


if __name__ == "__main__":
    main()