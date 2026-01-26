"""
Web-based Interactive CSV Plotter with Statistics
- Flask backend for data processing
- HTML/JavaScript frontend for interactive plotting
- Column selection
- Statistical metrics calculation
- Correlation analysis
"""

# ===========================
# AUTO-INSTALL DEPENDENCIES
# ===========================

import subprocess
import sys

def install_if_missing(package_name, import_name=None):
    """Install package if not already installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} already installed")
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} installed successfully")

print("\n" + "=" * 60)
print("CHECKING REQUIRED MODULES")
print("=" * 60)

required_packages = [
    ('flask', 'flask'),
    ('pandas', 'pandas'),
    ('numpy', 'numpy'),
]

for package, import_name in required_packages:
    install_if_missing(package, import_name)

print("=" * 60 + "\n")

# ===========================
# IMPORTS
# ===========================

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import logging

# ===========================
# SETUP LOGGING
# ===========================

LOG_FILE = 'error_log.txt'

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {msg}"
    print(log_entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

log_message("=" * 80)
log_message("WEB-BASED INTERACTIVE PLOTTER STARTED")

# ===========================
# FLASK APP SETUP
# ===========================

app = Flask(__name__)
FILTERED_CSV_DIR = Path("csv_filtered")

# In-memory cache for loaded data
current_csv = None
current_df = None

# ===========================
# API ENDPOINTS
# ===========================

@app.route('/')
def index():
    """Serve main HTML page"""
    return render_template('plotter.html')

@app.route('/api/list-csvs', methods=['GET'])
def list_csvs():
    """Get list of available CSV files"""
    csv_files = []
    
    for folder in FILTERED_CSV_DIR.glob("*/"):
        for csv in folder.glob("*_filtered.csv"):
            size_mb = csv.stat().st_size / (1024**2)
            csv_files.append({
                'path': str(csv),
                'name': f"{csv.parent.name}/{csv.name}",
                'size': f"{size_mb:.1f} MB"
            })
    
    csv_files.sort(key=lambda x: x['name'])
    log_message(f"[INFO] Listed {len(csv_files)} CSV files")
    return jsonify({'files': csv_files})

@app.route('/api/load-csv', methods=['POST'])
def load_csv():
    """Load a CSV file and return column information"""
    global current_csv, current_df
    
    data = request.json
    csv_path = data.get('path')
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # Convert timestamp if present
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp').reset_index(drop=True)
            except:
                pass
        
        current_csv = csv_path
        current_df = df
        
        # Get column info
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        log_message(f"[USER] Loaded CSV: {Path(csv_path).name}")
        log_message(f"  - Rows: {len(df):,}")
        log_message(f"  - Columns: {len(df.columns)}")
        log_message(f"  - Numeric columns: {len(numeric_cols)}")
        
        return jsonify({
            'success': True,
            'rows': len(df),
            'columns': list(df.columns),
            'numeric_columns': numeric_cols,
            'has_timestamp': 'timestamp' in df.columns
        })
    except Exception as e:
        log_message(f"[ERROR] Failed to load CSV: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/plot-data', methods=['POST'])
def plot_data():
    """Generate plot data for selected columns"""
    global current_df
    
    if current_df is None:
        return jsonify({'success': False, 'error': 'No CSV loaded'})
    
    data = request.json
    selected_columns = data.get('columns', [])
    
    if not selected_columns:
        return jsonify({'success': False, 'error': 'No columns selected'})
    
    try:
        df = current_df.copy()
        
        # Prepare x-axis
        if 'timestamp' in df.columns:
            x_data = df['timestamp'].astype(str).tolist()
            x_label = 'Timestamp'
        else:
            x_data = list(range(len(df)))
            x_label = 'Sample Index'
        
        # Prepare plot series
        plot_series = []
        for col in selected_columns:
            if col in df.columns:
                y_data = df[col].fillna(None).tolist()
                plot_series.append({
                    'name': col,
                    'x': x_data,
                    'y': y_data
                })
        
        log_message(f"[USER] Plotted {len(plot_series)} columns")
        
        return jsonify({
            'success': True,
            'series': plot_series,
            'x_label': x_label
        })
    except Exception as e:
        log_message(f"[ERROR] Plot generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/statistics', methods=['POST'])
def get_statistics():
    """Calculate statistics for selected columns"""
    global current_df
    
    if current_df is None:
        return jsonify({'success': False, 'error': 'No CSV loaded'})
    
    data = request.json
    selected_columns = data.get('columns', [])
    stats_types = data.get('stats', [])
    
    if not selected_columns or not stats_types:
        return jsonify({'success': False, 'error': 'Columns or stats not selected'})
    
    try:
        df = current_df[selected_columns].select_dtypes(include=[np.number])
        
        results = {}
        
        for col in selected_columns:
            if col not in df.columns:
                continue
            
            col_data = df[col].dropna()
            col_stats = {}
            
            if 'mean' in stats_types:
                col_stats['mean'] = float(col_data.mean())
            if 'median' in stats_types:
                col_stats['median'] = float(col_data.median())
            if 'std' in stats_types:
                col_stats['std'] = float(col_data.std())
            if 'min' in stats_types:
                col_stats['min'] = float(col_data.min())
            if 'max' in stats_types:
                col_stats['max'] = float(col_data.max())
            if 'count' in stats_types:
                col_stats['count'] = int(col_data.count())
            if 'variance' in stats_types:
                col_stats['variance'] = float(col_data.var())
            if 'q25' in stats_types:
                col_stats['q25'] = float(col_data.quantile(0.25))
            if 'q75' in stats_types:
                col_stats['q75'] = float(col_data.quantile(0.75))
            
            results[col] = col_stats
        
        log_message(f"[USER] Calculated statistics for {len(results)} columns")
        
        return jsonify({
            'success': True,
            'statistics': results
        })
    except Exception as e:
        log_message(f"[ERROR] Statistics calculation failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/correlation', methods=['POST'])
def get_correlation():
    """Calculate correlation matrix between selected columns"""
    global current_df
    
    if current_df is None:
        return jsonify({'success': False, 'error': 'No CSV loaded'})
    
    data = request.json
    selected_columns = data.get('columns', [])
    
    if len(selected_columns) < 2:
        return jsonify({'success': False, 'error': 'Need at least 2 columns for correlation'})
    
    try:
        df = current_df[selected_columns].select_dtypes(include=[np.number])
        corr_matrix = df.corr()
        
        # Convert to JSON-serializable format
        corr_dict = {}
        for col1 in corr_matrix.columns:
            corr_dict[col1] = {}
            for col2 in corr_matrix.index:
                corr_dict[col1][col2] = float(corr_matrix.loc[col2, col1])
        
        log_message(f"[USER] Calculated correlation for {len(selected_columns)} columns")
        
        return jsonify({
            'success': True,
            'correlation': corr_dict,
            'columns': list(corr_matrix.columns)
        })
    except Exception as e:
        log_message(f"[ERROR] Correlation calculation failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ===========================
# RUN SERVER
# ===========================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("WEB-BASED INTERACTIVE PLOTTER")
    print("=" * 80)
    print("\nServer starting...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    log_message("[INFO] Starting Flask server on http://localhost:5000")
    
    app.run(debug=True, use_reloader=False)
