"""Executive Reporting section — downloadable PDF summarizing the current filters."""
import requests
import streamlit as st

from utils.config import API_BASE_URL


def render(params: dict) -> None:
    st.markdown('<div class="eyebrow">Executive Reporting</div>', unsafe_allow_html=True)
    st.markdown('<div class="display-title">One PDF, everything an executive needs</div>', unsafe_allow_html=True)
    st.caption(
        "Bundles the KPI summary, profitability highlights, pricing/discount breakdown, revenue leakage, "
        "3-month forecast, and business recommendations for the filters currently selected in the sidebar."
    )

    st.write("")

    if st.button("Generate report", key="generate_report_btn"):
        with st.spinner("Building report..."):
            resp = requests.get(f"{API_BASE_URL}/api/report/generate", params=params, timeout=60)
            resp.raise_for_status()
            st.session_state["report_pdf_bytes"] = resp.content

    if "report_pdf_bytes" in st.session_state:
        st.download_button(
            "Download executive_report.pdf",
            data=st.session_state["report_pdf_bytes"],
            file_name="executive_report.pdf",
            mime="application/pdf",
            key="download_report_btn",
        )
