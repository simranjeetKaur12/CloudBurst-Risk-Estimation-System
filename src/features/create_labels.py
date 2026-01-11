import pandas as pd
from pathlib import Path

# =========================
# PATHS
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_CSV = PROJECT_ROOT / "data" / "processed" / "era5_features_uttarakhand.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "processed" / "era5_labeled_uttarakhand.csv"

print("🚀 Creating labels from ERA5 data")
print(f"📥 Input: {INPUT_CSV}")
print(f"📤 Output: {OUTPUT_CSV}")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_CSV, parse_dates=["time"])

# Convert precipitation from meters → mm
df["tp_mm"] = df["tp"] * 1000.0

# -------------------------
# EXTREME RAIN LABEL
# -------------------------
threshold = df["tp_mm"].quantile(0.99)
print(f"🔥 Extreme rainfall threshold (99th percentile): {threshold:.2f} mm")

df["extreme_rain"] = (df["tp_mm"] >= threshold).astype(int)

# -------------------------
# BASIC FEATURE ENGINEERING
# -------------------------
df["wind_speed"] = (df["u10"]**2 + df["v10"]**2) ** 0.5
df["temp_c"] = df["t2m"] - 273.15
df["pressure_hpa"] = df["sp"] / 100.0

# -------------------------
# FINAL CLEANUP
# -------------------------
df = df.dropna()
df = df.sort_values("time")

# Save
df.to_csv(OUTPUT_CSV, index=False)

print("✅ Label creation complete")
print(df["extreme_rain"].value_counts())
