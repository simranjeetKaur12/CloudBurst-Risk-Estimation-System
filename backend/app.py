from __future__ import annotations

import os
from pathlib import Path

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shapely.geometry import Point

try:
    from src.common.himalaya_chunks import assign_chunk
except ModuleNotFoundError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from src.common.himalaya_chunks import assign_chunk

app = FastAPI(title="Cloudburst Risk Prediction API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
SHAPEFILE_CANDIDATES = [
    BASE_DIR / "data" / "shapefiles" / "india_districts.shp",
    BASE_DIR / "data" / "shapefiles" / "geoBoundaries-IND-ADM2.shp",
]

FEATURES = [
    "t2m",
    "u10",
    "v10",
    "sp",
    "tcwv",
    "wind_speed",
    "tcwv_3h",
    "tcwv_6h",
    "sp_drop_3h",
    "t2m_grad",
]

CHUNK_TO_MODEL = {
    "western": BASE_DIR / "models" / "western_model.pkl",
    "central": BASE_DIR / "models" / "central_model.pkl",
    "eastern": BASE_DIR / "models" / "eastern_model.pkl",
}
CHUNK_TO_TIMESERIES = {
    "western": BASE_DIR / "data" / "processed" / "labeled_cloudburst_district_western.csv",
    "central": BASE_DIR / "data" / "processed" / "labeled_cloudburst_district_central.csv",
    "eastern": BASE_DIR / "data" / "processed" / "labeled_cloudburst_district_eastern.csv",
}


class DistrictRequest(BaseModel):
    district: str = Field(..., min_length=2)


def _tier_from_score(score_100: float) -> tuple[str, str]:
    if score_100 < 40:
        return ("LOW", "GREEN")
    if score_100 < 60:
        return ("YELLOW", "YELLOW")
    if score_100 < 80:
        return ("ORANGE", "ORANGE")
    return ("RED", "RED")


def _pick_shapefile() -> Path | None:
    for path in SHAPEFILE_CANDIDATES:
        if path.exists():
            return path
    return None


def _load_districts() -> tuple[gpd.GeoDataFrame, bool, str | None]:
    shp_path = _pick_shapefile()
    if shp_path is None:
        return gpd.GeoDataFrame(columns=["district", "state", "geometry"], geometry="geometry", crs="EPSG:4326"), False, None

    os.environ["SHAPE_RESTORE_SHX"] = "YES"
    gdf = gpd.read_file(shp_path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    cols_lower = {c.lower(): c for c in gdf.columns}
    district_col = None
    state_col = None
    for candidate in ["district", "district_n", "dist_name", "name", "dtname", "shapename"]:
        if candidate in cols_lower:
            district_col = cols_lower[candidate]
            break
    for candidate in ["state", "state_name", "st_nm", "stname", "province", "adm1_name"]:
        if candidate in cols_lower:
            state_col = cols_lower[candidate]
            break

    has_attrs = district_col is not None and state_col is not None
    gdf["district"] = gdf[district_col].astype(str) if district_col else [f"District_{i}" for i in range(len(gdf))]
    gdf["state"] = gdf[state_col].astype(str) if state_col else "Unknown"

    centroids = gdf.to_crs("EPSG:3857").geometry.centroid.to_crs("EPSG:4326")
    gdf["centroid_lat"] = centroids.y
    gdf["centroid_lon"] = centroids.x
    gdf["chunk"] = [assign_chunk(lat, lon) for lat, lon in zip(gdf["centroid_lat"], gdf["centroid_lon"])]
    gdf = gdf[gdf["chunk"].notna()].copy()
    return gdf[["district", "state", "chunk", "centroid_lat", "centroid_lon", "geometry"]].reset_index(drop=True), has_attrs, str(shp_path)


def _load_models() -> dict[str, dict]:
    output = {}
    for chunk, path in CHUNK_TO_MODEL.items():
        if path.exists():
            output[chunk] = joblib.load(path)
    return output


def _load_lead_time() -> dict:
    path = BASE_DIR / "results" / "lead_time_analysis.csv"
    if not path.exists():
        return {"estimated_hours": None, "yellow_hr": None, "orange_hr": None, "red_hr": None}
    df = pd.read_csv(path)
    yellow = float(df["lead_YELLOW_hr"].median()) if "lead_YELLOW_hr" in df else None
    orange = float(df["lead_ORANGE_hr"].median()) if "lead_ORANGE_hr" in df else None
    red = float(df["lead_RED_hr"].median()) if "lead_RED_hr" in df else None
    estimated = orange if orange is not None else (yellow if yellow is not None else red)
    return {"estimated_hours": estimated, "yellow_hr": yellow, "orange_hr": orange, "red_hr": red}


DISTRICTS_GDF, HAS_DISTRICT_ATTRS, SHAPEFILE_USED = _load_districts()
MODELS = _load_models()
LEAD = _load_lead_time()


def _district_search(query: str) -> pd.DataFrame:
    q = query.strip().lower()
    exact = DISTRICTS_GDF[DISTRICTS_GDF["district"].str.lower() == q]
    if not exact.empty:
        return exact
    return DISTRICTS_GDF[DISTRICTS_GDF["district"].str.lower().str.contains(q, regex=False)]


def _load_chunk_ts(chunk: str) -> pd.DataFrame:
    path = CHUNK_TO_TIMESERIES.get(chunk)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail=f"Missing time-series file for chunk '{chunk}'.")
    return pd.read_csv(path, parse_dates=["time"]).sort_values("time")


def _district_row_for_prediction(district: str, chunk: str) -> tuple[pd.Series, pd.DataFrame]:
    df = _load_chunk_ts(chunk)
    if "district_name" in df.columns:
        local = df[df["district_name"].astype(str).str.lower() == district.lower()].copy()
    else:
        local = df.copy()
    if local.empty:
        local = df.copy()
    local = local.sort_values("time")
    return local.iloc[-1], local


def _compute_contributions(row: pd.Series) -> dict[str, float]:
    moisture = abs(float(row.get("tcwv_3h", 0.0)))
    pressure = abs(float(row.get("sp_drop_3h", 0.0)))
    rainfall = abs(float(row.get("rain_3h", row.get("rain_mm", 0.0))))
    wind = abs(float(row.get("wind_speed", 0.0)))
    values = {
        "Moisture content": moisture,
        "Pressure anomaly": pressure,
        "Rain intensity spike": rainfall,
        "Wind convergence": wind,
    }
    total = sum(values.values()) or 1.0
    return {k: round(v * 100.0 / total, 1) for k, v in values.items()}


def _lead_time_text(df_last10d: pd.DataFrame) -> tuple[float | None, str]:
    if len(df_last10d) < 6:
        return LEAD["estimated_hours"], "Insufficient recent observations; using historical median lead-time."

    def _slope(series: pd.Series) -> float:
        y = series.astype(float).to_numpy()
        x = np.arange(len(y), dtype=float)
        if np.allclose(y.std(), 0):
            return 0.0
        m = np.polyfit(x, y, 1)[0]
        return float(m)

    moisture_rate = _slope(df_last10d.get("tcwv_3h", pd.Series([0] * len(df_last10d))))
    pressure_rate = _slope(df_last10d.get("sp_drop_3h", pd.Series([0] * len(df_last10d))))
    rain_rate = _slope(df_last10d.get("rain_mm", pd.Series([0] * len(df_last10d))))

    if moisture_rate > 0.05 and pressure_rate < -0.1 and rain_rate > 0.01:
        return 12.0, "Current atmospheric buildup suggests elevated risk within 12-24 hours."
    if moisture_rate > 0.02 and rain_rate > 0.005:
        return 24.0, "Developing instability suggests possible escalation in 24-36 hours."
    return LEAD["estimated_hours"], "Current trend does not show rapid escalation; continue routine monitoring."


def _layman_explanation(score_100: float, row: pd.Series, lead_text: str) -> str:
    high_moisture = float(row.get("tcwv_3h", 0.0)) > float(row.get("tcwv", 0.0))
    pressure_drop = float(row.get("sp_drop_3h", 0.0)) < 0
    rain_increase = float(row.get("rain_3h", row.get("rain_mm", 0.0))) > float(row.get("rain_mm", 0.0))

    if score_100 >= 60 and high_moisture and pressure_drop and rain_increase:
        return (
            "The atmosphere over this district is currently holding unusually high moisture levels, "
            "combined with falling pressure and increasing rainfall intensity. "
            "These conditions are similar to patterns observed before past cloudburst events. "
            f"{lead_text}"
        )
    return (
        "Current atmospheric conditions are relatively stable. No strong combined signal of abnormal "
        "moisture buildup, pressure disturbance, and rainfall surge is detected right now. "
        f"{lead_text}"
    )


def _run_recent_pipeline_stub(chunk: str, district: str) -> dict:
    # Placeholder for live ERA5/IMERG fetch and transformation of the last 10 days.
    # The API still uses the latest available processed chunk time-series row.
    return {
        "status": "used_cached_processed_data",
        "note": f"Live 10-day fetch for {district} ({chunk}) is not executed in API request path.",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "shapefile_used": SHAPEFILE_USED,
        "district_rows": int(len(DISTRICTS_GDF)),
        "district_attributes_present": HAS_DISTRICT_ATTRS,
        "models_loaded": sorted(MODELS.keys()),
    }


@app.get("/districts")
def list_districts(q: str | None = None, limit: int = 300) -> dict:
    if DISTRICTS_GDF.empty:
        return {"districts": []}
    frame = DISTRICTS_GDF
    if q:
        frame = _district_search(q)
    frame = frame.sort_values("district").head(max(1, min(limit, 1000)))
    return {
        "districts": [
            {
                "district": str(r["district"]),
                "state": str(r["state"]),
                "chunk": str(r["chunk"]),
            }
            for _, r in frame.iterrows()
        ]
    }


@app.post("/predict-district")
def predict_district(payload: DistrictRequest) -> dict:
    if DISTRICTS_GDF.empty:
        raise HTTPException(status_code=404, detail="District shapefile is not loaded.")

    matches = _district_search(payload.district)
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"District '{payload.district}' not found.")

    district_row = matches.iloc[0]
    district = str(district_row["district"])
    state = str(district_row["state"])
    chunk = str(district_row["chunk"])
    lat = float(district_row["centroid_lat"])
    lon = float(district_row["centroid_lon"])

    if chunk not in MODELS:
        raise HTTPException(status_code=404, detail=f"Missing model models/{chunk}_model.pkl.")

    pipeline_status = _run_recent_pipeline_stub(chunk, district)
    latest_row, district_df = _district_row_for_prediction(district, chunk)
    district_last10d = district_df[district_df["time"] >= (district_df["time"].max() - pd.Timedelta(days=10))]

    model_bundle = MODELS[chunk]
    rf_model = model_bundle["rf_model"]
    xgb_model = model_bundle["xgb_model"]

    x = pd.DataFrame([{f: float(latest_row[f]) for f in FEATURES}])
    rf_prob = float(rf_model.predict_proba(x)[:, 1][0])
    xgb_prob = float(xgb_model.predict_proba(x)[:, 1][0])
    ensemble_prob = 0.5 * rf_prob + 0.5 * xgb_prob
    score_100 = round(ensemble_prob * 100.0, 2)
    risk_level, alert_tier = _tier_from_score(score_100)

    lead_hours, lead_text = _lead_time_text(district_last10d)
    explanation = _layman_explanation(score_100, latest_row, lead_text)
    contributions = _compute_contributions(latest_row)

    visualization = {
        "timestamps": district_last10d["time"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        "rain_trend": district_last10d.get("rain_mm", pd.Series(dtype=float)).astype(float).fillna(0).round(4).tolist(),
        "moisture_trend": district_last10d.get("tcwv_3h", pd.Series(dtype=float)).astype(float).fillna(0).round(4).tolist(),
        "pressure_drop_trend": district_last10d.get("sp_drop_3h", pd.Series(dtype=float)).astype(float).fillna(0).round(4).tolist(),
        "wind_convergence_trend": district_last10d.get("wind_speed", pd.Series(dtype=float)).astype(float).fillna(0).round(4).tolist(),
    }

    return {
        "input": {"district": payload.district},
        "resolved_location": {"district": district, "state": state, "chunk": chunk, "lat": lat, "lon": lon},
        "pipeline": pipeline_status,
        "risk_score": score_100,
        "risk_score_0_1": round(ensemble_prob, 4),
        "risk_level": risk_level,
        "alert_tier": alert_tier,
        "lead_time_estimate_hours": lead_hours,
        "lead_time_analysis": {
            "estimated_hours": lead_hours,
            "text": lead_text,
            "yellow_hr": LEAD["yellow_hr"],
            "orange_hr": LEAD["orange_hr"],
            "red_hr": LEAD["red_hr"],
        },
        "model_breakdown": {
            "rf_probability": round(rf_prob, 4),
            "xgb_probability": round(xgb_prob, 4),
            "ensemble_probability": round(ensemble_prob, 4),
        },
        "top_contributing_factors": contributions,
        "visualization": visualization,
        "layman_explanation": explanation,
    }


@app.post("/predict-location")
def predict_location(payload: dict) -> dict:
    # Backward-compatible fallback: map lat/lon to district then reuse district flow.
    lat = float(payload.get("latitude", payload.get("lat")))
    lon = float(payload.get("longitude", payload.get("lon")))
    if DISTRICTS_GDF.empty:
        raise HTTPException(status_code=404, detail="District shapefile is not loaded.")
    point = Point(lon, lat)
    hit = DISTRICTS_GDF[DISTRICTS_GDF.geometry.contains(point)]
    if hit.empty:
        cent = DISTRICTS_GDF.geometry.centroid
        idx = int(((cent.x - lon) ** 2 + (cent.y - lat) ** 2).argmin())
        district_name = str(DISTRICTS_GDF.iloc[idx]["district"])
    else:
        district_name = str(hit.iloc[0]["district"])
    return predict_district(DistrictRequest(district=district_name))
