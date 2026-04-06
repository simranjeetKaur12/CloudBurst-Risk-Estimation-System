import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

FEATURES = [
    "t2m",
    "u10",
    "v10",
    "sp",
    "tcwv",
    "wind_speed",
    "tcwv_3h",
    "tcwv_6h",
    "sp_drop_3h",
    "t2m_grad",
]
TARGET = "cloudburst"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_csv", type=str, default="data/processed/test.csv")
    parser.add_argument("--group_col", type=str, default="region")
    parser.add_argument("--model_path", type=str, default="models/xgb_early_warning.pkl")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--output_csv", type=str, default="results/validation_by_group.csv")
    return parser.parse_args()


def metrics_for_group(df: pd.DataFrame, model, threshold: float) -> dict:
    x = df[FEATURES]
    y = df[TARGET].values
    probs = model.predict_proba(x)[:, 1]
    preds = (probs >= threshold).astype(int)

    return {
        "rows": int(len(df)),
        "events": int(df[TARGET].sum()),
        "auc": float(roc_auc_score(y, probs)) if len(set(y)) > 1 else float("nan"),
        "pr_auc": float(average_precision_score(y, probs)) if len(set(y)) > 1 else float("nan"),
        "f1": float(f1_score(y, preds, zero_division=0)),
        "recall": float(recall_score(y, preds, zero_division=0)),
        "precision": float(precision_score(y, preds, zero_division=0)),
    }


def main():
    args = parse_args()
    df = pd.read_csv(args.test_csv)
    if args.group_col not in df.columns:
        raise ValueError(f"Column '{args.group_col}' missing in {args.test_csv}")
    model = joblib.load(args.model_path)

    records = []
    for group_value, group_df in df.groupby(args.group_col):
        rec = metrics_for_group(group_df, model, args.threshold)
        rec[args.group_col] = group_value
        records.append(rec)

    out = pd.DataFrame(records).sort_values(args.group_col)
    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)

    print("Saved ->", out_csv)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
