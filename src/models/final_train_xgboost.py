import pandas as pd
import xgboost as xgb
from sklearn.metrics import classification_report, roc_auc_score
from pathlib import Path

TRAIN_CSV = Path("data/processed/train.csv")
TEST_CSV  = Path("data/processed/test.csv")

print("🚀 Training XGBoost model")

# -------------------------------
# Load data
# -------------------------------
train = pd.read_csv(TRAIN_CSV)
test  = pd.read_csv(TEST_CSV)

FEATURES = [
    "t2m", "u10", "v10", "wind_speed",
    "tcwv", "tcwv_3h", "tcwv_6h",
    "sp", "sp_drop_3h",
    "t2m_grad",
    "rain_mm", "rain_3h", "rain_6h",
    "rain_peak_3h",
    "rain_lag1", "rain_lag2"
]

X_train = train[FEATURES]
y_train = train["cloudburst"]

X_test = test[FEATURES]
y_test = test["cloudburst"]

# -------------------------------
# Handle imbalance
# -------------------------------
scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()

# -------------------------------
# Model
# -------------------------------
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------------
# Evaluation
# -------------------------------
pred = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1]

print("\n📊 Classification Report")
print(classification_report(y_test, pred, digits=4))

print("ROC-AUC:", roc_auc_score(y_test, proba))
