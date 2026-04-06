from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests


API_BASE_URL = os.getenv("CLOUDBURST_API_BASE", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT_SECONDS = int(os.getenv("CLOUDBURST_API_TIMEOUT", "30"))


class ApiError(RuntimeError):
    pass


def _request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
    except requests.RequestException as exc:
        raise ApiError(f"Cannot reach backend at {API_BASE_URL}: {exc}") from exc

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise ApiError(f"API error {response.status_code}: {detail}")

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError("Backend returned non-JSON response.") from exc


def _request_any(method: str, paths: list[str], **kwargs: Any) -> dict[str, Any]:
    last_error: ApiError | None = None
    for path in paths:
        try:
            return _request(method, path, **kwargs)
        except ApiError as exc:
            last_error = exc
    if last_error is None:
        raise ApiError("No API route candidates provided.")
    raise last_error


def get_health() -> dict[str, Any]:
    return _request("GET", "/health")


def list_districts(query: str = "", zone: str | None = None, limit: int = 250) -> list[dict[str, Any]]:
    params = {"limit": limit}
    if query:
        params["q"] = query
    if zone:
        params["zone"] = zone
    payload = _request("GET", "/districts", params=params)
    return payload.get("districts", [])


def run_pipeline(district: str, force_refresh: bool = False) -> dict[str, Any]:
    return _request_any(
        "POST",
        ["/pipeline/run", "/pipeline"],
        json={"district": district, "force_refresh": force_refresh},
    )


def infer_district(district: str, force_refresh: bool = False) -> dict[str, Any]:
    return _request_any(
        "POST",
        ["/inference/district", "/predict-district"],
        json={"district": district, "force_refresh": force_refresh},
    )


def model_insights(detailed: bool = False, token: str | None = None) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"} if token else None
    return _request_any(
        "GET",
        ["/model-insights", "/insights/model"],
        params={"detailed": detailed},
        headers=headers,
    )


def historical_events(district: str = "", state: str = "", severity: str = "", limit: int = 200) -> list[dict[str, Any]]:
    params = {"limit": limit}
    if district:
        params["district"] = district
    if state:
        params["state"] = state
    if severity:
        params["severity"] = severity
    payload = _request_any("GET", ["/historical-events", "/events/historical"], params=params)
    return payload.get("events", [])


def replay_event(event_id: int) -> dict[str, Any]:
    return _request_any(
        "GET",
        ["/historical-events/replay", "/events/replay"],
        params={"event_id": event_id},
    )


def load_results_csv(file_name: str) -> pd.DataFrame:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "results", file_name)
    if not os.path.exists(path):
        raise ApiError(f"Results file not found: {file_name}")
    return pd.read_csv(path)
