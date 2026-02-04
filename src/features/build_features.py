import pandas as pd
from pathlib import Path

IN_CSV  = Path("data/processed/era5_imerg_merged.csv")
OUT_CSV = Path("data/processed/era5_imerg_features.csv")

print("🚀 Building physical cloudburst features")

df = pd.read_csv(IN_CSV, parse_dates=["time"])
df = df.sort_values("time").reset_index(drop=True)

# =====================================================
# RAINFALL FEATURES (IMERG)
# =====================================================

# 1-hour rainfall (already there as rain_mm)
# df["rain_mm"]

# 3-hour rolling rainfall
df["rain_3h"] = df["rain_mm"].rolling(window=3).sum()

# 6-hour accumulated rainfall
df["rain_6h"] = df["rain_mm"].rolling(window=6).sum()

# Peak intensity in last 3 hours
df["rain_peak_3h"] = df["rain_mm"].rolling(window=3).max()

# Rainfall lags
df["rain_lag1"] = df["rain_mm"].shift(1)
df["rain_lag2"] = df["rain_mm"].shift(2)

# =====================================================
# WIND FEATURES (ERA5)
# =====================================================

df["wind_speed"] = (df["u10"]**2 + df["v10"]**2) ** 0.5

# =====================================================
# MOISTURE FEATURES
# =====================================================

df["tcwv_3h"] = df["tcwv"].rolling(window=3).mean()
df["tcwv_6h"] = df["tcwv"].rolling(window=6).mean()

# =====================================================
# DYNAMIC / THERMODYNAMIC FEATURES
# =====================================================

# Pressure drop over 3 hours (negative = falling pressure)
df["sp_drop_3h"] = df["sp"] - df["sp"].shift(3)

# Temperature gradient
df["t2m_grad"] = df["t2m"] - df["t2m"].shift(1)

# =====================================================
# CLEANUP
# =====================================================

# Drop rows with NaNs created by rolling/shift
df = df.dropna().reset_index(drop=True)

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_CSV, index=False)

print("✅ Feature engineering complete")
print("Rows:", len(df))
print("Saved →", OUT_CSV)
