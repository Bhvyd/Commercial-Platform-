"""Business Insights Engine section — auto-generated executive recommendations."""
import streamlit as st

from frontend.common import fetch


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Business Insights Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">What the numbers are telling you</div>', unsafe_allow_html=True)
    st.caption("Generated automatically from the analytics above — every line is a direct read of the current filters, not a canned message.")

    st.write("")

    insights = fetch("/api/insights/generate", params)
    if not insights:
        st.caption("Not enough data in this selection to generate insights.")
        return

    for item in insights:
        with st.container(border=True):
            st.markdown(f'<div class="chart-title">{item["title"]}</div>', unsafe_allow_html=True)
            st.markdown(item["detail"])
