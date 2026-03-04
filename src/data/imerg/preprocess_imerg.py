import argparse
import glob
import logging
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

try:
    from src.common.regions import list_regions, resolve_bbox
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.common.regions import list_regions, resolve_bbox

GROUP = "Grid"
RAIN_VAR = "precipitation"
FILL_VALUE = -9999.9


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", type=str, default="data/raw/imerg")
    parser.add_argument("--region", type=str, default="himalayan_west")
    parser.add_argument(
        "--bbox",
        type=str,
        default=None,
        help="Custom bbox in 'north,west,south,east'. Overrides --region preset.",
    )
    parser.add_argument("--output_csv", type=str, default=None)
    parser.add_argument("--processed_csv", type=str, default=None)
    parser.add_argument("--delete_raw", action="store_true")
    parser.add_argument("--list_regions", action="store_true")
    return parser.parse_args()


def preprocess_imerg(args):
    region_key, bbox = resolve_bbox(region=args.region, bbox=args.bbox)
    north, west, south, east = bbox

    raw_dir = Path(args.raw_dir) / region_key
    legacy_raw_dir = Path(args.raw_dir)
    if not raw_dir.exists() and legacy_raw_dir.exists():
        raw_dir = legacy_raw_dir
    out_csv = (
        Path(args.output_csv)
        if args.output_csv
        else Path(f"data/processed/imerg_halfhourly_{region_key}.csv")
    )
    if args.processed_csv:
        processed_csv = Path(args.processed_csv)
    else:
        candidate = Path(f"data/processed/imerg_processed_days_{region_key}.csv")
        legacy_candidate = Path("data/processed/imerg_processed_days.csv")
        processed_csv = legacy_candidate if region_key == "uttarakhand" and legacy_candidate.exists() else candidate

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    processed_csv.parent.mkdir(parents=True, exist_ok=True)

    processed_days = set()
    if processed_csv.exists():
        df = pd.read_csv(processed_csv, parse_dates=["date"])
        processed_days = set(df["date"].dt.date)

    logging.info("Region: %s | Area: %s", region_key, bbox)
    logging.info("Loaded %d processed days", len(processed_days))

    if not out_csv.exists():
        pd.DataFrame(columns=["time", "region", "rain_mm_hr"]).to_csv(out_csv, index=False)

    files = sorted(glob.glob(str(raw_dir / "**/*.HDF5"), recursive=True))
    new_days = set()

    for file_path in files:
        try:
            name = Path(file_path).name
            date_part = name.split("3IMERG.")[1][:8]
            time_part = name.split("-S")[1][:6]
            timestamp = datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
            day = timestamp.date()

            if day in processed_days:
                continue

            with xr.open_dataset(file_path, group=GROUP, decode_times=False, mask_and_scale=True) as ds:
                rain = ds[RAIN_VAR].where(ds[RAIN_VAR] != FILL_VALUE)
                rain = rain.sel(lat=slice(south, north), lon=slice(west, east))
                rain_mean = float(rain.mean(skipna=True).values)

            if np.isnan(rain_mean):
                continue

            pd.DataFrame(
                [{"time": timestamp, "region": region_key, "rain_mm_hr": rain_mean}]
            ).to_csv(out_csv, mode="a", header=False, index=False)

            new_days.add(day)

            if args.delete_raw:
                os.remove(file_path)

        except Exception as exc:
            logging.error("Failed: %s | %s", file_path, exc)

    if new_days:
        pd.DataFrame([{"date": d} for d in sorted(new_days)]).to_csv(
            processed_csv,
            mode="a",
            header=not processed_csv.exists(),
            index=False,
        )

    logging.info("New days processed: %d", len(new_days))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.list_regions:
        print("\n".join(list_regions()))
        raise SystemExit(0)
    preprocess_imerg(args)
