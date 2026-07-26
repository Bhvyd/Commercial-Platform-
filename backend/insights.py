"""Business Insights Engine: rule-based executive recommendations generated
from the same aggregates the other modules already compute — no separate
model, just thresholds applied to real numbers."""
from datetime import date

from sqlalchemy.engine import Connection

from backend.leakage_queries import get_leakage_summary
from backend.profitability_queries import get_margin_trend, get_profitability_by_dimension
from backend.queries import get_kpi_summary, get_revenue_by_region, get_revenue_by_segment


def generate_insights(conn: Connection, start_date: date, end_date: date, region, category, segment) -> list[dict]:
    insights = []

    summary = get_kpi_summary(conn, start_date, end_date, region, category, segment)
    if summary["sales_growth_pct"] is not None:
        if summary["sales_growth_pct"] > 0:
            insights.append({
                "title": f"Revenue grew {summary['sales_growth_pct']:.1f}% YoY",
                "detail": f"Gross margin currently sits at {summary['gross_margin_pct']:.1f}%.",
            })
        else:
            insights.append({
                "title": f"Revenue declined {abs(summary['sales_growth_pct']):.1f}% YoY",
                "detail": "Review the pipeline and top-performing regions/segments below for where to focus.",
            })

    by_region = get_revenue_by_region(conn, start_date, end_date, region, category, segment)
    if by_region:
        top = by_region[0]
        insights.append({
            "title": f"{top['label']} is the strongest-performing region",
            "detail": f"Contributes {top['revenue']:,.0f} in revenue, the highest of any region in the selected period.",
        })

    by_segment = get_revenue_by_segment(conn, start_date, end_date, region, category, segment)
    if by_segment:
        top = max(by_segment, key=lambda r: r["gross_profit"])
        insights.append({
            "title": f"{top['label']} contributes the most gross profit",
            "detail": f"{top['gross_profit']:,.0f} in gross profit from the {top['label']} segment in the selected period.",
        })

    worst_category = get_profitability_by_dimension(conn, "category", start_date, end_date, region, category, segment, sort_by="margin_pct", ascending=True, limit=1)
    if worst_category:
        wc = worst_category[0]
        insights.append({
            "title": f"{wc['label']} requires pricing review",
            "detail": f"Lowest gross margin of any category at {wc['margin_pct']:.1f}%, versus revenue of {wc['revenue']:,.0f}.",
        })

    worst_products = get_profitability_by_dimension(conn, "product", start_date, end_date, region, category, segment, sort_by="margin_pct", ascending=True, limit=1)
    if worst_products:
        wp = worst_products[0]
        insights.append({
            "title": f"{wp['label']} should be considered for a price increase",
            "detail": f"Margin of only {wp['margin_pct']:.1f}%, the lowest of any product in the selected period.",
        })

    leakage = get_leakage_summary(conn, start_date, end_date, region, category, segment)
    excessive = next((l for l in leakage if "Excessive" in l["category"]), None)
    if excessive and excessive["count"] > 0:
        insights.append({
            "title": "Margin is being eroded by excessive discounting",
            "detail": f"{excessive['count']:,} transactions carried a discount above 50%, an estimated {excessive['impact']:,.0f} in lost discount value.",
        })

    margin_trend = get_margin_trend(conn, start_date, end_date, region, category, segment)
    if len(margin_trend) >= 2:
        change = margin_trend[-1]["margin_pct"] - margin_trend[0]["margin_pct"]
        if abs(change) >= 0.5:
            direction = "declining" if change < 0 else "improving"
            insights.append({
                "title": f"Gross margin is {direction} over the selected period",
                "detail": f"Moved from {margin_trend[0]['margin_pct']:.1f}% to {margin_trend[-1]['margin_pct']:.1f}%.",
            })

    return insights
