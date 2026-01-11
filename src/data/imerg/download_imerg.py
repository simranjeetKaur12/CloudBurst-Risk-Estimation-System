from tqdm import tqdm
import earthaccess
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import time

# ==============================
# CONFIG
# ==============================

START_YEAR = 2006
END_YEAR   = 2014
MONSOON_MONTHS = [6, 7, 8, 9]

IMERG_SHORT_NAME = "GPM_3IMERGHH"
IMERG_VERSION = "07"
PROVIDER = "GES_DISC"

RAW_DIR = Path("data/raw/imerg")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 🔑 This file tracks PROCESSED DAYS (not timestamps)
PROCESSED_DAYS_CSV = Path("data/processed/imerg_processed_days.csv")
PROCESSED_DAYS_CSV.parent.mkdir(parents=True, exist_ok=True)

SLEEP_SECONDS = 1

# ==============================
# LOGIN
# ==============================
earthaccess.login(persist=True)

# ==============================
# LOAD PROCESSED DAYS
# ==============================
processed_days = set()

if PROCESSED_DAYS_CSV.exists():
    df_days = pd.read_csv(PROCESSED_DAYS_CSV, parse_dates=["date"])
    processed_days = set(df_days["date"].dt.date)

print(f"📌 Loaded {len(processed_days)} processed days")

# ==============================
# DOWNLOAD LOOP
# ==============================
for year in range(START_YEAR, END_YEAR + 1):
    for month in MONSOON_MONTHS:

        print(f"\n📅 Year {year}, Month {month}")

        start_date = datetime(year, month, 1)
        end_date = (
            datetime(year, month + 1, 1) - timedelta(days=1)
            if month < 12 else
            datetime(year, 12, 31)
        )

        current = start_date

        while current <= end_date:
            day = current.date()

            # ✅ Skip if already processed
            if day in processed_days:
                print(f"  ✅ {day} already processed — skipping")
                current += timedelta(days=1)
                continue

            save_path = RAW_DIR / f"{year}/{month:02d}/{current.day:02d}"
            save_path.mkdir(parents=True, exist_ok=True)

            # ✅ Skip if raw files already exist
            if any(save_path.glob("*.HDF5")):
                print(f"  📁 Raw files exist for {day} — skipping download")
                current += timedelta(days=1)
                continue

            print(f"  ⬇ Downloading {day}")

            results = earthaccess.search_data(
                short_name=IMERG_SHORT_NAME,
                version=IMERG_VERSION,
                temporal=(
                    current.strftime("%Y-%m-%d"),
                    (current + timedelta(days=1)).strftime("%Y-%m-%d"),
                ),
                provider=PROVIDER,
            )

            if not results:
                print(f"  ⚠ No granules found")
                current += timedelta(days=1)
                continue

            for g in tqdm(results, desc="    Granules", unit="file"):
                earthaccess.download(g, save_path, threads=1)
                time.sleep(SLEEP_SECONDS)

            current += timedelta(days=1)

print("\n✅ IMERG download completed safely")
