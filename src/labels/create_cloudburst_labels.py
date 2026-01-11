import pandas as pd
from pathlib import Path

IN_CSV = Path("data/processed/era5_imerg_features_2005_2015.csv")
OUT_CSV = Path("data/processed/labeled_cloudburst_2005_2015.csv")

print("🚀 Creating percentile-based cloudburst labels")

df = pd.read_csv(IN_CSV, parse_dates=["time"])
df = df.sort_values("time").reset_index(drop=True)

# --------------------------------
# Compute thresholds
# --------------------------------
p99_1h = df["rain_mm"].quantile(0.99)
p99_3h = df["rain_3h"].quantile(0.99)
p99_6h = df["rain_6h"].quantile(0.99)

print("📊 Thresholds:")
print(f"1h rain ≥ {p99_1h:.3f} mm")
print(f"3h rain ≥ {p99_3h:.3f} mm")
print(f"6h rain ≥ {p99_6h:.3f} mm")

# --------------------------------
# Label
# --------------------------------
df["cloudburst"] = (
    (df["rain_mm"] >= p99_1h) |
    (df["rain_3h"] >= p99_3h) |
    (df["rain_6h"] >= p99_6h)
).astype(int)

# --------------------------------
# Summary
# --------------------------------
total = len(df)
events = df["cloudburst"].sum()

print(f"Total hours      : {total}")
print(f"Extreme events   : {events}")
print(f"Event ratio      : {events/total:.3f}")

df.to_csv(OUT_CSV, index=False)
print("✅ Saved:", OUT_CSV)
