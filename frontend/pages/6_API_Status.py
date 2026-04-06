from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api_client import ApiError, get_health
from ui import hero, metric_strip, setup_page, status_text, top_nav


setup_page("API Status | Cloudburst")
top_nav("API Status")

hero(
    "API Status and Operational Health",
    "Monitor backend readiness and runtime metadata used by district risk inference.",
)

try:
    health = get_health()
except ApiError as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

st.markdown(f"Service state: {status_text(True)}", unsafe_allow_html=True)
metric_strip(
    [
        ("District Rows", str(health.get("district_rows", "NA"))),
        ("Shapefile", str(health.get("shapefile_used", "NA"))),
        ("Models Loaded", ", ".join(health.get("models_loaded", [])) or "None"),
        ("District Attributes", str(health.get("district_attributes_present", "NA"))),
    ]
)

with st.expander("Raw health payload"):
    st.json(health)
