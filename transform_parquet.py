import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Configuration
BASE_DIR = Path(r"c:\Users\EvanJacobs\Documents\OmniaOffline\Data Cleaning")
PARQUET_SOURCE = BASE_DIR / "parquet_source"
CSV_OUTPUT = BASE_DIR / "csv_output"
AI_MEMORY = BASE_DIR / "AI_MEMORY.md"
ERROR_LOG = BASE_DIR / "error_log.txt"

class ParquetTransformer:
    def __init__(self):
        self.error_log = []
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "datasets": {}
        }
        # Clear previous error log on init
        with open(ERROR_LOG, 'w', encoding='utf-8') as f:
            f.write(f"=== Transformation Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    def _log_error(self, message):
        """Log error to both console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        self.error_log.append(log_line)
        print(log_line)
        with open(ERROR_LOG, 'a', encoding='utf-8') as f:
            f.write(log_line + "\n")
    
    def transform_all(self):
        """Main transformation pipeline"""
        if not PARQUET_SOURCE.exists():
            error_msg = f"[ERROR] Source directory not found: {PARQUET_SOURCE}"
            self._log_error(error_msg)
            return
        
        # Find all parquet files
        parquet_files = list(PARQUET_SOURCE.glob("**/*.parquet"))
        self.results["total_files"] = len(parquet_files)
        
        if not parquet_files:
            info_msg = "[INFO] No parquet files found in parquet_source/"
            self._log_error(info_msg)
            return
        
        self._log_error(f"[INFO] Found {len(parquet_files)} parquet file(s)")
        
        # Transform each file
        for pq_file in parquet_files:
            self._transform_file(pq_file)
        
        # Update AI memory
        self._update_ai_memory()
        self._print_summary()
    
    def _transform_file(self, pq_file):
        """Transform single parquet file to CSV"""
        try:
            # Extract parent folder name (ANP2, NAP2, etc) and file name
            parent_folder = pq_file.parent.name
            file_name = pq_file.stem
            dataset_key = f"{parent_folder}/{file_name}"
            
            self._log_error(f"[PROCESSING] {parent_folder}/{pq_file.name}...")
            
            # Read parquet
            df = pd.read_parquet(pq_file)
            
            # Create output directory organized by parent folder
            output_dir = CSV_OUTPUT / parent_folder
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write CSV
            csv_path = output_dir / f"{file_name}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            # Log results
            self.results["datasets"][dataset_key] = {
                "status": "success",
                "parent_folder": parent_folder,
                "file_name": file_name,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "file_size_mb": pq_file.stat().st_size / (1024 * 1024),
                "csv_path": str(csv_path)
            }
            self.results["successful"] += 1
            self._log_error(f"[SUCCESS] CSV created: {file_name}.csv")
            
        except Exception as e:
            parent_folder = pq_file.parent.name
            file_name = pq_file.stem
            dataset_key = f"{parent_folder}/{file_name}"
            error_msg = f"[ERROR] Failed to process {pq_file.name}: {str(e)}"
            self._log_error(error_msg)
            self.results["datasets"][dataset_key] = {
                "status": "failed",
                "error": str(e)
            }
            self.results["failed"] += 1
    
    def _update_ai_memory(self):
        """Update AI_MEMORY.md with latest results"""
        memory_content = f"""# AI Memory - Data Transformation Log

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Files: {self.results['total_files']}
- Successful: {self.results['successful']}
- Failed: {self.results['failed']}

## Dataset Inventory

"""
        for dataset_key, info in self.results["datasets"].items():
            if info["status"] == "success":
                checkmark = "[OK]"
                memory_content += f"""### {dataset_key}
- **Status:** {checkmark} Converted
- **Records:** {info['rows']:,}
- **Columns:** {info['columns']}
- **Column Names:** {', '.join(info['column_names'])}
- **Original Size:** {info['file_size_mb']:.2f} MB
- **Output Location:** `csv_output/{info['parent_folder']}/{info['file_name']}.csv`

"""
            else:
                x_mark = "[FAILED]"
                memory_content += f"""### {dataset_key}
- **Status:** {x_mark} Failed
- **Error:** {info['error']}

"""
        
        memory_content += """## Schema Reference
[Column information and data types documented here]

## Processing Notes
- All parquet files in parquet_source/ are automatically scanned
- Each dataset gets its own folder in csv_output/
- Original files remain unchanged

## Next Steps
- [ ] Review CSV outputs
- [ ] Validate data integrity
- [ ] Archive completed datasets

"""
        with open(AI_MEMORY, 'w', encoding='utf-8') as f:
            f.write(memory_content)
    
    def _print_summary(self):
        """Print transformation summary"""
        summary = "\n" + "="*60 + "\nTRANSFORMATION SUMMARY\n" + "="*60 + f"\nTotal Files Processed: {self.results['total_files']}\nSuccessful: {self.results['successful']}\nFailed: {self.results['failed']}\nError Log: {ERROR_LOG}\n" + "="*60
        self._log_error(summary)

if __name__ == "__main__":
    transformer = ParquetTransformer()
    transformer.transform_all()
