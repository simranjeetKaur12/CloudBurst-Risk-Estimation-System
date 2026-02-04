import pandas as pd
from pathlib import Path

IN_CSV = Path("data/processed/labeled_cloudburst.csv")

TRAIN_CSV = Path("data/processed/train.csv")
TEST_CSV  = Path("data/processed/test.csv")

print("🚀 Creating time-based train/test split")

df = pd.read_csv(IN_CSV, parse_dates=["time"])
df = df.sort_values("time")

# -------------------------------
# Time-based split (80 / 20)
# -------------------------------
split_idx = int(len(df) * 0.8)

train = df.iloc[:split_idx]
test  = df.iloc[split_idx:]

train.to_csv(TRAIN_CSV, index=False)
test.to_csv(TEST_CSV, index=False)

print("✅ Split complete")
print(f"Train size: {len(train)}")
print(f"Test size : {len(test)}")
print(f"Train events: {train['cloudburst'].sum()}")
print(f"Test events : {test['cloudburst'].sum()}")
