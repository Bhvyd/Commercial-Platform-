"""Executive Reporting: assembles a downloadable PDF from the same aggregates
every other module already computes."""
from datetime import date

from fpdf import FPDF
from sqlalchemy.engine import Connection

from backend.insights import generate_insights
from backend.leakage_queries import get_leakage_summary
from backend.pricing_queries import get_discount_bands
from backend.profitability_queries import get_profitability_by_dimension
from backend.queries import get_kpi_summary
from backend.sales_queries import get_revenue_forecast


def _section(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 13)
    pdf.ln(4)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)


def _mc(pdf: FPDF, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, text)


def build_report_pdf(conn: Connection, start_date: date, end_date: date, region, category, segment) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Commercial Performance Intelligence Platform", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Executive Report: {start_date} to {end_date}", new_x="LMARGIN", new_y="NEXT")

    summary = get_kpi_summary(conn, start_date, end_date, region, category, segment)
    _section(pdf, "KPI Summary")
    _mc(pdf,
        f"Revenue: {summary['revenue']:,.0f}\n"
        f"Gross Profit: {summary['gross_profit']:,.0f}\n"
        f"Gross Margin: {summary['gross_margin_pct']:.1f}%\n"
        f"Average Order Value: {summary['average_order_value']:,.0f}\n"
        f"Active Customers: {summary['active_customers']:,}",
    )

    top_products = get_profitability_by_dimension(conn, "product", start_date, end_date, region, category, segment, sort_by="gross_profit", ascending=False, limit=5)
    bottom_products = get_profitability_by_dimension(conn, "product", start_date, end_date, region, category, segment, sort_by="margin_pct", ascending=True, limit=5)
    _section(pdf, "Profitability")
    _mc(pdf, "Top 5 products by gross profit:\n" + "\n".join(f"  {p['label']}: {p['gross_profit']:,.0f}" for p in top_products))
    _mc(pdf, "Bottom 5 products by margin %:\n" + "\n".join(f"  {p['label']}: {p['margin_pct']:.1f}%" for p in bottom_products))

    bands = get_discount_bands(conn, start_date, end_date, region, category, segment)
    _section(pdf, "Pricing & Discount")
    _mc(pdf, "\n".join(f"  {b['label']}: revenue {b['revenue']:,.0f}, margin {b['margin_pct']:.1f}%" for b in bands))

    leakage = get_leakage_summary(conn, start_date, end_date, region, category, segment)
    _section(pdf, "Revenue Leakage")
    _mc(pdf, "\n".join(f"  {l['category']}: {l['count']:,} transactions, estimated impact {l['impact']:,.0f}" for l in leakage))

    forecast = get_revenue_forecast(conn, start_date, end_date, region, category, segment)
    forecast_only = [f for f in forecast if f["is_forecast"]]
    _section(pdf, "Revenue Forecast (next 3 months)")
    _mc(pdf, "\n".join(f"  {f['label']}: {f['revenue']:,.0f}" for f in forecast_only))

    insights = generate_insights(conn, start_date, end_date, region, category, segment)
    _section(pdf, "Business Recommendations")
    _mc(pdf, "\n".join(f"  - {i['title']}: {i['detail']}" for i in insights))

    return bytes(pdf.output())
