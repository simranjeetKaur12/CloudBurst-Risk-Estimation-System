import argparse
from pathlib import Path

import numpy as np
import pandas as pd

WINDOW_HOURS = 48


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--risk_csv", type=str, default="results/risk_tier_predictions.csv")
    parser.add_argument("--historic_csv", type=str, default="data/historic_events.csv")
    parser.add_argument("--output_csv", type=str, default="results/lead_time_analysis.csv")
    parser.add_argument("--window_hours", type=int, default=WINDOW_HOURS)
    parser.add_argument("--group_col", type=str, default="region")
    parser.add_argument("--group_value", type=str, default=None)
    return parser.parse_args()


def first_alert_hours(window: pd.DataFrame, event_time: pd.Timestamp, tier: str) -> float:
    hits = window[window["risk_tier"] == tier]
    if len(hits) == 0:
        return float("nan")
    first_hit = pd.to_datetime(hits["time"]).min()
    return (event_time - first_hit).total_seconds() / 3600.0


def main():
    args = parse_args()

    risk = pd.read_csv(args.risk_csv, parse_dates=["time"])
    historic = pd.read_csv(args.historic_csv, parse_dates=["Date"], dayfirst=True)

    if args.group_col in risk.columns:
        if args.group_value is None:
            unique_groups = risk[args.group_col].dropna().astype(str).unique().tolist()
            if len(unique_groups) > 1:
                print(
                    "Multiple groups detected in risk data. "
                    "Use --group_value to validate a specific region/district."
                )
                print("Available groups:", unique_groups)
                return
        else:
            risk = risk[risk[args.group_col].astype(str).str.lower() == args.group_value.lower()].copy()

    if risk.empty:
        raise RuntimeError("No risk rows available for lead-time analysis.")

    historic = historic[historic["Date"].between(risk["time"].min(), risk["time"].max())].copy()
    print(f"Valid historic events: {len(historic)}")

    records = []
    risk = risk.sort_values("time")

    for _, event in historic.iterrows():
        event_time = event["Date"]
        window_start = event_time - pd.Timedelta(hours=args.window_hours)
        window = risk[(risk["time"] >= window_start) & (risk["time"] <= event_time)]

        records.append(
            {
                "event_date": event_time,
                "location": event.get("Location", ""),
                "state": event.get("State", ""),
                "severity": event.get("Severity", ""),
                "lead_YELLOW_hr": first_alert_hours(window, event_time, "YELLOW"),
                "lead_ORANGE_hr": first_alert_hours(window, event_time, "ORANGE"),
                "lead_RED_hr": first_alert_hours(window, event_time, "RED"),
            }
        )

    lead_df = pd.DataFrame(records)
    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    lead_df.to_csv(out_csv, index=False)

    print("Lead-time analysis saved ->", out_csv)
    if not lead_df.empty:
        print(lead_df[["lead_YELLOW_hr", "lead_ORANGE_hr", "lead_RED_hr"]].describe().round(2))


if __name__ == "__main__":
    main()
