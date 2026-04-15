import argparse
import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def run(script: str, *args: str):
    cmd = [sys.executable, script, *args]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Failed: {script}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, required=True)
    parser.add_argument("--districts_file", type=str, required=True)
    parser.add_argument("--district_id_col", type=str, default="district_id")
    parser.add_argument("--district_name_col", type=str, default="district_name")
    parser.add_argument("--district_region_col", type=str, default=None)
    parser.add_argument("--start", type=str, default="2005-01-01")
    parser.add_argument("--end", type=str, default="2026-01-01")
    parser.add_argument("--monsoon_only", action="store_true")
    return parser.parse_args()


def _build_zero_imerg_hourly(region: str) -> Path:
    era5_path = ROOT / f"data/processed/era5_district_features_{region}.csv"
    out_path = ROOT / f"data/processed/imerg_hourly_district_{region}.csv"
    if not era5_path.exists():
        raise FileNotFoundError(f"Cannot create IMERG fallback without ERA5 district features: {era5_path}")

    era5 = pd.read_csv(era5_path, parse_dates=["time"])
    required = [col for col in ["region", "district_id", "district_name", "time"] if col in era5.columns]
    if "region" not in required:
        era5["region"] = region
        required = [col for col in ["region", "district_id", "district_name", "time"] if col in era5.columns]

    fallback = era5[required].copy()
    fallback["rain_mm"] = 0.0
    fallback = fallback.sort_values(required).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fallback.to_csv(out_path, index=False)
    logging.warning("IMERG unavailable for %s. Wrote zero-rain fallback -> %s", region, out_path)
    return out_path


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)

    common = [
        "--region",
        args.region,
        "--districts_file",
        args.districts_file,
        "--district_id_col",
        args.district_id_col,
        "--district_name_col",
        args.district_name_col,
    ]
    if args.district_region_col:
        common += ["--district_region_col", args.district_region_col]

    run(
        "src/data/district/extract_era5_district_features.py",
        *common,
        "--start",
        args.start,
        "--end",
        args.end,
    )
    try:
        run("src/data/district/extract_imerg_district_halfhourly.py", *common)
        run(
            "src/data/imerg/aggregate_imerg.py",
            "--region",
            args.region,
            "--input_csv",
            f"data/processed/imerg_halfhourly_district_{args.region}.csv",
            "--output_csv",
            f"data/processed/imerg_hourly_district_{args.region}.csv",
        )
    except RuntimeError as exc:
        logging.warning("District IMERG extraction failed for %s: %s", args.region, exc)
        _build_zero_imerg_hourly(args.region)

    merge_args = [
        "--regions",
        args.region,
        "--era5_pattern",
        "data/processed/era5_district_features_{region}.csv",
        "--imerg_pattern",
        "data/processed/imerg_hourly_district_{region}.csv",
        "--output_csv",
        f"data/processed/era5_imerg_merged_district_{args.region}.csv",
    ]
    if args.monsoon_only:
        merge_args.append("--monsoon_only")
    run("src/data/imerg/merge_era5_imerg.py", *merge_args)

    run(
        "src/features/build_features.py",
        "--input_csv",
        f"data/processed/era5_imerg_merged_district_{args.region}.csv",
        "--output_csv",
        f"data/processed/era5_imerg_features_district_{args.region}.csv",
    )
    run(
        "src/labels/create_cloudburst_labels.py",
        "--input_csv",
        f"data/processed/era5_imerg_features_district_{args.region}.csv",
        "--output_csv",
        f"data/processed/labeled_cloudburst_district_{args.region}.csv",
    )

    print("District dataset pipeline completed for region:", args.region)


if __name__ == "__main__":
    main()
