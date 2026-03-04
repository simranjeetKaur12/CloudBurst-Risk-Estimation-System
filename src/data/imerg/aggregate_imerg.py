import argparse
import logging
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default="himalayan_west")
    parser.add_argument("--input_csv", type=str, default=None)
    parser.add_argument("--output_csv", type=str, default=None)
    return parser.parse_args()


def aggregate(args):
    in_csv = Path(args.input_csv) if args.input_csv else Path(f"data/processed/imerg_halfhourly_{args.region}.csv")
    out_csv = Path(args.output_csv) if args.output_csv else Path(f"data/processed/imerg_hourly_{args.region}.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    logging.info("Aggregating IMERG to hourly for region: %s", args.region)

    df = pd.read_csv(in_csv)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    if "region" not in df.columns:
        df["region"] = args.region
    df = df.dropna(subset=["time", "rain_mm_hr"])

    df["rain_mm"] = df["rain_mm_hr"] * 0.5
    df["time"] = df["time"].dt.floor("h")

    group_keys = ["region"]
    for col in ["district_id", "district_name"]:
        if col in df.columns:
            group_keys.append(col)
    group_keys.append("time")

    hourly = df.groupby(group_keys, as_index=False)["rain_mm"].sum().sort_values(group_keys)
    hourly.to_csv(out_csv, index=False)

    logging.info("Saved -> %s", out_csv)
    logging.info("Rows: %d", len(hourly))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    aggregate(args)
