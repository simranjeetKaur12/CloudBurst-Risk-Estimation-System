import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from xgboost import XGBClassifier

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
    parser.add_argument("--train_csv", type=str, default="data/processed/train.csv")
    parser.add_argument("--test_csv", type=str, default="data/processed/test.csv")
    parser.add_argument("--group_col", type=str, default="region")
    parser.add_argument("--min_positive", type=int, default=25)
    parser.add_argument("--models_dir", type=str, default="models/by_group")
    parser.add_argument("--results_csv", type=str, default="results/model_performance_by_group.csv")
    return parser.parse_args()


def evaluate(model, x_test, y_test):
    y_prob = model.predict_proba(x_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)
    return {
        "auc": float(roc_auc_score(y_test, y_prob)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
    }


def train_for_group(group_value, train_df, test_df, models_dir: Path):
    x_train = train_df[FEATURES]
    y_train = train_df[TARGET]
    x_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    group_dir = models_dir / str(group_value)
    group_dir.mkdir(parents=True, exist_ok=True)

    records = []

    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=50,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(x_train, y_train)
    joblib.dump(rf, group_dir / "rf_early_warning.pkl")
    rec = evaluate(rf, x_test, y_test)
    rec.update({"group": group_value, "model": "rf"})
    records.append(rec)

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
    joblib.dump(xgb, group_dir / "xgb_early_warning.pkl")
    rec = evaluate(xgb, x_test, y_test)
    rec.update({"group": group_value, "model": "xgb"})
    records.append(rec)

    lr = LogisticRegression(max_iter=500, class_weight="balanced", n_jobs=-1)
    lr.fit(x_train, y_train)
    joblib.dump(lr, group_dir / "lr_early_warning.pkl")
    rec = evaluate(lr, x_test, y_test)
    rec.update({"group": group_value, "model": "lr"})
    records.append(rec)

    joblib.dump(FEATURES, group_dir / "feature_list.pkl")
    return records


def main():
    args = parse_args()
    train_df = pd.read_csv(args.train_csv)
    test_df = pd.read_csv(args.test_csv)

    if args.group_col not in train_df.columns:
        raise ValueError(f"Column '{args.group_col}' missing in train data")
    if args.group_col not in test_df.columns:
        raise ValueError(f"Column '{args.group_col}' missing in test data")

    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    all_records = []
    common_groups = sorted(set(train_df[args.group_col].astype(str)) & set(test_df[args.group_col].astype(str)))

    for group in common_groups:
        g_train = train_df[train_df[args.group_col].astype(str) == group].copy()
        g_test = test_df[test_df[args.group_col].astype(str) == group].copy()
        positives = int(g_train[TARGET].sum())
        if positives < args.min_positive:
            print(f"Skipping group={group}; train positives={positives} (< {args.min_positive})")
            continue
        print(f"Training group={group} | train={len(g_train)} test={len(g_test)} positives={positives}")
        all_records.extend(train_for_group(group, g_train, g_test, models_dir))

    results = pd.DataFrame(all_records)
    results_path = Path(args.results_csv)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, index=False)
    print("Saved group model metrics ->", results_path)


if __name__ == "__main__":
    main()
