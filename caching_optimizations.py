#!/usr/bin/env python
"""
Caching optimizations for Magic_v1.0.py
Implements strategic caching for frequently called functions
"""

from functools import lru_cache, wraps
import hashlib
import pickle
import numpy as np
from collections import OrderedDict
import time

class MagicCacheOptimizations:
    """Collection of caching strategies for Magic's frequently called functions"""

    # Global cache statistics for monitoring
    cache_stats = {
        'hits': 0,
        'misses': 0,
        'evictions': 0
    }

    @staticmethod
    def make_hashable(obj):
        """Convert unhashable types to hashable for caching"""
        if isinstance(obj, (list, np.ndarray)):
            return tuple(obj) if isinstance(obj, list) else tuple(obj.flatten())
        elif isinstance(obj, dict):
            return tuple(sorted(obj.items()))
        elif isinstance(obj, set):
            return tuple(sorted(obj))
        return obj

    @classmethod
    def cache_with_numpy(cls, maxsize=128):
        """
        Decorator for caching functions that take NumPy arrays as arguments
        Standard @lru_cache doesn't work with mutable/unhashable types
        """
        def decorator(func):
            # Create a wrapped version that handles NumPy arrays
            @lru_cache(maxsize=maxsize)
            def cached_func(*args, **kwargs):
                # Convert all arguments to hashable types
                hashable_args = tuple(cls.make_hashable(arg) for arg in args)
                hashable_kwargs = tuple((k, cls.make_hashable(v))
                                       for k, v in sorted(kwargs.items()))
                return func(*args, **kwargs)

            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Try to use cached version
                    hashable_args = tuple(cls.make_hashable(arg) for arg in args)
                    hashable_kwargs = {k: cls.make_hashable(v)
                                      for k, v in kwargs.items()}
                    result = cached_func(*hashable_args, **hashable_kwargs)
                    cls.cache_stats['hits'] += 1
                except TypeError:
                    # Fall back to uncached version if hashing fails
                    result = func(*args, **kwargs)
                    cls.cache_stats['misses'] += 1
                return result

            wrapper.cache_info = cached_func.cache_info
            wrapper.cache_clear = cached_func.cache_clear
            return wrapper
        return decorator

    @staticmethod
    def persistent_cache(cache_file='magic_cache.pkl'):
        """
        Decorator for persistent caching across runs
        Useful for expensive computations that don't change between runs
        """
        def decorator(func):
            # Try to load existing cache
            try:
                with open(cache_file, 'rb') as f:
                    cache = pickle.load(f)
            except (FileNotFoundError, EOFError):
                cache = {}

            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                key = hashlib.md5(
                    f"{func.__name__}:{args}:{kwargs}".encode()
                ).hexdigest()

                if key in cache:
                    return cache[key]

                result = func(*args, **kwargs)
                cache[key] = result

                # Save cache to disk
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache, f)

                return result

            wrapper.cache = cache
            wrapper.clear_cache = lambda: cache.clear()
            return wrapper
        return decorator


# Specific cached functions for Magic_v1.0.py

@lru_cache(maxsize=10000)
def cached_float_conversion(value_str):
    """
    Cached float conversion for repeated string-to-float conversions
    Used heavily in peak processing loops
    """
    return float(value_str)


@lru_cache(maxsize=5000)
def cached_split_and_convert(line, delimiter=' '):
    """
    Cached splitting and conversion of peak data lines
    Returns tuple of floats for the numeric fields
    """
    parts = line.split(delimiter)
    result = [parts[0]]  # Keep first part as string (usually ID)
    for part in parts[1:]:
        try:
            result.append(float(part))
        except ValueError:
            result.append(part)
    return tuple(result)


@lru_cache(maxsize=1000)
def cached_distance_calculation(coord1, coord2):
    """
    Cached Euclidean distance calculation
    coord1 and coord2 should be tuples of coordinates
    """
    return sum((a - b) ** 2 for a, b in zip(coord1, coord2)) ** 0.5


