from pathlib import Path
import sys

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import auc, precision_recall_curve, roc_curve

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api_client import ApiError, load_results_csv, model_insights
from ui import hero, metric_strip, setup_page, style_plotly_figure, top_nav


def _load_insights_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    perf_df = load_results_csv("model_performance.csv")
    chunk_df = load_results_csv("chunk_ensemble_performance.csv")
    prob_df = load_results_csv("risk_probabilities.csv")

    try:
        payload = model_insights(detailed=True)
        if payload.get("models"):
            perf_df = pd.DataFrame(payload["models"])
        if payload.get("zone_metrics"):
            chunk_df = pd.DataFrame(payload["zone_metrics"])
        if payload.get("probability_samples"):
            prob_df = pd.DataFrame(payload["probability_samples"])
    except ApiError:
        pass

    return perf_df, chunk_df, prob_df


setup_page("Cloudburst Model Insights")
top_nav("Model Insights")

hero(
    "Model Reliability and Decision Support Quality",
    "Inspect measured discrimination, recall behavior, and probability separation based on project result artifacts.",
)

perf_df, chunk_df, prob_df = _load_insights_frames()

best_auc = perf_df["auc"].max() if "auc" in perf_df.columns else np.nan
best_recall = perf_df["recall"].max() if "recall" in perf_df.columns else np.nan
best_f1 = perf_df["f1"].max() if "f1" in perf_df.columns else np.nan

metric_strip(
    [
        ("Best AUC", f"{best_auc:.3f}" if pd.notna(best_auc) else "NA"),
        ("Best Recall", f"{best_recall:.3f}" if pd.notna(best_recall) else "NA"),
        ("Best F1", f"{best_f1:.3f}" if pd.notna(best_f1) else "NA"),
        ("Scored Timepoints", f"{len(prob_df)}"),
    ]
)

top_left, top_right = st.columns([1.2, 1], gap="large")
with top_left:
    if "model" in perf_df.columns:
        mdf = perf_df.copy()
        metric_cols = [c for c in ["auc", "recall", "precision", "f1"] if c in mdf.columns]
        if HAS_PLOTLY:
            fig_perf = px.bar(
                mdf,
                x="model",
                y=metric_cols,
                barmode="group",
            )
            fig_perf.update_layout(title="Overall Model Performance")
            st.plotly_chart(style_plotly_figure(fig_perf, height=380), use_container_width=True)
        else:
            st.markdown("### Overall Model Performance")
            st.bar_chart(mdf.set_index("model")[metric_cols], use_container_width=True)

with top_right:
    if {"true_label", "probability"}.issubset(prob_df.columns):
        p0 = prob_df[prob_df["true_label"] == 0]["probability"]
        p1 = prob_df[prob_df["true_label"] == 1]["probability"]
        if HAS_PLOTLY:
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(x=p0, nbinsx=40, name="Non-event", opacity=0.75))
            fig_hist.add_trace(go.Histogram(x=p1, nbinsx=40, name="Event", opacity=0.75))
            fig_hist.update_layout(barmode="overlay", title="Probability Separation")
            st.plotly_chart(style_plotly_figure(fig_hist, height=380), use_container_width=True)
        else:
            hist_df = pd.DataFrame({"Non-event": p0.reset_index(drop=True), "Event": p1.reset_index(drop=True)})
            st.markdown("### Probability Separation")
            st.line_chart(hist_df, use_container_width=True)

curve_left, curve_right = st.columns(2, gap="large")
if {"true_label", "probability"}.issubset(prob_df.columns):
    y_true = prob_df["true_label"].astype(int).to_numpy()
    y_prob = prob_df["probability"].astype(float).to_numpy()

    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)

    if HAS_PLOTLY:
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"Model ROC (AUC={roc_auc:.3f})"))
        fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Chance", line=dict(dash="dash")))
        fig_roc.update_layout(title="ROC Curve", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")

        fig_pr = go.Figure()
        fig_pr.add_trace(go.Scatter(x=recall, y=precision, mode="lines", name=f"PR Curve (AUC={pr_auc:.3f})"))
        fig_pr.update_layout(title="Precision-Recall Curve", xaxis_title="Recall", yaxis_title="Precision")

        with curve_left:
            st.plotly_chart(style_plotly_figure(fig_roc, height=360), use_container_width=True)
        with curve_right:
            st.plotly_chart(style_plotly_figure(fig_pr, height=360), use_container_width=True)
    else:
        with curve_left:
            st.markdown(f"### ROC Curve (AUC={roc_auc:.3f})")
            st.line_chart(pd.DataFrame({"tpr": tpr}, index=fpr), use_container_width=True)
        with curve_right:
            st.markdown(f"### PR Curve (AUC={pr_auc:.3f})")
            st.line_chart(pd.DataFrame({"precision": precision}, index=recall), use_container_width=True)

st.markdown("### Zone-Wise Ensemble Performance")
if {"chunk", "model", "auc", "recall"}.issubset(chunk_df.columns):
    chunk_f = chunk_df.copy()
    chunk_f["chunk"] = chunk_f["chunk"].str.title()
    if HAS_PLOTLY:
        fig_chunk_auc = px.bar(chunk_f, x="chunk", y="auc", color="model", barmode="group", title="AUC by Zone and Model")
        st.plotly_chart(style_plotly_figure(fig_chunk_auc, height=340), use_container_width=True)

        fig_chunk_recall = px.bar(
            chunk_f,
            x="chunk",
            y="recall",
            color="model",
            barmode="group",
            title="Recall by Zone and Model",
        )
        st.plotly_chart(style_plotly_figure(fig_chunk_recall, height=340), use_container_width=True)
    else:
        st.markdown("#### AUC by Zone and Model")
        st.bar_chart(chunk_f.pivot_table(index="chunk", columns="model", values="auc"), use_container_width=True)
        st.markdown("#### Recall by Zone and Model")
        st.bar_chart(chunk_f.pivot_table(index="chunk", columns="model", values="recall"), use_container_width=True)

with st.expander("Raw metrics tables"):
    st.markdown("#### model_performance.csv")
    st.dataframe(perf_df, use_container_width=True, hide_index=True)
    st.markdown("#### chunk_ensemble_performance.csv")
    st.dataframe(chunk_df, use_container_width=True, hide_index=True)
