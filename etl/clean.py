"""Clean stage: fix safely-fixable issues. Everything else was already
quarantined in validate.py.
"""
import pandas as pd

CODE_COLUMNS = ["customer_code", "sku", "rep_code", "region_code", "invoice_number"]


def clean_sales(sales: pd.DataFrame) -> pd.DataFrame:
    df = sales.copy()
    for col in CODE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    df = df.drop_duplicates(subset=["source_row_id"], keep="first")
    return df
