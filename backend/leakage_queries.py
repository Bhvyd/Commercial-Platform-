"""SQL queries backing Revenue Leakage Detection: excessive discounts,
negative-margin transactions, duplicate invoices, and price inconsistencies.
"""
from datetime import date

from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.queries import FACT_JOIN, _build_where

EXCESSIVE_DISCOUNT_THRESHOLD = 50


def get_leakage_summary(conn: Connection, start_date: date, end_date: date, region, category, segment) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)

    excessive = conn.execute(
        text(f"""
            SELECT COUNT(*) AS count, COALESCE(SUM(f.discount_amount), 0) AS impact
            {FACT_JOIN} WHERE {where_sql} AND f.discount_pct > {EXCESSIVE_DISCOUNT_THRESHOLD}
        """),
        params,
    ).mappings().one()

    neg_margin = conn.execute(
        text(f"""
            SELECT COUNT(*) AS count, COALESCE(SUM(ABS(f.gross_profit)), 0) AS impact
            {FACT_JOIN} WHERE {where_sql} AND f.is_return = false AND f.gross_profit < 0
        """),
        params,
    ).mappings().one()

    duplicates = conn.execute(
        text(f"""
            SELECT COUNT(*) AS count, COALESCE(SUM(revenue), 0) AS impact FROM (
                SELECT f.invoice_number, SUM(f.extended_revenue) AS revenue
                {FACT_JOIN} WHERE {where_sql}
                GROUP BY f.invoice_number
                HAVING COUNT(DISTINCT f.customer_id) > 1 OR COUNT(DISTINCT f.date_key) > 1
            ) sub
        """),
        params,
    ).mappings().one()

    price_inconsistencies = conn.execute(
        text(f"""
            SELECT COUNT(*) AS count, 0 AS impact FROM (
                SELECT f.customer_id, f.product_id, f.date_key
                {FACT_JOIN} WHERE {where_sql}
                GROUP BY f.customer_id, f.product_id, f.date_key
                HAVING COUNT(DISTINCT f.net_price) > 1
            ) sub
        """),
        params,
    ).mappings().one()

    return [
        {"category": "Excessive Discounts (>50%)", "count": excessive["count"], "impact": float(excessive["impact"])},
        {"category": "Negative-Margin Transactions", "count": neg_margin["count"], "impact": float(neg_margin["impact"])},
        {"category": "Duplicate Invoice Numbers", "count": duplicates["count"], "impact": float(duplicates["impact"])},
        {"category": "Price Inconsistencies", "count": price_inconsistencies["count"], "impact": float(price_inconsistencies["impact"])},
    ]


def get_flagged_transactions(conn: Connection, leak_type: str, start_date: date, end_date: date, region, category, segment, limit: int = 50) -> list[dict]:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    params["limit"] = limit

    if leak_type == "excessive_discount":
        sql = f"""
            SELECT f.invoice_number, c.customer_name, p.product_name, f.discount_pct, f.net_price, f.gross_profit
            {FACT_JOIN} WHERE {where_sql} AND f.discount_pct > {EXCESSIVE_DISCOUNT_THRESHOLD}
            ORDER BY f.discount_pct DESC LIMIT :limit
        """
    elif leak_type == "negative_margin":
        sql = f"""
            SELECT f.invoice_number, c.customer_name, p.product_name, f.discount_pct, f.net_price, f.gross_profit
            {FACT_JOIN} WHERE {where_sql} AND f.is_return = false AND f.gross_profit < 0
            ORDER BY f.gross_profit ASC LIMIT :limit
        """
    elif leak_type == "duplicate_invoices":
        sql = f"""
            SELECT f.invoice_number, NULL AS customer_name, NULL AS product_name, NULL AS discount_pct,
                   NULL AS net_price, SUM(f.extended_revenue) AS gross_profit
            {FACT_JOIN} WHERE {where_sql}
            GROUP BY f.invoice_number
            HAVING COUNT(DISTINCT f.customer_id) > 1 OR COUNT(DISTINCT f.date_key) > 1
            ORDER BY gross_profit DESC LIMIT :limit
        """
    else:  # price_inconsistencies
        sql = f"""
            SELECT NULL AS invoice_number, c.customer_name, p.product_name, NULL AS discount_pct,
                   NULL AS net_price, COUNT(DISTINCT f.net_price) AS gross_profit
            {FACT_JOIN} WHERE {where_sql}
            GROUP BY c.customer_name, p.product_name
            HAVING COUNT(DISTINCT f.net_price) > 1
            ORDER BY gross_profit DESC LIMIT :limit
        """
    return [dict(r) for r in conn.execute(text(sql), params).mappings()]
