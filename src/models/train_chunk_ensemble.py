import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from xgboost import XGBClassifier

try:
    from src.common.himalaya_chunks import list_chunks, normalize_chunks
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from src.common.himalaya_chunks import list_chunks, normalize_chunks

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
    parser.add_argument("--chunks", nargs="+", default=list_chunks())
    parser.add_argument(
        "--labeled_pattern",
        type=str,
        default="data/processed/labeled_cloudburst_district_{chunk}.csv",
    )
    parser.add_argument("--models_dir", type=str, default="models/chunks")
    parser.add_argument("--results_csv", type=str, default="results/chunk_ensemble_performance.csv")
    parser.add_argument("--latest_out_csv", type=str, default="data/processed/chunk_latest_features.csv")
    parser.add_argument("--stats_out_json", type=str, default="data/processed/chunk_feature_stats.json")
    parser.add_argument("--split_ratio", type=float, default=0.8)
    parser.add_argument("--min_rows", type=int, default=500)
    parser.add_argument("--min_positive", type=int, default=25)
    return parser.parse_args()


def split_time_per_district(df: pd.DataFrame, ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts, test_parts = [], []
    if "district_id" in df.columns:
        group_col = "district_id"
    elif "district_name" in df.columns:
        group_col = "district_name"
    elif "region" in df.columns:
        group_col = "region"
    else:
        group_col = "__single_group__"
        df = df.copy()
        df[group_col] = "all"
    for _, group in df.groupby(group_col):
        g = group.sort_values("time")
        idx = int(len(g) * ratio)
        train_parts.append(g.iloc[:idx])
        test_parts.append(g.iloc[idx:])
    train = pd.concat(train_parts, ignore_index=True)
    test = pd.concat(test_parts, ignore_index=True)
    return train, test


def evaluate(y_true: np.ndarray, probs: np.ndarray, threshold: float = 0.5) -> dict:
    preds = (probs >= threshold).astype(int)
    return {
        "auc": float(roc_auc_score(y_true, probs)),
        "f1": float(f1_score(y_true, preds, zero_division=0)),
        "recall": float(recall_score(y_true, preds, zero_division=0)),
        "precision": float(precision_score(y_true, preds, zero_division=0)),
    }


def _risk_level(p: float) -> str:
    if p >= 0.75:
        return "RED"
    if p >= 0.50:
        return "ORANGE"
    if p >= 0.30:
        return "YELLOW"
    return "LOW"


def main():
    args = parse_args()
    chunks = normalize_chunks(args.chunks)

    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    perf_records = []
    latest_rows = []
    stats_payload = {}

    for chunk in chunks:
        csv_path = Path(args.labeled_pattern.format(chunk=chunk))
        if not csv_path.exists():
            print(f"Skipping {chunk}: missing {csv_path}")
            continue

        df = pd.read_csv(csv_path, parse_dates=["time"]).sort_values("time")
        if len(df) < args.min_rows:
            print(f"Skipping {chunk}: only {len(df)} rows")
            continue

        train_df, test_df = split_time_per_district(df, args.split_ratio)
        if int(train_df[TARGET].sum()) < args.min_positive:
            print(f"Skipping {chunk}: train positives={int(train_df[TARGET].sum())}")
            continue

        x_train, y_train = train_df[FEATURES], train_df[TARGET]
        x_test, y_test = test_df[FEATURES], test_df[TARGET]

        rf = RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=50,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        rf.fit(x_train, y_train)
        rf_prob = rf.predict_proba(x_test)[:, 1]

        scale_pos_weight = max((y_train == 0).sum() / max((y_train == 1).sum(), 1), 1.0)
        xgb = XGBClassifier(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        )
        xgb.fit(x_train, y_train)
        xgb_prob = xgb.predict_proba(x_test)[:, 1]

        ensemble_prob = 0.5 * rf_prob + 0.5 * xgb_prob

        chunk_dir = models_dir / chunk
        chunk_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(rf, chunk_dir / "rf_early_warning.pkl")
        joblib.dump(xgb, chunk_dir / "xgb_early_warning.pkl")
        joblib.dump(FEATURES, chunk_dir / "feature_list.pkl")
        # Requested deployment artifact names.
        joblib.dump(
            {
                "chunk": chunk,
                "rf_model": rf,
                "xgb_model": xgb,
                "ensemble_weights": {"rf": 0.5, "xgb": 0.5},
                "features": FEATURES,
            },
            Path("models") / f"{chunk}_model.pkl",
        )

        meta = {
            "chunk": chunk,
            "ensemble_weights": {"rf": 0.5, "xgb": 0.5},
            "features": FEATURES,
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
        }
        (chunk_dir / "ensemble_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        rf_metrics = evaluate(y_test.to_numpy(), rf_prob)
        rf_metrics.update({"chunk": chunk, "model": "rf"})
        perf_records.append(rf_metrics)
        xgb_metrics = evaluate(y_test.to_numpy(), xgb_prob)
        xgb_metrics.update({"chunk": chunk, "model": "xgb"})
        perf_records.append(xgb_metrics)
        ens_metrics = evaluate(y_test.to_numpy(), ensemble_prob)
        ens_metrics.update({"chunk": chunk, "model": "ensemble"})
        perf_records.append(ens_metrics)

        # Latest district rows for location inference.
        if "district_id" in df.columns:
            latest_group_col = "district_id"
        elif "district_name" in df.columns:
            latest_group_col = "district_name"
        elif "region" in df.columns:
            latest_group_col = "region"
        else:
            latest_group_col = "__single_group__"
            df = df.copy()
            df[latest_group_col] = "all"

        latest = df.sort_values("time").groupby(latest_group_col, as_index=False).tail(1).copy()
        if "district_id" not in latest.columns:
            latest["district_id"] = latest_group_col + ":" + latest[latest_group_col].astype(str)
        if "district_name" not in latest.columns:
            latest["district_name"] = latest[latest_group_col].astype(str)
        latest["chunk"] = chunk
        rf_latest = rf.predict_proba(latest[FEATURES])[:, 1]
        xgb_latest = xgb.predict_proba(latest[FEATURES])[:, 1]
        ens_latest = 0.5 * rf_latest + 0.5 * xgb_latest
        latest["rf_probability"] = rf_latest
        latest["xgb_probability"] = xgb_latest
        latest["ensemble_probability"] = ens_latest
        latest["risk_level"] = latest["ensemble_probability"].apply(_risk_level)
        latest_rows.append(latest)

        stats_payload[chunk] = {
            feature: {
                "p10": float(df[feature].quantile(0.10)),
                "p50": float(df[feature].quantile(0.50)),
                "p90": float(df[feature].quantile(0.90)),
            }
            for feature in FEATURES
        }

        print(f"Trained chunk={chunk} | train={len(train_df)} test={len(test_df)}")

    perf_df = pd.DataFrame(perf_records)
    results_csv = Path(args.results_csv)
    results_csv.parent.mkdir(parents=True, exist_ok=True)
    perf_df.to_csv(results_csv, index=False)

    if latest_rows:
        latest_df = pd.concat(latest_rows, ignore_index=True)
        latest_out = Path(args.latest_out_csv)
        latest_out.parent.mkdir(parents=True, exist_ok=True)
        latest_df.to_csv(latest_out, index=False)

    stats_out = Path(args.stats_out_json)
    stats_out.parent.mkdir(parents=True, exist_ok=True)
    stats_out.write_text(json.dumps(stats_payload, indent=2), encoding="utf-8")

    print("Saved performance ->", results_csv)
    print("Saved latest features ->", args.latest_out_csv)
    print("Saved feature stats ->", args.stats_out_json)


if __name__ == "__main__":
    main()
