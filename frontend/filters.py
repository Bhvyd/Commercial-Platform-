"""Sidebar filters shared by every page. Session-state keys (start_date,
end_date, region, category, segment, preset) persist across page navigation
within a browser session, so filters chosen on one page stay set on another.
"""
from datetime import date as date_cls
from datetime import timedelta

import streamlit as st

from frontend.common import fetch_filter_options

PRESETS = ["Last 12 months", "Last 90 days", "Year to date", "All time"]


def _preset_range(preset: str, min_date: date_cls, max_date: date_cls) -> tuple[date_cls, date_cls]:
    if preset == "Last 12 months":
        return max(min_date, max_date - timedelta(days=365)), max_date
    if preset == "Last 90 days":
        return max(min_date, max_date - timedelta(days=90)), max_date
    if preset == "Year to date":
        return max(min_date, date_cls(max_date.year, 1, 1)), max_date
    return min_date, max_date  # All time


def render_sidebar_filters() -> dict:
    """Renders the sidebar and returns the API query-params dict for the
    currently selected filters. Call once per page, at the top."""
    options = fetch_filter_options()
    min_date = date_cls.fromisoformat(options["min_date"])
    max_date = date_cls.fromisoformat(options["max_date"])

    def _apply_preset() -> None:
        st.session_state.start_date, st.session_state.end_date = _preset_range(
            st.session_state.preset, min_date, max_date
        )

    if "start_date" not in st.session_state:
        st.session_state.start_date, st.session_state.end_date = _preset_range("Last 12 months", min_date, max_date)

    with st.sidebar:
        st.markdown("**Filters**")
        st.selectbox("Quick range", PRESETS, key="preset", on_change=_apply_preset)
        date_col1, date_col2 = st.columns(2)
        date_col1.date_input("From", min_value=min_date, max_value=max_date, key="start_date")
        date_col2.date_input("To", min_value=min_date, max_value=max_date, key="end_date")
        if (st.session_state.start_date, st.session_state.end_date) != _preset_range(
            st.session_state.get("preset", "Last 12 months"), min_date, max_date
        ):
            st.caption("Custom range")
        region = st.selectbox("Region", ["All"] + options["regions"], key="region_filter")
        category = st.selectbox("Category", ["All"] + options["categories"], key="category_filter")
        segment = st.selectbox("Customer Segment", ["All"] + options["segments"], key="segment_filter")

    start_date, end_date = st.session_state.start_date, st.session_state.end_date
    if start_date > end_date:
        st.sidebar.error("'From' date must be before 'To' date.")
        st.stop()

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "region": None if region == "All" else region,
        "category": None if category == "All" else category,
        "segment": None if segment == "All" else segment,
    }
