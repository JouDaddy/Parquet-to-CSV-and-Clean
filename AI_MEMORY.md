# AI Memory - Data Transformation Context

**Project:** OmniaOffline Data Cleaning  
**Created:** 2026-01-22  
**Last Updated:** 2026-01-28

## Purpose
This file serves as persistent AI context for understanding:
- Data structure and datasets being processed
- Transformation history and status
- Data quality notes
- Schema information for analysis
- Error tracking and troubleshooting
- Known issues and solutions

## CRITICAL: Issues Encountered & Solutions

### Issue 1: Missing PyArrow Library
**Error:** Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'. Missing optional dependency 'pyarrow'.

**Root Cause:** PyArrow wasn't installed in the Python environment.

**Solution Applied:**
```
pip install pyarrow --upgrade
```
**Status:** FIXED 

---

### Issue 2: Unicode Encoding Error in Logs
**Error:** UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'

**Root Cause:** Arrow character () and special unicode characters couldn't be encoded in the default Windows console encoding (cp1252). This occurred when:
- Logging success messages with arrow characters
- Writing to error_log.txt without utf-8 encoding
- Writing to AI_MEMORY.md without utf-8 encoding

**Solutions Applied:**
1. Changed log file writes to use UTF-8 encoding:
   - Line 20: `with open(ERROR_LOG, 'a', encoding='utf-8')`
   - Line 157: `with open(AI_MEMORY, 'w', encoding='utf-8')`
   
2. Changed CSV export to use UTF-8:
   - Line 83: `df.to_csv(csv_path, index=False, encoding='utf-8')`

3. Removed special unicode characters from log messages - use plain ASCII:
   - AVOID: `[SUCCESS]  file.csv` (arrow char causes issues)
   - USE: `[SUCCESS] CSV created: file.csv`

**Status:** FIXED 

---

### Issue 3: Flask Web App Route and Folder Creation Errors
**Error:** 
- "POST /api/validate-files HTTP/1.1" 404 errors
- "failed to fetch" when saving to new folders
- Missing @app.route decorator causing endpoint not found

**Root Cause:** 
1. Missing Flask route decorator for `/api/validate-files` endpoint
2. Insufficient error handling for folder creation paths
3. No validation of parent directory existence before creating new folders

**Solutions Applied:**
1. **Restored missing route decorator:**
   ```python
   @app.route('/api/validate-files', methods=['POST'])
   def validate_files():
   ```

2. **Added folder creation validation:**
   ```python
   # Validate parent path exists before creating new folder
   parent_path = Path(parent_path_str).resolve()
   if not parent_path.exists():
       raise ValueError(f"Parent path does not exist: {parent_path}")
   ```

3. **Improved error handling in JavaScript:**
   ```javascript
   .then(response => {
       if (!response.ok) {
           return response.text().then(text => {
               throw new Error(`HTTP ${response.status}: ${text}`);
           });
       }
       return response.json();
   })
   ```

4. **Added debug logging for troubleshooting:**
   - Request method, headers, and data logging
   - Path resolution and directory creation logging

**Features Added:**
- ✅ **Output folder selection**: Default, existing folder, or create new folder
- ✅ **Custom folder creation**: Specify name and parent path
- ✅ **Path validation**: Checks parent directory exists
- ✅ **Better error messages**: Specific HTTP status and error details

**Status:** FIXED 

---

## Transformation Results

### Successful Run: 2026-01-22 14:34-14:35

| Dataset | Files | Size | Status | Notes |
|---------|-------|------|--------|-------|
| ANP2 for July - Nov 2025 | 4 | 404 MB |  COMPLETE | All CSVs created |
| NAP2 for July - Nov 2025 | 4 | 1.3 GB |  COMPLETE | All CSVs created |
| **TOTAL** | **8** | **~1.7 GB** |  SUCCESS | 100% conversion rate |

### Files Created:

