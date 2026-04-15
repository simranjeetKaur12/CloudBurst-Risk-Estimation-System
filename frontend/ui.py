from __future__ import annotations

import streamlit as st

PRIMARY_BG = "#0F172A"
CARD_BG = "#1F2937"
SURFACE_BG = "#111827"
BORDER_COLOR = "#374151"
DIVIDER_COLOR = "#334155"
PRIMARY_TEXT = "#F9FAFB"
SECONDARY_TEXT = "#D1D5DB"
MUTED_TEXT = "#9CA3AF"
DISABLED_TEXT = "#6B7280"
PRIMARY_ACCENT = "#2563EB"
HOVER_ACCENT = "#1D4ED8"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
DANGER = "#DC2626"
LOW_BG = "#052e16"
LOW_TEXT = "#22c55e"
MODERATE_BG = "#451a03"
MODERATE_TEXT = "#f59e0b"
HIGH_BG = "#450a0a"
HIGH_TEXT = "#ef4444"


RISK_COLOR = {
    "LOW": LOW_TEXT,
    "MODERATE": MODERATE_TEXT,
    "HIGH": HIGH_TEXT,
    "GREEN": LOW_TEXT,
    "YELLOW": MODERATE_TEXT,
    "ORANGE": WARNING,
    "RED": HIGH_TEXT,
}


def setup_page(title: str, icon: str = "🌧️") -> None:
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_css()


