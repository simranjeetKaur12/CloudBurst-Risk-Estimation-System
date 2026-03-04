import argparse
from pathlib import Path

import pandas as pd

try:
    from src.common.regions import list_regions, normalize_region_list
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[3]))
    from src.common.regions import list_regions, normalize_region_list

MONSOON_MONTHS = [6, 7, 8, 9]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regions", nargs="+", default=["himalayan_west"])
    parser.add_argument("--era5_pattern", type=str, default="data/processed/era5_features_{region}.csv")
    parser.add_argument("--imerg_pattern", type=str, default="data/processed/imerg_hourly_{region}.csv")
    parser.add_argument("--output_csv", type=str, default="data/processed/era5_imerg_merged_all_regions.csv")
    parser.add_argument("--monsoon_only", action="store_true")
    parser.add_argument("--list_regions", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list_regions:
        print("\n".join(list_regions()))
        return

    regions = normalize_region_list(args.regions)
    frames = []

    for region in regions:
        era5_csv = Path(args.era5_pattern.format(region=region))
        imerg_csv = Path(args.imerg_pattern.format(region=region))

        if region == "uttarakhand":
            if not era5_csv.exists() and Path("data/processed/era5_features_uttarakhand.csv").exists():
                era5_csv = Path("data/processed/era5_features_uttarakhand.csv")
            if not imerg_csv.exists() and Path("data/processed/imerg_hourly_uttarakhand.csv").exists():
                imerg_csv = Path("data/processed/imerg_hourly_uttarakhand.csv")

        if not era5_csv.exists():
            raise FileNotFoundError(f"Missing ERA5 file for {region}: {era5_csv}")
        if not imerg_csv.exists():
            raise FileNotFoundError(f"Missing IMERG file for {region}: {imerg_csv}")

        era5 = pd.read_csv(era5_csv, parse_dates=["time"])
        imerg = pd.read_csv(imerg_csv, parse_dates=["time"])

        if "region" not in era5.columns:
            era5["region"] = region
        if "region" not in imerg.columns:
            imerg["region"] = region

        if args.monsoon_only:
            era5 = era5[era5["time"].dt.month.isin(MONSOON_MONTHS)]
            imerg = imerg[imerg["time"].dt.month.isin(MONSOON_MONTHS)]

        join_keys = ["region", "time"]
        if "district_id" in era5.columns and "district_id" in imerg.columns:
            join_keys.append("district_id")
        if "district_name" in era5.columns and "district_name" in imerg.columns:
            join_keys.append("district_name")

        merged = pd.merge(era5, imerg, on=join_keys, how="inner").sort_values(join_keys)
        frames.append(merged)

    sort_cols = ["region"]
    if any("district_id" in frame.columns for frame in frames):
        sort_cols.append("district_id")
    sort_cols.append("time")
    output = pd.concat(frames, ignore_index=True).sort_values(sort_cols).reset_index(drop=True)
    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(out_csv, index=False)

    print("Merge complete")
    print("Regions:", regions)
    print("Rows:", len(output))
    print("Saved ->", out_csv)


if __name__ == "__main__":
    main()