**ANP2 Folder:**
- pi_data_20251230_125107.csv (105 MB)
- pi_data_20251230_132810.csv (100 MB)
- pi_data_20251230_141953.csv (101 MB)
- pi_data_20251230_143627.csv (97 MB)

**NAP2 Folder:**
- pi_data_20251229_151817.csv (332 MB)
- pi_data_20251229_155201.csv (321 MB)
- pi_data_20251230_082720.csv (331 MB)
- pi_data_20251230_092335.csv (320 MB)

**Other Files:**
- complete_tag_inventory.txt (Newly created)

## How to Run (For Next Time) 

**Prerequisites (MUST DO FIRST):**
```powershell
pip install pyarrow --upgrade
```

**Run the script:**
```powershell
cd "c:\Users\EvanJacobs\Documents\OmniaOffline\Data Cleaning"
python transform_parquet.py
```

**Or use VS Code shortcut:** Ctrl + F5 (while viewing transform_parquet.py)

## Directory Structure
```
OmniaOffline/Data Cleaning/
 parquet_source/                Source parquet files
    ANP2 for July - Nov 2025/  4 .parquet files
    NAP2 for July - Nov 2025/  4 .parquet files
 csv_output/                    Generated CSV outputs
    ANP2 for July - Nov 2025/  4 CSV files (auto-created)
    NAP2 for July - Nov 2025/  4 CSV files (auto-created)
 csv_filtered/                  Filtered CSV outputs
    ANP2 for July - Nov 2025/  Filtered ANP2 files
    NAP2 for July - Nov 2025/  Filtered NAP2 files
 templates/                      Web app templates
    filter.html                 CSV filter web interface
 transform_parquet.py           Main conversion script
 filter_csv_columns.py          Column filter script (CLI)
 filter_csv_web.py              Column filter script (Web UI)
 error_log.txt                  Execution log (auto-created)
 AI_MEMORY.md                   This file
 .venv/                         Python virtual environment
```

## What the Script Does
1. Scans `parquet_source/` recursively for all .parquet files
2. Groups by parent folder name (ANP2, NAP2, etc)
3. Converts each .parquet to .csv with UTF-8 encoding
4. Creates organized folders in `csv_output/` matching source structure
5. Logs all operations to `error_log.txt` with timestamps
6. Updates this `AI_MEMORY.md` with results and metadata
7. Records: file names, row counts, column counts, file sizes, errors

## Logs & Monitoring

**IMPORTANT: All scripts log to error_log.txt**
Every script created and run in this project logs all operations to error_log.txt:
- Timestamps for every action
- Success/failure status
- Errors and warnings
- User selections and inputs
- File operations and results

**error_log.txt:**
- Contains every transformation step from ALL scripts
- Timestamps for each operation
- Success/failure status for each file
- Search term history and column selections
- Useful for debugging if issues occur

**AI_MEMORY.md:**
- Auto-updated after each run
- Contains dataset inventory
- Records transformation history
- Tracks known issues
- Documents all script versions and updates

## Available Scripts

### transform_parquet.py (Main Conversion)
**Purpose:** Convert Parquet files to CSV format
**Usage:** `python transform_parquet.py`
**Output:** Creates CSV files in `csv_output/` folders

### filter_csv_columns.py (CLI Column Filter)
**Purpose:** Filter CSV columns via command line interface
**Usage:** `python filter_csv_columns.py`
**Features:** Interactive column selection, search functionality

### filter_csv_web.py (Web Column Filter)
**Purpose:** Filter CSV columns via web browser interface
**Usage:** `python filter_csv_web.py` then open http://127.0.0.1:5000
**Features:** 
- Web-based column selection with search
- Multiple output folder options (default, existing, or create new)
- Real-time validation and error handling
- Batch processing of multiple CSV files

## Data Schema Info
[To be updated - run data_analysis.py to extract schema]

## Known Issues & Workarounds

