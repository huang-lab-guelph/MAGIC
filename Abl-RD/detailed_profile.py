#!/usr/bin/env python
"""
Detailed profiling to identify bottlenecks in Magic_v1.0.py
"""
import cProfile
import pstats
import io
import sys
import os

def profile_magic():
    """Profile the Magic script execution"""

    # Set up environment
    os.chdir('/Users/felipe/Documents/MAGIC/Abl-RD')
    sys.path.insert(0, '..')
    sys.argv = ['../Magic_v1.0.py', 'start_MG.txt']

    # Create profiler
    pr = cProfile.Profile()

    # Profile the execution
    pr.enable()

    # Run the script
    with open('../Magic_v1.0.py', 'r') as f:
        code = compile(f.read(), '../Magic_v1.0.py', 'exec')
        try:
            exec(code, {'__name__': '__main__', '__file__': '../Magic_v1.0.py'})
        except SystemExit:
            pass

    pr.disable()

    # Print statistics
    print("\n" + "="*80)
    print("TOP 50 FUNCTIONS BY CUMULATIVE TIME")
    print("="*80)
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(50)
    print(s.getvalue())

    print("\n" + "="*80)
    print("TOP 50 FUNCTIONS BY TOTAL TIME (excluding subcalls)")
    print("="*80)
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.print_stats(50)
    print(s.getvalue())

    print("\n" + "="*80)
    print("TOP 30 FUNCTIONS BY NUMBER OF CALLS")
    print("="*80)
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('calls')
    ps.print_stats(30)
    print(s.getvalue())

    # Save to file for later analysis
    pr.dump_stats('profile_stats.prof')
    print("\nProfile saved to profile_stats.prof")
    print("You can analyze it with: python -m pstats profile_stats.prof")

if __name__ == "__main__":
    profile_magic()