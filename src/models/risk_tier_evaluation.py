import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

MAX_ALERTS = {"RED": 1, "ORANGE": 3}
WINDOW_HOURS = 24


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_csv", type=str, default="data/processed/test.csv")
    parser.add_argument("--model_path", type=str, default="models/xgb_early_warning.pkl")
    parser.add_argument("--feature_list", type=str, default="models/feature_list.pkl")
    parser.add_argument("--group_col", type=str, default="region")
    parser.add_argument("--risk_prob_out", type=str, default="results/risk_probabilities.csv")
    parser.add_argument("--risk_tier_out", type=str, default="results/risk_tier_predictions.csv")
    parser.add_argument("--summary_out", type=str, default="results/risk_tier_summary.csv")
    return parser.parse_args()


def find_threshold(prob_series: pd.Series, time_index: pd.Series, max_alerts_per_month: float) -> float:
    frame = pd.DataFrame({"p": prob_series.values}, index=pd.to_datetime(time_index))

    lo = frame["p"].quantile(0.90)
    hi = frame["p"].quantile(0.99)
    if np.isclose(lo, hi):
        return float(hi)

    for threshold in np.linspace(hi, lo, 400):
        alerts = (frame["p"] >= threshold).astype(int)
        monthly = alerts.resample("ME").sum().mean()
        if 0 < monthly <= max_alerts_per_month:
            return float(threshold)
    return float(frame["p"].quantile(0.995))


def event_recall(df: pd.DataFrame, tiers: list[str]) -> float:
    event_times = pd.to_datetime(df.loc[df["true_label"] == 1, "time"])
    if len(event_times) == 0:
        return float("nan")

    hits = 0
    local = df.sort_values("time").copy()
    local["time"] = pd.to_datetime(local["time"])
    local = local.set_index("time")

    for event_time in event_times:
        window = local.loc[event_time - pd.Timedelta(hours=WINDOW_HOURS): event_time + pd.Timedelta(hours=WINDOW_HOURS)]
        if window["risk_tier"].isin(tiers).any():
            hits += 1
    return hits / len(event_times)


def assign_tier(probability: float, red_th: float, orange_th: float, yellow_th: float) -> str:
    if probability >= red_th:
        return "RED"
    if probability >= orange_th:
        return "ORANGE"
    if probability >= yellow_th:
        return "YELLOW"
    return "NORMAL"


def main():
    args = parse_args()
    features = joblib.load(args.feature_list)
    model = joblib.load(args.model_path)

    df = pd.read_csv(args.test_csv, parse_dates=["time"]).sort_values("time")
    if args.group_col not in df.columns:
        df[args.group_col] = "global"

    all_probs = []
    all_tiers = []
    summary_rows = []

    for group_value, group in df.groupby(args.group_col):
        x = group[features]
        y = group["cloudburst"].values
        probs = model.predict_proba(x)[:, 1]

        red_th = find_threshold(pd.Series(probs), group["time"], MAX_ALERTS["RED"])
        orange_th = min(find_threshold(pd.Series(probs), group["time"], MAX_ALERTS["ORANGE"]), red_th)
        yellow_th = min(float(np.quantile(probs, 0.80)), orange_th)

        result = group[[args.group_col, "time"]].copy()
        result["probability"] = probs
        result["true_label"] = y
        result["risk_tier"] = result["probability"].apply(
            lambda p: assign_tier(float(p), red_th, orange_th, yellow_th)
        )

        all_probs.append(result[[args.group_col, "time", "probability", "true_label"]])
        all_tiers.append(result)

        monthly_alerts = (
            result.set_index("time")["risk_tier"].isin(["RED", "ORANGE"]).resample("ME").sum().mean()
        )
        summary_rows.append(
            {
                args.group_col: group_value,
                "rows": int(len(group)),
                "events": int(result["true_label"].sum()),
                "red_threshold": red_th,
                "orange_threshold": orange_th,
                "yellow_threshold": yellow_th,
                "recall_red": event_recall(result, ["RED"]),
                "recall_red_orange": event_recall(result, ["RED", "ORANGE"]),
                "recall_all_tiers": event_recall(result, ["RED", "ORANGE", "YELLOW"]),
                "avg_alerts_per_month_red_orange": float(monthly_alerts),
            }
        )

    prob_df = pd.concat(all_probs, ignore_index=True).sort_values([args.group_col, "time"])
    tier_df = pd.concat(all_tiers, ignore_index=True).sort_values([args.group_col, "time"])
    summary_df = pd.DataFrame(summary_rows).sort_values(args.group_col)

    Path(args.risk_prob_out).parent.mkdir(parents=True, exist_ok=True)
    prob_df.to_csv(args.risk_prob_out, index=False)
    tier_df.to_csv(args.risk_tier_out, index=False)
    summary_df.to_csv(args.summary_out, index=False)

    print("Risk tier evaluation completed")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
