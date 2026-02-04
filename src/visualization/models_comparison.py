# reports/research_paper_figures/fig7_model_comparison.py

import pandas as pd
import matplotlib.pyplot as plt

# Load real evaluation results
df = pd.read_csv("results/model_performance.csv")

df = df.set_index("model")

fig, ax = plt.subplots(figsize=(7, 4))

df[["auc", "f1"]].plot(
    kind="bar",
    ax=ax,
    width=0.75,
    edgecolor="black"
)

ax.set_ylabel("Score")
ax.set_ylim(0, 1)
ax.set_title("Comparison of ML Models for Cloudburst Risk Prediction")

ax.legend(
    ["AUC (ROC)", "F1-score"],
    frameon=False,
    loc="upper left"
)

ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(
    "figures/output/fig7_model_comparison.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()
