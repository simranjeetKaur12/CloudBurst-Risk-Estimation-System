import argparse
import glob
import logging
import os
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", type=str, default="data/raw/era5")
    parser.add_argument("--region", type=str, default="himalayan_west")
    parser.add_argument(
        "--bbox",
        type=str,
        default=None,
        help="Custom bbox in 'north,west,south,east'. Overrides --region preset.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="If omitted, uses data/processed/era5_features_<region>.csv",
    )
    parser.add_argument("--start", type=str, default="2005-01-01")
    parser.add_argument("--end", type=str, default="2025-01-01")
    parser.add_argument("--list_regions", action="store_true")
    return parser.parse_args()


def normalize_coords(ds):
    if "latitude" not in ds.coords and "lat" in ds.coords:
        ds = ds.rename({"lat": "latitude"})
    if "longitude" not in ds.coords and "lon" in ds.coords:
        ds = ds.rename({"lon": "longitude"})
    if "valid_time" in ds.coords:
        ds = ds.rename({"valid_time": "time"})
    return ds


def process_single_file(nc_file, start_time, end_time, north, west, south, east, agg="mean"):
    ds = xr.open_dataset(nc_file)
    ds = normalize_coords(ds)

    ds = ds.sel(latitude=slice(north, south), longitude=slice(west, east))

    time_index = pd.to_datetime(ds.time.values).floor("h")
    mask = (time_index >= start_time) & (time_index < end_time)
    if not mask.any():
        return None

    ds = ds.isel(time=mask)
    time_index = time_index[mask]

    data = {}
    vars_to_use = ["t2m", "u10", "v10", "sp", "tcwv"] if agg == "mean" else ["tp"]

    for var in vars_to_use:
        if var not in ds:
            continue
        da = ds[var]
        da = da.mean(["latitude", "longitude"]) if agg == "mean" else da.sum(["latitude", "longitude"])
        values = da.values
        if values.ndim == 0:
            values = np.repeat(values, len(time_index))
        data[var] = values

    if not data:
        return None
    return pd.DataFrame(data, index=time_index)


def process_directory(path, start_time, end_time, north, west, south, east, agg):
    files = sorted(glob.glob(os.path.join(path, "*.nc")))
    dfs = []
    for file_path in files:
        df = process_single_file(file_path, start_time, end_time, north, west, south, east, agg)
        if df is not None:
            dfs.append(df)
    if not dfs:
        return None
    return pd.concat(dfs).sort_index()


def main():
    args = parse_args()
    if args.list_regions:
        print("\n".join(list_regions()))
        return

    logging.basicConfig(level=logging.INFO)

    region_key, bbox = resolve_bbox(region=args.region, bbox=args.bbox)
    north, west, south, east = bbox

    start_time = pd.Timestamp(args.start)
    end_time = pd.Timestamp(args.end)

    output_path = Path(args.output) if args.output else Path(f"data/processed/era5_features_{region_key}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    base_dir = Path(args.raw_dir) / region_key
    instant_dir = base_dir / "instant"
    accum_dir = base_dir / "accum"
    flat_dir = base_dir

    # Backward compatibility for older layout:
    # data/raw/era5/{instant,accum} (without per-region folder)
    legacy_base = Path(args.raw_dir)
    if not instant_dir.exists() and (legacy_base / "instant").exists():
        instant_dir = legacy_base / "instant"
    if not accum_dir.exists() and (legacy_base / "accum").exists():
        accum_dir = legacy_base / "accum"

    logging.info("Region: %s | Area: %s", region_key, bbox)
    if instant_dir.exists() and accum_dir.exists():
        logging.info("Processing ERA5 instant directory: %s", instant_dir)
        df_instant = process_directory(str(instant_dir), start_time, end_time, north, west, south, east, "mean")

        logging.info("Processing ERA5 accum directory: %s", accum_dir)
        df_accum = process_directory(str(accum_dir), start_time, end_time, north, west, south, east, "sum")
    else:
        logging.info("Processing ERA5 flat directory: %s", flat_dir)
        df_instant = process_directory(str(flat_dir), start_time, end_time, north, west, south, east, "mean")
        df_accum = process_directory(str(flat_dir), start_time, end_time, north, west, south, east, "sum")

    if df_instant is not None and df_accum is not None:
        df = df_instant.join(df_accum, how="inner")
    else:
        df = df_instant if df_instant is not None else df_accum

    if df is None or df.empty:
        raise RuntimeError(
            f"No ERA5 data found for region '{region_key}' in {base_dir} "
            f"(or legacy path {legacy_base})."
        )

    df = df[~df.index.duplicated()].sort_index()
    df["region"] = region_key
    df = df.reset_index().rename(columns={"index": "time"})
    df.to_csv(output_path, index=False)

    logging.info("Saved -> %s", output_path)
    logging.info("Rows: %d", len(df))


if __name__ == "__main__":
    main()
