"""RFM segmentation and repeat-purchase stats for Customer Analytics."""
from datetime import date

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Connection

from backend.queries import FACT_JOIN, NET_PROFIT, NET_REVENUE, _build_where


def get_rfm(conn: Connection, start_date: date, end_date: date, region, category, segment, limit: int = 20) -> dict:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT
            c.customer_name AS label,
            MAX(f.date_key) AS last_order_date,
            COUNT(DISTINCT f.invoice_number) AS frequency,
            COALESCE({NET_REVENUE}, 0) AS monetary,
            COALESCE({NET_PROFIT}, 0) AS gross_profit
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY c.customer_name
    """
    rows = [dict(r) for r in conn.execute(text(sql), params).mappings()]
    if not rows:
        return {"segments": [], "top_customers": []}

    df = pd.DataFrame(rows)
    df["recency_days"] = (pd.Timestamp(end_date) - pd.to_datetime(df["last_order_date"])).dt.days

    if len(df) < 5:
        df["segment"] = "Regular"
        segment_counts = df["segment"].value_counts().reset_index()
        segment_counts.columns = ["label", "customer_count"]
        top_customers = df.sort_values("monetary", ascending=False).head(limit)[
            ["label", "recency_days", "frequency", "monetary", "gross_profit", "segment"]
        ]
        return {"segments": segment_counts.to_dict("records"), "top_customers": top_customers.to_dict("records")}

    def score(series: pd.Series, higher_is_better: bool) -> pd.Series:
        # rank ascending (smallest value = rank 1), then map that rank's quantile
        # to a 1-5 score in the direction that makes "better" = 5.
        ranked = series.rank(method="first")
        labels = [1, 2, 3, 4, 5] if higher_is_better else [5, 4, 3, 2, 1]
        return pd.qcut(ranked, 5, labels=labels).astype(int)

    df["r_score"] = score(df["recency_days"], higher_is_better=False)  # fewer days since last order = better
    df["f_score"] = score(df["frequency"], higher_is_better=True)
    df["m_score"] = score(df["monetary"], higher_is_better=True)

    def label_segment(row) -> str:
        if row.r_score >= 4 and row.f_score >= 4 and row.m_score >= 4:
            return "Champions"
        if row.r_score <= 2 and row.f_score <= 2:
            return "At Risk"
        if row.f_score >= 4:
            return "Loyal"
        if row.r_score >= 4:
            return "Recent"
        return "Regular"

    df["segment"] = df.apply(label_segment, axis=1)

    segment_counts = df["segment"].value_counts().reset_index()
    segment_counts.columns = ["label", "customer_count"]

    top_customers = df.sort_values("monetary", ascending=False).head(limit)[
        ["label", "recency_days", "frequency", "monetary", "gross_profit", "segment"]
    ]

    return {
        "segments": segment_counts.to_dict("records"),
        "top_customers": top_customers.to_dict("records"),
    }


def get_repeat_purchase_stats(conn: Connection, start_date: date, end_date: date, region, category, segment) -> dict:
    where_sql, params = _build_where(start_date, end_date, region, category, segment)
    sql = f"""
        SELECT COUNT(DISTINCT f.invoice_number) AS order_count
        {FACT_JOIN}
        WHERE {where_sql}
        GROUP BY f.customer_id
    """
    order_counts = [r[0] for r in conn.execute(text(sql), params)]
    if not order_counts:
        return {"total_customers": 0, "repeat_customers": 0, "repeat_rate_pct": 0.0, "avg_orders_per_customer": 0.0}

    total = len(order_counts)
    repeat = sum(1 for c in order_counts if c > 1)
    return {
        "total_customers": total,
        "repeat_customers": repeat,
        "repeat_rate_pct": round(repeat / total * 100, 1),
        "avg_orders_per_customer": round(sum(order_counts) / total, 2),
    }
