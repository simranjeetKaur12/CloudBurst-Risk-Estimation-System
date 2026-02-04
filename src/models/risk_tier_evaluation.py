import numpy as np
import pandas as pd
import joblib

# ==============================
# CONFIG
# ==============================
MAX_ALERTS = {
    "RED": 1,
    "ORANGE": 3,
    "YELLOW": 7,
}

WINDOW_HOURS = 24

# ==============================
# Load data
# ==============================
feature_list = joblib.load("models/feature_list.pkl")

df = (
    pd.read_csv("data/processed/test.csv", parse_dates=["time"])
    .set_index("time")
    .sort_index()
)

X = df[feature_list]
y = df["cloudburst"].values

# ==============================
# Load model
# ==============================
model = joblib.load("models/xgb_early_warning.pkl")

# ==============================
# Predict probabilities
# ==============================
probs = model.predict_proba(X)[:, 1]

results = pd.DataFrame(
    {
        "probability": probs,
        "true_label": y,
    },
    index=df.index,
)

results.to_csv("results/risk_probabilities.csv")

# ==============================
# Budget-based thresholding (FIXED)
# ==============================
def find_threshold(probs, index, max_alerts_per_month):
    df = pd.DataFrame({"p": probs}, index=index)

    for th in np.linspace(df["p"].quantile(0.99), df["p"].quantile(0.90), 400):
        alerts = (df["p"] >= th).astype(int)
        monthly = alerts.resample("ME").sum().mean()

        if 0 < monthly <= max_alerts_per_month:
            return th

    return df["p"].quantile(0.995)


red_th = find_threshold(probs, results.index, MAX_ALERTS["RED"])
orange_th = find_threshold(probs, results.index, MAX_ALERTS["ORANGE"])
yellow_th = np.quantile(probs, 0.80)

# enforce hierarchy
orange_th = min(orange_th, red_th)
yellow_th = min(yellow_th, orange_th)

print("\n=== Risk Tier Thresholds ===")
print(f"RED    : {red_th:.4f}")
print(f"ORANGE : {orange_th:.4f}")
print(f"YELLOW : {yellow_th:.4f}")

# ==============================
# Assign tiers
# ==============================
def assign_tier(p):
    if p >= red_th:
        return "RED"
    elif p >= orange_th:
        return "ORANGE"
    elif p >= yellow_th:
        return "YELLOW"
    else:
        return "NORMAL"

results["risk_tier"] = results["probability"].apply(assign_tier)
results.to_csv("results/risk_tier_predictions.csv")

# ==============================
# Event-level recall (±24h)
# ==============================
def event_recall(results, tiers):
    event_times = results.index[results["true_label"] == 1]
    hits = 0

    for t in event_times:
        window = results.loc[
            t - pd.Timedelta(hours=WINDOW_HOURS) :
            t + pd.Timedelta(hours=WINDOW_HOURS)
        ]

        if window["risk_tier"].isin(tiers).any():
            hits += 1

    return hits / len(event_times) if len(event_times) else np.nan


print("\n=== Event Coverage (Recall ±24h) ===")
print(f"RED only       : {event_recall(results, ['RED']):.3f}")
print(f"RED + ORANGE   : {event_recall(results, ['RED','ORANGE']):.3f}")
print(f"ALL TIERS      : {event_recall(results, ['RED','ORANGE','YELLOW']):.3f}")

# ==============================
# Operational Load
# ==============================
monthly_alerts = (
    results["risk_tier"]
    .isin(["RED", "ORANGE"])
    .resample("ME")
    .sum()
)

print("\n=== Operational Load ===")
print(f"Avg alerts/month (RED+ORANGE): {monthly_alerts.mean():.2f}")

# ==============================
# Diagnostics
# ==============================
print("\n=== Alert Distribution ===")
print(results["risk_tier"].value_counts())

print("\n=== Probability Summary ===")
print(results["probability"].describe())

print("\nTop 20 probabilities:")
print(
    results.sort_values("probability", ascending=False)
    .head(20)[["probability", "true_label"]]
)
