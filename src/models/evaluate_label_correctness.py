import pandas as pd
from datetime import timedelta

HISTORIC_CSV = "data/historic_events.csv"
LABELED_CSV = "data/processed/labeled_cloudburst.csv"

# --------------------------------
# LOAD DATA
# --------------------------------
historic = pd.read_csv(
    HISTORIC_CSV,
    parse_dates=["Date"],
    dayfirst=True
)

# --------------------------------
# FILTER VALID EVENTS
# --------------------------------
historic = historic[
    (historic["Date"].dt.year >= 2001) &
    (historic["Severity"].isin(["Moderate", "Severe", "Catastrophic"])) &
    (~historic["Location"].str.contains("glacial|avalanche", case=False, na=False))
]

print(f"Filtered historic events (valid): {len(historic)}")


labels = pd.read_csv(
    LABELED_CSV,
    parse_dates=["time"]
)

print(f"Total historic events: {len(historic)}")

# Only hours labeled as cloudburst
detected_hours = labels[labels["cloudburst"] == 1]["time"]

# --------------------------------
# MATCH WITH ±24 HOUR WINDOW
# --------------------------------
WINDOW = timedelta(hours=24)

def detected_within_window(event_date):
    start = event_date - WINDOW
    end = event_date + WINDOW
    return ((detected_hours >= start) & (detected_hours <= end)).any()

historic["Detected"] = historic["Date"].apply(detected_within_window)

# --------------------------------
# METRICS
# --------------------------------
total = len(historic)
detected = historic["Detected"].sum()
missed = total - detected
recall = detected / total

print("\n=== LABEL CORRECTNESS (±24h window) ===")
print(f"Total historic events   : {total}")
print(f"Detected by labels      : {detected}")
print(f"Missed events           : {missed}")
print(f"Recall                  : {recall:.2%}")

# --------------------------------
# MISSED EVENTS
# --------------------------------
print("\n=== MISSED EVENTS ===")
print(
    historic[~historic["Detected"]][
        ["Date", "Location", "State", "Severity", "Detected"]
    ].to_string(index=False)
)
