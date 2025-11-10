# MAGIC Python 2.7 → Python 3.13 Migration Plan

## Executive Summary
MAGIC is a 7,158-line NMR spectroscopy tool for automated methyl assignment. This plan migrates the core algorithm files from Python 2.7 to Python 3.13, **excluding Sparky GUI plugins** (MAGIC_Act.py, MAGIC_View.py) which will be archived.

---

## 1. Current Codebase Analysis

### 1.1 Core Files to Migrate (5 files)

| File | Lines | Purpose | Main Functions |
|------|-------|---------|----------------|
| **Magic_v1.0.py** | 2,022 | Core MAGIC algorithm (v1.0) | `distances()`, `score()`, iterative assignment with multiprocessing |
| **Magic_200520.py** | 2,177 | Enhanced MAGIC algorithm (2020-05-20) | Same as v1.0 but more sophisticated |
| **generate.py** | 202 | Input file generator | Peak typing, geminal pairing, creates `seq.auto` |
| **generate_new.py** | 217 | Enhanced generator with renaming | Similar to generate.py + rename functionality |
| **MAGIC_Net.py** | 726 | Network analysis & visualization | PDB methyl extraction, connectivity matrices, NOE networks, PDF plots |

### 1.2 Files to EXCLUDE from Migration (2 files)

- **MAGIC_Act.py** (1,172 lines) - Sparky GUI plugin - NOT MIGRATING
- **MAGIC_View.py** (642 lines) - Sparky GUI plugin - NOT MIGRATING

These will be moved to an `archive/` or `deprecated/` folder.

### 1.3 Current Dependencies
- **Python version:** 2.7.18
- **Scientific stack:** numpy==1.16.6, pandas==0.24.2, matplotlib==2.2.5, seaborn==0.9.1
- **System modules:** multiprocessing, psutil, resource, datetime, shutil, os, sys, math, re, types

### 1.4 Usage Flow (from MAGIC_instructions.pdf)
1. Generate 2D peak list: `python generate.py [2D_peaks] [seq.fasta] [labeling] [start_num] [rename]`
2. Edit generated peak list and start.txt parameter file
3. Run MAGIC: `python Magic_v1.0.py start.txt`
4. Output: Time-stamped folder with input/, output/, run/ subdirectories
5. Network analysis: `python MAGIC_Net.py [name] [pdb]`

---

## 2. Python 2→3 Migration Issues by File

### 2.1 Magic_v1.0.py (2,022 lines) - CRITICAL

**Python 2 Issues Found:**
1. **cPickle (19 occurrences):** Line 9 import + 18 load/dump calls
2. **Print statements (11 occurrences):** Lines scattered throughout
3. **Multiprocessing:** Line 8 - needs spawn method testing
4. **File I/O (30+ occurrences):** All open() calls need encoding
5. **Integer division:** Distance calculations and array indexing

**Migration Complexity:** HIGH (core algorithm with serialization)

---

### 2.2 Magic_200520.py (2,177 lines) - CRITICAL

**Python 2 Issues Found:**
1. **cPickle (21 occurrences):** Line 9 import + 20 load/dump calls
2. **Print statements (9 occurrences)**
3. **Multiprocessing:** Line 8
4. **File I/O (35+ occurrences)**
5. **Integer division:** Mathematical operations

**Migration Complexity:** HIGH (enhanced version of v1.0)

---

### 2.3 generate.py (202 lines) - MEDIUM

**Python 2 Issues Found:**
1. **cPickle (1 occurrence):** Line 9 - imported but UNUSED (can delete)
2. **Print statements (10 occurrences):** Lines 14, 42, 66-68, etc.
3. **Multiprocessing (1 occurrence):** Line 8 - imported but UNUSED (can delete)
4. **File I/O (10+ occurrences):** Peak list and sequence file reading

**Migration Complexity:** MEDIUM (input processing, no parallelization)

---

### 2.4 generate_new.py (217 lines) - MEDIUM

**Python 2 Issues Found:**
1. **cPickle (1 occurrence):** Line 9 - imported but UNUSED (can delete)
2. **Print statements (12 occurrences)**
3. **File I/O (12+ occurrences)**

**Migration Complexity:** MEDIUM (similar to generate.py)

---

