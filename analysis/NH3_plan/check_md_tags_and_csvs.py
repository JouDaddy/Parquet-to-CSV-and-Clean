import re
import glob
import os
import csv

md_path = r'c:/Users/EvanJacobs/Documents/OmniaOffline/Parquet to CSV and CLean/NH3_Air_Ratio_and_Turbine_IGV_Analysis_Plan.md'
csv_root = r'c:/Users/EvanJacobs/Documents/OmniaOffline/Parquet to CSV and CLean/csv_output'

# Read MD
with open(md_path, 'r', encoding='utf-8') as f:
    md = f.read()

# Extract backticked tokens
backticked = re.findall(r'`([^`]+)`', md)

# Extract slash-style tags (e.g., 95HIC403/PV) and underscore words like Total_Air_Flow
slash_tags = re.findall(r"\b[0-9A-Za-z_\-\.]+/[A-Za-z0-9_\-]+\b", md)
underscore_tags = re.findall(r"\b[A-Za-z0-9_]+\b", md)

# Build candidate tags set: prefer backticked and slash tags
candidates = set()
for t in backticked:
    t = t.strip()
    if t:
        candidates.add(t)
for t in slash_tags:
    candidates.add(t)

# Also add explicit tags often referenced in plan (common names)
extra = ['Total_Air_Flow','Total_NH3_Flow','NAP2_Plant_Load.NAP2_Load_Output']
for e in extra:
    candidates.add(e)

candidates = sorted(candidates)

# Find CSV files
csv_files = glob.glob(os.path.join(csv_root, '**', '*.csv'), recursive=True)

report = []
for path in csv_files:
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            header = next(reader)
            headers = [h.strip() for h in header]
    except Exception as e:
        report.append((path, 'ERROR_READING', str(e)))
        continue
    missing = [t for t in candidates if t not in headers]
    present = [t for t in candidates if t in headers]
    report.append((path, len(missing)==0, missing, present))

# Summarize
print('Extracted candidate tags (count={}):'.format(len(candidates)))
for t in candidates:
    print('-', t)

print('\nCSV Files checked ({}):'.format(len(csv_files)))
for r in report:
    path = r[0]
    status = r[1]
    if status == 'ERROR_READING':
        print(path, 'ERROR:', r[2])
    else:
        ok = 'ALL_PRESENT' if r[1] else 'MISSING'
        print('\nFile:', path)
        print('  Status:', ok)
        print('  Missing count:', len(r[2]))
        if r[2]:
            print('  Missing tags sample:', r[2][:10])
        print('  Present tags sample:', r[3][:10])

# Also compute tags present in all files
all_present = None
for r in report:
    if r[1] == 'ERROR_READING':
        continue
    headers = None
    try:
        with open(r[0], 'r', encoding='utf-8', errors='replace') as f:
            headers = next(csv.reader([f.readline()]))
    except:
        headers = []
    hset = set([h.strip() for h in headers])
    if all_present is None:
        all_present = hset
    else:
        all_present &= hset

if all_present is None:
    all_present = set()

print('\nTags present in ALL CSVs (intersection count={}):'.format(len(all_present)))
for t in sorted(all_present):
    print('-', t)

# Save a simple report file
out_path = os.path.join(os.path.dirname(md_path), 'tag_check_report.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('Candidate tags ({}):\n'.format(len(candidates)))
    for t in candidates:
        f.write(t + '\n')
    f.write('\nCSV files checked ({}):\n'.format(len(csv_files)))
    for r in report:
        path = r[0]
        status = r[1]
        if status == 'ERROR_READING':
            f.write(f'{path} ERROR: {r[2]}\n')
        else:
            ok = 'ALL_PRESENT' if r[1] else 'MISSING'
            f.write(f'File: {path}\n  Status: {ok}\n  Missing count: {len(r[2])}\n')
            if r[2]:
                f.write('  Missing sample: ' + ','.join(r[2][:10]) + '\n')
            f.write('  Present sample: ' + ','.join(r[3][:10]) + '\n')
    f.write('\nTags present in ALL CSVs (intersection):\n')
    for t in sorted(all_present):
        f.write(t + '\n')

print('\nReport written to', out_path)
