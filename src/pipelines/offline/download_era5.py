from __future__ import annotations

import argparse
import calendar
from datetime import datetime, timedelta
from pathlib import Path

import cdsapi

try:
    from src.common.regions import resolve_bbox
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.common.regions import resolve_bbox

VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_temperature",
    "surface_pressure",
    "total_precipitation",
    "total_column_water_vapour",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download ERA5 data for the recent N-day window.")
    parser.add_argument("--region", required=True)
    parser.add_argument("--days", type=int, default=10)
    parser.add_argument("--output_dir", default="data/raw/era5")
    return parser.parse_args()


def _month_segments(start: datetime, end: datetime) -> list[tuple[int, int, list[str]]]:
    segments: list[tuple[int, int, list[str]]] = []
    cursor = datetime(start.year, start.month, 1)
    while cursor <= end:
        year = cursor.year
        month = cursor.month
        _, month_days = calendar.monthrange(year, month)
        segment_start = max(start, datetime(year, month, 1))
        segment_end = min(end, datetime(year, month, month_days))
        days = [f"{d:02d}" for d in range(segment_start.day, segment_end.day + 1)]
        segments.append((year, month, days))
        if month == 12:
            cursor = datetime(year + 1, 1, 1)
        else:
            cursor = datetime(year, month + 1, 1)
    return segments


def main() -> None:
    args = parse_args()
    region_key, bbox = resolve_bbox(region=args.region, bbox=None)
    north, west, south, east = bbox

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=max(1, args.days))

    out_root = Path(args.output_dir) / region_key
    out_root.mkdir(parents=True, exist_ok=True)

    client = cdsapi.Client()
    for year, month, days in _month_segments(start_date, end_date):
        out_file = out_root / f"era5_{region_key}_{year}_{month:02d}_latest.zip"
        request = {
            "product_type": "reanalysis",
            "variable": VARIABLES,
            "year": str(year),
            "month": f"{month:02d}",
            "day": days,
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": [north, west, south, east],
            "data_format": "netcdf",
            "download_format": "unarchived",
        }
        client.retrieve("reanalysis-era5-single-levels", request, str(out_file))

    print(f"ERA5 latest-window download complete for {region_key} ({args.days} days)")


if __name__ == "__main__":
    main()
