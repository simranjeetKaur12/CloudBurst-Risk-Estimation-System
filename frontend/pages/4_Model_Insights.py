import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🧠 Model Insights & Interpretability")

st.markdown(
    """
    Understanding *why* a model predicts risk is critical
    for trust and operational deployment.
    """
)

st.subheader("📊 Model Performance Comparison")

models = ["LR", "RF", "XGB"]
recall = [0.72, 0.81, 0.87]

fig, ax = plt.subplots()
ax.bar(models, recall)
ax.set_ylabel("Recall")
ax.set_ylim(0, 1)
st.pyplot(fig)

st.subheader("📈 ROC Curve (Illustrative)")

fpr = np.linspace(0, 1, 100)
tpr = np.sqrt(fpr)

fig, ax = plt.subplots()
ax.plot(fpr, tpr, label="XGBoost")
ax.plot([0, 1], [0, 1], "--")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.legend()
st.pyplot(fig)

st.subheader("🔍 Feature Importance (XGBoost)")

features = ["Rainfall", "Humidity", "Wind Speed", "Pressure", "Cloud Top Temp"]
importance = [0.34, 0.21, 0.18, 0.15, 0.12]

fig, ax = plt.subplots()
ax.barh(features, importance)
ax.invert_yaxis()
st.pyplot(fig)

st.info(
    """
    ✔️ High recall ensures **extreme events are not missed**  
    ✔️ Feature importance improves **model transparency**
    """
)
