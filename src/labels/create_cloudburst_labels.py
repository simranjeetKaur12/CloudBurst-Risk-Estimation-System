import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", type=str, default="data/processed/era5_imerg_features_all_regions.csv")
    parser.add_argument("--output_csv", type=str, default="data/processed/labeled_cloudburst_all_regions.csv")
    return parser.parse_args()


def label_one_region(group: pd.DataFrame) -> pd.DataFrame:
    g = group.sort_values("time").copy()

    p97_1h = g["rain_mm"].quantile(0.97)
    p97_3h = g["rain_3h"].quantile(0.97)
    p97_6h = g["rain_6h"].quantile(0.97)

    p95_peak = g["rain_peak_3h"].quantile(0.95)
    p10_sp_drop = g["sp_drop_3h"].quantile(0.10)
    p90_tcwv = g["tcwv_3h"].quantile(0.90)

    tier1 = (
        (g["rain_mm"] >= p97_1h)
        | (g["rain_3h"] >= p97_3h)
        | (g["rain_6h"] >= p97_6h)
    )

    tier2 = (
        (g["rain_peak_3h"] >= p95_peak)
        & (g["sp_drop_3h"] <= p10_sp_drop)
        & (g["tcwv_3h"] >= p90_tcwv)
    )

    g["cloudburst"] = (tier1 | tier2).astype(int)
    g["label_rule_tier1"] = tier1.astype(int)
    g["label_rule_tier2"] = tier2.astype(int)
    return g


def main():
    args = parse_args()
    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        legacy = Path("data/processed/era5_imerg_features.csv")
        if legacy.exists():
            in_csv = legacy
    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_csv, parse_dates=["time"]).sort_values(["region", "time"]).reset_index(drop=True)
    if "region" not in df.columns:
        df["region"] = "unknown"

    if "district_id" in df.columns:
        group_col = "district_id"
    elif "district_name" in df.columns:
        group_col = "district_name"
    else:
        group_col = "region"

    labeled_parts = [label_one_region(group) for _, group in df.groupby(group_col, sort=False)]
    labeled = pd.concat(labeled_parts, ignore_index=True)
    labeled.to_csv(out_csv, index=False)

    summary = labeled.groupby(group_col)["cloudburst"].agg(["count", "sum", "mean"]).rename(
        columns={"count": "rows", "sum": "cloudburst_hours", "mean": "event_ratio"}
    )
    print("Cloudburst labels created")
    print(summary)
    print("Saved ->", out_csv)


if __name__ == "__main__":
    main()
