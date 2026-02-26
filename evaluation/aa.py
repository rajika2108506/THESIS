import pandas as pd

df = pd.read_excel("data/manual_annotations.xlsx")

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\nFIRST 5 ROWS:")
print(df.head())