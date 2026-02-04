import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# CONFIG
# =========================
RISK_CSV = Path("results/risk_tier_predictions.csv")
HISTORIC_CSV = Path("data/historic_events.csv")

EVENT_DATE = "2021-07-18"   # <-- change this to any detected event
WINDOW_HOURS = 72           # hours before event

# =========================
# LOAD DATA
# =========================
risk = pd.read_csv(RISK_CSV, parse_dates=["time"]).set_index("time")
historic = pd.read_csv(HISTORIC_CSV, parse_dates=["Date"], dayfirst=True)

event_date = pd.to_datetime(EVENT_DATE)

# =========================
# SELECT EVENT WINDOW
# =========================
start = event_date - pd.Timedelta(hours=WINDOW_HOURS)
end = event_date + pd.Timedelta(hours=6)

df = risk.loc[start:end].copy()

if df.empty:
    raise ValueError("No data found for selected event window")

# =========================
# PLOT
# =========================
plt.figure(figsize=(10, 5))

plt.plot(
    df.index,
    df["probability"],
    color="black",
    linewidth=2,
    label="Cloudburst Risk Probability",
)

# Thresholds (derived from tiers)
thresholds = {
    "YELLOW": df[df["risk_tier"] == "YELLOW"]["probability"].min(),
    "ORANGE": df[df["risk_tier"] == "ORANGE"]["probability"].min(),
    "RED": df[df["risk_tier"] == "RED"]["probability"].min(),
}

colors = {
    "YELLOW": "gold",
    "ORANGE": "orange",
    "RED": "red",
}

for tier, th in thresholds.items():
    if pd.notna(th):
        plt.axhline(
            th,
            linestyle="--",
            color=colors[tier],
            alpha=0.7,
            label=f"{tier} threshold",
        )

# Event time
plt.axvline(
    event_date,
    color="blue",
    linestyle=":",
    linewidth=2,
    label="Observed Cloudburst",
)

# =========================
# STYLING
# =========================
plt.title(f"Risk Escalation Prior to Cloudburst ({EVENT_DATE})", fontsize=14)
plt.ylabel("Predicted Risk Probability")
plt.xlabel("Time")
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"figures/output/fig_risk_escalation_{EVENT_DATE}.png", dpi=300)
plt.close()