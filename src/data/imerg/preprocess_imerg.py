import os
import glob
from pathlib import Path
from datetime import datetime

import xarray as xr
import pandas as pd
import numpy as np

# =====================
# PATHS
# =====================
PROJECT_ROOT = Path(__file__).resolve().parents[3]

IMERG_DIR = PROJECT_ROOT / "data/raw/imerg"
OUT_CSV = PROJECT_ROOT / "data/processed/imerg_halfhourly_uttarakhand.csv"
PROCESSED_DAYS_CSV = PROJECT_ROOT / "data/processed/imerg_processed_days.csv"

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# =====================
# REGION
# =====================
LAT_MIN, LAT_MAX = 28.0, 31.5
LON_MIN, LON_MAX = 77.0, 81.0

GROUP = "Grid"
RAIN_VAR = "precipitation"
FILL_VALUE = -9999.9

DELETE_RAW_FILES = False

print("🚀 IMERG preprocessing started")

# =====================
# LOAD PROCESSED DAYS
# =====================
processed_days = set()

if PROCESSED_DAYS_CSV.exists():
    df = pd.read_csv(PROCESSED_DAYS_CSV, parse_dates=["date"])
    processed_days = set(df["date"].dt.date)

print(f"📌 Loaded {len(processed_days)} processed days")

# =====================
# INIT OUTPUT
# =====================
if not OUT_CSV.exists():
    pd.DataFrame(columns=["time", "rain_mm_hr"]).to_csv(OUT_CSV, index=False)

files = sorted(glob.glob(str(IMERG_DIR / "**/*.HDF5"), recursive=True))
print(f"📂 Found {len(files)} IMERG files")

new_days = set()

for f in files:
    try:
        name = Path(f).name

        date_part = name.split("3IMERG.")[1][:8]
        time_part = name.split("-S")[1][:6]
        timestamp = datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
        day = timestamp.date()

        if day in processed_days:
            continue

        ds = xr.open_dataset(
            f,
            group=GROUP,
            decode_times=False,
            mask_and_scale=True,
        )

        rain = ds[RAIN_VAR].where(ds[RAIN_VAR] != FILL_VALUE)

        rain = rain.sel(
            lat=slice(LAT_MIN, LAT_MAX),
            lon=slice(LON_MIN, LON_MAX),
        )

        rain_mean = float(rain.mean(skipna=True).values)
        ds.close()

        if np.isnan(rain_mean):
            continue

        pd.DataFrame(
            [{"time": timestamp, "rain_mm_hr": rain_mean}]
        ).to_csv(OUT_CSV, mode="a", header=False, index=False)

        new_days.add(day)

        if DELETE_RAW_FILES:
            os.remove(f)

    except Exception as e:
        print(f"❌ Failed: {f}\n{e}")

# =====================
# UPDATE PROCESSED DAYS
# =====================
if new_days:
    pd.DataFrame(
        [{"date": d} for d in sorted(new_days)]
    ).to_csv(
        PROCESSED_DAYS_CSV,
        mode="a",
        header=not PROCESSED_DAYS_CSV.exists(),
        index=False,
    )

print("🎉 IMERG preprocessing COMPLETE")
print(f"📅 New days processed: {len(new_days)}")
