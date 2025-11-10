#!/bin/bash
# Performance test script for MBP_diMe dataset

echo "================================================================"
echo "MAGIC PERFORMANCE TEST - MBP_diMe Dataset"
echo "================================================================"
echo "Date: $(date)"
echo "Dataset: MBP_diMe (Maltose Binding Protein, ILVM labeling)"
echo "================================================================"
echo ""

# Change to MBP_diMe directory
cd MBP_diMe

# Function to run and time a test
run_test() {
    local script=$1
    local desc=$2

    echo "----------------------------------------"
    echo "Testing: $desc"
    echo "Script: $script"
    echo "----------------------------------------"

    # Run with timing
    START=$(date +%s)
    timeout 300 python ../$script start_MG.txt 2>&1 | tee test_output.tmp | tail -5
    EXIT_CODE=$?
    END=$(date +%s)

    ELAPSED=$((END - START))

    if [ $EXIT_CODE -eq 124 ]; then
        echo "✗ TIMEOUT after 300 seconds"
    elif [ $EXIT_CODE -eq 0 ] || grep -q "Assignment complete" test_output.tmp 2>/dev/null; then
        echo "✓ Completed in ${ELAPSED} seconds"
    else
        echo "✗ Failed with exit code $EXIT_CODE"
    fi

    echo ""
    rm -f test_output.tmp

    return $ELAPSED
}

# Test each version
echo "STARTING TESTS..."
echo ""

# Baseline
run_test "Magic_v1.0.py" "BASELINE (Original version)"
BASELINE_TIME=$?

# Initial optimizations
run_test "Magic_v1_optimized.py" "OPTIMIZED (Dictionary + defaultdict optimizations)"
OPT_TIME=$?

# Fast version with caching
run_test "Magic_v1_fast.py" "FAST (With cached float conversions)"
FAST_TIME=$?

# Fully optimized (may be slower due to overhead)
run_test "Magic_v1_fully_optimized.py" "FULL (Vectorization + sparse matrices)"
FULL_TIME=$?

# Return to parent directory
cd ..

# Summary
echo "================================================================"
echo "PERFORMANCE SUMMARY - MBP_diMe"
echo "================================================================"
echo "Baseline:        ${BASELINE_TIME}s"
echo "Optimized:       ${OPT_TIME}s"
echo "Fast+Cache:      ${FAST_TIME}s"
echo "Full Vector:     ${FULL_TIME}s"
echo ""

# Calculate improvements
if [ $BASELINE_TIME -gt 0 ] && [ $OPT_TIME -gt 0 ]; then
    IMPROVEMENT=$(echo "scale=1; ($BASELINE_TIME - $OPT_TIME) * 100 / $BASELINE_TIME" | bc)
    SPEEDUP=$(echo "scale=2; $BASELINE_TIME / $OPT_TIME" | bc)
    echo "Best improvement: ${IMPROVEMENT}% (${SPEEDUP}x speedup)"
fi

echo "================================================================"