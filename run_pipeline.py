"""
Cloudburst Risk Estimation Pipeline (Multi-Region)
==================================================

Runs the full workflow for one or more regions:
1. ERA5 download/extract/preprocess
2. IMERG download/preprocess/aggregate
3. ERA5-IMERG merge
4. Feature engineering
5. Labeling
6. Train/test split
7. Model training
8. Risk evaluation and lead-time analysis
9. Alert-signal generation for app notifications/explanations
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script_path: str, *args: str):
    cmd = [sys.executable, script_path, *args]
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Failed at {script_path}")
    print(f"Completed: {script_path}")


def _first_existing(*paths: Path) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_year", type=int, required=True)
    parser.add_argument("--end_year", type=int, required=True)
    parser.add_argument("--regions", nargs="+", default=["himalayan_west"])
    parser.add_argument("--skip_download", action="store_true")
    parser.add_argument("--monsoon_only", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    print("Pipeline start")
    print("Regions:", args.regions)
    print("Years:", args.start_year, "to", args.end_year)

    for region in args.regions:
        era5_feature_path = _first_existing(
            ROOT / f"data/processed/era5_features_{region}.csv",
            ROOT / "data/processed/era5_features_uttarakhand.csv" if region == "uttarakhand" else ROOT / "__missing__",
        )
        imerg_hourly_path = _first_existing(
            ROOT / f"data/processed/imerg_hourly_{region}.csv",
            ROOT / "data/processed/imerg_hourly_uttarakhand.csv" if region == "uttarakhand" else ROOT / "__missing__",
        )

        if not args.skip_download:
            run(
                "src/data/era5/download_era5.py",
                "--start_year",
                str(args.start_year),
                "--end_year",
                str(args.end_year),
                "--region",
                region,
            )
            run("src/data/imerg/download_imerg.py", "--start_year", str(args.start_year), "--end_year", str(args.end_year), "--region", region)

        era5_raw_dir = ROOT / f"data/raw/era5/{region}"
        era5_legacy_raw_dir = ROOT / "data/raw/era5"
        has_era5_raw = any(era5_raw_dir.rglob("*.nc")) or any(era5_legacy_raw_dir.rglob("*.nc"))
        if has_era5_raw:
            run("src/data/era5/unzip_era5.py", "--region", region)
            run("src/data/era5/preprocess_era5.py", "--region", region)
        elif era5_feature_path is not None:
            print(f"Skipping ERA5 preprocess for {region}; using existing {era5_feature_path}")
        else:
            raise RuntimeError(f"No ERA5 raw files or processed features found for region '{region}'")

        imerg_raw_dir = ROOT / f"data/raw/imerg/{region}"
        imerg_legacy_raw_dir = ROOT / "data/raw/imerg"
        has_imerg_raw = any(imerg_raw_dir.rglob("*.HDF5")) or any(imerg_legacy_raw_dir.rglob("*.HDF5"))
        if has_imerg_raw:
            run("src/data/imerg/preprocess_imerg.py", "--region", region)
            run("src/data/imerg/aggregate_imerg.py", "--region", region)
        elif imerg_hourly_path is not None:
            print(f"Skipping IMERG preprocess for {region}; using existing {imerg_hourly_path}")
        else:
            raise RuntimeError(f"No IMERG raw files or processed hourly data found for region '{region}'")

    merge_args = ["--regions", *args.regions]
    if args.monsoon_only:
        merge_args.append("--monsoon_only")
    run("src/data/imerg/merge_era5_imerg.py", *merge_args)

    run("src/features/build_features.py")
    run("src/labels/create_cloudburst_labels.py")
    run("src/models/train_test_split.py")
    run("src/models/train_models.py")
    run("src/models/risk_tier_evaluation.py")
    if len(args.regions) == 1:
        run("src/models/lead_time_analysis.py", "--group_value", args.regions[0])
    else:
        print("Skipping lead_time_analysis for multi-region run. Run it later per region using --group_value.")
    run("src/features/generate_alert_signals.py")

    print("Pipeline completed successfully")


if __name__ == "__main__":
    main()
