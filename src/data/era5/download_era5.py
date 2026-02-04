import cdsapi
from pathlib import Path
import calendar
import time

# ==============================
# CONFIG
# ==============================

OUTPUT_DIR = Path("data/raw/era5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Uttarakhand bounding box
# [North, West, South, East]
AREA = [31.2, 78.5, 29.0, 80.5]

VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_dewpoint_temperature",
    "2m_temperature",
    "mean_sea_level_pressure",
    "surface_pressure",
    "total_precipitation",
    "convective_precipitation",
    "large_scale_precipitation",
    "convective_available_potential_energy",
    "total_column_water_vapour",
]

START_YEAR = 2005
END_YEAR = 2024   # ⚠ TEST WITH ONE YEAR FIRST

# ==============================
# DOWNLOAD
# ==============================

def download_era5():
    client = cdsapi.Client()

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):

            out_file = OUTPUT_DIR / f"era5_{year}_{month:02d}.nc"
            if out_file.exists():
                print(f"✔ Exists: {out_file.name}")
                continue

            days = [
                f"{d:02d}"
                for d in range(1, calendar.monthrange(year, month)[1] + 1)
            ]

            request = {
                "product_type": "reanalysis",
                "variable": VARIABLES,
                "year": str(year),
                "month": f"{month:02d}",
                "day": days,
                "time": [f"{h:02d}:00" for h in range(24)],
                "area": AREA,
                "format": "netcdf",  # ✅ THIS IS THE KEY
            }

            print(f"⬇ Downloading ERA5 {year}-{month:02d}")
            client.retrieve(
                "reanalysis-era5-single-levels",
                request,
                str(out_file),
            )

            

    print("✅ DONE")

if __name__ == "__main__":
    download_era5()
