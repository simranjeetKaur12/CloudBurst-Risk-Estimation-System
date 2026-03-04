import streamlit as st
from PIL import Image

st.title("📈 Event Analysis & Lead-Time Evaluation")

st.markdown(
    """
    ### 🔬 Why This Matters

    Disaster mitigation depends not only on accuracy,
    but on **how early the system raises alarms**.

    This page demonstrates:
    - Risk escalation before an extreme event
    - Trade-off between lead-time & false alarms
    """
)

st.subheader("📅 Case Study: 18 July 2021 Cloudburst")

img_escalation = Image.open(
    "frontend/assets/fig_risk_escalation_2021-07-18.png"
)
st.image(
    img_escalation,
    caption="Risk probability escalation prior to cloudburst",
    use_container_width=True
)

st.subheader("⏱️ Lead-Time vs Accuracy Trade-off")

img_tradeoff = Image.open(
    "frontend/assets/fig_leadtime_tradeoff.png"
)
st.image(
    img_tradeoff,
    caption="Lead-time vs precision-recall trade-off",
    use_container_width=True
)

st.success(
    """
    🧠 **Key Insight:**  
    The model detects elevated risk **hours before event onset**,
    enabling early warnings and disaster preparedness.
    """
)
