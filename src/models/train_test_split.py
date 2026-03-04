import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", type=str, default="data/processed/labeled_cloudburst_all_regions.csv")
    parser.add_argument("--train_csv", type=str, default="data/processed/train.csv")
    parser.add_argument("--test_csv", type=str, default="data/processed/test.csv")
    parser.add_argument("--train_ratio", type=float, default=0.8)
    return parser.parse_args()


def split_group(group: pd.DataFrame, train_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    g = group.sort_values("time")
    split_idx = int(len(g) * train_ratio)
    return g.iloc[:split_idx], g.iloc[split_idx:]


def main():
    args = parse_args()
    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        legacy = Path("data/processed/labeled_cloudburst.csv")
        if legacy.exists():
            in_csv = legacy
    train_csv = Path(args.train_csv)
    test_csv = Path(args.test_csv)
    train_csv.parent.mkdir(parents=True, exist_ok=True)
    test_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_csv, parse_dates=["time"])
    if "region" not in df.columns:
        df["region"] = "unknown"
    if "district_id" in df.columns:
        group_col = "district_id"
    elif "district_name" in df.columns:
        group_col = "district_name"
    else:
        group_col = "region"

    train_parts = []
    test_parts = []
    for _, group in df.groupby(group_col):
        train_g, test_g = split_group(group, args.train_ratio)
        train_parts.append(train_g)
        test_parts.append(test_g)

    sort_cols = ["region", "time"]
    if group_col != "region":
        sort_cols = [group_col, "time"]
    train = pd.concat(train_parts, ignore_index=True).sort_values(sort_cols)
    test = pd.concat(test_parts, ignore_index=True).sort_values(sort_cols)

    train.to_csv(train_csv, index=False)
    test.to_csv(test_csv, index=False)

    print("Time-based split complete")
    print("Train size:", len(train))
    print("Test size:", len(test))
    print("Train events:", int(train["cloudburst"].sum()))
    print("Test events:", int(test["cloudburst"].sum()))


if __name__ == "__main__":
    main()
