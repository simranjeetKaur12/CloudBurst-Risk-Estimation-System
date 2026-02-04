import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Choose best model (XGBoost recommended)
model = joblib.load("models/xgb_early_warning.pkl")

test_df = pd.read_csv("data/processed/test.csv")
X_test = test_df[joblib.load("models/feature_list.pkl")]
y_test = test_df["cloudburst"]

y_pred = (model.predict_proba(X_test)[:,1] >= 0.5).astype(int)

cm = confusion_matrix(y_test, y_pred)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["No Cloudburst", "Cloudburst"]
)

plt.figure(figsize=(5,5))
disp.plot(cmap="Blues", values_format="d")
plt.title("Confusion Matrix for Cloudburst Prediction")

plt.savefig("figures/output/fig_confusion_matrix.png", dpi=300, bbox_inches="tight")
plt.close()
