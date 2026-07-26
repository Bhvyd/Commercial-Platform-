"""Pricing & Discount Analytics section — discount/margin erosion + pricing simulator."""
import streamlit as st

from frontend.common import CHART_CONFIG, bar_chart, fetch, fmt_compact, fmt_pct, md_safe


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Pricing &amp; Discount Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">Discount impact &amp; margin erosion</div>', unsafe_allow_html=True)

    bands = fetch("/api/pricing/discount-bands", params)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Revenue by discount band</div>', unsafe_allow_html=True)
            if bands:
                st.plotly_chart(bar_chart(bands, value_key="revenue", text_fmt=fmt_compact), use_container_width=True, config=CHART_CONFIG, key="pricing_band_revenue")
    with c2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Margin % by discount band</div>', unsafe_allow_html=True)
            if bands:
                st.plotly_chart(
                    bar_chart(bands, value_key="margin_pct", text_fmt=fmt_pct, zero_based=False),
                    use_container_width=True, config=CHART_CONFIG, key="pricing_band_margin",
                )

    st.caption(
        "Margin % typically falls as the discount band rises — a band where it doesn't (or where it goes negative) "
        "is where discounting is eroding margin fastest."
    )

    st.write("")
    st.markdown('<div class="display-title" style="font-size:1.3rem;">Pricing simulation</div>', unsafe_allow_html=True)

    products = fetch("/api/pricing/products", {})
    product_name = st.selectbox("Product", products, key="pricing_product")

    detail = fetch("/api/pricing/product-detail", dict(params, product_name=product_name))

    with st.container(border=True):
        list_price = detail["list_price"]
        standard_cost = detail["standard_cost"]
        quantity = detail["quantity"]
        current_revenue = detail["revenue"]
        current_profit = detail["gross_profit"]
        current_margin = (current_profit / current_revenue * 100) if current_revenue else 0.0

        st.caption(md_safe(
            f"List price {fmt_compact(list_price)} · Standard cost {fmt_compact(standard_cost)} · "
            f"{quantity:,} units sold in the selected period · avg discount {detail['avg_discount_pct']:.1f}%"
        ))

        sim_col1, sim_col2 = st.columns(2)
        new_list_price = sim_col1.number_input("Simulated list price ($)", min_value=0.0, value=float(list_price), step=1.0, key="pricing_sim_price")
        new_discount_pct = sim_col2.slider("Simulated discount %", min_value=0.0, max_value=95.0, value=float(round(detail["avg_discount_pct"], 1)), step=0.5, key="pricing_sim_discount")

        new_net_price = new_list_price * (1 - new_discount_pct / 100)
        projected_revenue = new_net_price * quantity
        projected_cost = standard_cost * quantity
        projected_profit = projected_revenue - projected_cost
        projected_margin = (projected_profit / projected_revenue * 100) if projected_revenue else 0.0

        st.markdown("At the same sales volume (units held constant), this pricing would have produced:")
        m1, m2, m3 = st.columns(3)
        m1.metric("Revenue", fmt_compact(projected_revenue), f"{fmt_compact(projected_revenue - current_revenue)} vs actual")
        m2.metric("Gross Profit", fmt_compact(projected_profit), f"{fmt_compact(projected_profit - current_profit)} vs actual")
        m3.metric("Gross Margin", f"{projected_margin:.1f}%", f"{projected_margin - current_margin:+.1f}pp vs actual")
