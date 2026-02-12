from datasets import load_dataset
import pandas as pd

# Load the dataset directly from Hugging Face
dataset = load_dataset("dair-ai/emotion", split="test")

# Convert to pandas DataFrame
df = pd.DataFrame(dataset)

# Save as CSV
df.to_csv("emotion_dataset.csv", index=False)

print("CSV file created successfully!")
print("Rows:", len(df))
print("Columns:", df.columns)
