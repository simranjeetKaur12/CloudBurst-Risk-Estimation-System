import streamlit as st
from PIL import Image

st.title("🌧️ Cloudburst Risk Assessment System")

st.markdown(
    """
    ### 🚨 Problem Statement

    Cloudbursts are **high-intensity localized rainfall events** that cause
    flash floods, landslides, and infrastructure damage—especially in
    **mountainous regions like Uttarakhand**.

    ⚠️ Existing systems:
    - Provide **low lead-time**
    - Lack **probabilistic uncertainty**
    - Are not decision-oriented

    ---
    ### 🎯 Our Solution

    An **AI-driven early warning system** that:
    - Predicts **risk probability**
    - Provides **risk tiers**
    - Enables **early intervention**
    """
)

st.subheader("📍 Study Area")

img_study = Image.open("frontend/assets/fig1_study_area.png")
st.image(img_study, caption="Study Area: Uttarakhand Himalayan Region", use_container_width=True)

st.subheader("🧠 System Architecture")

img_arch = Image.open("frontend/assets/system_architecture.png")
st.image(img_arch, caption="End-to-End Cloudburst Risk Prediction Pipeline", use_container_width=True)

st.success("➡️ Use the sidebar to explore risk dashboards and model insights.")
