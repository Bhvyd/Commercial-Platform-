"""Sales Performance section — trends, regional/product/rep performance, forecast."""
import plotly.graph_objects as go
import streamlit as st

from frontend.common import CHART_CONFIG, TICK_SIZE, bar_chart, fetch, fmt_compact
from frontend.theme import ACCENT, INK_MUTED, INK_SECONDARY, MONO, SANS, SURFACE, SURFACE_BORDER


def _forecast_chart(points: list[dict]):
    actual = [p for p in points if not p["is_forecast"]]
    forecast = [p for p in points if p["is_forecast"]]
    bridge = actual[-1:] + forecast  # connect the two lines visually

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[p["label"] for p in actual], y=[p["revenue"] for p in actual],
        mode="lines", line=dict(color=ACCENT, width=2), name="Actual",
        customdata=[fmt_compact(p["revenue"]) for p in actual],
        hovertemplate="%{x|%b %Y}: %{customdata}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[p["label"] for p in bridge], y=[p["revenue"] for p in bridge],
        mode="lines", line=dict(color=INK_MUTED, width=2, dash="dash"), name="Forecast",
        customdata=[fmt_compact(p["revenue"]) for p in bridge],
        hovertemplate="%{x|%b %Y}: %{customdata} (forecast)<extra></extra>",
    ))
    fig.update_layout(
        height=260, margin=dict(l=10, r=60, t=10, b=30), plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        font=dict(color=INK_SECONDARY, family=SANS, size=TICK_SIZE), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        dragmode=False, hovermode="closest",
    )
    fig.update_xaxes(tickfont=dict(family=MONO, size=TICK_SIZE), showgrid=False, zeroline=False, fixedrange=True)
    fig.update_yaxes(tickfont=dict(family=MONO, size=TICK_SIZE), gridcolor=SURFACE_BORDER, zeroline=False, tickformat="$.2s", fixedrange=True)
    return fig


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Sales Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">Trends, leaders, and what\'s next</div>', unsafe_allow_html=True)

    forecast = fetch("/api/sales/forecast", dict(params, periods_ahead=3))
    with st.container(border=True):
        st.markdown('<div class="chart-title">Revenue trend with 3-month forecast</div>', unsafe_allow_html=True)
        st.plotly_chart(_forecast_chart(forecast), use_container_width=True, config=CHART_CONFIG, key="sales_forecast")
    st.caption("Forecast is a simple linear trend projection, not a seasonal model — treat it as directional, not exact.")

    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Revenue by region</div>', unsafe_allow_html=True)
            by_region = fetch("/api/kpis/revenue-by-region", params)
            st.plotly_chart(bar_chart(by_region), use_container_width=True, config=CHART_CONFIG, key="sales_by_region")
    with c2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Sales rep leaderboard (gross profit)</div>', unsafe_allow_html=True)
            reps = fetch("/api/profitability/by-dimension", dict(params, dimension="rep", sort_by="gross_profit", ascending=False, limit=10))
            if reps:
                st.plotly_chart(bar_chart(reps, value_key="gross_profit", text_fmt=fmt_compact), use_container_width=True, config=CHART_CONFIG, key="sales_rep_leaderboard")

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="chart-title">Top 10 products by revenue</div>', unsafe_allow_html=True)
        by_product = fetch("/api/kpis/revenue-by-product", params | {"limit": 10})
        st.plotly_chart(bar_chart(by_product), use_container_width=True, config=CHART_CONFIG, key="sales_by_product")
