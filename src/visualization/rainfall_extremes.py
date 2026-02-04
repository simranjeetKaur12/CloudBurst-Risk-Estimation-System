import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "data/processed/imerg_halfhourly_uttarakhand.csv",
    parse_dates=["time"]
)

sample = df.iloc[:400]

plt.figure(figsize=(9, 3))
plt.plot(sample["time"], sample["rain_mm_hr"], color="black", linewidth=0.8)

plt.ylabel("Rainfall (mm/hr)")
plt.xlabel("Time")
plt.title("IMERG Half-hourly Rainfall Showing Short-duration Extremes")

plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/output/fig3_rainfall_extremes.png", dpi=300)
plt.close()
