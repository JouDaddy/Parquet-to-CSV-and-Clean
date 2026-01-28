import argparse
import os

try:
    import pyarrow.parquet as pq
    import pyarrow as pa
except Exception:
    pq = None
    pa = None

def scan_parquet_files(root):
    result = {}
    min_time = None
    max_time = None
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
                    # Find datetime columns
                    schema = pf.schema_arrow
                    datetime_cols = [field.name for field in schema if pa and pa.types.is_timestamp(field.type)]
                    if datetime_cols:
                        table = pq.read_table(full, columns=datetime_cols)
                        df = table.to_pandas()
                        for col in datetime_cols:
                            if not df[col].empty:
                                col_min = df[col].min()
                                col_max = df[col].max()
                                if min_time is None or col_min < min_time:
                                    min_time = col_min
                                if max_time is None or col_max > max_time:
                                    max_time = col_max
                else:
                    import pandas as pd
                    df = pd.read_parquet(full)
                    cols = list(df.columns.astype(str))
                    # Find datetime columns
                    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                    for col in datetime_cols:
                        if not df[col].empty:
                            col_min = df[col].min()
                            col_max = df[col].max()
                            if min_time is None or col_min < min_time:
                                min_time = col_min
                            if max_time is None or col_max > max_time:
                                max_time = col_max
            except Exception as e:
                cols = [f'__error__:{type(e).__name__}: {e}']
            for col in cols:
                if col not in result:
                    result[col] = []
                result[col].append(rel)
    return dict(sorted(result.items())), min_time, max_time

def main():
    p = argparse.ArgumentParser(description='Search Parquet column headers')
    p.add_argument('--root', default='parquet_source', help='Root folder to scan')
    p.add_argument('--search', default='', help='Search query (substring, case-insensitive)')
    args = p.parse_args()
    if not os.path.isdir(args.root):
        print(f'Root folder not found: {args.root}')
        return
    cache, min_time, max_time = scan_parquet_files(args.root)
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
    if min_time is not None and max_time is not None:
        print(f'Data time range: {min_time} to {max_time}')
    else:
        print('No datetime data found.')

if __name__ == '__main__':
    main()
