import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "data/processed/era5_labeled_uttarakhand.csv",
    parse_dates=["time"]
)

sample = df.iloc[:300]

fig, ax1 = plt.subplots(figsize=(9, 3))

ax1.plot(sample["time"], sample["tcwv"], label="TCWV", linewidth=1)
ax1.set_ylabel("TCWV (kg/m²)")

ax2 = ax1.twinx()
ax2.plot(sample["time"], sample["wind_speed"], linestyle="--", label="Wind Speed")
ax2.set_ylabel("Wind Speed (m/s)")

ax1.set_title("ERA5 Atmospheric Precursors Prior to Cloudburst")
fig.legend(loc="upper right")

plt.tight_layout()
plt.savefig("figures/output/fig4_era5_precursors.png", dpi=300)
plt.close()
