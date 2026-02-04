import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from pathlib import Path

# ------------------
# Load data
# ------------------
test_df = pd.read_csv("data/processed/test.csv")

X_test = test_df[joblib.load("models/feature_list.pkl")]
y_test = test_df["cloudburst"]

models = {
    "Logistic Regression": joblib.load("models/lr_early_warning.pkl"),
    "Random Forest": joblib.load("models/rf_early_warning.pkl"),
    "XGBoost": joblib.load("models/xgb_early_warning.pkl"),
}

plt.figure(figsize=(6.5, 6))

for name, model in models.items():
    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.2f})")

plt.plot([0,1], [0,1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves for Cloudburst Early Warning Models")
plt.legend()
plt.grid(alpha=0.3)

plt.savefig("figures/output/fig_roc_curves.png", dpi=300, bbox_inches="tight")
plt.close()
