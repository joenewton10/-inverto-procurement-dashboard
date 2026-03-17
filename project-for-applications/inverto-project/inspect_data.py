import pandas as pd

FILE = r"C:\Users\Joe\Desktop\application\Job Application\project-for-applications\inverto-project\data\export_CAN_2023_2018.csv"

# Sample first 1000 rows to inspect structure
sample = pd.read_csv(FILE, nrows=1000, low_memory=False)

print("Shape of sample:", sample.shape)
print("\n--- COLUMNS ---")
for col in sample.columns:
    print(f"  {col}")
print("\n--- FIRST 3 ROWS ---")
print(sample.head(3).to_string())
print("\n--- DTYPES ---")
print(sample.dtypes)