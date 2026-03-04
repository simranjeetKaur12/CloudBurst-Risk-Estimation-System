import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", type=str, default="data/processed/era5_imerg_features_all_regions.csv")
    parser.add_argument("--output_csv", type=str, default="data/processed/alert_signals_all_regions.csv")
    parser.add_argument("--notify_score", type=int, default=70)
    return parser.parse_args()


def _thresholds(group: pd.DataFrame) -> dict[str, float]:
    return {
        "rain_mm": float(group["rain_mm"].quantile(0.90)),
        "rain_3h": float(group["rain_3h"].quantile(0.90)),
        "rain_6h": float(group["rain_6h"].quantile(0.90)),
        "tcwv_3h": float(group["tcwv_3h"].quantile(0.85)),
        "wind_speed": float(group["wind_speed"].quantile(0.85)),
        "sp_drop_3h": float(group["sp_drop_3h"].quantile(0.10)),
        "t2m_grad": float(group["t2m_grad"].abs().quantile(0.90)),
    }


def _layman_explanation(active: list[str], risk_level: str) -> str:
    if not active:
        return "Weather is currently stable with low short-term cloudburst risk."
    reasons = ", ".join(active)
    return (
        f"Current weather shows {reasons}. These signals can increase the chance of intense short-duration rainfall. "
        f"Overall risk is {risk_level}."
    )


def _evaluate_row(row: pd.Series, th: dict[str, float], notify_score: int) -> dict:
    flags = {
        "heavy_recent_rain": row["rain_mm"] >= th["rain_mm"],
        "rain_buildup_3h": row["rain_3h"] >= th["rain_3h"],
        "rain_buildup_6h": row["rain_6h"] >= th["rain_6h"],
        "high_moisture": row["tcwv_3h"] >= th["tcwv_3h"],
        "strong_winds": row["wind_speed"] >= th["wind_speed"],
        "pressure_drop": row["sp_drop_3h"] <= th["sp_drop_3h"],
        "temp_instability": abs(row["t2m_grad"]) >= th["t2m_grad"],
    }

    weights = {
        "heavy_recent_rain": 18,
        "rain_buildup_3h": 20,
        "rain_buildup_6h": 16,
        "high_moisture": 14,
        "strong_winds": 10,
        "pressure_drop": 14,
        "temp_instability": 8,
    }
    score = int(sum(weights[k] for k, v in flags.items() if v))

    if score >= 80:
        risk_level = "SEVERE"
    elif score >= 60:
        risk_level = "HIGH"
    elif score >= 35:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    label_map = {
        "heavy_recent_rain": "very heavy recent rainfall",
        "rain_buildup_3h": "rapid 3-hour rain accumulation",
        "rain_buildup_6h": "persistent 6-hour rainfall buildup",
        "high_moisture": "high atmospheric moisture",
        "strong_winds": "strong near-surface winds",
        "pressure_drop": "a notable pressure drop",
        "temp_instability": "temperature instability",
    }
    active_reasons = [label_map[key] for key, value in flags.items() if value]

    hard_trigger = flags["rain_buildup_3h"] and flags["pressure_drop"] and flags["high_moisture"]
    notify = score >= notify_score or hard_trigger

    return {
        "condition_score": score,
        "condition_risk_level": risk_level,
        "trigger_notification": int(notify),
        "active_condition_count": int(sum(flags.values())),
        "active_conditions": "|".join([k for k, v in flags.items() if v]),
        "layman_explanation": _layman_explanation(active_reasons, risk_level),
    }


def main():
    args = parse_args()
    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        legacy = Path("data/processed/era5_imerg_features.csv")
        if legacy.exists():
            in_csv = legacy
    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_csv, parse_dates=["time"]).sort_values(["region", "time"]).reset_index(drop=True)
    if "region" not in df.columns:
        df["region"] = "unknown"
    if "district_id" in df.columns:
        group_col = "district_id"
    elif "district_name" in df.columns:
        group_col = "district_name"
    else:
        group_col = "region"

    all_parts = []
    for group_value, group in df.groupby(group_col, sort=False):
        th = _thresholds(group)
        metrics = group.apply(lambda r: _evaluate_row(r, th, args.notify_score), axis=1, result_type="expand")
        merged = pd.concat([group.reset_index(drop=True), metrics], axis=1)
        merged["threshold_scope"] = group_value
        all_parts.append(merged)

    sort_cols = [group_col, "time"] if group_col != "region" else ["region", "time"]
    out = pd.concat(all_parts, ignore_index=True).sort_values(sort_cols)
    out.to_csv(out_csv, index=False)

    print("Alert signals generated")
    print("Rows:", len(out))
    print("Notification rows:", int(out["trigger_notification"].sum()))
    print("Saved ->", out_csv)


if __name__ == "__main__":
    main()
