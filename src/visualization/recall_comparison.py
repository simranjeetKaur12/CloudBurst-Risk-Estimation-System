import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/model_performance.csv")

df = df.set_index("model")[["recall"]].sort_values("recall", ascending=False)

plt.figure(figsize=(6,4))
df.plot(kind="bar", legend=False, edgecolor="black")

plt.ylabel("Recall")
plt.ylim(0,1)
plt.title("Recall Comparison of Early Warning Models")
plt.grid(axis="y", alpha=0.3)

plt.savefig("figures/output/fig_recall_comparison.png", dpi=300, bbox_inches="tight")
plt.close()
