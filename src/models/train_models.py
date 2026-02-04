# src/models/train_models_early_warning.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    recall_score, precision_score, f1_score, roc_auc_score
)
from xgboost import XGBClassifier
import joblib
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

TRAIN_FILE = DATA_DIR / "train.csv"
TEST_FILE  = DATA_DIR / "test.csv"

# -----------------------------
# Load data
# -----------------------------
train_df = pd.read_csv(TRAIN_FILE)
test_df  = pd.read_csv(TEST_FILE)

# -----------------------------
# Leakage-free feature set
# -----------------------------
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

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]

print("Train samples:", X_train.shape)
print("Test samples :", X_test.shape)
print("Positive ratio (train):", y_train.mean())

# -----------------------------
# Helper function
# -----------------------------
def evaluate(model, X_test, y_test, name):
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)

    result = {
        "model": name,
        "auc": roc,
        "f1": f1,
        "recall": recall,
        "precision": precision
    }

    results_path = Path("results/model_performance.csv")
    results_path.parent.mkdir(parents=True, exist_ok=True)

    if results_path.exists():
        df = pd.read_csv(results_path)
        df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
    else:
        df = pd.DataFrame([result])

    df.to_csv(results_path, index=False)

    print(f"\n{name}")
    print("Recall   :", recall)
    print("Precision:", precision)
    print("F1       :", f1)
    print("ROC AUC  :", roc)

# -----------------------------
# Random Forest (imbalance-aware)
# -----------------------------
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=50,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)
evaluate(rf, X_test, y_test, "Random Forest (Early Warning)")

joblib.dump(rf, MODEL_DIR / "rf_early_warning.pkl")

# -----------------------------
# XGBoost (best for tabular extremes)
# -----------------------------
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

xgb = XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)

xgb.fit(X_train, y_train)
evaluate(xgb, X_test, y_test, "XGBoost (Early Warning)")

joblib.dump(xgb, MODEL_DIR / "xgb_early_warning.pkl")

# -----------------------------
# Logistic Regression (baseline)
# -----------------------------
lr = LogisticRegression(
    max_iter=500,
    class_weight="balanced",
    n_jobs=-1
)

lr.fit(X_train, y_train)
evaluate(lr, X_test, y_test, "Logistic Regression (Early Warning)")

joblib.dump(lr, MODEL_DIR / "lr_early_warning.pkl")

joblib.dump(X_train.columns.tolist(), "models/feature_list.pkl")


print("\n✅ Early-warning models trained & saved")