### Windows Console Encoding Issue (RESOLVED)
**Problem:** Default Windows console uses cp1252 encoding which can't handle unicode
**Workaround:** Always use encoding=\'utf-8\' in file operations
**Status:** Applied to all file writes in script 


### Large File Processing
**Observation:** NAP2 files take ~20 seconds each to convert (normal for large files)
**Status:** Expected behavior 
### VS Code CSV Preview Issue (LARGE FILES)
**Problem:** CSV files won't preview in VS Code - shows grey screen
**Root Cause:** File sizes too large for default preview
- ANP2 files: 100-105 MB each
- NAP2 files: 320-332 MB each
- VS Code struggles with CSVs over 50MB

**Installed Extensions:**
- Excel Viewer (installed) - works but struggles with 300MB+ files
- Rainbow CSV (NOT installed) - recommended for large files

**Solutions:**
1. **For quick preview:** Use Excel instead of VS Code (works fine)
2. **For VS Code viewing:** Install Rainbow CSV extension
   ```
   Extension ID: mechatroner.rainbow-csv
   ```
3. **For full data exploration:** Install Data Preview
   ```
   Extension ID: randomfractalsinc.vscode-data-preview
   ```

**Status:** DOCUMENTED - not a bug, expected behavior for large files ✓
## Future Enhancements
- [ ] Add data validation rules for row count/column consistency
- [ ] Implement error retry logic for failed conversions
- [ ] Add compression option for large CSVs
- [ ] Create data quality report comparing parquet vs CSV
- [ ] Add schema extraction and documentation
- [ ] Create progress bar for large files

## Quick Reference: Encoding Settings
```python
# ALWAYS use these in file operations:
encoding=\'utf-8\'  # For reading/writing files
encoding=\'utf-8\'  # For CSV exports
encoding=\'utf-8\'  # For log files
```

## If Script Fails Next Time:
1. Check `error_log.txt` for detailed error messages
2. Verify PyArrow is installed: `pip install pyarrow --upgrade`
3. Check that parquet source files exist in correct folders
4. Ensure output folder permissions allow writing
5. Look for encoding issues if unicode characters appear

---
**Script Version:** 1.0 (2026-01-22)  
**Last Successful Run:** 2026-01-22 14:34:56 UTC  
**Next Run:** [when user executes script]

---

# SCRIPT 2: CSV Column Filter

**File:** filter_csv_columns.py  
**Created:** 2026-01-22  
**Purpose:** Select, search, and filter CSV columns by name, then save filtered version

## Features
- Browse and select CSV from csv_output/ folder
- Display all column headers with numbering
- Search columns by name (contains search)
- Interactive selection of which columns to keep
- Auto-save to csv_filtered/ folder
- Full logging to error_log.txt

## How to Run
```powershell
cd "c:\Users\EvanJacobs\Documents\OmniaOffline\Data Cleaning"
python filter_csv_columns.py
```

**Or use VS Code:** Ctrl + F5 (while viewing filter_csv_columns.py)

## Workflow
1. Script finds all CSV files in csv_output/
2. User selects which CSV to filter
3. Script displays all column headers (tabs)
4. User can search for columns by name (contains search)
5. User enters column numbers to KEEP (comma-separated)
6. User confirms save
7. Filtered CSV saved to csv_filtered/ folder with "_filtered" suffix
8. All actions logged to error_log.txt

## Example Usage
```
AVAILABLE CSV FILES
=====================================
1. ANP2 for July - Nov 2025/pi_data_20251230_125107.csv (105.1 MB)
2. ANP2 for July - Nov 2025/pi_data_20251230_132810.csv (100.4 MB)
...

Select CSV file number: 1

COLUMN HEADERS
=====================================
Total columns: 45

 1. timestamp
 2. tag_device
 3. tag_sensor
 4. tag_location
 5. value
...

Search for columns (contains search): tag
Found 3 column(s) containing 'tag':
  1. tag_device
  2. tag_sensor
  3. tag_location

Enter column numbers to KEEP: 1,3,5,6
Selected columns (4):
  - timestamp
  - tag_sensor
  - value
  - unit

Save filtered CSV? (y/n): y

FILE SAVED SUCCESSFULLY
=====================================
Location: c:\Users\...\csv_filtered\pi_data_20251230_125107_filtered.csv
Rows: 1250000
Columns: 4
Size: 8.45 MB
```

