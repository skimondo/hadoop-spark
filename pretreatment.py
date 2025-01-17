import pandas as pd

foreign_exchange_csv_path = "33100036-eng/33100036.csv"
foreign_exchange_csv_path_updated = "33100036-eng/33100036-treated.csv"

print("Loading CSV file...")
df = pd.read_csv(foreign_exchange_csv_path)
print("CSV file loaded successfully.")

print("Starting data treatment...")
print("Removing unnecessary columns...")
df = df.drop(columns=['GEO', 'DGUID', 'SCALAR_FACTOR', 'SCALAR_ID', 'VECTOR', 'COORDINATE', 'STATUS', 'SYMBOL',])

print("Removing columns with no relevant data...")
df = df[df['VALUE'] != 0]

print("Renaming columns...")
df = df.rename(columns={
    'REF_DATE': 'date',
    'Type of currency': 'currency',
    'UOM': 'unit_of_measure',
    'UOM_ID': 'unit_of_measure_id',
    'VALUE': 'Exchange_Rate',
    'TERMINATED': 'Terminated',
    'DECIMALS': 'Decimal_Places'
})

print("Saving new treated csv...")
df.to_csv(foreign_exchange_csv_path_updated, index=False)

print(f"\nData treatment completed. Treated file saved in '{foreign_exchange_csv_path_updated}'")
