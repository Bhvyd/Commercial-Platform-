"""Commercial Performance Intelligence Platform — Streamlit frontend entry point.

Visual direction: Consulting Deck / Financial Press, dark espresso-charcoal
surface. See DESIGN.md at the project root for the full system record.

Run: streamlit run frontend/app.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.common import inject_css
from frontend.filters import render_sidebar_filters
from frontend.sections import (
    customer_analytics,
    executive_summary,
    insights,
    leakage,
    pricing,
    profitability,
    reporting,
    sales_performance,
)

st.set_page_config(page_title="Commercial Performance Intelligence Platform", layout="wide")
inject_css()

params = render_sidebar_filters()

tab_labels = [
    "Executive Summary",
    "Profitability Analysis",
    "Pricing & Discount",
    "Revenue Leakage",
    "Sales Performance",
    "Customer Analytics",
    "Business Insights",
    "Executive Reporting",
]
tabs = st.tabs(tab_labels)

with tabs[0]:
    executive_summary.render(params)
with tabs[1]:
    profitability.render(params)
with tabs[2]:
    pricing.render(params)
with tabs[3]:
    leakage.render(params)
with tabs[4]:
    sales_performance.render(params)
with tabs[5]:
    customer_analytics.render(params)
with tabs[6]:
    insights.render(params)
with tabs[7]:
    reporting.render(params)
