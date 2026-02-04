import pandas as pd
from pathlib import Path

# --------------------------------
# CONFIG
# --------------------------------
IN_CSV = Path("data/processed/era5_imerg_features.csv")
OUT_CSV = Path("data/processed/labeled_cloudburst.csv")

print("🚀 Creating calibrated cloudburst labels")

# --------------------------------
# LOAD
# --------------------------------
df = pd.read_csv(IN_CSV, parse_dates=["time"])
df = df.sort_values("time").reset_index(drop=True)

# --------------------------------
# DATA-DRIVEN THRESHOLDS
# --------------------------------
p97_1h = df["rain_mm"].quantile(0.97)
p97_3h = df["rain_3h"].quantile(0.97)
p97_6h = df["rain_6h"].quantile(0.97)

p95_peak = df["rain_peak_3h"].quantile(0.95)
p90_sp_drop = df["sp_drop_3h"].quantile(0.10)  # negative tail
p90_tcwv = df["tcwv_3h"].quantile(0.90)

print("\n=== Thresholds ===")
print(f"1h rain ≥ {p97_1h:.4f}")
print(f"3h rain ≥ {p97_3h:.4f}")
print(f"6h rain ≥ {p97_6h:.4f}")
print(f"3h peak ≥ {p95_peak:.4f}")
print(f"SP drop ≤ {p90_sp_drop:.2f}")
print(f"TCWV 3h ≥ {p90_tcwv:.2f}")

# --------------------------------
# LABEL LOGIC
# --------------------------------

# Tier 1: Extreme relative rainfall
tier1 = (
    (df["rain_mm"] >= p97_1h) |
    (df["rain_3h"] >= p97_3h) |
    (df["rain_6h"] >= p97_6h)
)

# Tier 2: Concentrated burst + atmospheric trigger
tier2 = (
    (df["rain_peak_3h"] >= p95_peak) &
    (df["sp_drop_3h"] <= p90_sp_drop) &
    (df["tcwv_3h"] >= p90_tcwv)
)

df["cloudburst"] = (tier1 | tier2).astype(int)

# --------------------------------
# SUMMARY
# --------------------------------
total = len(df)
events = df["cloudburst"].sum()

print("\n=== LABEL SUMMARY ===")
print(f"Total hours       : {total}")
print(f"Cloudburst hours : {events}")
print(f"Event ratio      : {events / total:.4f}")
print("Tier-1 count     :", tier1.sum())
print("Tier-2 count     :", tier2.sum())

# --------------------------------
# SAVE
# --------------------------------
df.to_csv(OUT_CSV, index=False)
print("\n✅ Saved:", OUT_CSV)
