"""Profitability Analysis section — profit breakdowns, margin trend, loss-making customers."""
import streamlit as st

from frontend.common import CHART_CONFIG, bar_chart, fetch, fmt_compact, fmt_pct, trend_chart

DIMENSIONS = {"Product": "product", "Customer": "customer", "Category": "category", "Region": "region", "Sales Rep": "rep"}
SORTS = {
    "Highest gross profit": ("gross_profit", False),
    "Lowest gross profit": ("gross_profit", True),
    "Highest margin %": ("margin_pct", False),
    "Lowest margin %": ("margin_pct", True),
}


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Profitability Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">Where the margin comes from</div>', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns(2)
    dimension_label = ctrl1.selectbox("Break down by", list(DIMENSIONS.keys()), key="profit_dimension")
    sort_label = ctrl2.selectbox("Rank by", list(SORTS.keys()), key="profit_sort")
    sort_by, ascending = SORTS[sort_label]

    breakdown_params = dict(params, dimension=DIMENSIONS[dimension_label], sort_by=sort_by, ascending=ascending, limit=15)
    breakdown = fetch("/api/profitability/by-dimension", breakdown_params)

    with st.container(border=True):
        st.markdown(f'<div class="chart-title">{sort_label} by {dimension_label.lower()}</div>', unsafe_allow_html=True)
        if breakdown:
            value_key, text_fmt = ("margin_pct", fmt_pct) if sort_by == "margin_pct" else ("gross_profit", fmt_compact)
            st.plotly_chart(
                bar_chart(breakdown, value_key=value_key, text_fmt=text_fmt, zero_based=(sort_by != "margin_pct")),
                use_container_width=True, config=CHART_CONFIG, key="profit_breakdown",
            )
        else:
            st.caption("No data for this selection.")

    st.write("")

    trend = fetch("/api/profitability/margin-trend", params)
    with st.container(border=True):
        st.markdown('<div class="chart-title">Gross margin trend</div>', unsafe_allow_html=True)
        st.plotly_chart(
            trend_chart(trend, value_key="margin_pct", tick_format=".1f", tick_suffix="%"),
            use_container_width=True, config=CHART_CONFIG, key="profit_margin_trend",
        )

    st.write("")

    loss_makers = fetch("/api/profitability/loss-making-customers", dict(params, limit=50))
    with st.container(border=True):
        st.markdown('<div class="chart-title">Loss-making customers</div>', unsafe_allow_html=True)
        if loss_makers:
            total_impact = sum(row["gross_profit"] for row in loss_makers)
            st.caption(f"{len(loss_makers)} customers with negative gross profit — estimated impact {fmt_compact(total_impact)}")
            st.plotly_chart(
                bar_chart(loss_makers[:15], value_key="gross_profit", text_fmt=fmt_compact),
                use_container_width=True, config=CHART_CONFIG, key="profit_loss_makers",
            )
        else:
            st.caption("No loss-making customers in the selected filters.")
