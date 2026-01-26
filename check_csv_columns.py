import pandas as pd

df1 = pd.read_csv('c:/Users/EvanJacobs/Documents/OmniaOffline/Parquet to CSV and CLean/csv_output/ANP2 for July - Nov 2025/pi_data_20251230_125107.csv')
df2 = pd.read_csv('c:/Users/EvanJacobs/Documents/OmniaOffline/Parquet to CSV and CLean/csv_output/NAP2 for July - Nov 2025/pi_data_20251229_151817.csv')

print('ANP2 Columns:', df1.columns.tolist())
print('NAP2 Columns:', df2.columns.tolist())