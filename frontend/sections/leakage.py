"""Revenue Leakage Detection section."""
import pandas as pd
import streamlit as st

from frontend.common import CHART_CONFIG, bar_chart, fetch, fmt_compact

LEAK_TYPES = {
    "Excessive Discounts (>50%)": "excessive_discount",
    "Negative-Margin Transactions": "negative_margin",
    "Duplicate Invoice Numbers": "duplicate_invoices",
    "Price Inconsistencies": "price_inconsistencies",
}


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Revenue Leakage Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">Where revenue is quietly slipping away</div>', unsafe_allow_html=True)

    summary = fetch("/api/leakage/summary", params)
    total_impact = sum(row["impact"] for row in summary)

    cols = st.columns(len(summary) + 1)
    cols[0].metric("Total estimated impact", fmt_compact(total_impact))
    for c, row in zip(cols[1:], summary):
        c.metric(row["category"], f"{row['count']:,}", fmt_compact(row["impact"]) + " impact")

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="chart-title">Estimated financial impact by anomaly type</div>', unsafe_allow_html=True)
        chart_data = [{"label": r["category"], "impact": r["impact"]} for r in summary]
        st.plotly_chart(bar_chart(chart_data, value_key="impact", text_fmt=fmt_compact), use_container_width=True, config=CHART_CONFIG, key="leakage_impact")

    st.write("")
    st.markdown('<div class="display-title" style="font-size:1.3rem;">Flagged transactions</div>', unsafe_allow_html=True)
    leak_label = st.selectbox("Anomaly type", list(LEAK_TYPES.keys()), key="leakage_type")
    rows = fetch("/api/leakage/transactions", dict(params, leak_type=LEAK_TYPES[leak_label], limit=50))

    with st.container(border=True):
        if rows:
            df = pd.DataFrame(rows).dropna(axis=1, how="all")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No flagged transactions for this selection.")
