import pandas as pd
import numpy as np

# ==============================
# CONFIG
# ==============================
RISK_CSV = "results/risk_tier_predictions.csv"
HISTORIC_CSV = "data/historic_events.csv"
WINDOW_HOURS = 48   # max look-back window

# ==============================
# LOAD DATA
# ==============================
risk = pd.read_csv(
    RISK_CSV,
    parse_dates=["time"],
    index_col="time"
)

historic = pd.read_csv(
    HISTORIC_CSV,
    parse_dates=["Date"],
    dayfirst=True
)

# Keep only events within model time span
historic = historic[
    historic["Date"].between(risk.index.min(), risk.index.max())
].copy()

print(f"Valid historic events: {len(historic)}")

# ==============================
# LEAD TIME COMPUTATION
# ==============================
records = []

for _, event in historic.iterrows():
    event_time = event["Date"]

    window_start = event_time - pd.Timedelta(hours=WINDOW_HOURS)

    window = risk.loc[
        (risk.index >= window_start) &
        (risk.index <= event_time)
    ]

    def first_alert(tier):
        hits = window[window["risk_tier"] == tier]
        if len(hits) == 0:
            return np.nan
        return (event_time - hits.index.min()).total_seconds() / 3600

    records.append({
        "event_date": event_time,
        "location": event["Location"],
        "state": event["State"],
        "severity": event["Severity"],
        "lead_YELLOW_hr": first_alert("YELLOW"),
        "lead_ORANGE_hr": first_alert("ORANGE"),
        "lead_RED_hr": first_alert("RED"),
    })

lead_df = pd.DataFrame(records)

# ==============================
# SAVE RESULTS
# ==============================
lead_df.to_csv("results/lead_time_analysis.csv", index=False)

print("\n=== LEAD TIME SUMMARY (hours) ===")
print(lead_df[[
    "lead_YELLOW_hr",
    "lead_ORANGE_hr",
    "lead_RED_hr"
]].describe().round(2))

# ==============================
# DETECTION RATES
# ==============================
print("\n=== Detection Rate ===")
for tier in ["YELLOW", "ORANGE", "RED"]:
    detected = lead_df[f"lead_{tier}_hr"].notna().mean()
    print(f"{tier:7s}: {detected*100:.1f}%")

# ==============================
# EARLIEST WARNINGS
# ==============================
print("\n=== Median Lead Times (hours) ===")
for tier in ["YELLOW", "ORANGE", "RED"]:
    median = lead_df[f"lead_{tier}_hr"].median()
    print(f"{tier:7s}: {median:.2f}")