## Key Options
- **Enter 'all'** to keep all columns
- **Enter 'none'** to start fresh with no columns
- **Press Enter** when searching to skip search and proceed

## Output
- **Location:** csv_filtered/ folder (organized by source: ANP2 or NAP2)
- **Naming:** [original_name]_filtered.csv
- **Encoding:** UTF-8
- **Index:** Not included in output
- **Folder Structure:** Automatically matches source folder (ANP2/NAP2)

---

## Implementation Notes

**Filter Script Update (2026-01-22):**
- Script now detects source folder (ANP2 or NAP2)
- Automatically creates matching subfolder in csv_filtered/
- Saves filtered files to csv_filtered/[source_folder_name]/
- Folder structure pre-created manually for organization
- Error logging integrated - all operations logged to error_log.txt
- Fixed: Column selection validation improved with better error messages
  * Detects invalid column numbers and provides specific feedback
  * Shows first 20 columns when many columns selected
  * Logs column names to error_log.txt for tracking

**Known Working:**
- Script loads large CSVs (100+ MB) without issues
- Column header display works correctly
- Search function works (contains matching)
- Column selection with comma-separated numbers
- Save to organized subfolder structure
- All logging working to error_log.txt
---

# SCRIPT 3: Web-based CSV Filter (filter_csv_web.py)

**File:** `filter_csv_web.py` & `templates/filter.html`
**Created:** 2026-01-23

## Bugfix: JavaScript TypeError on Render (2026-01-23)

**Issue Reported:** User reported a persistent browser error: `TypeError: Cannot read properties of undefined (reading 'replace')`.

**Investigation:**
*   The error occurred in the JavaScript `renderColumns` function, indicating an object in the `structuredColumns` array from the backend was missing an `id` property.
*   An initial fix to the Python `load_csv` function's logic did not resolve the issue, suggesting the problem was not just the algorithm but the data itself.
*   The new hypothesis is that `pandas.read_csv` might be producing non-string column headers (e.g., `None` or `NaN`) if the CSV header row is malformed. A non-string value would fail during JSON serialization or cause the `item.id` to be undefined/null on the frontend.

**Fix Applied (Attempt 2):**
1.  **Modified `filter_csv_web.py`:**
    *   Added a defensive check at the start of the `for col in current_columns:` loop in the `load_csv` endpoint.
    *   The line `if not isinstance(col, str): continue` was added to explicitly skip any column header that is not a string. This prevents non-string values from being processed and passed to the frontend, hardening the script against malformed CSV headers.

**Status:** FIX APPLIED (Attempt 2). This is a more robust fix targeting the likely root cause of the error.

## UI/Logic Overhaul: Hierarchical View and Timestamp Enforcement (2026-01-23)

**Request:** The user requested to bring back the parent-child hierarchy for column selection, while also ensuring the `timestamp` column is always the first column in the filtered output file. This reverses a previous change that had flattened the UI.

**Changes Applied:**
1.  **Backend (`filter_csv_web.py`):**
    *   **Re-instated Hierarchy Logic:** The `/api/load-csv` endpoint was significantly updated. It now processes the column list into a `structured_columns` array that groups child columns (e.g., `96LIC001/SP`) under their respective parents (e.g., `96LIC001`). It also identifies standalone columns and gives the `timestamp` column a unique type for special handling on the frontend. This structure is sent to the UI, preserving the original column order.
    *   **Enforced Timestamp Position:** The `/api/save-filtered` endpoint was hardened. It now checks for the existence of a `timestamp` column in the original data. If it exists, it is automatically inserted as the first column in the final output file, regardless of whether it was selected in the UI. This guarantees its top position.

