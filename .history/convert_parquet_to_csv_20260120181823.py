import pandas as pd

df = pd.read_parquet("test-00000-of-00001.parquet")

print("Number of rows:", len(df))
print("Columns:", df.columns)
print(df.head())

df.to_csv("emotion_test_dataset.csv", index=False)

print("CSV file written")