@lru_cache(maxsize=5000)
def cached_ppm_check(ppm1, ppm2, range_val):
    """
    Cached check for whether two PPM values are within range
    Used extensively in peak neighbor finding
    """
    return abs(ppm1 - ppm2) < range_val


class SmartMatrixCache:
    """
    Intelligent matrix cache with adaptive sizing and LRU eviction
    Monitors hit rate and adjusts cache size accordingly
    """

    def __init__(self, initial_size=500, min_size=100, max_size=5000):
        self.cache = OrderedDict()
        self.current_max_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 60  # seconds

    def _make_key(self, *args, **kwargs):
        """Create a hashable key from arguments"""
        key_parts = []
        for arg in args:
            if isinstance(arg, np.ndarray):
                key_parts.append(('array', arg.shape, arg.dtype, hash(arg.tobytes())))
            elif isinstance(arg, (list, tuple)):
                key_parts.append(('seq', tuple(arg)))
            else:
                key_parts.append(('val', arg))

        for k, v in sorted(kwargs.items()):
            key_parts.append(('kw', k, v))

        return tuple(key_parts)

    def get(self, key_args, compute_func=None):
        """
        Get value from cache or compute it
        key_args: tuple of arguments to use as key
        compute_func: function to call if cache miss
        """
        key = self._make_key(*key_args)

        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            self._check_adaptive_resize()
            return self.cache[key]

        self.misses += 1

        if compute_func is not None:
            value = compute_func(*key_args)
            self.put(key_args, value)
            return value

        return None

    def put(self, key_args, value):
        """Store value in cache"""
        key = self._make_key(*key_args)

        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            if len(self.cache) >= self.current_max_size:
                # Evict least recently used
                self.cache.popitem(last=False)
                MagicCacheOptimizations.cache_stats['evictions'] += 1

            self.cache[key] = value

    def _check_adaptive_resize(self):
        """Adjust cache size based on hit rate"""
        current_time = time.time()
        if current_time - self.last_adjustment < self.adjustment_interval:
            return

        total_accesses = self.hits + self.misses
        if total_accesses == 0:
            return

        hit_rate = self.hits / total_accesses

        if hit_rate > 0.8 and self.current_max_size < self.max_size:
            # High hit rate - increase cache
            self.current_max_size = min(
                int(self.current_max_size * 1.5),
                self.max_size
            )
        elif hit_rate < 0.3 and self.current_max_size > self.min_size:
            # Low hit rate - decrease cache
            self.current_max_size = max(
                int(self.current_max_size * 0.7),
                self.min_size
            )

        self.last_adjustment = current_time

    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def info(self):
        """Return cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.current_max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'evictions': MagicCacheOptimizations.cache_stats['evictions']
        }


def integrate_caching(magic_module):
    """
    Integrate caching into the existing Magic module
    This function monkey-patches the module with cached versions
    """

    # Create global cache instances
    if not hasattr(magic_module, '_matrix_cache'):
        magic_module._matrix_cache = SmartMatrixCache()

    if not hasattr(magic_module, '_distance_cache'):
        magic_module._distance_cache = {}

    # Replace float() calls with cached version in specific functions
    original_noe2matrix = magic_module.noe2matrix if hasattr(magic_module, 'noe2matrix') else None

    if original_noe2matrix:
        def cached_noe2matrix(*args, **kwargs):
            # Replace float() with cached_float_conversion in the function
            # This is a simplified example - in practice you'd need to modify
            # the function more carefully
            import builtins
            old_float = builtins.float
            builtins.float = cached_float_conversion
            try:
                result = original_noe2matrix(*args, **kwargs)
            finally:
                builtins.float = old_float
            return result

        magic_module.noe2matrix = cached_noe2matrix

    print("Caching integration complete!")
    return magic_module


def benchmark_caching():
    """Benchmark the caching optimizations"""
    import random

    print("=" * 60)
    print("CACHING PERFORMANCE BENCHMARK")
    print("=" * 60)

    # Test float conversion caching
    test_values = [str(random.random() * 100) for _ in range(100)]
    test_values_repeated = test_values * 10  # Repeat values to test caching

    # Without caching
    start = time.perf_counter()
    for val in test_values_repeated:
        _ = float(val)
    uncached_time = time.perf_counter() - start

    # With caching
    start = time.perf_counter()
    for val in test_values_repeated:
        _ = cached_float_conversion(val)
    cached_time = time.perf_counter() - start

    print(f"Float conversion (1000 conversions, 100 unique):")
    print(f"  Uncached: {uncached_time:.4f} seconds")
    print(f"  Cached:   {cached_time:.4f} seconds")
    print(f"  Speedup:  {uncached_time/cached_time:.2f}x")
    print(f"  Cache info: {cached_float_conversion.cache_info()}")

    # Test distance caching
    coords = [(random.random(), random.random(), random.random())
              for _ in range(50)]
    coord_pairs = [(coords[i], coords[j])
                   for i in range(50) for j in range(i+1, 50)]
    coord_pairs_repeated = coord_pairs * 3  # Repeat for caching benefit

    # Without caching
    start = time.perf_counter()
    for c1, c2 in coord_pairs_repeated:
        _ = sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5
    uncached_time = time.perf_counter() - start

    # With caching
    start = time.perf_counter()
    for c1, c2 in coord_pairs_repeated:
        _ = cached_distance_calculation(c1, c2)
    cached_time = time.perf_counter() - start

    print(f"\nDistance calculations ({len(coord_pairs_repeated)} calculations):")
    print(f"  Uncached: {uncached_time:.4f} seconds")
    print(f"  Cached:   {cached_time:.4f} seconds")
    print(f"  Speedup:  {uncached_time/cached_time:.2f}x")

    # Test smart matrix cache
    cache = SmartMatrixCache()
    test_matrices = [np.random.rand(10, 10) for _ in range(20)]

    # Simulate repeated access pattern
    access_pattern = list(range(20)) * 5
    random.shuffle(access_pattern)

    for idx in access_pattern:
        matrix = cache.get((idx,), lambda x: test_matrices[x])

    print(f"\nSmart Matrix Cache Performance:")
    info = cache.info()
    print(f"  Cache size: {info['size']}/{info['max_size']}")
    print(f"  Hit rate:   {info['hit_rate']:.1%}")
    print(f"  Hits:       {info['hits']}")
    print(f"  Misses:     {info['misses']}")
    print(f"  Evictions:  {info['evictions']}")

    print("\n" + "=" * 60)
    print("Expected benefits:")
    print("- 2-5x speedup for repeated float conversions")
    print("- 3-10x speedup for repeated distance calculations")
    print("- 10-20% overall improvement from smart caching")


if __name__ == "__main__":
    benchmark_caching()

    print("\n" + "=" * 60)
    print("INTEGRATION INSTRUCTIONS")
    print("=" * 60)
    print("""
To integrate caching into Magic_v1.0.py:

1. Add imports at the top:
   from caching_optimizations import (
       cached_float_conversion,
       cached_split_and_convert,
       cached_distance_calculation,
       cached_ppm_check,
       SmartMatrixCache,
       integrate_caching
   )

2. Replace float() calls in hot loops:
   # Before: float(value)
   # After:  cached_float_conversion(value)

3. Replace distance calculations:
   # Before: math.sqrt((x1-x2)**2 + (y1-y2)**2)
   # After:  cached_distance_calculation((x1,y1), (x2,y2))

4. Add caching to pure functions:
   # Add decorator to functions that are called repeatedly
   @lru_cache(maxsize=1000)
   def your_pure_function(args):
       ...

5. Use SmartMatrixCache for matrix operations:
   matrix_cache = SmartMatrixCache()
   matrix = matrix_cache.get(key, compute_matrix_func)

6. Monitor cache performance:
   print(matrix_cache.info())
""")