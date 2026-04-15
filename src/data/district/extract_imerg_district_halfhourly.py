import argparse
import glob
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

try:
    from src.data.district.spatial_utils import build_cell_index_map, load_districts
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.data.district.spatial_utils import build_cell_index_map, load_districts

GROUP = "Grid"
RAIN_VAR = "precipitation"
FILL_VALUE = -9999.9


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--raw_dir", type=str, default="data/raw/imerg")
    parser.add_argument("--districts_file", type=str, required=True)
    parser.add_argument("--district_id_col", type=str, default="district_id")
    parser.add_argument("--district_name_col", type=str, default="district_name")
    parser.add_argument("--district_region_col", type=str, default=None)
    parser.add_argument("--output_csv", type=str, default=None)
    return parser.parse_args()


def _timestamp_from_name(file_name: str) -> datetime:
    date_part = file_name.split("3IMERG.")[1][:8]
    time_part = file_name.split("-S")[1][:6]
    return datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")


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

    raw_root = Path(args.raw_dir) / args.region
    legacy_raw_root = Path(args.raw_dir)
    if not raw_root.exists() and legacy_raw_root.exists():
        raw_root = legacy_raw_root
    files = sorted(glob.glob(str(raw_root / "**/*.HDF5"), recursive=True))
    if not files:
        raise FileNotFoundError(f"No IMERG HDF5 files found under {raw_root}")

    cell_map = None
    grid_signature = None
    rows = []

    for file_path in files:
        file_name = Path(file_path).name
        timestamp = _timestamp_from_name(file_name)

        with xr.open_dataset(file_path, group=GROUP, decode_times=False, mask_and_scale=True) as ds:
            if RAIN_VAR not in ds:
                continue
            rain = ds[RAIN_VAR]
            rain = rain.where(rain != FILL_VALUE)

            lat_values = ds["lat"].values
            lon_values = ds["lon"].values

            signature = (len(lat_values), len(lon_values), float(lat_values.min()), float(lon_values.min()))
            if cell_map is None or signature != grid_signature:
                cell_map = build_cell_index_map(lat_values, lon_values, districts)
                grid_signature = signature

            rain_arr = np.asarray(rain.values)
            if rain_arr.ndim == 3:
                rain_arr = rain_arr[0]

            for district_id, idx_info in cell_map.items():
                values = rain_arr[idx_info["lat_idx"], idx_info["lon_idx"]]
                rain_mean = float(np.nanmean(values))
                if np.isnan(rain_mean):
                    continue

                rows.append(
                    {
                        "region": args.region,
                        "district_id": district_id,
                        "district_name": idx_info["district_name"],
                        "time": timestamp,
                        "rain_mm_hr": rain_mean,
                    }
                )

    out = pd.DataFrame(rows).sort_values(["region", "district_id", "time"]).reset_index(drop=True)
    out_csv = (
        Path(args.output_csv)
        if args.output_csv
        else Path(f"data/processed/imerg_halfhourly_district_{args.region}.csv")
    )
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)

    logging.info("Saved -> %s", out_csv)
    logging.info("Rows: %d", len(out))


if __name__ == "__main__":
    main()
