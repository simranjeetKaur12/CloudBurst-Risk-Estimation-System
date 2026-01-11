import pandas as pd
from pathlib import Path

ERA5_CSV  = Path("data/processed/era5_features_uttarakhand.csv")
IMERG_CSV = Path("data/processed/imerg_hourly_uttarakhand.csv")
OUT_CSV   = Path("data/processed/era5_imerg_merged_2007_2017.csv")

MONSOON_MONTHS = [6, 7, 8, 9]

print("🚀 Merging ERA5 + IMERG")

era5 = pd.read_csv(ERA5_CSV, parse_dates=["time"])
imerg = pd.read_csv(IMERG_CSV, parse_dates=["time"])

era5 = era5[era5["time"].dt.month.isin(MONSOON_MONTHS)]
imerg = imerg[imerg["time"].dt.month.isin(MONSOON_MONTHS)]

df = pd.merge(era5, imerg, on="time", how="inner")
df = df.sort_values("time")

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_CSV, index=False)

print("✅ Merge complete")
print("Rows:", len(df))
