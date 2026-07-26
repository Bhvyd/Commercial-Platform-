"""Customer Analytics section — RFM segmentation, repeat purchase, high-value customers."""
import pandas as pd
import streamlit as st

from frontend.common import CHART_CONFIG, bar_chart, fetch, fmt_compact


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Customer Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">Who drives the business</div>', unsafe_allow_html=True)

    repeat = fetch("/api/customers/repeat-purchase", params)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total customers", f"{repeat['total_customers']:,}")
    col2.metric("Repeat customers", f"{repeat['repeat_customers']:,}")
    col3.metric("Repeat purchase rate", f"{repeat['repeat_rate_pct']:.1f}%")
    col4.metric("Avg orders / customer", f"{repeat['avg_orders_per_customer']:.1f}")

    st.write("")

    rfm = fetch("/api/customers/rfm", dict(params, limit=15))

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Customers by RFM segment</div>', unsafe_allow_html=True)
            segments = rfm["segments"]
            if segments:
                chart_data = sorted(segments, key=lambda r: r["customer_count"], reverse=True)
                st.plotly_chart(
                    bar_chart([{"label": s["label"], "count": s["customer_count"]} for s in chart_data], value_key="count", text_fmt=lambda v: f"{int(v):,}"),
                    use_container_width=True, config=CHART_CONFIG, key="customer_rfm_segments",
                )
    with c2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">High-value customers (by revenue)</div>', unsafe_allow_html=True)
            top = rfm["top_customers"]
            if top:
                st.plotly_chart(
                    bar_chart(top, value_key="monetary", text_fmt=fmt_compact),
                    use_container_width=True, config=CHART_CONFIG, key="customer_high_value",
                )

    st.caption(
        "RFM segments: Champions (recent, frequent, high-spend), Loyal (frequent), Recent (recently acquired), "
        "At Risk (infrequent and not recent), Regular (everyone else)."
    )

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="chart-title">Top customers detail</div>', unsafe_allow_html=True)
        if rfm["top_customers"]:
            df = pd.DataFrame(rfm["top_customers"]).rename(columns={
                "label": "Customer", "recency_days": "Days since last order", "frequency": "Orders",
                "monetary": "Revenue", "gross_profit": "Gross Profit", "segment": "Segment",
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
