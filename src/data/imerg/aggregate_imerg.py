import pandas as pd
from pathlib import Path

IN_CSV  = Path("data/processed/imerg_halfhourly_uttarakhand.csv")
OUT_CSV = Path("data/processed/imerg_hourly_uttarakhand.csv")

print("🚀 Aggregating IMERG → hourly")

df = pd.read_csv(IN_CSV)

df["time"] = pd.to_datetime(df["time"], format="mixed", errors="coerce")
df = df.dropna(subset=["time", "rain_mm_hr"])

df["rain_mm"] = df["rain_mm_hr"] * 0.5
df["time"] = df["time"].dt.floor("h")

hourly = (
    df.groupby("time", as_index=False)["rain_mm"]
      .sum()
)

hourly.to_csv(OUT_CSV, index=False)

print("✅ Hourly aggregation complete")
print(f"Rows: {len(hourly)}")
