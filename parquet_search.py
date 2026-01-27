import argparse
import os

try:
    import pyarrow.parquet as pq
except Exception:
    pq = None

def scan_parquet_files(root):
    result = {}
    exts = ('.parquet', '.pq')
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith(exts):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, start=os.getcwd())
            cols = []
            try:
                if pq is not None:
                    pf = pq.ParquetFile(full)
                    cols = list(pf.schema.names)
                else:
                    import pandas as pd
                    df = pd.read_parquet(full)
                    cols = list(df.columns.astype(str))
            except Exception as e:
                cols = [f'__error__:{type(e).__name__}: {e}']
            for col in cols:
                if col not in result:
                    result[col] = []
                result[col].append(rel)
    return dict(sorted(result.items()))

def main():
    p = argparse.ArgumentParser(description='Search Parquet column headers')
    p.add_argument('--root', default='parquet_source', help='Root folder to scan')
    p.add_argument('--search', default='', help='Search query (substring, case-insensitive)')
    args = p.parse_args()
    if not os.path.isdir(args.root):
        print(f'Root folder not found: {args.root}')
        return
    cache = scan_parquet_files(args.root)
    query = args.search.strip().lower()
    if query:
        matches = [col for col in cache if query in col.lower()]
        print(f'Matching columns ({len(matches)}):')
        for col in matches:
            print(f'  {col}')
    else:
        print(f'All unique columns ({len(cache)}):')
        for col in cache:
            print(f'  {col}')

if __name__ == '__main__':
    main()
