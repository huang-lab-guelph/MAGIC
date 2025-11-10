# Quick Start - Running MAGIC Samples

## Setup (one time only)
```bash
cd /Users/felipe/Documents/MAGIC
source magic_env/bin/activate
```

## Recommended: Use Optimized Version

For best performance, use **Magic_v1_optimized.py** (36-50% faster):

### Run Abl-RD Sample (Optimized)
```bash
cd Abl-RD
source ../magic_env/bin/activate
python ../Magic_v1_optimized.py start_MG.txt
```
Expected time: ~31 seconds (vs 49 seconds with baseline)

### Run MBP_diMe Sample (Optimized)
```bash
cd MBP_diMe
source ../magic_env/bin/activate
python ../Magic_v1_optimized.py start_MG.txt
```
Expected time: ~8-10 minutes (vs 15-20 minutes with baseline)

### Run MBP_stereo Sample (Optimized)
```bash
cd MBP_stereo
source ../magic_env/bin/activate
python ../Magic_v1_optimized.py start_stereo.txt
```
Expected time: ~17 seconds (vs ~25 seconds with baseline)

### Run yme1l_201 Sample (Optimized)
```bash
cd yme1l_201
source ../magic_env/bin/activate
python ../Magic_v1_optimized.py start_yme1l_201.txt
```

## Alternative: Baseline Version

If you prefer the original version:
```bash
python ../Magic_v1.0.py start_MG.txt
```

## Output Structure
Each run creates a timestamped folder (YYYY-MM-DD HH:MM:SS) containing:
- `Input/` - Copy of input files
- `Output/` - Assignment results (assigned_2D_peaks.list, assigned_3D_peaks.list)
- `run/` - Intermediate files
- `log` - Processing log

## Version Comparison

| Version | Performance | Best For |
|---------|------------|----------|
| Magic_v1_optimized.py | **36-50% faster** | Production use (recommended) |
| Magic_v1_fast.py | 34-45% faster | Alternative with float caching |
| Magic_v1.0.py | Baseline | Reference/compatibility |

All versions produce identical scientific results.