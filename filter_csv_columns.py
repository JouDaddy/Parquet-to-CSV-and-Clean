import os
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(r"c:\Users\EvanJacobs\Documents\OmniaOffline\Data Cleaning")
CSV_OUTPUT = BASE_DIR / "csv_output"
FILTERED_OUTPUT = BASE_DIR / "csv_filtered"
ERROR_LOG = BASE_DIR / "error_log.txt"

def log_to_file(message):
    """Log to error_log.txt"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(ERROR_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")

class CSVColumnFilter:
    def __init__(self):
        self.csv_files = []
        self.selected_file = None
        self.df = None
        self.selected_columns = []
        log_to_file("[INFO] CSV Column Filter initialized")
    
    def find_csv_files(self):
        """Find all CSV files in csv_output folder"""
        try:
            csv_files = list(CSV_OUTPUT.glob("**/*.csv"))
            if not csv_files:
                log_to_file("[ERROR] No CSV files found in csv_output/")
                return False
            
            self.csv_files = sorted(csv_files)
            log_to_file(f"[INFO] Found {len(self.csv_files)} CSV file(s)")
            return True
        except Exception as e:
            log_to_file(f"[ERROR] Failed to find CSV files: {str(e)}")
            return False
    
    def display_csv_menu(self):
        """Display available CSV files and let user select"""
        print("\n" + "="*60)
        print("AVAILABLE CSV FILES")
        print("="*60)
        
        for i, csv_file in enumerate(self.csv_files, 1):
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"{i}. {csv_file.parent.name}/{csv_file.name} ({size_mb:.1f} MB)")
        
        while True:
            try:
                choice = input("\nSelect CSV file number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    log_to_file("[INFO] User quit from CSV selection")
                    return False
                
                index = int(choice) - 1
                if 0 <= index < len(self.csv_files):
                    self.selected_file = self.csv_files[index]
                    log_to_file(f"[SELECTED] {self.selected_file.name}")
                    return True
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def load_csv(self):
        """Load the selected CSV file"""
        try:
            print(f"\nLoading {self.selected_file.name}...")
            self.df = pd.read_csv(self.selected_file, encoding='utf-8')
            log_to_file(f"[INFO] Loaded CSV: {self.selected_file.name} ({len(self.df)} rows, {len(self.df.columns)} columns)")
            return True
        except Exception as e:
            log_to_file(f"[ERROR] Failed to load CSV: {str(e)}")
            print(f"Error loading CSV: {e}")
            return False
    
    def display_columns(self):
        """Display all column headers"""
        print("\n" + "="*60)
        print("COLUMN HEADERS")
        print("="*60)
        print(f"Total columns: {len(self.df.columns)}\n")
        
        for i, col in enumerate(self.df.columns, 1):
            print(f"{i:2d}. {col}")
        
        print("\n" + "="*60)
    
    def search_columns(self):
        """Search/filter columns by name (contains search)"""
        while True:
            print("\n" + "="*60)
            print("SEARCH COLUMNS")
            print("="*60)
            
            search_term = input("Search for columns (contains search) - or press Enter to skip: ").strip().lower()
            
            if not search_term:
                log_to_file("[INFO] User skipped column search")
                break
            
            matches = [col for col in self.df.columns if search_term in col.lower()]
            
            if not matches:
                print(f"No columns found containing '{search_term}'")
                continue
            
            print(f"\nFound {len(matches)} column(s) containing '{search_term}':")
            for i, col in enumerate(matches, 1):
                print(f"  {i}. {col}")
            
            log_to_file(f"[SEARCH] Found {len(matches)} columns matching '{search_term}'")
            break
    
    def select_columns_interactive(self):
        """Interactive column selection"""
        self.display_columns()
        self.search_columns()
        
        print("\n" + "="*60)
        print("SELECT COLUMNS TO KEEP")
        print("="*60)
        print("Enter column numbers separated by commas (e.g., 1,3,5)")
        print("Or enter 'all' to keep all columns")
        print("Or enter 'none' to start from scratch")
        
        while True:
            try:
                choice = input("\nEnter column numbers to KEEP: ").strip().lower()
                
                if choice == 'all':
                    self.selected_columns = list(self.df.columns)
                    log_to_file(f"[SELECTION] User selected ALL {len(self.selected_columns)} columns")
                    break
                
                if choice == 'none':
                    self.selected_columns = []
                    log_to_file("[SELECTION] User selected NONE - starting fresh")
                    break
                
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                
                # Validate indices
                invalid_indices = [i for i in indices if not (0 <= i < len(self.df.columns))]
                if invalid_indices:
                    print(f"Invalid column numbers: {[i+1 for i in invalid_indices]}. Please try again.")
                    continue
                
                self.selected_columns = [self.df.columns[i] for i in indices]
                log_to_file(f"[SELECTION] User selected {len(self.selected_columns)} columns: {', '.join(self.selected_columns[:5])}...")
                break
            
            except ValueError as e:
                log_to_file(f"[ERROR] Invalid input: {str(e)}")
                print("Please enter valid column numbers (comma-separated integers)")
        
        if self.selected_columns:
            print(f"\nSelected columns ({len(self.selected_columns)}):")
            for col in self.selected_columns[:20]:  # Show first 20
                print(f"  - {col}")
            if len(self.selected_columns) > 20:
                print(f"  ... and {len(self.selected_columns) - 20} more")
        else:
            print("\nNo columns selected.")
    
    def save_filtered_csv(self):
        """Save filtered CSV to new output folder organized by source"""
        if not self.selected_columns:
            print("No columns selected. Nothing to save.")
            log_to_file("[WARNING] User attempted to save with no columns selected")
            return False
        
        try:
            # Get the parent folder name (ANP2 for July - Nov 2025, etc)
            source_folder = self.selected_file.parent.name
            
            # Create filtered output folder with matching subfolder structure
            filtered_subfolder = FILTERED_OUTPUT / source_folder
            filtered_subfolder.mkdir(parents=True, exist_ok=True)
            
            # Filter dataframe
            filtered_df = self.df[self.selected_columns]
            
            # Generate output filename
            original_name = self.selected_file.stem
            filtered_name = f"{original_name}_filtered.csv"
            output_path = filtered_subfolder / filtered_name
            
            # Save
            filtered_df.to_csv(output_path, index=False, encoding='utf-8')
            
            file_size = output_path.stat().st_size / (1024 * 1024)
            log_to_file(f"[SUCCESS] Saved filtered CSV: {source_folder}/{filtered_name} ({len(filtered_df)} rows, {len(self.selected_columns)} columns, {file_size:.2f} MB)")
            
            print("\n" + "="*60)
            print("FILE SAVED SUCCESSFULLY")
            print("="*60)
            print(f"Location: {output_path}")
            print(f"Rows: {len(filtered_df)}")
            print(f"Columns: {len(self.selected_columns)}")
            print(f"Size: {file_size:.2f} MB")
            print("="*60)
            
            return True
        
        except Exception as e:
            log_to_file(f"[ERROR] Failed to save filtered CSV: {str(e)}")
            print(f"Error saving file: {e}")
            return False
    
    def run(self):
        """Main workflow"""
        print("\n" + "="*60)
        print("CSV COLUMN FILTER")
        print("="*60)
        
        # Find files
        if not self.find_csv_files():
            return
        
        # Select file
        if not self.display_csv_menu():
            return
        
        # Load CSV
        if not self.load_csv():
            return
        
        # Select columns
        self.select_columns_interactive()
        
        # Save
        if input("\nSave filtered CSV? (y/n): ").lower() == 'y':
            self.save_filtered_csv()
        else:
            log_to_file("[INFO] User cancelled save operation")

if __name__ == "__main__":
    filter_tool = CSVColumnFilter()
    filter_tool.run()
    print("\nDone!")
