"""SQL aggregation queries backing the Profitability Analysis endpoints."""
from datetime import date

from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.queries import FACT_JOIN, NET_PROFIT, NET_REVENUE, _build_where

DIMENSION_COLUMNS = {
    "product": "p.product_name",
    "customer": "c.customer_name",
    "category": "p.category",
    "region": "r.region_name",
    "rep": "sr.rep_name",
}

SORT_COLUMNS = {"gross_profit": "gross_profit", "margin_pct": "margin_pct"}


def get_profitability_by_dimension(
    conn: Connection,
    dimension: str,
    start_date: date,
    end_date: date,
    region,
    category,
    segment,
    sort_by: str = "gross_profit",
    ascending: bool = False,
    limit: int = 15,
) -> list[dict]:
    col = DIMENSION_COLUMNS[dimension]
    sort_col = SORT_COLUMNS.get(sort_by, "gross_profit")
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    params["limit"] = limit
    order = "ASC" if ascending else "DESC"
    sql = f"""
        SELECT
            {col} AS label,
            COALESCE({NET_REVENUE}, 0) AS revenue,
            COALESCE({NET_PROFIT}, 0) AS gross_profit,
            CASE WHEN COALESCE({NET_REVENUE}, 0) = 0 THEN 0
                 ELSE COALESCE({NET_PROFIT}, 0) / NULLIF({NET_REVENUE}, 0) * 100 END AS margin_pct
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY {col}
        ORDER BY {sort_col} {order}
        LIMIT :limit
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def get_margin_trend(conn: Connection, start_date: date, end_date: date, region, category, segment) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT
            DATE_TRUNC('month', f.date_key)::date AS label,
            COALESCE({NET_REVENUE}, 0) AS revenue,
            COALESCE({NET_PROFIT}, 0) AS gross_profit,
            CASE WHEN COALESCE({NET_REVENUE}, 0) = 0 THEN 0
                 ELSE COALESCE({NET_PROFIT}, 0) / NULLIF({NET_REVENUE}, 0) * 100 END AS margin_pct
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY 1
        ORDER BY 1
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]


def get_loss_making_customers(conn: Connection, start_date: date, end_date: date, region, category, segment, limit: int = 15) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    params["limit"] = limit
    sql = f"""
        SELECT
            c.customer_name AS label,
            COALESCE({NET_REVENUE}, 0) AS revenue,
            COALESCE({NET_PROFIT}, 0) AS gross_profit
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY c.customer_name
        HAVING COALESCE({NET_PROFIT}, 0) < 0
        ORDER BY gross_profit ASC
        LIMIT :limit
    """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]
