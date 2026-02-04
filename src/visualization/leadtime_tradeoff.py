import pandas as pd
import matplotlib.pyplot as plt

lead_df = pd.DataFrame({
    "Risk Tier": ["YELLOW", "ORANGE", "RED"],
    "Detection Rate (%)": [78.9, 31.6, 15.8],
    "Median Lead Time (hrs)": [48, 35.5, 6]
})

plt.figure(figsize=(6,4))

plt.scatter(
    lead_df["Median Lead Time (hrs)"],
    lead_df["Detection Rate (%)"],
    s=150
)

for _, row in lead_df.iterrows():
    plt.text(
        row["Median Lead Time (hrs)"]+0.5,
        row["Detection Rate (%)"]-2,
        row["Risk Tier"]
    )

plt.xlabel("Median Lead Time (hours)")
plt.ylabel("Detection Rate (%)")
plt.title("Lead-Time vs Detection Tradeoff")
plt.grid(alpha=0.3)

plt.savefig("figures/output/fig_leadtime_tradeoff.png", dpi=300, bbox_inches="tight")
plt.close()