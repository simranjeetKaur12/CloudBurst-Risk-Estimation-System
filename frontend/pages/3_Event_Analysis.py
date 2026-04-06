from pathlib import Path
import sys

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api_client import ApiError, historical_events, load_results_csv, replay_event
from ui import hero, metric_strip, setup_page, style_plotly_figure, top_nav


def _load_event_table() -> pd.DataFrame:
    try:
        events = historical_events(limit=400)
        if events:
            df = pd.DataFrame(events)
            rename = {
                "district": "location",
                "tier": "severity",
            }
            return df.rename(columns=rename)
    except ApiError:
        pass

    fallback = load_results_csv("lead_time_analysis.csv")
    fallback = fallback.rename(columns={"event_date": "date"})
    return fallback


setup_page("Cloudburst Event Analysis")
top_nav("Event Analysis")

hero(
    "Historical Event Analysis and Lead-Time Quality",
    "Review documented cloudburst events, inspect lead-time availability by severity, and replay archived signals when backend support is available.",
)

events_df = _load_event_table()
if events_df.empty:
    st.error("No historical event records available.")
    st.stop()

if "date" in events_df.columns:
    events_df["date"] = pd.to_datetime(events_df["date"], errors="coerce")
elif "event_date" in events_df.columns:
    events_df["event_date"] = pd.to_datetime(events_df["event_date"], errors="coerce")

severity_col = "severity" if "severity" in events_df.columns else None
location_col = "location" if "location" in events_df.columns else ("district" if "district" in events_df.columns else None)

metric_strip(
    [
        ("Recorded Events", f"{len(events_df)}"),
        ("Distinct States", f"{events_df['state'].nunique() if 'state' in events_df.columns else 'NA'}"),
        (
            "Median Yellow Lead",
            f"{events_df['lead_YELLOW_hr'].median():.0f}h" if "lead_YELLOW_hr" in events_df.columns else "NA",
        ),
        (
            "Median Orange Lead",
            f"{events_df['lead_ORANGE_hr'].median():.0f}h" if "lead_ORANGE_hr" in events_df.columns else "NA",
        ),
    ]
)

left, right = st.columns([1, 1], gap="large")
with left:
    if severity_col:
        sev = (
            events_df[severity_col]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("severity")
            .reset_index(name="events")
        )
        if HAS_PLOTLY:
            fig_sev = px.bar(sev, x="severity", y="events", color="events", color_continuous_scale="YlOrRd")
            fig_sev.update_layout(title="Events by Severity", coloraxis_showscale=False)
            st.plotly_chart(style_plotly_figure(fig_sev), use_container_width=True)
        else:
            st.markdown("### Events by Severity")
            st.bar_chart(sev.set_index("severity")["events"], use_container_width=True)

with right:
    if "lead_YELLOW_hr" in events_df.columns and severity_col:
        lead_long = events_df[[severity_col, "lead_YELLOW_hr", "lead_ORANGE_hr", "lead_RED_hr"]].melt(
            id_vars=[severity_col],
            value_vars=["lead_YELLOW_hr", "lead_ORANGE_hr", "lead_RED_hr"],
            var_name="threshold",
            value_name="lead_hours",
        )
        lead_long = lead_long.dropna(subset=["lead_hours"])
        if HAS_PLOTLY:
            fig_box = px.box(
                lead_long,
                x=severity_col,
                y="lead_hours",
                color="threshold",
                points="all",
            )
            fig_box.update_layout(title="Lead-Time Distribution by Severity")
            st.plotly_chart(style_plotly_figure(fig_box), use_container_width=True)
        else:
            pivot = lead_long.pivot_table(index=severity_col, columns="threshold", values="lead_hours", aggfunc="median")
            st.markdown("### Lead-Time Distribution by Severity")
            st.bar_chart(pivot, use_container_width=True)

show_cols = [c for c in ["date", "event_date", location_col, "state", severity_col, "lead_YELLOW_hr", "lead_ORANGE_hr", "lead_RED_hr"] if c and c in events_df.columns]
st.markdown("### Event Registry")
st.dataframe(events_df[show_cols].sort_values(show_cols[0], ascending=False), use_container_width=True, hide_index=True)

if location_col:
    options = events_df[location_col].fillna("Unknown").astype(str).tolist()
    selected = st.selectbox("Event location", options)
    event_row = events_df[events_df[location_col].astype(str) == selected].iloc[0]
    st.markdown("### Selected Event Snapshot")
    snapshot = {
        "location": selected,
        "state": event_row.get("state", "Unknown"),
        "severity": event_row.get(severity_col, "Unknown") if severity_col else "Unknown",
        "yellow_lead_hr": event_row.get("lead_YELLOW_hr", None),
        "orange_lead_hr": event_row.get("lead_ORANGE_hr", None),
        "red_lead_hr": event_row.get("lead_RED_hr", None),
    }
    st.json(snapshot)

if "event_id" in events_df.columns:
    selected_id = int(st.selectbox("Replay event id", events_df["event_id"].dropna().astype(int).tolist()))
    if st.button("Replay Archived Event"):
        try:
            payload = replay_event(selected_id)
            st.json(payload)
        except ApiError as exc:
            st.error(str(exc))
