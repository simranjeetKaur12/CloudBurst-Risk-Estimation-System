from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from api_client import ApiError, get_health, infer_district, list_districts, load_results_csv
from ui import (
    MUTED_TEXT,
    SECONDARY_TEXT,
    hero,
    metric_strip,
    panel,
    panel_end,
    risk_badge,
    section_title,
    status_text,
)


def _fallback_districts() -> list[dict]:
    base_dir = Path(__file__).resolve().parents[1]
    lookup_path = base_dir / "data" / "processed" / "himalaya_district_lookup.csv"
    if not lookup_path.exists():
        return []
    df = pd.read_csv(lookup_path)
    cols = {c.lower(): c for c in df.columns}
    district_col = cols.get("district_name", "district_name")
    chunk_col = cols.get("chunk", "chunk")
    state_col = cols.get("state", None)
    output = []
    for _, row in df.iterrows():
        output.append(
            {
                "district": str(row.get(district_col, "Unknown")),
                "state": str(row.get(state_col, "Unknown")) if state_col else "Unknown",
                "chunk": str(row.get(chunk_col, "unknown")),
                "centroid_lat": float(row.get("centroid_lat", 30.0)),
                "centroid_lon": float(row.get("centroid_lon", 78.0)),
            }
        )
    return output


def _metrics_snapshot(district_count: int) -> list[tuple[str, str]]:
    model_perf = load_results_csv("model_performance.csv")
    lead_df = load_results_csv("lead_time_analysis.csv")

    best_auc = model_perf["auc"].max() if "auc" in model_perf.columns else 0.0
    recall = model_perf["recall"].max() if "recall" in model_perf.columns else 0.0
    yellow = lead_df["lead_YELLOW_hr"].median() if "lead_YELLOW_hr" in lead_df.columns else None

    return [
        ("Himalayan Districts in Scope", f"{district_count}"),
        ("Best AUC", f"{best_auc:.3f}"),
        ("Best Recall", f"{recall:.3f}"),
        ("Median Yellow Lead", f"{yellow:.0f}h" if pd.notna(yellow) else "NA"),
    ]


def _district_map(lat: float, lon: float) -> pd.DataFrame:
    return pd.DataFrame({"lat": [lat], "lon": [lon]})


def render_home() -> None:
    hero(
        "Zone-Specific Cloudburst Risk Estimation and Early Warning",
        "District-first intelligence for the Indian Himalayas with probabilistic alerts, lead-time cues, and interpretable atmospheric signals.",
    )

    backend_online = True
    health_data = {}
    try:
        health_data = get_health()
        districts = list_districts(limit=600)
    except ApiError as exc:
        backend_online = False
        st.warning(f"Backend is offline. Showing local data snapshot only: {exc}")
        districts = _fallback_districts()

    if not districts:
        st.error("No district metadata available. Check backend health and lookup files.")
        st.stop()

    metric_strip(_metrics_snapshot(len(districts)))

    section_title("District Situation Preview", "Select a district and inspect the most recent modeled warning signal.")

    district_labels = [f"{d['district']} | {d.get('state', 'Unknown')} | {d.get('chunk', 'unknown').title()}" for d in districts]
    selected_label = st.selectbox("District search", district_labels, index=0)
    selected_name = selected_label.split("|")[0].strip()

    left, right = st.columns([1.15, 1.85], gap="large")
    with left:
        panel()
        st.markdown("### Selected District")
        st.write(selected_label)
        st.markdown(f"Backend status: {status_text(backend_online)}", unsafe_allow_html=True)
        if backend_online:
            if st.button("Load Latest District Risk", use_container_width=True):
                try:
                    st.session_state["home_result"] = infer_district(selected_name)
                except ApiError as exc:
                    st.error(str(exc))
        else:
            st.caption("Run the backend API to enable live district inference.")
        panel_end()

    with right:
        result = st.session_state.get("home_result") if backend_online else None
        if result and result.get("resolved_location"):
            loc = result["resolved_location"]
            st.map(_district_map(float(loc.get("lat", 30.0)), float(loc.get("lon", 78.0))), size=180)
            badge = risk_badge(result.get("alert_tier", "LOW"))
            st.markdown(f"Latest alert tier: {badge}", unsafe_allow_html=True)
            st.caption(result.get("layman_explanation", ""))
        else:
            selected = next((d for d in districts if d["district"] == selected_name), districts[0])
            lat = float(selected.get("centroid_lat", 30.0))
            lon = float(selected.get("centroid_lon", 78.0))
            st.map(_district_map(lat, lon), size=180)
            st.caption("Preview map is centered on district centroid. Run live inference to load current risk tier.")

    section_title("Operational Notes")
    st.markdown(
        f"""
        <div class="cb-card">
            <div class="cb-metric-label" style="color:{SECONDARY_TEXT};">System Mode</div>
            <div class="cb-metric-value">District-level, zone-aware probabilistic warning</div>
            <div class="cb-subtle" style="margin-top:8px;color:{MUTED_TEXT};">
                Model stack combines Random Forest and XGBoost outputs into an ensemble score calibrated for early warning recall.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if health_data:
        with st.expander("Backend health payload"):
            st.json(health_data)
