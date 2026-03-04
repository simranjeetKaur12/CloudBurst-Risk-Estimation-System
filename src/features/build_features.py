import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", type=str, default="data/processed/era5_imerg_merged_all_regions.csv")
    parser.add_argument("--output_csv", type=str, default="data/processed/era5_imerg_features_all_regions.csv")
    return parser.parse_args()


def add_features(group: pd.DataFrame) -> pd.DataFrame:
    g = group.sort_values("time").copy()

    g["rain_3h"] = g["rain_mm"].rolling(window=3).sum()
    g["rain_6h"] = g["rain_mm"].rolling(window=6).sum()
    g["rain_peak_3h"] = g["rain_mm"].rolling(window=3).max()
    g["rain_lag1"] = g["rain_mm"].shift(1)
    g["rain_lag2"] = g["rain_mm"].shift(2)

    g["wind_speed"] = (g["u10"] ** 2 + g["v10"] ** 2) ** 0.5

    g["tcwv_3h"] = g["tcwv"].rolling(window=3).mean()
    g["tcwv_6h"] = g["tcwv"].rolling(window=6).mean()

    g["sp_drop_3h"] = g["sp"] - g["sp"].shift(3)
    g["t2m_grad"] = g["t2m"] - g["t2m"].shift(1)
    g["temp_c"] = g["t2m"] - 273.15
    g["pressure_hpa"] = g["sp"] / 100.0

    return g


def main():
    args = parse_args()
    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        legacy = Path("data/processed/era5_imerg_merged.csv")
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

    featured_parts = [add_features(group) for _, group in df.groupby(group_col, sort=False)]
    featured = pd.concat(featured_parts, ignore_index=True)
    featured = featured.dropna().reset_index(drop=True)
    featured.to_csv(out_csv, index=False)

    print("Feature engineering complete")
    print("Rows:", len(featured))
    print("Saved ->", out_csv)


if __name__ == "__main__":
    main()
