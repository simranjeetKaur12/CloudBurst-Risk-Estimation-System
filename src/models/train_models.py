import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
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
    parser.add_argument("--model_dir", type=str, default="models")
    parser.add_argument("--results_csv", type=str, default="results/model_performance.csv")
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def evaluate(model, x_test, y_test, name: str, threshold: float) -> dict:
    y_prob = model.predict_proba(x_test)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)

    return {
        "model": name,
        "auc": float(roc_auc_score(y_test, y_prob)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
    }


def main():
    args = parse_args()
    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    train_df = pd.read_csv(args.train_csv)
    test_df = pd.read_csv(args.test_csv)

    x_train = train_df[FEATURES]
    y_train = train_df[TARGET]
    x_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    print("Train samples:", x_train.shape)
    print("Test samples :", x_test.shape)
    print("Positive ratio (train):", float(y_train.mean()))

    results = []

    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=50,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(x_train, y_train)
    joblib.dump(rf, model_dir / "rf_early_warning.pkl")
    results.append(evaluate(rf, x_test, y_test, "Random Forest (Early Warning)", args.threshold))

    pos = max((y_train == 1).sum(), 1)
    neg = (y_train == 0).sum()
    scale_pos_weight = max(neg / pos, 1.0)
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
    joblib.dump(xgb, model_dir / "xgb_early_warning.pkl")
    results.append(evaluate(xgb, x_test, y_test, "XGBoost (Early Warning)", args.threshold))

    # Scaling improves LR convergence on mixed-scale meteorological features.
    lr = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, class_weight="balanced", solver="lbfgs"),
    )
    lr.fit(x_train, y_train)
    joblib.dump(lr, model_dir / "lr_early_warning.pkl")
    results.append(evaluate(lr, x_test, y_test, "Logistic Regression (Early Warning)", args.threshold))

    results_df = pd.DataFrame(results)
    results_path = Path(args.results_csv)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    if results_path.exists():
        old = pd.read_csv(results_path)
        results_df = pd.concat([old, results_df], ignore_index=True)
    results_df.to_csv(results_path, index=False)

    joblib.dump(FEATURES, model_dir / "feature_list.pkl")

    print("Models trained and saved successfully.")
    print(results_df.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()
