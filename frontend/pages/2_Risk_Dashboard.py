import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.title("⚠️ Risk Dashboard")

st.markdown(
    """
    Upload meteorological features to estimate **cloudburst risk probability**
    using different ML models.
    """
)

# Upload CSV
uploaded_file = st.file_uploader("📤 Upload Feature CSV", type=["csv"])

# Model selection
model = st.selectbox(
    "🤖 Select Model",
    ["Logistic Regression", "Random Forest", "XGBoost"]
)

model_map = {
    "Logistic Regression": "lr",
    "Random Forest": "rf",
    "XGBoost": "xgb"
}

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📄 Preview of input data:", df.head())

    if st.button("🚀 Predict Risk"):
        with st.spinner("Sending data to backend..."):

             uploaded_file.seek(0)

             response = requests.post(
                "http://127.0.0.1:8001/predict",
                files={"file": (uploaded_file.name, uploaded_file, "text/csv")},
                data={"model": model_map[model]}
             )

        if response.status_code == 200:
            result = response.json()

            predictions = result["predictions"]

            df["risk_probability"] = [p["risk_probability"] for p in predictions]
            df["risk_tier"] = [p["risk_tier"] for p in predictions]

            st.success(f"Average Risk Level: {result['risk_level']}")

            st.subheader("📊 Risk Probability Timeline")

            fig, ax = plt.subplots()
            ax.plot(df.index, df["risk_probability"])
            ax.set_xlabel("Time")
            ax.set_ylabel("Risk Probability")
            ax.set_ylim(0, 1)
            st.pyplot(fig)

            st.subheader("🚦 Risk Tiers")
            st.dataframe(df[["risk_probability", "risk_tier"]])

        else:
            st.error(f"Backend error: {response.text}")