2.  **Frontend (`templates/filter.html`):**
    *   **Hierarchical Rendering:** The entire `<script>` block was rewritten. The `renderColumns` JavaScript function now consumes the `structured_columns` array to build a hierarchical view. It creates parent items that can be checked to select/deselect all their children, and it renders standalone columns and the special `timestamp` column (which is checked and disabled by default).
    *   **Updated UI Interactions:** All helper functions (`filterColumns`, `selectAll`, `saveFiltered`, etc.) were adapted to work with the new, more complex DOM, ensuring that searching and bulk selections work intuitively with the hierarchy.

**Status:** IMPLEMENTED. The UI now displays columns in their original order with a clear parent-child structure. The backend guarantees that `timestamp` leads the filtered file, fulfilling all parts of the user's request.

## UI/Logic Overhaul: Simplified Column Selection (2026-01-23)

**Request:** After previous fixes failed to resolve the timestamp issue, the user requested a simpler interface. The desire was to see all columns in their original order and select them from a flat list, with the backend ensuring that a selected timestamp column would automatically be the first column in the output.

**Changes Applied:**
1.  **Frontend (`templates/filter.html`):**
    *   **Removed Hierarchy View:** The complex JavaScript logic for creating a parent/child hierarchy of columns was completely removed.
    *   **Implemented Flat List:** Replaced the hierarchy with a simple function (`renderColumns`) that iterates through all columns in the order received from the backend and displays them as a single, scrollable grid of checkboxes.
    *   **Refactored JS Functions:** All associated JavaScript functions (`saveFiltered`, `selectAll`, `filterColumns`, etc.) were updated to work with the new, simpler DOM structure, which now uses a single `.column-checkbox` class.

2.  **Backend (`filter_csv_web.py`):**
    *   **Modified `save_filtered` Endpoint:** The logic was changed to give the user full control. It no longer forces the inclusion of `timestamp`. Instead, it inspects the list of columns *selected by the user*.
    *   **"Automagic" Timestamp Ordering:** If a column that looks like `timestamp` (case-insensitive, ignoring potential BOM characters) is found in the user's selection, it is automatically moved to the beginning of the column list for the output file. This fulfills the request to have it "automagically" be the first column if selected.

**Status:** SUPERSEDED. This version was replaced by the hierarchical view described above.

## Bugfix: Timestamp Not Included (Attempt 2) (2026-01-23)

**Issue Reported:** User reported that the 'timestamp' column is still not being included in the filtered CSV file. This is a recurrence of a previously reported issue.

**Investigation:**
*   The previous fix, which refactored the JavaScript on the frontend, did not resolve the issue.
*   The new hypothesis is that the CSV files may contain a Byte Order Mark (BOM) at the beginning of the file.
*   A BOM is an invisible character that can cause the first column's name to be misread by `pandas`. For example, instead of being read as `'timestamp'`, it might be read as `'\ufefftimestamp'`.
*   This would cause all checks for the string `'timestamp'` to fail, both in the Python backend and the JavaScript frontend, preventing the column from being correctly identified and included.

**Fix Applied:**
1.  **Modified `filter_csv_web.py`:**
    *   In the `load_csv` function, the `pd.read_csv()` call was updated.
    *   The encoding was changed from `'utf-8'` to `'utf-8-sig'`.
    *   The `'utf-8-sig'` codec in Python is specifically designed to handle and correctly parse UTF-8 encoded files that begin with a BOM.

**Status:** FIX APPLIED & RETAINED. While this was part of a superseded change, the `utf-8-sig` modification was kept in subsequent versions as it represents a best practice for handling potentially BOM-encoded CSV files.