from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
CHUNK_INPUTS = {
    "western": ROOT / "data" / "processed" / "labeled_cloudburst_district_western.csv",
    "central": ROOT / "data" / "processed" / "labeled_cloudburst_district_central.csv",
    "eastern": ROOT / "data" / "processed" / "labeled_cloudburst_district_eastern.csv",
}
LOOKUP_PATH = ROOT / "data" / "processed" / "himalaya_district_lookup.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build compact latest feature tables per chunk.")
    parser.add_argument("--days", type=int, default=10)
    parser.add_argument("--output_dir", default="data/processed")
    return parser.parse_args()


def _district_col(df: pd.DataFrame) -> str:
    for col in ("district_name", "district"):
        if col in df.columns:
            return col
    raise ValueError("Input dataset must contain 'district_name' or 'district' column")


def _district_lookup_by_chunk() -> dict[str, list[str]]:
    if not LOOKUP_PATH.exists():
        return {}
    lookup = pd.read_csv(LOOKUP_PATH)
    if "chunk" not in lookup.columns or "district_name" not in lookup.columns:
        return {}
    output: dict[str, list[str]] = {}
    for chunk, group in lookup.groupby("chunk", sort=False):
        output[str(chunk)] = sorted(group["district_name"].dropna().astype(str).unique().tolist())
    return output


def _compute_summary(group: pd.DataFrame, district_col: str, chunk: str, days: int) -> dict:
    g = group.sort_values("time")
    latest = g.iloc[-1]
    last_time = pd.to_datetime(latest["time"])
    window = g[g["time"] >= (last_time - pd.Timedelta(days=days))].copy()

    rain_mean_10d = float(window.get("rain_mm", pd.Series([0.0])).mean())
    rain_total_10d = float(window.get("rain_mm", pd.Series([0.0])).sum())

    row = {
        "district": str(latest[district_col]),
        "chunk": chunk,
        "feature_time": last_time.isoformat(),
        "rain_mean_10d": rain_mean_10d,
        "rain_total_10d": rain_total_10d,
    }

    for col in ["t2m", "u10", "v10", "sp", "tcwv", "wind_speed", "tcwv_3h", "tcwv_6h", "sp_drop_3h", "t2m_grad", "rain_mm", "rain_3h"]:
        row[col] = float(latest[col]) if col in latest and pd.notna(latest[col]) else 0.0

    return row


def _compute_recent_rows(group: pd.DataFrame, district_col: str, chunk: str, days: int) -> list[dict]:
    g = group.sort_values("time").copy()
    latest = g.iloc[-1]
    last_time = pd.to_datetime(latest["time"])
    window = g[g["time"] >= (last_time - pd.Timedelta(days=days))].copy()
    if window.empty:
        return []

    rain_series = pd.to_numeric(window.get("rain_mm", pd.Series(index=window.index, dtype=float)), errors="coerce").fillna(0.0)
    window["rain_mean_10d"] = float(rain_series.mean())
    window["rain_total_10d"] = float(rain_series.sum())
    window["district"] = str(latest[district_col])
    window["chunk"] = chunk
    window["feature_time"] = pd.to_datetime(window["time"]).dt.strftime("%Y-%m-%dT%H:%M:%S")

    output_cols = [
        "district",
        "chunk",
        "feature_time",
        "time",
        "rain_mean_10d",
        "rain_total_10d",
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
        "rain_mm",
        "rain_3h",
    ]
    for col in output_cols:
        if col not in window.columns:
            window[col] = 0.0

    return window[output_cols].to_dict(orient="records")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    district_lookup = _district_lookup_by_chunk()

    for chunk, input_path in CHUNK_INPUTS.items():
        if not input_path.exists():
            raise FileNotFoundError(f"Missing chunk source dataset: {input_path}")

        df = pd.read_csv(input_path, parse_dates=["time"])
        rows: list[dict] = []
        try:
            district_col = _district_col(df)
            rows = [
                row
                for _, group in df.groupby(district_col, sort=False)
                if not group.empty
                for row in _compute_recent_rows(group, district_col, chunk, args.days)
            ]
        except ValueError:
            if df.empty:
                raise
            if chunk not in district_lookup or not district_lookup[chunk]:
                raise
            recent_rows = _compute_recent_rows(df, "time", chunk, args.days)
            rows = [
                {
                    **row,
                    "district": district_name,
                }
                for district_name in district_lookup[chunk]
                for row in recent_rows
            ]

        latest_df = pd.DataFrame(rows).sort_values(["district", "feature_time"]).reset_index(drop=True)
        out_path = output_dir / f"latest_features_{chunk}.csv"
        latest_df.to_csv(out_path, index=False)
        print(f"Saved {out_path} ({len(latest_df)} rows)")


if __name__ == "__main__":
    main()
