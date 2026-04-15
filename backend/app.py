from __future__ import annotations

import sqlite3
import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Cloudburst Risk Prediction API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DISTRICT_LOOKUP_CANDIDATES = [
    BASE_DIR / "data" / "processed" / "himalaya_district_lookup.csv",
    BASE_DIR / "data" / "processed" / "himalaya_districts_with_chunks.geojson",
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

CHUNK_TO_LATEST_FEATURES = {
    "western": BASE_DIR / "data" / "processed" / "latest_features_western.csv",
    "central": BASE_DIR / "data" / "processed" / "latest_features_central.csv",
    "eastern": BASE_DIR / "data" / "processed" / "latest_features_eastern.csv",
}

DB_PATH = BASE_DIR / "data" / "app_users.db"
RESULTS_DIR = BASE_DIR / "results"
HISTORIC_EVENTS_PATH = BASE_DIR / "data" / "historic_events.csv"


class DistrictRequest(BaseModel):
    district: str = Field(..., min_length=2)


class UserDistrictSelection(BaseModel):
    user_id: str = Field(..., min_length=8)
    district: str = Field(..., min_length=2)


def _zone_name_from_chunk(chunk: str) -> str:
    chunk_norm = chunk.strip().lower()
    if chunk_norm == "western":
        return "Western"
    if chunk_norm == "central":
        return "Central"
    return "Eastern"


def _risk_tier_from_alert(alert_tier: str) -> str:
    tier = alert_tier.strip().upper()
    if tier in {"LOW", "GREEN"}:
        return "LOW"
    if tier in {"YELLOW", "MODERATE"}:
        return "MODERATE"
    return "HIGH"


def _tier_from_score(score_100: float) -> tuple[str, str]:
    if score_100 < 40:
        return ("LOW", "GREEN")
    if score_100 < 60:
        return ("YELLOW", "YELLOW")
    if score_100 < 80:
        return ("ORANGE", "ORANGE")
    return ("RED", "RED")


def _pick_district_lookup() -> Path | None:
    for path in DISTRICT_LOOKUP_CANDIDATES:
        if path.exists():
            return path
    return None


def _load_districts() -> tuple[pd.DataFrame, str | None]:
    lookup_path = _pick_district_lookup()
    if lookup_path is None:
        return pd.DataFrame(columns=["district_id", "district", "state", "chunk", "centroid_lat", "centroid_lon"]), None

    if lookup_path.suffix.lower() == ".csv":
        frame = pd.read_csv(lookup_path)
        rename_map = {}
        if "district_name" in frame.columns:
            rename_map["district_name"] = "district"
        if "shapeName" in frame.columns:
            rename_map["shapeName"] = "district"
        if "district_id" not in frame.columns and "shapeID" in frame.columns:
            rename_map["shapeID"] = "district_id"
        frame = frame.rename(columns=rename_map)
    else:
        with lookup_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        rows: list[dict] = []
        for feature in payload.get("features", []):
            props = feature.get("properties", {}) or {}
            rows.append(
                {
                    "district_id": props.get("shapeID"),
                    "district": props.get("shapeName"),
                    "state": props.get("state", "Unknown"),
                    "chunk": props.get("chunk"),
                    "centroid_lat": props.get("centroid_lat"),
                    "centroid_lon": props.get("centroid_lon"),
                }
            )
        frame = pd.DataFrame(rows)

    if "district" not in frame.columns:
        raise ValueError(f"{lookup_path.name} must include a district or district_name column.")
    if "chunk" not in frame.columns:
        raise ValueError(f"{lookup_path.name} must include a chunk column.")
    if "centroid_lat" not in frame.columns or "centroid_lon" not in frame.columns:
        raise ValueError(f"{lookup_path.name} must include centroid_lat and centroid_lon columns.")

    if "district_id" not in frame.columns:
        frame["district_id"] = frame["district"]
    if "state" not in frame.columns:
        frame["state"] = "Unknown"

    frame = frame.copy()
    frame["district"] = frame["district"].astype(str)
    frame["state"] = frame["state"].fillna("Unknown").astype(str)
    frame["chunk"] = frame["chunk"].astype(str)
    frame["centroid_lat"] = pd.to_numeric(frame["centroid_lat"], errors="coerce")
    frame["centroid_lon"] = pd.to_numeric(frame["centroid_lon"], errors="coerce")
    frame = frame.dropna(subset=["district", "chunk", "centroid_lat", "centroid_lon"]).reset_index(drop=True)
    return frame[["district_id", "district", "state", "chunk", "centroid_lat", "centroid_lon"]], str(lookup_path)


def _load_lead_time() -> dict:
    path = RESULTS_DIR / "lead_time_analysis.csv"
    if not path.exists():
        return {"estimated_hours": None, "yellow_hr": None, "orange_hr": None, "red_hr": None}
    df = pd.read_csv(path)
    yellow = float(df["lead_YELLOW_hr"].median()) if "lead_YELLOW_hr" in df else None
    orange = float(df["lead_ORANGE_hr"].median()) if "lead_ORANGE_hr" in df else None
    red = float(df["lead_RED_hr"].median()) if "lead_RED_hr" in df else None
    estimated = orange if orange is not None else (yellow if yellow is not None else red)
    return {"estimated_hours": estimated, "yellow_hr": yellow, "orange_hr": orange, "red_hr": red}


def _ensure_user_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                district TEXT NOT NULL,
                state TEXT,
                chunk TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _save_user_district(user_id: str, district: str, state: str, chunk: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, district, state, chunk, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                district=excluded.district,
                state=excluded.state,
                chunk=excluded.chunk,
                updated_at=excluded.updated_at
            """,
            (user_id, district, state, chunk, pd.Timestamp.utcnow().isoformat()),
        )
        conn.commit()


def _get_user_district(user_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT user_id, district, state, chunk, updated_at FROM user_preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "user_id": row[0],
        "district": row[1],
        "state": row[2],
        "chunk": row[3],
        "updated_at": row[4],
    }


DISTRICTS_DF, DISTRICT_LOOKUP_USED = _load_districts()
LEAD = _load_lead_time()
_ensure_user_db()


def _district_search(query: str) -> pd.DataFrame:
    q = query.strip().lower()
    exact = DISTRICTS_DF[DISTRICTS_DF["district"].str.lower() == q]
    if not exact.empty:
        return exact
    return DISTRICTS_DF[DISTRICTS_DF["district"].str.lower().str.contains(q, regex=False)]


@lru_cache(maxsize=3)
def _load_model_bundle(chunk: str) -> dict:
    model_path = CHUNK_TO_MODEL.get(chunk)
    if model_path is None or not model_path.exists():
        raise FileNotFoundError(f"Missing model for chunk '{chunk}'.")
    return joblib.load(model_path)


@lru_cache(maxsize=3)
def _load_chunk_latest_features(chunk: str) -> pd.DataFrame:
    path = CHUNK_TO_LATEST_FEATURES.get(chunk)
    if path is None or not path.exists():
        raise FileNotFoundError(
            f"Missing precomputed latest features for chunk '{chunk}'. "
            "Run the offline pipeline to generate latest_features_<chunk>.csv."
        )
    df = pd.read_csv(path)
    if "district" not in df.columns and "district_name" in df.columns:
        df = df.rename(columns={"district_name": "district"})
    if "district" not in df.columns:
        raise ValueError(f"{path.name} must include a 'district' or 'district_name' column.")
    return df


def load_latest_features(district: str) -> tuple[pd.Series, pd.DataFrame, dict]:
    if DISTRICTS_DF.empty:
        raise HTTPException(status_code=404, detail="District lookup table is not loaded.")

    matches = _district_search(district)
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"District '{district}' not found.")

    district_row = matches.iloc[0]
    resolved_district = str(district_row["district"])
    state = str(district_row["state"])
    chunk = str(district_row["chunk"])
    lat = float(district_row["centroid_lat"])
    lon = float(district_row["centroid_lon"])

    try:
        latest_df = _load_chunk_latest_features(chunk)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    district_latest = latest_df[latest_df["district"].astype(str).str.lower() == resolved_district.lower()]
    if district_latest.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No latest precomputed features found for district '{resolved_district}' in chunk '{chunk}'. "
                "Run the offline pipeline and regenerate latest features."
            ),
        )

    if "feature_time" in district_latest.columns:
        district_latest = district_latest.copy()
        district_latest["_sort_time"] = pd.to_datetime(district_latest["feature_time"], errors="coerce")
        district_latest = district_latest.sort_values("_sort_time").drop(columns="_sort_time")
    elif "time" in district_latest.columns:
        district_latest = district_latest.copy()
        district_latest["_sort_time"] = pd.to_datetime(district_latest["time"], errors="coerce")
        district_latest = district_latest.sort_values("_sort_time").drop(columns="_sort_time")

    row = district_latest.iloc[-1]
    metadata = {
        "district": resolved_district,
        "state": state,
        "chunk": chunk,
        "lat": lat,
        "lon": lon,
    }
    return row, district_latest.reset_index(drop=True), metadata


def _safe_float(row: pd.Series, key: str, default: float = 0.0) -> float:
    value = row.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _compute_contributions(row: pd.Series) -> dict[str, float]:
    moisture = abs(_safe_float(row, "tcwv_3h", _safe_float(row, "tcwv", 0.0)))
    pressure = abs(_safe_float(row, "sp_drop_3h", 0.0))
    rainfall = abs(_safe_float(row, "rain_3h", _safe_float(row, "rain_mm", 0.0)))
    wind = abs(_safe_float(row, "wind_speed", 0.0))
    values = {
        "Moisture content": moisture,
        "Pressure anomaly": pressure,
        "Rain intensity spike": rainfall,
        "Wind convergence": wind,
    }
    total = sum(values.values()) or 1.0
    return {k: round(v * 100.0 / total, 1) for k, v in values.items()}


def _layman_explanation(score_100: float, row: pd.Series, lead_text: str) -> str:
    high_moisture = _safe_float(row, "tcwv_3h", 0.0) > _safe_float(row, "tcwv", 0.0)
    pressure_drop = _safe_float(row, "sp_drop_3h", 0.0) < 0
    rain_increase = _safe_float(row, "rain_3h", 0.0) > _safe_float(row, "rain_mm", 0.0)

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


def _build_visualization(history: pd.DataFrame) -> tuple[dict, list[dict]]:
    timestamps: list[str] = []
    rain_trend: list[float] = []
    moisture_trend: list[float] = []
    pressure_drop_trend: list[float] = []
    wind_trend: list[float] = []
    timeline: list[dict] = []

    for _, row in history.iterrows():
        timestamp = str(row.get("feature_time", row.get("time", pd.Timestamp.utcnow().isoformat())))
        rain = round(_safe_float(row, "rain_mm", 0.0), 4)
        moisture = round(_safe_float(row, "tcwv_3h", _safe_float(row, "tcwv", 0.0)), 4)
        pressure_drop = round(_safe_float(row, "sp_drop_3h", 0.0), 4)
        wind = round(_safe_float(row, "wind_speed", 0.0), 4)

        timestamps.append(timestamp)
        rain_trend.append(rain)
        moisture_trend.append(moisture)
        pressure_drop_trend.append(pressure_drop)
        wind_trend.append(wind)
        timeline.append(
            {
                "timestamp": timestamp,
                "rainfall": rain,
                "moisture": moisture,
                "pressure_drop": pressure_drop,
                "wind": wind,
            }
        )

    visualization = {
        "timestamps": timestamps,
        "rain_trend": rain_trend,
        "moisture_trend": moisture_trend,
        "pressure_drop_trend": pressure_drop_trend,
        "wind_convergence_trend": wind_trend,
    }
    return visualization, timeline


def _results_csv(name: str) -> Path:
    return RESULTS_DIR / name


def _clean_json_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    return value


def _frame_records(df: pd.DataFrame) -> list[dict]:
    records: list[dict] = []
    for row in df.to_dict(orient="records"):
        records.append({str(key): _clean_json_value(value) for key, value in row.items()})
    return records


def _load_result_records(file_name: str) -> list[dict]:
    path = _results_csv(file_name)
    if not path.exists():
        return []
    return _frame_records(pd.read_csv(path))


def _load_historic_events() -> pd.DataFrame:
    if not HISTORIC_EVENTS_PATH.exists():
        return pd.DataFrame(columns=["event_id", "date", "location", "district", "state", "severity"])

    frame = pd.read_csv(HISTORIC_EVENTS_PATH)
    rename_map = {
        "Date": "date",
        "Location": "location",
        "District": "district",
        "State": "state",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Time": "time",
        "Deaths": "deaths",
        "Injured": "injured",
        "Missing": "missing",
        "Description": "description",
        "Season": "season",
        "Severity": "severity",
        "Region": "region",
        "Elevation_Zone": "elevation_zone",
    }
    frame = frame.rename(columns=rename_map).copy()
    frame.insert(0, "event_id", range(1, len(frame) + 1))
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce", dayfirst=True)
    return frame


def _load_replay_events() -> pd.DataFrame:
    path = _results_csv("lead_time_analysis.csv")
    if not path.exists():
        return pd.DataFrame(columns=["event_id", "event_date", "location", "state", "severity"])

    frame = pd.read_csv(path).copy()
    frame.insert(0, "event_id", range(1, len(frame) + 1))
    if "event_date" in frame.columns:
        frame["event_date"] = pd.to_datetime(frame["event_date"], errors="coerce")
    return frame


def _predict_for_district(district: str) -> dict:
    row, history, metadata = load_latest_features(district)
    chunk = metadata["chunk"]

    try:
        model_bundle = _load_model_bundle(chunk)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    missing_features = [f for f in FEATURES if f not in row.index]
    if missing_features:
        raise HTTPException(
            status_code=503,
            detail=(
                "Latest feature file is missing required inference columns: "
                + ", ".join(missing_features)
            ),
        )

    x = pd.DataFrame([{f: _safe_float(row, f) for f in FEATURES}])
    rf_model = model_bundle["rf_model"]
    xgb_model = model_bundle["xgb_model"]

    rf_prob = float(rf_model.predict_proba(x)[:, 1][0])
    xgb_prob = float(xgb_model.predict_proba(x)[:, 1][0])
    ensemble_prob = 0.5 * rf_prob + 0.5 * xgb_prob

    score_100 = round(ensemble_prob * 100.0, 2)
    risk_level, alert_tier = _tier_from_score(score_100)
    risk_tier = _risk_tier_from_alert(alert_tier)
    zone = _zone_name_from_chunk(chunk)

    confidence = float(max(0.0, min(1.0, 1.0 - abs(rf_prob - xgb_prob))))
    lead_text = "Offline batch features were refreshed from the latest 10-day atmospheric window."
    lead_hours = LEAD["estimated_hours"]

    contributions = _compute_contributions(row)
    explanation = _layman_explanation(score_100, row, lead_text)
    visualization, timeline = _build_visualization(history)

    rainfall_spike = bool(_safe_float(row, "rain_3h", 0.0) > 1.25 * max(0.1, _safe_float(row, "rain_mm", 0.0)))
    moisture_surge = bool(_safe_float(row, "tcwv_3h", 0.0) > _safe_float(row, "tcwv", 0.0))
    cape_high = bool(_safe_float(row, "tcwv_6h", 0.0) > _safe_float(row, "tcwv", 0.0))

    insights: list[str] = []
    if rainfall_spike:
        insights.append("Recent rainfall accumulation is elevated relative to baseline.")
    if moisture_surge:
        insights.append("Atmospheric moisture is above district baseline.")
    if cape_high:
        insights.append("Convective instability proxy remains elevated.")
    if not insights:
        insights.append("No strong precursor surge is currently detected; continue routine monitoring.")

    return {
        "district": metadata["district"],
        "zone": zone,
        "risk_tier": risk_tier,
        "probability": round(ensemble_prob, 4),
        "confidence": round(confidence, 4),
        "last_updated": pd.Timestamp.utcnow().isoformat(),
        "timeline": timeline,
        "precursors": {
            "rainfall_spike": rainfall_spike,
            "moisture_surge": moisture_surge,
            "cape_high": cape_high,
        },
        "insights": insights,
        "input": {"district": district},
        "resolved_location": {
            "district": metadata["district"],
            "state": metadata["state"],
            "chunk": chunk,
            "lat": metadata["lat"],
            "lon": metadata["lon"],
        },
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


@app.get("/health")
def health() -> dict:
    latest_features_status = {}
    for chunk, path in CHUNK_TO_LATEST_FEATURES.items():
        latest_features_status[chunk] = {
            "path": str(path.relative_to(BASE_DIR)),
            "exists": path.exists(),
        }

    models_loaded = [chunk for chunk, path in CHUNK_TO_MODEL.items() if path.exists()]
    district_attributes_present = bool(
        {"district", "state", "chunk", "centroid_lat", "centroid_lon"}.issubset(DISTRICTS_DF.columns)
    )

    return {
        "status": "ok",
        "mode": "online_inference_only",
        "district_lookup_used": DISTRICT_LOOKUP_USED,
        "shapefile_used": DISTRICT_LOOKUP_USED,
        "district_rows": int(len(DISTRICTS_DF)),
        "models_available": {chunk: path.exists() for chunk, path in CHUNK_TO_MODEL.items()},
        "models_loaded": models_loaded,
        "latest_features_available": latest_features_status,
        "district_attributes_present": district_attributes_present,
    }


@app.get("/districts")
def list_districts(q: str | None = None, limit: int = 300) -> dict:
    if DISTRICTS_DF.empty:
        return {"districts": []}
    frame = DISTRICTS_DF
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


@app.get("/user-profile")
def get_user_profile(user_id: str) -> dict:
    if not user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    profile = _get_user_district(user_id.strip())
    if profile is None:
        return {"user_id": user_id.strip(), "preferred_district": None}
    return {
        "user_id": profile["user_id"],
        "preferred_district": {
            "district": profile["district"],
            "state": profile["state"],
            "chunk": profile["chunk"],
            "updated_at": profile["updated_at"],
        },
    }


@app.post("/user-profile/select-district")
def select_user_district(payload: UserDistrictSelection) -> dict:
    if DISTRICTS_DF.empty:
        raise HTTPException(status_code=404, detail="District lookup table is not loaded.")

    matches = _district_search(payload.district)
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"District '{payload.district}' not found.")

    district_row = matches.iloc[0]
    district = str(district_row["district"])
    state = str(district_row["state"])
    chunk = str(district_row["chunk"])
    _save_user_district(payload.user_id.strip(), district, state, chunk)
    return {
        "user_id": payload.user_id.strip(),
        "selected": {
            "district": district,
            "state": state,
            "chunk": chunk,
        },
    }


@app.get("/predict")
def predict(district: str | None = None, user_id: str | None = None) -> dict:
    selected_district = district.strip() if district else ""
    selected_user = user_id.strip() if user_id else ""

    if not selected_district and selected_user:
        profile = _get_user_district(selected_user)
        if profile is None:
            raise HTTPException(status_code=404, detail="No saved district found for this user_id.")
        selected_district = str(profile["district"])

    if not selected_district:
        raise HTTPException(status_code=400, detail="Provide district or user_id with saved district.")

    result = _predict_for_district(selected_district)
    if selected_user:
        resolved = result.get("resolved_location", {})
        _save_user_district(
            selected_user,
            str(resolved.get("district", selected_district)),
            str(resolved.get("state", "Unknown")),
            str(resolved.get("chunk", "")),
        )
    return result


@app.post("/predict-district")
def predict_district(payload: DistrictRequest) -> dict:
    return _predict_for_district(payload.district)


@app.post("/inference/district")
def inference_district(payload: DistrictRequest) -> dict:
    return _predict_for_district(payload.district)


@app.post("/predict-location")
def predict_location(payload: dict) -> dict:
    lat_value = payload.get("latitude", payload.get("lat"))
    lon_value = payload.get("longitude", payload.get("lon"))
    if lat_value is None or lon_value is None:
        raise HTTPException(status_code=400, detail="latitude/lat and longitude/lon are required")

    if DISTRICTS_DF.empty:
        raise HTTPException(status_code=404, detail="District lookup table is not loaded.")

    lat = float(lat_value)
    lon = float(lon_value)
    deltas = (DISTRICTS_DF["centroid_lat"] - lat) ** 2 + (DISTRICTS_DF["centroid_lon"] - lon) ** 2
    idx = int(deltas.argmin())
    district_name = str(DISTRICTS_DF.iloc[idx]["district"])

    return _predict_for_district(district_name)


@app.get("/model-insights")
@app.get("/insights/model")
def model_insights(detailed: bool = False) -> dict:
    models = _load_result_records("model_performance.csv")
    chunk_metrics = _load_result_records("chunk_ensemble_performance.csv")
    probability_samples = _load_result_records("risk_probabilities.csv")

    payload = {
        "models": models,
        "zone_metrics": chunk_metrics,
        "probability_samples": probability_samples if detailed else probability_samples[:200],
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    return payload


@app.get("/historical-events")
@app.get("/events/historical")
def historical_events(
    district: str = "",
    state: str = "",
    severity: str = "",
    limit: int = 200,
) -> dict:
    frame = _load_historic_events()
    if district.strip():
        frame = frame[frame["district"].astype(str).str.contains(district.strip(), case=False, na=False)]
    if state.strip():
        frame = frame[frame["state"].astype(str).str.contains(state.strip(), case=False, na=False)]
    if severity.strip():
        frame = frame[frame["severity"].astype(str).str.lower() == severity.strip().lower()]

    if "date" in frame.columns:
        frame = frame.sort_values("date", ascending=False, na_position="last")

    return {"events": _frame_records(frame.head(max(1, min(limit, 1000))))}


@app.get("/historical-events/replay")
@app.get("/events/replay")
def replay_event(event_id: int) -> dict:
    events = _load_replay_events()
    if events.empty:
        raise HTTPException(status_code=404, detail="No replayable historical events available.")

    match = events[events["event_id"] == event_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Historical event {event_id} not found.")

    row = match.iloc[0]
    location = str(row.get("location", "")).strip()
    replay_payload = {str(key): _clean_json_value(value) for key, value in row.items()}

    district_name = location.split("(")[0].strip()
    prediction = None
    if district_name:
        try:
            prediction = _predict_for_district(district_name)
        except HTTPException:
            prediction = None

    return {
        "event": replay_payload,
        "resolved_district": district_name or None,
        "prediction": prediction,
        "message": (
            "Replay uses the archived event registry plus the closest district prediction available in the current "
            "online inference dataset."
        ),
    }


@app.post("/pipeline")
@app.post("/pipeline/run")
def pipeline_run(payload: dict) -> dict:
    district = str(payload.get("district", "")).strip()
    if not district:
        raise HTTPException(status_code=400, detail="district is required")

    result = _predict_for_district(district)
    response = {
        "mode": "online_inference_only",
        "requested_refresh": bool(payload.get("force_refresh", False)),
        "message": (
            "Offline pipeline execution is not exposed from the hosted API. "
            "This compatibility route returns the latest precomputed district inference."
        ),
    }
    response.update(result)
    return response
