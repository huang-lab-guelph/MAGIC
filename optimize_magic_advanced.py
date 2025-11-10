#!/usr/bin/env python
"""
Advanced optimizations for Magic_v1.0.py based on bottleneck analysis
These optimizations focus on algorithmic improvements and reducing redundant operations
"""

import re
from functools import lru_cache
import numpy as np

# ==================== OPTIMIZATION 1: Pre-compiled Regex Patterns ====================
# Compile regex patterns once instead of in loops
PEAK_ID_PATTERN = re.compile(r'^([0-9]+)#')
RESIDUE_PATTERN = re.compile(r'\w(\d+)\w')
PEAK_RESIDUE_PATTERN = re.compile(r'(\d+)\w')

# ==================== OPTIMIZATION 2: Cached Float Conversions ====================
@lru_cache(maxsize=10000)
def cached_float(value):
    """Cache float conversions to avoid repeated parsing"""
    return float(value)

# ==================== OPTIMIZATION 3: Vectorized Distance Calculations ====================
def vectorized_distance_calc(coords1, coords2):
    """
    Vectorized distance calculation for multiple coordinate pairs
    Replace nested loops with NumPy operations
    """
    coords1 = np.array(coords1)
    coords2 = np.array(coords2)

    # Broadcasting for all pairs
    diff = coords1[:, np.newaxis, :] - coords2[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=2))
    return distances

# ==================== OPTIMIZATION 4: Batch String Processing ====================
def preprocess_peak_data(noe_peaks):
    """
    Pre-process all peak data once before loops
    Convert strings to appropriate types upfront
    """
    processed_peaks = []
    for peak in noe_peaks:
        parts = peak.split()
        processed = {
            'id': parts[0],
            'ppm1': float(parts[1]),
            'ppm2': float(parts[2]),
            'ppm3': float(parts[3]) if len(parts) > 3 else 0.0,
            'intensity': float(parts[4]) if len(parts) > 4 else 1.0
        }
        processed_peaks.append(processed)
    return processed_peaks

# ==================== OPTIMIZATION 5: Efficient Archive Merging ====================
def merge_archives_optimized(archive, result_dict):
    """
    Optimized archive merging without redundant list conversions
    """
    for peak, methyls in archive.items():
        if peak not in result_dict:
            result_dict[peak] = {}

        peak_dict = result_dict[peak]
        for methyl, value in methyls.items():
            if methyl not in peak_dict or value > peak_dict[methyl]:
                peak_dict[methyl] = value

    return result_dict

# ==================== OPTIMIZATION 6: Vectorized Peak Neighbor Analysis ====================
def find_peak_neighbors_vectorized(peak_coords, all_coords, ppm_range):
    """
    Vectorized version of peak neighbor finding
    Replace nested loops with NumPy broadcasting
    """
    peak_array = np.array(peak_coords)
    all_array = np.array(all_coords)

    # Calculate differences for all pairs at once
    diff = np.abs(all_array - peak_array)

    # Find neighbors within range
    within_range = np.all(diff < ppm_range, axis=1)
    neighbor_indices = np.where(within_range)[0]

    return neighbor_indices

# ==================== OPTIMIZATION 7: Batch File Operations ====================
class BatchFileWriter:
    """Context manager for batch file writing"""
    def __init__(self, filepath, batch_size=100):
        self.filepath = filepath
        self.batch_size = batch_size
        self.buffer = []
        self.file = None

    def __enter__(self):
        self.file = open(self.filepath, 'a')
        return self

    def write(self, content):
        self.buffer.append(content)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        if self.buffer and self.file:
            self.file.write(''.join(self.buffer))
            self.buffer = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        if self.file:
            self.file.close()

# ==================== OPTIMIZATION 8: Matrix Operations with NumPy ====================
def optimize_matrix_operations(matrix, indices):
    """
    Optimize matrix slicing operations using NumPy advanced indexing
    """
    # Convert to NumPy if not already
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix)

    # Use advanced indexing instead of nested loops
    # This is much faster than matrix[:, indices][indices, :]
    ix = np.ix_(indices, indices)
    return matrix[ix]

# ==================== OPTIMIZATION 9: Parallel Score Calculation ====================
def calculate_scores_vectorized(correlations, factors):
    """
    Vectorized score calculation to replace loop-based calculations
    """
    correlations = np.array(correlations)

    # Extract columns
    shared_neighbors = correlations[:, 5].astype(float)
    chi = correlations[:, 6].astype(float)
    sym = correlations[:, 7].astype(float)
    N = correlations[:, 3].astype(float)

    # Vectorized score calculation
    scores = np.sqrt(
        ((1 + shared_neighbors) ** 2) * sym * (factors[0] / (20 * chi * N**2))
    )

    return np.round(scores, 3)

# ==================== OPTIMIZATION 10: Memoized Peak Clustering ====================
@lru_cache(maxsize=1000)
def get_peak_cluster(peak_id, cluster_map):
    """
    Cached cluster lookup to avoid repeated searches
    """
    return cluster_map.get(peak_id, None)

# ==================== EXAMPLE INTEGRATION ====================
def demonstrate_optimizations():
    """
    Example of how to integrate these optimizations into Magic_v1.0.py
    """

    print("Advanced Optimizations for MAGIC")
    print("=" * 50)

    # Example 1: Replace string operations in loops
    print("\n1. String operations optimization:")
    print("   BEFORE: float(line.split()[1]) inside loop")
    print("   AFTER: Pre-process with preprocess_peak_data()")

    # Example 2: Replace nested loops with vectorization
    print("\n2. Nested loop optimization:")
    print("   BEFORE: for i in range(len(list1)):")
    print("           for j in range(len(list2)):")
    print("   AFTER: Use vectorized_distance_calc()")

    # Example 3: File I/O optimization
    print("\n3. File I/O optimization:")
    print("   BEFORE: open/write/close inside loop")
    print("   AFTER: Use BatchFileWriter context manager")

    # Example 4: Dictionary operations
    print("\n4. Dictionary optimization:")
    print("   BEFORE: if not x in list(dict.keys()):")
    print("   AFTER: if x not in dict:")

    # Example 5: Regex compilation
    print("\n5. Regex optimization:")
    print("   BEFORE: re.search(pattern, text) in loop")
    print("   AFTER: PATTERN.search(text) with pre-compiled")

    print("\n" + "=" * 50)
    print("Implementation Instructions:")
    print("1. Add these optimizations to Magic_v1.0.py imports")
    print("2. Replace identified bottlenecks with optimized functions")
    print("3. Test with small dataset first")
    print("4. Profile to verify improvements")
    print("5. Scale to larger datasets")

if __name__ == "__main__":
    demonstrate_optimizations()