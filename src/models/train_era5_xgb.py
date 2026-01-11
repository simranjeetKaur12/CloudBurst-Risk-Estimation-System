import os
import joblib
import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "era5_labeled_uttarakhand.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models", "era5")
os.makedirs(MODEL_DIR, exist_ok=True)

# =========================
# LOAD DATA
# =========================
print("📥 Loading ERA5 labeled data...")
df = pd.read_csv(DATA_PATH)

FEATURES = [
    "t2m", "u10", "v10", "sp", "tcwv",
    "wind_speed", "temp_c", "pressure_hpa"
]

TARGET = "extreme_rain"

X = df[FEATURES]
y = df[TARGET]

print("\n⚠️ Class distribution:")
print(y.value_counts())

# =========================
# TEMPORAL SPLIT (80/20)
# =========================
split_idx = int(0.8 * len(df))
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# Handle imbalance
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

# =========================
# MODEL
# =========================
pipeline = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        (
            "xgb",
            XGBClassifier(
                n_estimators=500,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)

# =========================
# TRAIN
# =========================
print("\n🚀 Training XGBoost...")
pipeline.fit(X_train, y_train)

# =========================
# EVALUATE
# =========================
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

print("\n📄 Classification Report (XGBoost):")
print(classification_report(y_test, y_pred, digits=4))

roc_auc = roc_auc_score(y_test, y_prob)
print(f"🔥 ROC-AUC: {roc_auc:.4f}")

# =========================
# SAVE MODEL
# =========================
model_path = os.path.join(MODEL_DIR, "era5_xgboost.joblib")
joblib.dump(pipeline, model_path)

print("\n💾 XGBoost model saved:", model_path)
