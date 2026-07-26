"""SQL aggregation queries backing the KPI endpoints.

All filtering and aggregation happens in Postgres (not pandas) since
fact_sales_line has 600K+ rows — filters are pushed down as WHERE clauses.
"""
from datetime import date

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Connection

FACT_JOIN = """
    FROM fact_sales_line f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_region r ON f.region_id = r.region_id
    JOIN dim_sales_rep sr ON f.sales_rep_id = sr.sales_rep_id
"""

NET_REVENUE = "SUM(CASE WHEN f.is_return THEN -f.extended_revenue ELSE f.extended_revenue END)"
NET_PROFIT = "SUM(CASE WHEN f.is_return THEN -f.gross_profit ELSE f.gross_profit END)"


def _build_where(start_date: date, end_date: date, region: str | None, category: str | None, segment: str | None):
    clauses = ["f.is_cancelled = false", "f.date_key BETWEEN :start_date AND :end_date"]
    params = {"start_date": start_date, "end_date": end_date}
    if region:
        clauses.append("r.region_code = :region")
        params["region"] = region
    if category:
        clauses.append("p.category = :category")
        params["category"] = category
    if segment:
        clauses.append("c.segment = :segment")
        params["segment"] = segment
    return " AND ".join(clauses), params


def get_filter_options(conn: Connection) -> dict:
    regions = [r[0] for r in conn.execute(text("SELECT region_code FROM dim_region ORDER BY region_code"))]
    categories = [r[0] for r in conn.execute(text("SELECT DISTINCT category FROM dim_product ORDER BY category"))]
    segments = [r[0] for r in conn.execute(text("SELECT DISTINCT segment FROM dim_customer ORDER BY segment"))]
    min_date, max_date = conn.execute(text("SELECT MIN(date_key), MAX(date_key) FROM fact_sales_line")).one()
    return {
        "regions": regions,
        "categories": categories,
        "segments": segments,
        "min_date": min_date,
        "max_date": max_date,
    }


def _period_aggregates(conn: Connection, start_date: date, end_date: date, region, category, segment) -> dict:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT
            COALESCE({NET_REVENUE}, 0) AS revenue,
            COALESCE({NET_PROFIT}, 0) AS gross_profit,
            COUNT(DISTINCT f.invoice_number) AS orders,
            COUNT(DISTINCT f.customer_id) AS active_customers
        {FACT_JOIN}
        WHERE {where_sql}
    """
    row = conn.execute(text(sql), params).mappings().one()
    return dict(row)


def get_kpi_summary(conn: Connection, start_date: date, end_date: date, region, category, segment) -> dict:
    current = _period_aggregates(conn, start_date, end_date, region, category, segment)

    prior_start = (pd.Timestamp(start_date) - pd.DateOffset(years=1)).date()
    prior_end = (pd.Timestamp(end_date) - pd.DateOffset(years=1)).date()
    prior = _period_aggregates(conn, prior_start, prior_end, region, category, segment)

    revenue = float(current["revenue"])
    gross_profit = float(current["gross_profit"])
    orders = int(current["orders"])
    active_customers = int(current["active_customers"])

    def growth_pct(curr: float, prev: float) -> float | None:
        if prev == 0:
            return None
        return round((curr - prev) / prev * 100, 2)

    return {
        "revenue": round(revenue, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_margin_pct": round(gross_profit / revenue * 100, 2) if revenue else 0.0,
        "average_order_value": round(revenue / orders, 2) if orders else 0.0,
        "active_customers": active_customers,
        "customer_growth_pct": growth_pct(active_customers, float(prior["active_customers"])),
        "sales_growth_pct": growth_pct(revenue, float(prior["revenue"])),
        "prior_period_start": prior_start,
        "prior_period_end": prior_end,
    }


def get_revenue_by_region(conn: Connection, start_date, end_date, region, category, segment) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT r.region_name AS label, COALESCE({NET_REVENUE}, 0) AS revenue, COALESCE({NET_PROFIT}, 0) AS gross_profit
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY r.region_name
        ORDER BY revenue DESC
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def get_revenue_by_segment(conn: Connection, start_date, end_date, region, category, segment) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT c.segment AS label, COALESCE({NET_REVENUE}, 0) AS revenue, COALESCE({NET_PROFIT}, 0) AS gross_profit
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY c.segment
        ORDER BY revenue DESC
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def get_revenue_trend(conn: Connection, start_date, end_date, region, category, segment) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT DATE_TRUNC('month', f.date_key)::date AS label, COALESCE({NET_REVENUE}, 0) AS revenue, COALESCE({NET_PROFIT}, 0) AS gross_profit
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY 1
        ORDER BY 1
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def get_revenue_by_product(conn: Connection, start_date, end_date, region, category, segment, limit: int = 10) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    params["limit"] = limit
    sql = f"""
        SELECT p.product_name AS label, COALESCE({NET_REVENUE}, 0) AS revenue, COALESCE({NET_PROFIT}, 0) AS gross_profit
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT :limit
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]