def top_nav(active: str) -> None:
    page_map = [
        ("Home", "app.py"),
        ("Risk Dashboard", "pages/2_Risk_Dashboard.py"),
        ("Event Analysis", "pages/3_Event_Analysis.py"),
        ("Model Insights", "pages/4_Model_Insights.py"),
        ("API Status", "pages/6_API_Status.py"),
    ]

    cols = st.columns([2.4, 1, 1, 1, 1, 1], gap="small")
    with cols[0]:
        st.markdown(
            """
            <div class="cb-topbar">
                <div class="cb-brand">
                    <div class="cb-logo">CB</div>
                    <div>
                        <div class="cb-brand-title">Cloudburst Risk Intelligence</div>
                        <div class="cb-brand-subtitle">Indian Himalayan Region decision support</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    for idx, (label, page) in enumerate(page_map, start=1):
        with cols[idx]:
            st.page_link(page, label=label, use_container_width=True)


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Source+Sans+3:wght@400;500;600&display=swap');

            :root {
                --bg: #0F172A;
                --surface: #111827;
                --card: #1F2937;
                --border: #374151;
                --divider: #334155;
                --text: #F9FAFB;
                --secondary: #D1D5DB;
                --muted: #9CA3AF;
                --disabled: #6B7280;
                --accent: #2563EB;
                --accent-hover: #1D4ED8;
                --success: #16A34A;
                --warning: #F59E0B;
                --danger: #DC2626;
                --low-bg: #052e16;
                --low-text: #22c55e;
                --moderate-bg: #451a03;
                --moderate-text: #f59e0b;
                --high-bg: #450a0a;
                --high-text: #ef4444;
            }

            .stApp {
                background: var(--bg);
                font-family: 'Source Sans 3', sans-serif;
                color: var(--text);
            }

            .stApp, .stApp p, .stApp li, .stApp div, .stApp span, .stApp label {
                color: var(--text);
            }

            .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
                color: var(--text);
            }

            .stApp [data-testid="stMarkdownContainer"] p,
            .stApp [data-testid="stMarkdownContainer"] li,
            .stApp [data-testid="stMarkdownContainer"] span {
                color: var(--text);
            }

            .stApp .stCaption {
                color: var(--muted);
            }

            .stApp .stAlert,
            .stApp .stInfo,
            .stApp .stSuccess,
            .stApp .stWarning,
            .stApp .stError {
                color: var(--text);
            }

            .stApp div[data-testid="stAlert"] {
                background: var(--surface);
                border: 1px solid var(--border);
                color: var(--text);
            }

            .stApp div[data-testid="stAlert"] p,
            .stApp div[data-testid="stAlert"] span,
            .stApp div[data-testid="stAlert"] li {
                color: var(--text);
            }

            .block-container {
                padding-top: 16px;
                padding-bottom: 32px;
                max-width: 1200px;
            }

            [data-testid="stSidebar"] {
                background: var(--surface);
                color: var(--text);
                border-right: 1px solid var(--border);
            }

            [data-testid="stSidebar"] * {
                color: var(--text);
            }

            .cb-topbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                padding: 16px;
                margin-bottom: 16px;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }

            .cb-brand {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                min-width: 280px;
            }

            .cb-logo {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                display: grid;
                place-items: center;
                background: var(--accent);
                color: #FFFFFF;
                font-weight: 800;
                letter-spacing: 0.04em;
            }

            .cb-brand-title {
                font-family: 'Manrope', sans-serif;
                font-size: 1rem;
                font-weight: 800;
                color: var(--text);
            }

            .cb-brand-subtitle {
                font-size: 0.85rem;
                color: var(--secondary);
            }

            .cb-nav {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                justify-content: flex-end;
            }

            .cb-nav-link {
                display: inline-flex;
                align-items: center;
                min-height: 38px;
                padding: 0.5rem 0.8rem;
                border-radius: 999px;
                text-decoration: none;
                font-weight: 700;
                color: var(--text);
                background: var(--card);
                border: 1px solid var(--border);
            }

            .cb-nav-link.active {
                color: #FFFFFF;
                background: var(--accent);
            }

            h1, h2, h3 {
                font-family: 'Manrope', sans-serif;
                letter-spacing: -0.02em;
            }

            h1 {
                font-size: 28px;
                font-weight: 800;
                color: var(--text);
            }

            h2 {
                font-size: 20px;
                font-weight: 600;
                color: var(--text);
            }

            h3 {
                font-size: 18px;
                font-weight: 600;
                color: var(--text);
            }

            .cb-hero {
                padding: 24px;
                border-radius: 12px;
                background: var(--surface);
                color: var(--text);
                border: 1px solid var(--border);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }

            .cb-hero h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 800;
            }

            .cb-hero p {
                font-size: 15px;
                color: var(--secondary);
                margin-top: 16px;
                max-width: 760px;
            }

            .cb-section {
                margin-top: 32px;
                margin-bottom: 32px;
            }

            .cb-panel {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }

            .cb-metric-strip {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 16px;
            }

            @media (max-width: 1100px) {
                .cb-metric-strip {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }

                .cb-topbar {
                    flex-direction: column;
                    align-items: stretch;
                }

                .cb-brand {
                    min-width: 0;
                }
            }

            @media (max-width: 700px) {
                .cb-metric-strip {
                    grid-template-columns: 1fr;
                }

                .block-container {
                    padding-left: 16px;
                    padding-right: 16px;
                }
            }

            .cb-status-connected {
                color: var(--success);
                font-weight: 800;
            }

            .cb-status-disconnected {
                color: var(--danger);
                font-weight: 800;
            }

            .cb-loader {
                border-radius: 12px;
                background: var(--divider);
                min-height: 120px;
            }

            .cb-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
                margin-top: 16px;
            }

            .cb-card {
                background: var(--card);
                border-radius: 12px;
                border: 1px solid var(--border);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                padding: 16px;
                overflow: hidden;
            }

            .cb-metric-label {
                color: var(--secondary);
                font-size: 14px;
                margin-bottom: 4px;
                line-height: 1.2;
            }

            .cb-metric-value {
                color: var(--text);
                font-family: 'Manrope', sans-serif;
                font-weight: 800;
                font-size: 16px;
                line-height: 1.25;
                word-break: break-word;
            }

            .cb-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.35rem 0.7rem;
                border-radius: 999px;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 0.8rem;
                letter-spacing: 0.03em;
            }

            .cb-explain {
                border-left: 4px solid var(--accent);
                background: var(--card);
                color: var(--text);
                padding: 16px;
                border-radius: 12px;
                margin-top: 16px;
            }

            .cb-subtle {
                color: var(--muted);
            }

            .stTextInput input,
            .stSelectbox div[data-baseweb="select"] > div,
            .stMultiselect div[data-baseweb="select"] > div,
            .stTextArea textarea {
                background: var(--surface) !important;
                color: var(--text) !important;
                border: 1px solid var(--border) !important;
                border-radius: 8px !important;
            }

            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: var(--muted) !important;
            }

            .stTextInput input:focus,
            .stTextArea textarea:focus {
                border: 1px solid var(--accent) !important;
                box-shadow: none !important;
            }

            .stButton > button {
                background: var(--accent) !important;
                color: #FFFFFF !important;
                border: 1px solid var(--accent) !important;
                border-radius: 8px !important;
                padding: 10px 16px !important;
                font-weight: 700 !important;
            }

            .stButton > button:hover {
                background: var(--accent-hover) !important;
                border-color: var(--accent-hover) !important;
            }

            .stButton > button:disabled {
                background: var(--disabled) !important;
                border-color: var(--disabled) !important;
                color: #FFFFFF !important;
            }

            .stMetric {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }

            .stMetric label,
            .stMetric div[data-testid="metric-container"] > div {
                color: var(--secondary) !important;
            }

            .stMetric [data-testid="stMetricValue"] {
                color: var(--text) !important;
            }

            .stDataFrame,
            .stDataFrame * {
                color: var(--text) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <section class=\"cb-hero\">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def panel() -> None:
    st.markdown('<div class="cb-panel">', unsafe_allow_html=True)


def panel_end() -> None:
    st.markdown('</div>', unsafe_allow_html=True)


def metric_strip(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items), gap="medium")
    for col, (label, value) in zip(cols, items):
        with col:
            metric_card(label, value)


def status_text(is_connected: bool) -> str:
    if is_connected:
        return "<span class='cb-status-connected'>Connected</span>"
    return "<span class='cb-status-disconnected'>Disconnected</span>"


def loading_state(message: str = "Loading data...") -> None:
    st.markdown(f"<div class='cb-panel'><div class='cb-loader'></div><div style='margin-top:12px; font-weight:600; color:#D1D5DB;'>{message}</div></div>", unsafe_allow_html=True)


def style_plotly_figure(fig, height: int = 320):
    fig.update_layout(
        height=height,
        paper_bgcolor=PRIMARY_BG,
        plot_bgcolor=SURFACE_BG,
        font=dict(color=PRIMARY_TEXT, family="Source Sans 3"),
        margin=dict(l=16, r=16, t=24, b=16),
        legend=dict(font=dict(color=SECONDARY_TEXT)),
    )
    fig.update_xaxes(
        gridcolor=BORDER_COLOR,
        zerolinecolor=DIVIDER_COLOR,
        linecolor=BORDER_COLOR,
        tickfont=dict(color=SECONDARY_TEXT),
        title=dict(font=dict(color=SECONDARY_TEXT)),
    )
    fig.update_yaxes(
        gridcolor=BORDER_COLOR,
        zerolinecolor=DIVIDER_COLOR,
        linecolor=BORDER_COLOR,
        tickfont=dict(color=SECONDARY_TEXT),
        title=dict(font=dict(color=SECONDARY_TEXT)),
    )
    return fig


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class=\"cb-card\">
            <div class=\"cb-metric-label\">{label}</div>
            <div class=\"cb-metric-value\">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(level: str) -> str:
    color = RISK_COLOR.get(level.upper(), PRIMARY_ACCENT)
    return f"<span class='cb-badge' style='background:{color};'>{level}</span>"
