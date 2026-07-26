"""Executive KPI Dashboard section."""
import streamlit as st

from frontend.common import CHART_CONFIG, bar_chart, fetch, fmt_compact, fmt_delta, trend_chart


def render(params: dict) -> None:
    end_year = params["end_date"][:4]
    st.markdown(f'<div class="eyebrow">Executive Summary — FY{end_year}</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">Commercial Performance Intelligence Platform</div>', unsafe_allow_html=True)

    summary = fetch("/api/kpis/summary", params)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Revenue", fmt_compact(summary["revenue"]), fmt_delta(summary["sales_growth_pct"]))
    col2.metric("Gross Profit", fmt_compact(summary["gross_profit"]))
    col3.metric("Gross Margin", f"{summary['gross_margin_pct']:.1f}%")
    col4.metric("Avg Order Value", fmt_compact(summary["average_order_value"]))
    col5.metric("Active Customers", f"{summary['active_customers']:,}", fmt_delta(summary["customer_growth_pct"]))

    st.write("")

    trend = fetch("/api/kpis/revenue-trend", params)
    with st.container(border=True):
        st.markdown('<div class="chart-title">Revenue trend</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(trend), use_container_width=True, config=CHART_CONFIG, key="exec_trend")

    by_region = fetch("/api/kpis/revenue-by-region", params)
    by_segment = fetch("/api/kpis/revenue-by-segment", params)
    by_product = fetch("/api/kpis/revenue-by-product", params | {"limit": 10})

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Revenue by region</div>', unsafe_allow_html=True)
            st.plotly_chart(bar_chart(by_region), use_container_width=True, config=CHART_CONFIG, key="exec_by_region")
    with c2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Revenue by customer segment</div>', unsafe_allow_html=True)
            st.plotly_chart(bar_chart(by_segment), use_container_width=True, config=CHART_CONFIG, key="exec_by_segment")

    with st.container(border=True):
        st.markdown('<div class="chart-title">Top 10 products by revenue</div>', unsafe_allow_html=True)
        st.plotly_chart(bar_chart(by_product), use_container_width=True, config=CHART_CONFIG, key="exec_by_product")
