import streamlit as st

# ------------------------------------------------------------
# App Configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="Cloudburst Early Warning System",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
st.sidebar.title("🌧️ Cloudburst Risk Intelligence")
st.sidebar.markdown("""
**Early Warning • Probabilistic Risk • Lead-Time Analysis**

This system integrates **satellite data**, **reanalysis products**,  
and **machine learning models** to deliver **actionable cloudburst risk alerts**.
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📌 Navigation
Use the pages on the left to explore:
- **Risk Prediction**
- **Event-Level Lead Time**
- **Model Reliability & Trust**
""")

# ------------------------------------------------------------
# Main Page Content
# ------------------------------------------------------------
st.title("Probabilistic Cloudburst Early Warning System")

st.markdown("""
---

### 🌍 What is the Problem?

Cloudbursts are **localized extreme rainfall events** that release  
**>100 mm of rain within a few hours**, often over complex terrain.

They frequently trigger:
- Flash floods
- Landslides
- Infrastructure collapse
- Loss of life

⚠️ **The challenge**:  
Conventional weather forecasts often **fail to provide sufficient lead time**  
or **communicate uncertainty clearly**, especially at regional scales.

---
""")

# ------------------------------------------------------------
# Why This System is Needed
# ------------------------------------------------------------
st.subheader("❓ Why Do We Need a New Approach?")

st.markdown("""
Existing early warning systems are largely:
- **Threshold-based**
- **Deterministic**
- **Not uncertainty-aware**

However, extreme weather is inherently **stochastic**.

This project addresses three critical gaps:

1. **Early Lead Time**  
   → Detect precursors **6–24 hours before** cloudburst onset

2. **Probabilistic Risk Communication**  
   → Move beyond yes/no alerts to **risk probabilities**

3. **Operational Interpretability**  
   → Ensure decisions can be **trusted by disaster managers**

---
""")

# ------------------------------------------------------------
# When & Where
# ------------------------------------------------------------
st.subheader("📍 When and Where is This System Applicable?")

st.markdown("""
**Geographical Focus**
- Mountainous and orographic regions
- Data-driven configuration allows scaling to other regions

**Temporal Scope**
- Historical analysis: Multi-year satellite & reanalysis data
- Operational mode: Near–real-time inference using daily inputs

This system is designed to support:
- **Disaster management authorities**
- **Early warning centers**
- **Hydro-meteorological agencies**

---
""")

# ------------------------------------------------------------
# How the System Works
# ------------------------------------------------------------
st.subheader("⚙️ How Does the System Work?")

st.markdown("""
The system follows a **modular, research-grade pipeline**:

1. **Data Ingestion**
   - Satellite precipitation products
   - Atmospheric reanalysis variables
   - Terrain and moisture indicators

2. **Feature Engineering**
   - Temporal aggregation
   - Atmospheric instability signals
   - Moisture convergence indicators

3. **Machine Learning Models**
   - Logistic Regression (baseline, interpretable)
   - Random Forest (non-linear patterns)
   - XGBoost (high-performance ensemble)

4. **Risk Stratification**
   - Outputs converted into **four operational risk tiers**
     - Low
     - Moderate
     - High
     - Severe

5. **Lead-Time Evaluation**
   - Event-centric analysis of **risk escalation**
   - Quantifies how early actionable signals emerge

---
""")

# ------------------------------------------------------------
# What Makes This Work Novel
# ------------------------------------------------------------
st.subheader("✨ What Makes This Work Novel?")

st.markdown("""
This project goes beyond prediction accuracy.

### 🔬 Research Contributions
- **Lead-time centric evaluation**, not just ROC scores
- **Risk escalation trajectories** before extreme events
- **Probabilistic decision support**, not binary alerts

### 🧠 Engineering Contributions
- Clean ML–Backend–Frontend separation
- Deployment-ready architecture
- Transparent, auditable modeling pipeline

The **Event Analysis** page demonstrates this novelty in detail.

---
""")

# ------------------------------------------------------------
# How to Use the Dashboard
# ------------------------------------------------------------
st.subheader("🧭 How to Use This Dashboard")

st.markdown("""
🔹 **Home**  
→ Understand the problem, study region, and system architecture

🔹 **Risk Dashboard**  
→ Upload feature CSV and generate probabilistic risk timelines

🔹 **Event Analysis**  
→ Examine real cloudburst events and early-warning lead time

🔹 **Model Insights**  
→ Compare models, interpret features, and assess reliability

Each page is designed to support **both scientific analysis and operational decision-making**.

---
""")

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<center><small>"
    "Cloudburst Risk Intelligence Platform | "
    "Probabilistic ML for Extreme Weather Early Warning"
    "</small></center>",
    unsafe_allow_html=True
)
