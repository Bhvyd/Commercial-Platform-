"""SQL aggregation queries backing the Pricing & Discount Analytics endpoints."""
from datetime import date

from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.queries import FACT_JOIN, NET_PROFIT, NET_REVENUE, _build_where

DISCOUNT_BAND_CASE = """
    CASE
        WHEN f.discount_pct < 5 THEN '0-5%'
        WHEN f.discount_pct < 10 THEN '5-10%'
        WHEN f.discount_pct < 15 THEN '10-15%'
        WHEN f.discount_pct < 20 THEN '15-20%'
        WHEN f.discount_pct < 30 THEN '20-30%'
        WHEN f.discount_pct < 50 THEN '30-50%'
        ELSE '50%+'
    END
"""


def get_discount_bands(conn: Connection, start_date: date, end_date: date, region, category, segment) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT
            {DISCOUNT_BAND_CASE} AS label,
            COUNT(*) AS transaction_count,
            COALESCE({NET_REVENUE}, 0) AS revenue,
            COALESCE({NET_PROFIT}, 0) AS gross_profit,
            CASE WHEN COALESCE({NET_REVENUE}, 0) = 0 THEN 0
                 ELSE COALESCE({NET_PROFIT}, 0) / NULLIF({NET_REVENUE}, 0) * 100 END AS margin_pct
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY 1
        ORDER BY MIN(f.discount_pct)
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def get_product_list(conn: Connection) -> list[str]:
    return [r[0] for r in conn.execute(text("SELECT product_name FROM dim_product ORDER BY product_name"))]


def get_product_pricing_detail(conn: Connection, product_name: str, start_date: date, end_date: date, region, category, segment) -> dict:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    params["product_name"] = product_name
    sql = f"""
        SELECT
            p.list_price,
            p.standard_cost,
            COALESCE(SUM(f.quantity), 0) AS quantity,
            COALESCE({NET_REVENUE}, 0) AS revenue,
            COALESCE({NET_PROFIT}, 0) AS gross_profit,
            COALESCE(AVG(f.discount_pct), 0) AS avg_discount_pct
        {FACT_JOIN}
        WHERE {where_sql} AND p.product_name = :product_name
        GROUP BY p.list_price, p.standard_cost
    """
    row = conn.execute(text(sql), params).mappings().first()
    if row is None:
        return {"list_price": 0, "standard_cost": 0, "quantity": 0, "revenue": 0, "gross_profit": 0, "avg_discount_pct": 0}
    return dict(row)
