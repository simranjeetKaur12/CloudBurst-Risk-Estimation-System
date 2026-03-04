import argparse
import calendar
import logging
import time
from pathlib import Path

import cdsapi

try:
    from src.common.regions import list_regions, resolve_bbox
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.common.regions import list_regions, resolve_bbox

DEFAULT_OUTPUT_DIR = "data/raw/era5"

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_year", type=int, required=True)
    parser.add_argument("--end_year", type=int, required=True)
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--region", type=str, default="himalayan_west")
    parser.add_argument(
        "--bbox",
        type=str,
        default=None,
        help="Custom bbox in 'north,west,south,east'. Overrides --region preset.",
    )
    parser.add_argument("--retry", type=int, default=3)
    parser.add_argument("--sleep_seconds", type=int, default=5)
    parser.add_argument("--list_regions", action="store_true")
    return parser.parse_args()


def download_era5(start_year, end_year, output_dir, retries, sleep_seconds, region, bbox):
    region_key, area = resolve_bbox(region=region, bbox=bbox)
    output_path = Path(output_dir) / region_key
    output_path.mkdir(parents=True, exist_ok=True)

    logging.info("Region: %s | Area: %s", region_key, area)
    client = cdsapi.Client()

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            out_file = output_path / f"era5_{region_key}_{year}_{month:02d}.nc"

            if out_file.exists():
                logging.info("Exists: %s", out_file.name)
                continue

            days = [f"{d:02d}" for d in range(1, calendar.monthrange(year, month)[1] + 1)]

            request = {
                "product_type": "reanalysis",
                "variable": VARIABLES,
                "year": str(year),
                "month": f"{month:02d}",
                "day": days,
                "time": [f"{h:02d}:00" for h in range(24)],
                "area": area,
                "format": "netcdf",
            }

            for attempt in range(retries):
                try:
                    logging.info("Downloading %s-%02d for %s", year, month, region_key)
                    client.retrieve("reanalysis-era5-single-levels", request, str(out_file))
                    break
                except Exception:
                    logging.warning("Retry %d/%d failed for %s", attempt + 1, retries, out_file.name)
                    if attempt == retries - 1:
                        raise
                    time.sleep(sleep_seconds)

    logging.info("ERA5 download complete for region: %s", region_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    if args.list_regions:
        print("\n".join(list_regions()))
        raise SystemExit(0)

    download_era5(
        start_year=args.start_year,
        end_year=args.end_year,
        output_dir=args.output_dir,
        retries=args.retry,
        sleep_seconds=args.sleep_seconds,
        region=args.region,
        bbox=args.bbox,
    )
