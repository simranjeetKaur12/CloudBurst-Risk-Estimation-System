from pathlib import Path
import sys

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api_client import ApiError, infer_district, list_districts
from ui import hero, metric_strip, risk_badge, setup_page, style_plotly_figure, top_nav


setup_page("Cloudburst Risk Dashboard")
top_nav("Risk Dashboard")

hero(
    "District Risk Dashboard",
    "Run zone-aware ensemble inference for a district and inspect atmospheric trend signals, lead-time estimate, and factor attribution.",
)

try:
    districts = list_districts(limit=700)
except ApiError as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

if not districts:
    st.error("No districts returned by backend.")
    st.stop()

district_df = pd.DataFrame(districts)
district_df["chunk"] = district_df["chunk"].astype(str)

filters, actions = st.columns([1.7, 1], gap="medium")
with filters:
    query = st.text_input("District search", placeholder="Type district name")
    zone = st.selectbox("Zone", ["All"] + sorted(district_df["chunk"].dropna().unique().tolist()))

    filtered = district_df.copy()
    if query.strip():
        filtered = filtered[filtered["district"].str.contains(query.strip(), case=False, na=False)]
    if zone != "All":
        filtered = filtered[filtered["chunk"].str.lower() == zone.lower()]

    if filtered.empty:
        st.warning("No district matched the selected filters.")
        st.stop()

    option_map = {
        f"{r.district} | {r.state} | {str(r.chunk).title()}": r.district
        for r in filtered.itertuples(index=False)
    }
    selected_label = st.selectbox("District", list(option_map.keys()))
    selected_district = option_map[selected_label]

with actions:
    st.write("")
    st.write("")
    run_clicked = st.button("Run District Inference", use_container_width=True)

if run_clicked:
    with st.spinner("Running ensemble inference..."):
        try:
            st.session_state["risk_result"] = infer_district(selected_district)
        except ApiError as exc:
            st.error(str(exc))
            st.stop()

result = st.session_state.get("risk_result")
if not result:
    st.info("Choose district filters and run inference to view current risk outputs.")
    st.stop()

risk_score = float(result.get("risk_score", 0.0))
tier = str(result.get("alert_tier", "LOW"))
lead = result.get("lead_time_analysis", {}).get("estimated_hours", result.get("lead_time_estimate_hours"))
ensemble = float(result.get("model_breakdown", {}).get("ensemble_probability", 0.0)) * 100.0

metric_strip(
    [
        ("Risk Score", f"{risk_score:.1f}/100"),
        ("Alert Tier", tier),
        ("Lead-Time Estimate", f"{lead:.1f}h" if lead is not None else "NA"),
        ("Ensemble Probability", f"{ensemble:.1f}%"),
    ]
)

st.markdown(f"Current alert: {risk_badge(tier)}", unsafe_allow_html=True)

viz = result.get("visualization", {})
ts = viz.get("timestamps", [])
if ts:
    trend_df = pd.DataFrame(
        {
            "time": pd.to_datetime(ts),
            "Rainfall": viz.get("rain_trend", []),
            "Moisture": viz.get("moisture_trend", []),
            "Pressure Drop": viz.get("pressure_drop_trend", []),
            "Wind": viz.get("wind_convergence_trend", []),
        }
    )

    col_a, col_b = st.columns([1.6, 1], gap="large")
    with col_a:
        if HAS_PLOTLY:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trend_df["time"], y=trend_df["Rainfall"], mode="lines", name="Rainfall"))
            fig.add_trace(go.Scatter(x=trend_df["time"], y=trend_df["Moisture"], mode="lines", name="Moisture"))
            fig.add_trace(go.Scatter(x=trend_df["time"], y=trend_df["Pressure Drop"], mode="lines", name="Pressure Drop"))
            fig.add_trace(go.Scatter(x=trend_df["time"], y=trend_df["Wind"], mode="lines", name="Wind"))
            fig.update_layout(title="10-Day Precursor Trend")
            st.plotly_chart(style_plotly_figure(fig, height=370), use_container_width=True)
        else:
            st.markdown("### 10-Day Precursor Trend")
            st.line_chart(trend_df.set_index("time")[["Rainfall", "Moisture", "Pressure Drop", "Wind"]], use_container_width=True)

    with col_b:
        factors = result.get("top_contributing_factors", {})
        if factors:
            factors_df = pd.DataFrame(
                {"factor": list(factors.keys()), "share": list(factors.values())}
            ).sort_values("share", ascending=True)
            if HAS_PLOTLY:
                fig_f = px.bar(
                    factors_df,
                    x="share",
                    y="factor",
                    orientation="h",
                    color="share",
                    color_continuous_scale=["#0ea5e9", "#2563eb", "#dc2626"],
                )
                fig_f.update_layout(title="Top Contributing Factors", coloraxis_showscale=False)
                st.plotly_chart(style_plotly_figure(fig_f, height=370), use_container_width=True)
            else:
                st.markdown("### Top Contributing Factors")
                st.bar_chart(factors_df.set_index("factor")["share"], use_container_width=True)

st.markdown("### Interpretation for Field Teams")
st.markdown(
    f"""
    <div class="cb-explain">
        {result.get('layman_explanation', 'No explanation provided by backend.')}
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Model and lead-time breakdown"):
    st.json(
        {
            "resolved_location": result.get("resolved_location", {}),
            "model_breakdown": result.get("model_breakdown", {}),
            "lead_time_analysis": result.get("lead_time_analysis", {}),
        }
    )