### 2.5 MAGIC_Net.py (726 lines) - MEDIUM-HIGH

**Python 2 Issues Found:**
1. **Print statements (14 occurrences):** Lines 76-81, 178, 382-411, 476, 545-557, 726
2. **exec() statements (2 occurrences):** Lines 109, 111 - dynamic DataFrame creation
3. **File I/O (20+ occurrences):** PDB file reading
4. **NO cPickle:** Clean on serialization

**Migration Complexity:** MEDIUM-HIGH (exec() needs refactoring, visualization dependencies)

---

## 3. Critical Python 2→3 Changes Required

### 3.1 PRIORITY 1: Code-Breaking Changes

#### **Issue 1: cPickle → pickle (Magic_v1.0.py, Magic_200520.py)**
- **Why critical:** Used extensively for serialization in main algorithm
- **Occurrences:** 40 total (19 + 21)
- **Fix:**
  ```python
  # Python 2
  import cPickle
  data = cPickle.load(file)
  cPickle.dump(data, file, -1)

  # Python 3
  import pickle
  data = pickle.load(file)
  pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
  ```
- **Compatibility tool:** Use `pickle.HIGHEST_PROTOCOL` for best compression
- **IMPORTANT:** Old pickle files from Python 2 may need `encoding='latin1'` parameter

#### **Issue 2: Print Statements → print() Function**
- **Occurrences:** 56 total across 5 files
- **Distribution:**
  - MAGIC_Net.py: 14 print statements
  - Magic_200520.py: 9 print statements
  - Magic_v1.0.py: 11 print statements
  - generate.py: 10 print statements
  - generate_new.py: 12 print statements
- **Examples:**
  ```python
  # Python 2
  print 'Duration: ' + str(runtime)
  print '''Usage: MAGIC-Net [output name] [pdb]'''
  print 'Number of methyls: '+str(A+I+2*L+M+T+2*V)

  # Python 3
  print('Duration: ' + str(runtime))
  print('''Usage: MAGIC-Net [output name] [pdb]''')
  print(f'Number of methyls: {A+I+2*L+M+T+2*V}')  # Better: use f-strings
  ```
- **Tool:** Use `2to3 -f print` for automated conversion, then manually review

#### **Issue 3: File I/O Encoding**
- **Occurrences:** 100+ open() calls
- **Why critical:** Python 3 requires explicit encoding
- **Fix:**
  ```python
  # Python 2
  HMQC_file = open('./'+str(sys.argv[1]), 'r')

  # Python 3
  HMQC_file = open('./'+str(sys.argv[1]), 'r', encoding='utf-8')

  # Better: Use context managers
  with open('./'+str(sys.argv[1]), 'r', encoding='utf-8') as HMQC_file:
      data = HMQC_file.read()
  ```

#### **Issue 4: Integer Division**
- **Why critical:** `5/2=2` in Python 2, `5/2=2.5` in Python 3
- **Impact:** Array indexing and distance calculations
- **Fix:** Use `//` for integer division explicitly
- **Action:** Manual audit of all `/` operators in numeric contexts

---

### 3.2 PRIORITY 2: Behavior Changes

#### **Issue 5: Multiprocessing (Magic_v1.0.py, Magic_200520.py)**
- **Change:** Python 3.8+ changed default spawn method on macOS
- **Impact:** Process forking behavior may differ
- **Fix:**
  ```python
  if __name__ == '__main__':
      import multiprocessing as mp
      mp.set_start_method('fork', force=True)  # Maintain Python 2 behavior
  ```
- **Testing required:** Verify parallel algorithm produces consistent results

#### **Issue 6: exec() Dynamic Code (MAGIC_Net.py lines 109, 111)**
- **Current code:**
  ```python
  exec(method + "_summary = pd.DataFrame(columns=[outcolumns])")
  exec(method + "_"+ str(lowCut) + "_PDB_summary = pd.DataFrame(columns = ['Resid','type'])")
  ```
- **Problem:** Dangerous, hard to debug, not Pythonic
- **Recommended refactor:**
  ```python
  # Use dictionary to store dataframes dynamically
  summaries = {}
  summaries[f"{method}_summary"] = pd.DataFrame(columns=[outcolumns])
  summaries[f"{method}_{lowCut}_PDB_summary"] = pd.DataFrame(columns=['Resid', 'type'])
  ```

