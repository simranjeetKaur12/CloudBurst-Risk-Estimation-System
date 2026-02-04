import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/labeled_cloudburst.csv")

counts = df["cloudburst"].value_counts(normalize=True) * 100

plt.figure(figsize=(4, 4))
counts.plot(kind="bar", color="gray", edgecolor="black")

plt.ylabel("Percentage (%)")
plt.title("Cloudburst Risk Class Distribution")

plt.tight_layout()
plt.savefig("figures/output/fig5_label_distribution.png", dpi=300)
plt.close()
