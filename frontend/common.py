"""Shared chart helpers, formatting, and CSS for every page in the app.

Visual direction: Consulting Deck / Financial Press, dark espresso-charcoal
surface. See DESIGN.md at the project root for the full system record.
"""
import plotly.graph_objects as go
import requests
import streamlit as st

from frontend.theme import ACCENT, INK_PRIMARY, INK_SECONDARY, MONO, PAGE_BG, SANS, SERIF, SURFACE, SURFACE_BORDER
from utils.config import API_BASE_URL

CHART_CONFIG = {"displayModeBar": False, "scrollZoom": False, "doubleClick": False}
TICK_SIZE = 13
LABEL_SIZE = 13


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        #MainMenu, footer, [data-testid="stMainMenuButton"], [data-testid="stAppDeployButton"] {{ visibility: hidden; height: 0; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stExpandSidebarButton"] {{ visibility: visible !important; }}

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            background-color: {PAGE_BG} !important;
        }}

        .block-container {{
            max-width: 1440px; margin-left: auto; margin-right: auto;
            padding-top: 2.5rem;
        }}

        [data-testid="stMetricLabel"] {{
            font-family: {SANS}; font-size: 0.7rem; text-transform: uppercase;
            letter-spacing: 0.06em; color: {INK_SECONDARY} !important;
        }}
        [data-testid="stMetricValue"] {{
            font-family: {MONO}; font-variant-numeric: tabular-nums;
            color: {INK_PRIMARY} !important;
        }}
        [data-testid="stMetricDelta"] {{
            font-family: {MONO}; background-color: transparent !important;
            color: {ACCENT} !important; padding: 0 !important;
        }}
        [data-testid="stMetricDelta"] svg {{ display: none; }}
        [data-testid="stMetricDelta"] p {{ color: {ACCENT} !important; }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {SURFACE};
            border: 1px solid {SURFACE_BORDER} !important;
            border-radius: 4px;
        }}

        .eyebrow {{
            font-family: {SANS}; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.14em; color: {ACCENT}; margin-bottom: 2px;
        }}
        .display-title {{
            font-family: {SERIF}; font-size: 1.9rem; font-weight: 600; color: {INK_PRIMARY};
            margin-bottom: 1.2rem;
        }}
        .chart-title {{
            font-family: {SERIF}; font-style: italic; font-size: 0.95rem; color: {INK_PRIMARY};
            margin-bottom: 0.6rem;
        }}
        [data-testid="stSidebar"] label {{
            font-family: {SANS}; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em;
            color: {INK_SECONDARY} !important;
        }}

        [data-testid="stTabs"] {{ margin-bottom: 0.5rem; }}
        [data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap: 4px; border-bottom: 1px solid {SURFACE_BORDER};
        }}
        [data-testid="stTabs"] button[data-baseweb="tab"] {{
            font-family: {SANS}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.04em; color: {INK_SECONDARY};
        }}
        [data-testid="stTabs"] button[aria-selected="true"] {{ color: {INK_PRIMARY} !important; }}
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background-color: {ACCENT} !important; }}
        [data-testid="stTabs"] [data-baseweb="tab-border"] {{ background-color: {SURFACE_BORDER} !important; }}

        @media (max-width: 640px) {{
            .block-container {{ padding-left: 1rem; padding-right: 1rem; padding-top: 1.5rem; }}
            .eyebrow {{ font-size: 0.6rem; }}
            .display-title {{ font-size: 1.25rem; margin-bottom: 0.8rem; }}
            .chart-title {{ font-size: 0.8rem; }}
            [data-testid="stMetricLabel"] {{ font-size: 0.6rem; }}
            [data-testid="stMetricValue"] {{ font-size: 1.05rem; }}
            [data-testid="stMetricDelta"] {{ font-size: 0.7rem; }}

            div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {{
                flex-wrap: wrap; row-gap: 0.75rem;
            }}
            div[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > div {{
                min-width: 45% !important; flex: 1 1 45% !important;
            }}

            [data-testid="stVerticalBlockBorderWrapper"] {{ padding: 0.4rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def fetch(path: str, params: dict) -> dict | list:
    resp = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=300)
def fetch_filter_options() -> dict:
    return fetch("/api/filters/options", {})


def fmt_delta(value: float | None) -> str | None:
    return f"{value:+.1f}% YoY" if value is not None else None


def fmt_compact(value: float) -> str:
    abs_v = abs(value)
    sign = "-" if value < 0 else ""
    if abs_v >= 1_000_000_000:
        return f"{sign}${abs_v / 1_000_000_000:.1f}B"
    if abs_v >= 1_000_000:
        return f"{sign}${abs_v / 1_000_000:.1f}M"
    return f"{sign}${abs_v:,.0f}"


def md_safe(text: str) -> str:
    """Escape $ so st.markdown/st.caption don't parse two dollar amounts as a LaTeX math span."""
    return text.replace("$", "\\$")


def _base_layout(fig: go.Figure, height: int) -> None:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=60, t=10, b=30),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(color=INK_SECONDARY, family=SANS, size=TICK_SIZE),
        showlegend=False,
        dragmode=False,
        hovermode="closest",
    )


def bar_row_height(n_items: int) -> int:
    """Scale panel height to the number of bars so 1-2 results (a narrow
    filter) don't render as a mostly-empty panel."""
    return max(120, min(620, 36 + n_items * 46))


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def bar_chart(items: list[dict], value_key: str = "revenue", height: int | None = None, text_fmt=fmt_compact, zero_based: bool = True):
    """zero_based=False tightens the axis to the data's own range instead of
    starting at 0 — needed for ratio/percentage metrics (e.g. margin %) that
    cluster in a narrow band, where a zero baseline makes every bar look the
    same length. Dollar metrics should stay zero-based (the default)."""
    labels = [i["label"] for i in items]
    values = [i[value_key] for i in items]
    text = [text_fmt(v) for v in values]
    positive_max = max((v for v in values if v > 0), default=0)
    negative_min = min((v for v in values if v < 0), default=0)

    if zero_based:
        x_range = [negative_min * 1.35 if negative_min else 0, positive_max * 1.35]
        textposition = "auto"
    else:
        vmin, vmax = min(values), max(values)
        pad = (vmax - vmin) * 0.3 or abs(vmax) * 0.1 or 1
        x_range = [vmin - pad, vmax + pad]
        textposition = "outside"  # "inside" centers on the full 0-based bar, which is off-screen here

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=ACCENT,
            width=0.4,
            text=text,
            textposition=textposition,
            cliponaxis=False,
            insidetextfont=dict(family=MONO, color=INK_PRIMARY, size=LABEL_SIZE),
            outsidetextfont=dict(family=MONO, color=INK_PRIMARY, size=LABEL_SIZE),
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    _base_layout(fig, height or bar_row_height(len(items)))
    fig.update_layout(margin=dict(l=10, r=70, t=10, b=30))
    fig.update_xaxes(visible=False, range=x_range, fixedrange=True)
    fig.update_yaxes(
        autorange="reversed", tickfont=dict(color=INK_SECONDARY, family=SANS, size=TICK_SIZE),
        showgrid=False, zeroline=False, fixedrange=True,
    )
    return fig


def trend_chart(items: list[dict], value_key: str = "revenue", height: int = 220, tick_format: str = "$.2s", tick_suffix: str = ""):
    labels = [i["label"] for i in items]
    values = [i[value_key] for i in items]
    fig = go.Figure(
        go.Scatter(
            x=labels,
            y=values,
            mode="lines",
            line=dict(color=ACCENT, width=2),
            hovertemplate="%{x|%b %Y}: %{y}<extra></extra>",
        )
    )
    _base_layout(fig, height)
    fig.update_xaxes(
        tickfont=dict(color=INK_SECONDARY, family=MONO, size=TICK_SIZE), showgrid=False,
        zeroline=False, fixedrange=True, nticks=6,
    )
    fig.update_yaxes(
        tickfont=dict(color=INK_SECONDARY, family=MONO, size=TICK_SIZE), gridcolor=SURFACE_BORDER,
        zeroline=False, tickformat=tick_format, ticksuffix=tick_suffix, fixedrange=True,
    )
    return fig
