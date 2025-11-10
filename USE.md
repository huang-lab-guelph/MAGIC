# Quick Start - Running MAGIC Samples

## Setup (one time only)
```bash
cd /Users/felipe/Documents/MAGIC
source magic_env/bin/activate
```

## Run Abl-RD Sample
```bash
cd Abl-RD
source ../magic_env/bin/activate
python ../Magic_v1.0.py start_MG.txt
```

## Run MBP_diMe Sample
```bash
cd MBP_diMe
source ../magic_env/bin/activate
python ../Magic_v1.0.py start_MG.txt
```

## Run MBP_stereo Sample
```bash
cd MBP_stereo
source ../magic_env/bin/activate
python ../Magic_v1.0.py start_stereo.txt
```

## Output
Each run creates a timestamped folder (YYYY-MM-DD HH:MM:SS) containing:
- `Input/` - Copy of input files
- `Output/` - Assignment results
- `log` - Processing log

## Notes
- MBP_stereo completes in ~25 seconds
- Abl-RD and MBP_diMe take longer (several minutes)