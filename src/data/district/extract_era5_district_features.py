import argparse
import glob
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

try:
    from src.data.district.spatial_utils import (
        build_cell_index_map,
        district_bbox_nwse,
        load_districts,
    )
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.data.district.spatial_utils import (
        build_cell_index_map,
        district_bbox_nwse,
        load_districts,
    )

INSTANT_VARS = ["t2m", "u10", "v10", "sp", "tcwv"]
ACCUM_VARS = ["tp"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--raw_dir", type=str, default="data/raw/era5")
    parser.add_argument("--districts_file", type=str, required=True)
    parser.add_argument("--district_id_col", type=str, default="district_id")
    parser.add_argument("--district_name_col", type=str, default="district_name")
    parser.add_argument("--district_region_col", type=str, default=None)
    parser.add_argument("--start", type=str, default="2005-01-01")
    parser.add_argument("--end", type=str, default="2026-01-01")
    parser.add_argument("--output_csv", type=str, default=None)
    return parser.parse_args()


def _normalize_coords(ds: xr.Dataset) -> xr.Dataset:
    if "latitude" not in ds.coords and "lat" in ds.coords:
        ds = ds.rename({"lat": "latitude"})
    if "longitude" not in ds.coords and "lon" in ds.coords:
        ds = ds.rename({"lon": "longitude"})
    if "valid_time" in ds.coords:
        ds = ds.rename({"valid_time": "time"})
    return ds


def _extract_from_files(
    files: list[str],
    variables: list[str],
    mode: str,
    start_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    districts,
    region: str,
) -> pd.DataFrame:
    rows = []
    cell_map = None
    grid_signature = None
    north, west, south, east = district_bbox_nwse(districts)

    for file_path in files:
        ds = xr.open_dataset(file_path)
        ds = _normalize_coords(ds)
        ds = ds.sel(latitude=slice(north, south), longitude=slice(west, east))
        if "time" not in ds.coords:
            continue

        times = pd.to_datetime(ds.time.values).floor("h")
        mask = (times >= start_ts) & (times < end_ts)
        if not mask.any():
            continue

        ds = ds.isel(time=mask)
        times = times[mask]

        lat_values = ds["latitude"].values
        lon_values = ds["longitude"].values
        signature = (len(lat_values), len(lon_values), float(lat_values.min()), float(lon_values.min()))
        if cell_map is None or signature != grid_signature:
            cell_map = build_cell_index_map(lat_values, lon_values, districts)
            grid_signature = signature

        valid_vars = [v for v in variables if v in ds.data_vars]
        if not valid_vars:
            continue

        for time_i, timestamp in enumerate(times):
            for district_id, idx_info in cell_map.items():
                record = {
                    "region": region,
                    "district_id": district_id,
                    "district_name": idx_info["district_name"],
                    "time": timestamp,
                }
                lat_idx = idx_info["lat_idx"]
                lon_idx = idx_info["lon_idx"]

                for var in valid_vars:
                    arr = np.asarray(ds[var].isel(time=time_i).values)
                    values = arr[lat_idx, lon_idx]
                    if mode == "sum":
                        record[var] = float(np.nansum(values))
                    else:
                        record[var] = float(np.nanmean(values))

                rows.append(record)

    return pd.DataFrame(rows)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)

    districts = load_districts(
        districts_file=args.districts_file,
        district_id_col=args.district_id_col,
        district_name_col=args.district_name_col,
        region_col=args.district_region_col,
        region_value=args.region,
    )

    base = Path(args.raw_dir) / args.region
    instant_files = sorted(glob.glob(str(base / "instant" / "*.nc")))
    accum_files = sorted(glob.glob(str(base / "accum" / "*.nc")))

    start_ts = pd.Timestamp(args.start)
    end_ts = pd.Timestamp(args.end)

    logging.info("Extracting ERA5 district features for region=%s", args.region)
    df_instant = _extract_from_files(
        files=instant_files,
        variables=INSTANT_VARS,
        mode="mean",
        start_ts=start_ts,
        end_ts=end_ts,
        districts=districts,
        region=args.region,
    )
    df_accum = _extract_from_files(
        files=accum_files,
        variables=ACCUM_VARS,
        mode="sum",
        start_ts=start_ts,
        end_ts=end_ts,
        districts=districts,
        region=args.region,
    )

    if df_instant.empty and df_accum.empty:
        raise RuntimeError("No district-level ERA5 records extracted.")

    merge_keys = ["region", "district_id", "district_name", "time"]
    if df_instant.empty:
        output = df_accum
    elif df_accum.empty:
        output = df_instant
    else:
        output = pd.merge(df_instant, df_accum, on=merge_keys, how="inner")

    output = output.sort_values(["region", "district_id", "time"]).reset_index(drop=True)

    out_csv = (
        Path(args.output_csv)
        if args.output_csv
        else Path(f"data/processed/era5_district_features_{args.region}.csv")
    )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(out_csv, index=False)

    logging.info("Saved -> %s", out_csv)
    logging.info("Rows: %d", len(output))


if __name__ == "__main__":
    main()