---

### 3.3 PRIORITY 3: Minor Adjustments

#### **Issue 7: Unused Imports**
- **generate.py:** `import cPickle` (line 9) - DELETE
- **generate.py:** `import multiprocessing` (line 8) - DELETE
- **generate_new.py:** `import cPickle` (line 9) - DELETE

#### **Issue 8: Dictionary Methods**
- **Status:** ✅ No `.iteritems()` in core files (only in MAGIC_Act.py which we're excluding)
- **Action:** None required for migration scope

#### **Issue 9: String Handling**
- **Status:** ✅ No `string.split()` in core files (only in Sparky plugins)
- **Action:** None required

---

## 4. Detailed Migration Procedure

### Phase 1: Environment Setup & Backup (1 hour)

**Step 1.1: Create Python 3.13 Environment**
```bash
# Using conda (recommended for scientific packages)
conda create -n magic-py313 python=3.13
conda activate magic-py313

# Or using venv
python3.13 -m venv magic-py313
source magic-py313/bin/activate  # Linux/Mac
# magic-py313\Scripts\activate  # Windows
```

**Step 1.2: Install Modern Dependencies**
```bash
pip install numpy pandas matplotlib seaborn psutil pytest
```

**Step 1.3: Create requirements.txt**
```txt
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
psutil>=5.9.0
pytest>=7.0.0
```

**Step 1.4: Backup & Branch**
```bash
# Create git branches
git checkout -b python3-migration
git add -A
git commit -m "Pre-migration backup: Python 2.7 original state"
```

**Step 1.5: Archive Sparky Files**
```bash
# Move Sparky GUI plugins to archive
mkdir -p archive/sparky_plugins
git mv MAGIC_Act.py archive/sparky_plugins/
git mv MAGIC_View.py archive/sparky_plugins/
echo "Sparky GUI plugins (Python 2.7 only) - not maintained" > archive/sparky_plugins/README.txt
git commit -m "Archive Sparky GUI plugins (not migrating)"
```

---

### Phase 2: Automated Migration with 2to3 (1-2 hours)

**Step 2.1: Run 2to3 on Core Files**
```bash
# Run 2to3 on the 5 core files
2to3 -w -n Magic_v1.0.py Magic_200520.py generate.py generate_new.py MAGIC_Net.py

# -w: Write changes back to files
# -n: No backup (.bak files not created, git tracks originals)
```

**Step 2.2: Review Automated Changes**
```bash
git diff  # Review all changes made by 2to3
```

**Expected 2to3 changes:**
- ✅ Print statements → print() functions
- ✅ Some import updates
- ⚠️ **Will NOT fix:** cPickle, file encoding, integer division, exec()

**Step 2.3: Commit Automated Changes**
```bash
git add -A
git commit -m "Apply 2to3 automated migration"
```

---

### Phase 3: Manual Critical Fixes (3-4 hours)

#### **Step 3.1: Fix cPickle → pickle**

**File: Magic_v1.0.py**

Line 9:
```python
# OLD:
import cPickle

# NEW:
import pickle
```

Search and replace all cPickle references (18 occurrences):
```python
# OLD pattern: cPickle.load(
# NEW pattern: pickle.load(

# OLD pattern: cPickle.dump(
# NEW pattern: pickle.dump(
```

Specific fixes:
```python
# OLD:
cPickle.dump(assignment_archive_to_save, file, -1)

# NEW:
pickle.dump(assignment_archive_to_save, file, protocol=pickle.HIGHEST_PROTOCOL)
```

**File: Magic_200520.py**

Same changes as Magic_v1.0.py (21 occurrences)

**Files: generate.py, generate_new.py**

Delete unused import:
```python
# DELETE this line:
import cPickle
```

---

#### **Step 3.2: Fix File I/O Encoding**

**Strategy:** Add `encoding='utf-8'` to all text file operations

**Search pattern:**
```bash
grep -n "open(" Magic_v1.0.py Magic_200520.py generate.py generate_new.py MAGIC_Net.py
```

**Example fixes:**

**generate.py (lines 26-28):**
```python
# OLD:
HMQC_file = open('./'+str(sys.argv[1]), 'r')
HMQC = HMQC_file.readlines()
HMQC_file.close()

# NEW (better: use context manager):
with open('./'+str(sys.argv[1]), 'r', encoding='utf-8') as HMQC_file:
    HMQC = HMQC_file.readlines()
```

**MAGIC_Net.py (line 127):**
```python
# OLD:
for line in open(pdb_name):
    ...

# NEW:
with open(pdb_name, 'r', encoding='utf-8') as pdb_file:
    for line in pdb_file:
        ...
```

**Apply systematically to all 100+ open() calls**

---

#### **Step 3.3: Integer Division Audit**

**Find all division operators:**
```bash
grep -n "[^/]/[^/=]" Magic_v1.0.py Magic_200520.py MAGIC_Net.py | grep -v "#" | grep -v "//"
```

**Manual review each case:**

1. **Array indexing** → Use `//`
   ```python
   # OLD (Python 2: 5/2=2):
   index = total_peaks / 2

   # NEW (Python 3: 5//2=2):
   index = total_peaks // 2
   ```

2. **Scientific calculations** → Keep `/`
   ```python
   # Keep as-is (float division desired):
   distance = sqrt((x2-x1)**2) / normalization_factor
   ```

3. **Distance thresholds** → Review carefully
   ```python
   # If comparing integers, use //
   # If comparing floats, use /
   ```

**Action:** Create a checklist of all division operations and mark each as reviewed

---

#### **Step 3.4: Delete Unused Imports**

**generate.py:**
```python
# DELETE:
import cPickle
import multiprocessing as mp
```

**generate_new.py:**
```python
# DELETE:
import cPickle
```

---

#### **Step 3.5: Multiprocessing Fix**

**Files: Magic_v1.0.py, Magic_200520.py**

Add at the start of `if __name__ == '__main__':` block:
```python
if __name__ == '__main__':
    import multiprocessing as mp

    # Set spawn method to maintain Python 2 behavior
    try:
        mp.set_start_method('fork', force=True)
    except RuntimeError:
        pass  # Already set

    # ... rest of main code
```

---

#### **Step 3.6: Refactor exec() Statements (MAGIC_Net.py)**

**Lines 109, 111 - Current code:**
```python
exec(method + "_summary = pd.DataFrame(columns=[outcolumns])")
exec(method + "_"+ str(lowCut) + "_PDB_summary = pd.DataFrame(columns = ['Resid','type'])")
```

**Refactored code:**
```python
# Use dictionary for dynamic dataframe storage
summaries = {}

# Replace line 109:
summaries[f"{method}_summary"] = pd.DataFrame(columns=[outcolumns])

# Replace line 111:
summaries[f"{method}_{lowCut}_PDB_summary"] = pd.DataFrame(columns=['Resid', 'type'])

# Later, when accessing these dataframes, use:
# summaries[f"{method}_summary"]
# instead of: exec("variable_name")
```

**Note:** This requires tracking where these dynamically-created variables are used and updating those references to use the `summaries` dictionary.

---

### Phase 4: Testing & Validation (4-5 hours)

#### **Step 4.1: Syntax Validation**
```bash
# Check all files compile without syntax errors
python3.13 -m py_compile Magic_v1.0.py
python3.13 -m py_compile Magic_200520.py
python3.13 -m py_compile generate.py
python3.13 -m py_compile generate_new.py
python3.13 -m py_compile MAGIC_Net.py

# Or all at once:
python3.13 -m py_compile *.py
```

#### **Step 4.2: Basic Execution Tests**

**Test generate.py:**
```bash
cd test_data/  # Use example data from MBP_stereo/ or similar
python ../generate.py hmqc.list seq.fasta AILMV 1 n
# Expected: Creates new_hmqc.list and seq.auto without errors
```

**Test generate_new.py:**
```bash
python ../generate_new.py hmqc.list seq.fasta AILMV 1 y cch_noesy.list
# Expected: Creates new_hmqc.list and seq.auto with geminal pairing
```

**Test MAGIC_Net.py:**
```bash
python ../MAGIC_Net.py test_output 4K33.pdb
# Expected: Creates PDF visualization without errors
```

**Test Magic_v1.0.py:**
```bash
# Prepare start.txt configuration file
python ../Magic_v1.0.py start.txt
# Expected: Runs without errors, creates time-stamped output folder
```

**Test Magic_200520.py:**
```bash
python ../Magic_200520.py start.txt
# Expected: Runs without errors, creates output
```

---

#### **Step 4.3: Unit Testing**

Create `tests/test_migration.py`:
```python
import pytest
import pickle
import numpy as np
from pathlib import Path

def test_pickle_operations():
    """Test pickle save/load works correctly"""
    test_data = {'assignments': [1, 2, 3], 'scores': [0.9, 0.8, 0.7]}

    # Save
    with open('test_output.pkl', 'wb') as f:
        pickle.dump(test_data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Load
    with open('test_output.pkl', 'rb') as f:
        loaded = pickle.load(f)

    assert loaded == test_data
    Path('test_output.pkl').unlink()  # Cleanup

def test_generate_output_format():
    """Test generate.py produces correct output format"""
    import subprocess
    result = subprocess.run([
        'python', 'generate.py',
        'tests/data/hmqc.list',
        'tests/data/seq.fasta',
        'AILMV', '1', 'n'
    ], capture_output=True, text=True)

    assert result.returncode == 0, f"generate.py failed: {result.stderr}"

    # Check output file exists and has correct format
    output_file = Path('new_hmqc.list')
    assert output_file.exists(), "new_hmqc.list not created"

    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) > 0, "Output file is empty"
        # Check first line has expected number of columns
        fields = lines[0].split()
        assert len(fields) >= 4, f"Expected ≥4 columns, got {len(fields)}"

def test_file_encoding():
    """Test that file I/O handles UTF-8 correctly"""
    test_content = "Test data with unicode: αβγ δεζ"

    with open('test_encoding.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)

    with open('test_encoding.txt', 'r', encoding='utf-8') as f:
        loaded = f.read()

    assert loaded == test_content
    Path('test_encoding.txt').unlink()

def test_integer_division():
    """Test integer division behaves correctly"""
    # Python 3 behavior
    assert 5 / 2 == 2.5, "Float division should return float"
    assert 5 // 2 == 2, "Integer division should return int"
    assert type(5 // 2) == int, "Integer division should return int type"

def test_multiprocessing_import():
    """Test multiprocessing module imports correctly"""
    import multiprocessing as mp
    assert mp.cpu_count() > 0, "Multiprocessing should detect CPUs"
```

**Run tests:**
```bash
pytest tests/test_migration.py -v
```

---

#### **Step 4.4: Integration Testing with Example Data**

**Use example datasets from subdirectories:**

```bash
# Test with MBP_stereo dataset (if available)
cd MBP_stereo/

# 1. Generate peak list
python ../generate.py hmqc_peaks.list sequence.fasta AILMV 1 n

# 2. Verify output files created
ls -l new_hmqc.list seq.auto

# 3. Check output format
head -n 5 new_hmqc.list

# 4. Edit start.txt to point to correct files

# 5. Run MAGIC algorithm
python ../Magic_v1.0.py start.txt

# 6. Check for output folder created (time-stamped)
ls -ltr | tail -5

# 7. Verify output files in output/ subdirectory
ls -l [timestamp_folder]/output/

# 8. Check assigned peak lists
head [timestamp_folder]/output/assigned_2D_peaks.list
```

**Repeat for Magic_200520.py and compare outputs**

---

#### **Step 4.5: Validation Checklist**

Create `VALIDATION.md` checklist:

- [ ] All 5 core Python files compile without syntax errors
- [ ] generate.py runs without errors
- [ ] generate_new.py runs without errors
- [ ] Generated peak lists have correct format (5 columns)
- [ ] seq.auto file created correctly
- [ ] Magic_v1.0.py runs without errors
- [ ] Magic_200520.py runs without errors
- [ ] Output folders created with correct structure (input/, output/, run/)
- [ ] Assigned 2D peak lists have correct format
- [ ] Assigned 3D peak lists have correct format
- [ ] MAGIC_Net.py generates PDF plots successfully
- [ ] Multiprocessing completes without deadlocks
- [ ] File I/O handles UTF-8 encoding correctly
- [ ] Pickle save/load operations work correctly
- [ ] No warnings about deprecated features
- [ ] All pytest tests pass

---

### Phase 5: Code Modernization (Optional, 2-3 hours)

#### **Step 5.1: Use f-strings for String Formatting**
```python
# OLD:
print('Number of methyls: '+str(A+I+2*L+M+T+2*V))
print('Duration: ' + str(runtime))

# NEW (Python 3.6+ f-strings):
print(f'Number of methyls: {A+I+2*L+M+T+2*V}')
print(f'Duration: {runtime}')
```

#### **Step 5.2: Use pathlib for File Paths**
```python
# OLD:
import os
pdb_path = os.path.join(directory, filename)

# NEW:
from pathlib import Path
pdb_path = Path(directory) / filename
```

#### **Step 5.3: Use Context Managers Everywhere**
```python
# OLD:
file = open('data.txt', 'r')
data = file.read()
file.close()

# NEW:
with open('data.txt', 'r', encoding='utf-8') as file:
    data = file.read()
```

#### **Step 5.4: Add Type Hints (Python 3.5+)**
```python
from typing import List, Dict, Tuple
import numpy as np

def distances(pdb_file: str, labeling: str) -> np.ndarray:
    """
    Calculate methyl-methyl distances from PDB structure.

    Args:
        pdb_file: Path to PDB file
        labeling: Labeling scheme (e.g., 'AILMV')

    Returns:
        Distance matrix as numpy array
    """
    ...
```

---

### Phase 6: Documentation Updates (2 hours)

#### **Step 6.1: Create README.md**

```markdown
# MAGIC - Methyl Assignment by Graphing Inference Construct

Automated methyl assignment in large proteins using NMR spectroscopy data.

## Python 3.13 Version

This codebase has been migrated from Python 2.7 to Python 3.13.

## Requirements

- Python 3.13+
- Dependencies (see requirements.txt):
  - numpy >= 1.24.0
  - pandas >= 2.0.0
  - matplotlib >= 3.7.0
  - seaborn >= 0.12.0
  - psutil >= 5.9.0

## Installation

```bash
# Create virtual environment
conda create -n magic python=3.13
conda activate magic

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Generate 2D Peak List

```bash
python generate.py [2D_peaks.list] [seq.fasta] [labeling] [start_num] [rename]
```

**Example:**
```bash
python generate.py hmqc.list seq.fasta AILMV 48 y
```

**Parameters:**
- `2D_peaks.list`: 2D peak list in Sparky format (no header)
- `seq.fasta`: Protein sequence in FASTA format
- `labeling`: Labeling scheme (e.g., AILMV for A, I, L, M, V methyls)
- `start_num`: Starting residue number
- `rename`: Rename peaks (y/n)

**Optional:** Add CCH NOESY peak list for geminal pairing:
```bash
python generate.py hmqc.list seq.fasta AILMV 48 y cch_noesy.list
```

**Outputs:**
- `new_hmqc.list`: Formatted 2D peak list with methyl types
- `seq.auto`: Construct methyl list

### 2. Configure Parameters

Edit `start.txt` configuration file:
- Line 3: 2D peak list filename
- Line 5: 3D CCH-NOESY peak list filename
- Line 7: PDB filename
- Line 9: Methyl list (seq.auto from step 1)
- Line 11: Labeling scheme (e.g., I,CD1;L,CD2;V,CG2;M)
- Line 14: VL labeling type (numerical code)
- Line 16: PPM tolerance (13C, 13C, 1H) - default: 0.1 0.1 0.01
- Line 18: Score threshold factor - default: 1
- Line 20: Distance thresholds (lower, upper) - default: 7 10
- Line 22: Score tolerance (off/on)

### 3. Run MAGIC Algorithm

```bash
python Magic_v1.0.py start.txt
```

Or use the enhanced version:
```bash
python Magic_200520.py start.txt
```

**Output:** Creates time-stamped folder containing:
- `input/`: Copy of all input files
- `output/`: Assigned 2D and 3D peak lists
- `run/`: Intermediate files (can be deleted after completion)

### 4. Network Analysis & Visualization

```bash
python MAGIC_Net.py [output_name] [pdb_file]
```

**Example:**
```bash
python MAGIC_Net.py FGFR3 4K33.pdb
```

Generates PDF plots with connectivity matrices and NOE network statistics.

## File Formats

### 2D Peak List (Input)
Sparky format, 3 columns:
```
7-?    26.611    1.283
7-?    26.326    0.846
...
```

### 3D CCH-NOESY Peak List (Input)
Sparky format, 5 columns:
```
7-7-7    12.643    22.716    0.841    99709132800
7-7-7    12.645    22.133    0.905    56579497984
...
```

### PDB File (Input)
Standard PDB format (coordinates only, no headers/HETATM).

### Sequence File (Input)
One-letter amino acid code only:
```
MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKL...
```

### Assigned 2D Peak List (Output)
```
A119CB-HB  21.845  0.843  8.78  1.0  {'A119CB': 224.991}
A121CB-HB  24.513  1.066  14.88  1.0  {'A121CB': 224.991}
...
```

Columns:
1. Best assignment (highest score)
2-3. 13C and 1H chemical shifts
4. Sum of peak-peak connection scores
5. NOE assignment completeness
6. All possible assignments with scores

## Testing

Run test suite:
```bash
pytest tests/test_migration.py -v
```

## Migration Notes

### Changes from Python 2.7
- Print statements → print() functions
- cPickle → pickle module
- File I/O now uses UTF-8 encoding explicitly
- Integer division uses `//` operator
- Multiprocessing uses explicit spawn method

### Sparky GUI Plugins
The Sparky GUI plugins (MAGIC_Act.py, MAGIC_View.py) have been archived in `archive/sparky_plugins/` as they require Python 2.7 and the NMRFAM-Sparky environment. The core MAGIC algorithm and utilities are fully functional without these plugins.

## Citation

Monneau, Y.R., Rossi, P., Bhaumik, A., Huang, C., Jiang, Y., Saleh, T., Xie, T., Xing, Q. and Kalodimos, C.G. (2017)
**Automatic methyl assignment in large proteins by the MAGIC algorithm**
*J. Biomol. NMR*

## License

Distributed AS-IS with no warranty. See DISCLAIMER in original instructions.

## Repository

https://github.com/huang-lab-guelph/MAGIC
```

#### **Step 6.2: Create MIGRATION_NOTES.md**

```markdown
# Python 2.7 → 3.13 Migration Notes

## Summary of Changes

### Files Migrated
- Magic_v1.0.py (2,022 lines)
- Magic_200520.py (2,177 lines)
- generate.py (202 lines)
- generate_new.py (217 lines)
- MAGIC_Net.py (726 lines)

### Files Archived (Not Migrated)
- MAGIC_Act.py → archive/sparky_plugins/
- MAGIC_View.py → archive/sparky_plugins/

**Reason:** Sparky GUI plugins require Python 2.7 and NMRFAM-Sparky environment.

## Critical Changes Made

### 1. cPickle → pickle
- **Files affected:** Magic_v1.0.py, Magic_200520.py
- **Changes:** 40 occurrences updated
- **Import:** `import pickle` (was `import cPickle`)
- **Usage:** `pickle.load()`, `pickle.dump()` (was `cPickle.load()`, `cPickle.dump()`)

### 2. Print Statements
- **Files affected:** All 5 core files
- **Changes:** 56 print statements converted to print() functions
- **Tool:** Automated with 2to3

### 3. File I/O Encoding
- **Files affected:** All 5 core files
- **Changes:** 100+ open() calls updated with encoding='utf-8'
- **Pattern:** `open(file, 'r', encoding='utf-8')`

### 4. Integer Division
- **Files affected:** Magic_v1.0.py, Magic_200520.py, MAGIC_Net.py
- **Changes:** Manual audit, updated critical operations to use `//`
- **Example:** `index = total // 2` (was `index = total / 2`)

### 5. Multiprocessing
- **Files affected:** Magic_v1.0.py, Magic_200520.py
- **Changes:** Added explicit spawn method: `mp.set_start_method('fork', force=True)`

### 6. exec() Refactoring
- **File affected:** MAGIC_Net.py (lines 109, 111)
- **Changes:** Replaced exec() with dictionary-based dataframe storage
- **Benefit:** Safer, more maintainable code

### 7. Unused Imports Removed
- **generate.py:** Removed `import cPickle`, `import multiprocessing`
- **generate_new.py:** Removed `import cPickle`

## Dependencies Updated

| Package | Python 2.7 Version | Python 3.13 Version |
|---------|-------------------|---------------------|
| numpy | 1.16.6 | ≥1.24.0 |
| pandas | 0.24.2 | ≥2.0.0 |
| matplotlib | 2.2.5 | ≥3.7.0 |
| seaborn | 0.9.1 | ≥0.12.0 |
| psutil | (old) | ≥5.9.0 |

## Testing Performed

- ✅ Syntax validation (py_compile)
- ✅ generate.py execution test
- ✅ generate_new.py execution test
- ✅ Magic_v1.0.py execution test
- ✅ Magic_200520.py execution test
- ✅ MAGIC_Net.py execution test
- ✅ Unit tests (pytest)
- ✅ Integration tests with example data
- ✅ File I/O encoding tests
- ✅ Pickle operations tests
- ✅ Multiprocessing tests

## Known Limitations

1. **No Python 2 Pickle Compatibility Testing:** Cannot compare results with old Python 2 pickles during migration.
2. **Sparky GUI Not Available:** Validation and visualization plugins not migrated.
3. **Algorithm Result Validation:** Cannot verify numerical equivalence with Python 2 outputs.

## Future Improvements

1. Add comprehensive pytest test suite
2. Add type hints throughout codebase
3. Refactor remaining exec() statements
4. Modernize code with f-strings and pathlib
5. Add CI/CD pipeline (GitHub Actions)
6. Create Docker container for reproducibility
7. Consider publishing to PyPI

## Migration Date

[DATE COMPLETED]

## Migrated By

[YOUR NAME]
```

#### **Step 6.3: Update .gitignore (if needed)**

Add to .gitignore:
```
# Python 3
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# MAGIC outputs
*_MAGIC_*/
output/
run/
*.pkl
new_*.list
seq.auto

# Virtual environments
magic-py313/
venv/
```

---

## 5. Timeline & Effort Estimation

| Phase | Task | Estimated Time |
|-------|------|----------------|
| 1 | Environment Setup & Backup | 1 hour |
| 2 | Automated Migration (2to3) | 1-2 hours |
| 3 | Manual Critical Fixes | 3-4 hours |
| 4 | Testing & Validation | 4-5 hours |
| 5 | Code Modernization (Optional) | 2-3 hours |
| 6 | Documentation Updates | 2 hours |
| **TOTAL** | **Core Migration** | **13-14 hours** |
| **TOTAL** | **With Modernization** | **15-17 hours** |

**Recommended timeline:** 2-3 days of focused work

---

## 6. Success Criteria

✅ **Migration is successful when:**

1. All 5 core Python files compile without syntax errors in Python 3.13
2. generate.py executes and produces correctly formatted output
3. generate_new.py executes and produces correctly formatted output
4. Magic_v1.0.py runs to completion without errors
5. Magic_200520.py runs to completion without errors
6. MAGIC_Net.py generates PDF visualizations successfully
7. Output files have correct format (assigned peak lists)
8. Multiprocessing completes without deadlocks
9. All pytest unit tests pass
10. Integration tests with example data succeed
11. Documentation is complete and accurate
12. Code is committed to git with clear history

---

## 7. Final Deliverables

### Code Files (Migrated)
- ✅ Magic_v1.0.py (Python 3.13)
- ✅ Magic_200520.py (Python 3.13)
- ✅ generate.py (Python 3.13)
- ✅ generate_new.py (Python 3.13)
- ✅ MAGIC_Net.py (Python 3.13)

### Archived Files
- 📦 archive/sparky_plugins/MAGIC_Act.py (Python 2.7 - not migrated)
- 📦 archive/sparky_plugins/MAGIC_View.py (Python 2.7 - not migrated)
- 📦 archive/sparky_plugins/README.txt

### Configuration
- requirements.txt
- .gitignore (updated)

### Documentation
- README.md (comprehensive usage guide)
- MIGRATION_NOTES.md (detailed migration log)
- VALIDATION.md (testing checklist)

### Testing
- tests/test_migration.py (pytest suite)
- tests/data/ (test datasets)

### Git History
- Clean commit history showing migration steps
- All changes tracked and documented

---

**END OF MIGRATION PLAN**
