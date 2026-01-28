import sys
import subprocess
import importlib

def check_and_install(package):
    """Checks if a package is installed and installs it if not."""
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"'{package}' not found. Installing...")
        try:
            # Use sys.executable to ensure pip is from the correct environment
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install '{package}'. Please install it manually and run the script again.")
            sys.exit(1)

# Check for required packages before proceeding
required_packages = ['pandas', 'flask']
for pkg in required_packages:
    check_and_install(pkg)

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify
import json

# Configuration
BASE_DIR = Path(r"c:\Users\EvanJacobs\Documents\OmniaOffline\Parquet-to-CSV-and-Clean")
CSV_OUTPUT = BASE_DIR / "csv_output"
FILTERED_OUTPUT = BASE_DIR / "csv_filtered"
ERROR_LOG = BASE_DIR / "error_log.txt"
TEMPLATES_DIR = BASE_DIR / "templates"

def log_to_file(message):
    """Log to error_log.txt"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")

# Flask app
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Global state
csv_files = []
selected_csvs = []  # List of selected CSV files
current_dfs = {}  # Dict of filename to dataframe
current_columns = []

def find_csv_files():
    """Find all CSV files"""
    global csv_files
    try:
        csv_files = sorted(list(CSV_OUTPUT.glob("**/*.csv")))
        log_to_file(f"[INFO] Found {len(csv_files)} CSV file(s)")
        return True
    except Exception as e:
        log_to_file(f"[ERROR] Failed to find CSV files: {str(e)}")
        return False

def build_column_hierarchy(columns):
    """Build hierarchical structure for parent-child columns (e.g., 96LIC001 -> [96LIC001/SP, 96LIC001/OUT, 96LIC001/PV])"""
    hierarchy = {}
    
    for col in columns:
        if '/' in col:
            parent = col.split('/')[0]
            if parent not in hierarchy:
                hierarchy[parent] = {'parent': parent, 'children': []}
            hierarchy[parent]['children'].append(col)
    
    # Sort children for each parent
    for parent in hierarchy:
        hierarchy[parent]['children'].sort()
    
    return hierarchy

@app.route('/')
def index():
    """Main page"""
    file_list = []
    for i, csv_file in enumerate(csv_files):
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        file_list.append({
            'index': i,
            'name': csv_file.name,
            'parent': csv_file.parent.name,
            'size': f"{size_mb:.1f} MB",
            'display': f"{csv_file.parent.name}/{csv_file.name}"
        })
    
    return render_template('filter.html', files=file_list)

@app.route('/api/get-folders', methods=['GET'])
def get_folders():
    """Get list of existing folders for output selection"""
    try:
        folders = []
        # Get folders from csv_filtered
        if FILTERED_OUTPUT.exists():
            for item in FILTERED_OUTPUT.iterdir():
                if item.is_dir():
                    folders.append({
                        'name': item.name,
                        'path': str(item)
                    })
        
        # Also include csv_output folders as options
        if CSV_OUTPUT.exists():
            for item in CSV_OUTPUT.iterdir():
                if item.is_dir():
                    folder_path = FILTERED_OUTPUT / item.name
                    if not any(f['path'] == str(folder_path) for f in folders):
                        folders.append({
                            'name': f"{item.name} (new)",
                            'path': str(folder_path)
                        })
        
        return jsonify({'folders': folders})
    
    except Exception as e:
        log_to_file(f"[ERROR] Failed to get folders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-files', methods=['POST'])
def validate_files():
    """Validate selected files have matching columns"""
    global selected_csvs, current_dfs, current_columns
    
    try:
        file_indices = request.json.get('indices', [])
        if not file_indices:
            return jsonify({'success': False, 'error': 'No files selected'})
        
        selected_csvs = [csv_files[i] for i in file_indices]
        current_dfs = {}
        column_sets = []
        
        for csv_file in selected_csvs:
            log_to_file(f"[VALIDATING] {csv_file.name}")
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            current_dfs[csv_file.name] = df
            columns = list(df.columns)
            column_sets.append(set(columns))
        
        # Check if all files have the same columns
        first_columns = column_sets[0]
        all_match = all(cols == first_columns for cols in column_sets)
        
        if not all_match:
            return jsonify({
                'success': False, 
                'error': 'Selected files have different column structures. Please select files with matching headers.'
            })
        
        current_columns = list(first_columns)
        hierarchy = build_column_hierarchy(current_columns)
        
        processed_items = set()
        structured_columns = []

        for col in current_columns:
            if not isinstance(col, str):
                log_to_file(f"[WARNING] Skipping non-string column header: {col}")
                continue

            if col in processed_items:
                continue

            is_timestamp = col.lstrip('\ufeff').lower() == 'timestamp'
            if is_timestamp:
                structured_columns.append({'id': col, 'type': 'timestamp'})
                processed_items.add(col)
                continue

            parent_name_of_col = col.split('/')[0] if '/' in col else col
            if parent_name_of_col in hierarchy:
                parent_group = hierarchy[parent_name_of_col]
                structured_columns.append({
                    'id': parent_group['parent'],
                    'type': 'parent',
                    'children': parent_group['children']
                })
                processed_items.add(parent_group['parent'])
                for child_col in parent_group['children']:
                    processed_items.add(child_col)
            else:
                structured_columns.append({'id': col, 'type': 'standalone'})
                processed_items.add(col)

        log_to_file(f"[SUCCESS] Validated {len(selected_csvs)} files with matching columns: {len(current_columns)} columns")
        
        return jsonify({
            'success': True,
            'files': [f.name for f in selected_csvs],
            'columns': structured_columns,
            'total_columns': len(current_columns),
            'total_files': len(selected_csvs)
        })
    
    except Exception as e:
        error_msg = f"Failed to validate files: {str(e)}"
        log_to_file(f"[ERROR] {error_msg}")
        return jsonify({'success': False, 'error': error_msg})

@app.route('/api/save-filtered', methods=['POST'])
def save_filtered():
    """Save filtered CSVs for all selected files"""
    global selected_csvs, current_dfs
    
    log_to_file(f"[DEBUG] save-filtered called with method: {request.method}")
    log_to_file(f"[DEBUG] Content-Type: {request.headers.get('Content-Type')}")
    log_to_file(f"[DEBUG] Request data: {request.get_data()}")
    
    try:
        if not current_dfs:
            raise ValueError("No files loaded")
        
        selected_columns = request.json.get('selected_columns', [])
        output_path = request.json.get('output_path')

        if not selected_columns:
            raise ValueError("No columns selected to save.")

        # --- Enforce Timestamp as First Column ---
        timestamp_col = None
        for col in list(current_dfs.values())[0].columns:  # Use first df to find timestamp
            if col.lstrip('\ufeff').lower() == 'timestamp':
                timestamp_col = col
                break
        
        final_columns = list(selected_columns)

        if timestamp_col:
            if timestamp_col in final_columns:
                final_columns.remove(timestamp_col)
            final_columns.insert(0, timestamp_col)
        # --- End of Timestamp Logic ---
        
        results = []
        total_saved = 0
        
        for csv_file in selected_csvs:
            # Determine output directory
            if output_path is None:
                # Default behavior
                source_folder = csv_file.parent.name
                output_dir = FILTERED_OUTPUT / source_folder
                log_to_file(f"[DEBUG] Using default output dir: {output_dir}")
            elif isinstance(output_path, str):
                # Existing folder selected
                output_dir = Path(output_path)
                log_to_file(f"[DEBUG] Using existing folder: {output_dir}")
            elif isinstance(output_path, dict):
                # New folder to create
                parent_path_str = output_path['parentPath']
                folder_name = output_path['name']
                
                # Validate inputs
                if not parent_path_str or not folder_name:
                    raise ValueError("Parent path and folder name cannot be empty")
                
                # Convert to Path object and resolve
                parent_path = Path(parent_path_str).resolve()
                if not parent_path.exists():
                    raise ValueError(f"Parent path does not exist: {parent_path}")
                
                output_dir = parent_path / folder_name
                log_to_file(f"[DEBUG] Creating new folder: {output_dir} (parent: {parent_path}, name: {folder_name})")
            else:
                raise ValueError("Invalid output path configuration")
            
            log_to_file(f"[DEBUG] Creating directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filtered dataframe
            final_columns_unique = list(dict.fromkeys(final_columns))
            filtered_df = current_dfs[csv_file.name][final_columns_unique]
            
            # Save
            original_name = csv_file.stem
            filtered_name = f"{original_name}_filtered.csv"
            output_file_path = output_dir / filtered_name
            
            filtered_df.to_csv(output_file_path, index=False, encoding='utf-8')
            
            file_size = output_file_path.stat().st_size / (1024 * 1024)
            
            # Determine display path
            try:
                display_path = output_file_path.relative_to(BASE_DIR)
            except ValueError:
                display_path = output_file_path
            
            log_to_file(f"[SUCCESS] Saved: {display_path} ({len(filtered_df)} rows, {len(final_columns_unique)} columns, {file_size:.2f} MB)")
            
            results.append({
                'filename': filtered_name,
                'path': str(display_path),
                'rows': len(filtered_df),
                'columns': len(final_columns_unique),
                'size': f"{file_size:.2f} MB"
            })
            total_saved += 1
        
        return jsonify({
            'success': True,
            'results': results,
            'total_saved': total_saved
        })
    
    except Exception as e:
        error_msg = f"Failed to save: {str(e)}"
        log_to_file(f"[ERROR] {error_msg}")
        return jsonify({'success': False, 'error': error_msg})

if __name__ == '__main__':
    log_to_file("[INFO] CSV Column Filter (Web) initialized")
    
    find_csv_files()
    
    if not csv_files:
        log_to_file("[ERROR] No CSV files found. Exiting.")
        print("No CSV files found in csv_output/")
        exit(1)
    
    # Open browser
    def open_browser():
        try:
            threading.Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
        except Exception as e:
            log_to_file(f"[WARNING] Could not open browser automatically: {e}")
    
    try:
        open_browser()
        log_to_file("[INFO] Browser window opening...")
    except Exception as e:
        log_to_file(f"[WARNING] Browser opening failed: {e}")
    
    app.run(debug=False, port=5000)
