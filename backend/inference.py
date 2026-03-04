import joblib
import pandas as pd
from backend.config import *

models = {
    "lr": joblib.load(LR_MODEL),
    "rf": joblib.load(RF_MODEL),
    "xgb": joblib.load(XGB_MODEL)
}

def assign_risk(prob):
    if prob >= RED_TH:
        return "RED"
    elif prob >= ORANGE_TH:
        return "ORANGE"
    elif prob >= YELLOW_TH:
        return "YELLOW"
    return "LOW"

def predict_risk(input_df: pd.DataFrame, model_name="xgb"):
    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not supported")

    model = models[model_name]
    probs = model.predict_proba(input_df)[:, 1]

    return [
        {
            "risk_probability": float(p),
            "risk_tier": assign_risk(p)
        }
        for p in probs
    ]
