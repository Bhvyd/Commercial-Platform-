"""Load stage: full-refresh load into the star schema.

A full truncate-and-reload is simplest and correct at this data volume — no
incremental upsert logic needed (YAGNI) since the whole pipeline reruns from
the raw layer each time.
"""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

STAR_SCHEMA_TABLES_IN_LOAD_ORDER = [
    "dim_region",
    "dim_sales_rep",
    "dim_customer",
    "dim_product",
    "dim_contract_pricing",
    "dim_date",
    "fact_sales_line",
]


def reset_warehouse(engine: Engine) -> None:
    with engine.begin() as conn:
        for table in reversed(STAR_SCHEMA_TABLES_IN_LOAD_ORDER):
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))


def load_table(df: pd.DataFrame, table_name: str, engine: Engine) -> None:
    df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=5000, method="multi")
