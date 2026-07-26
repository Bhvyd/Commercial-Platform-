"""Validate stage: schema/business-rule/referential-integrity checks.

Rows that fail are split out with a reason, not silently dropped — the
deliberate discount/margin/duplicate-invoice anomalies from the generator are
NOT rejected here (they're real business events for Revenue Leakage to find
later); only structurally broken rows are quarantined.
"""
import pandas as pd

from etl.config import MAX_DISCOUNT_PCT, MAX_QUANTITY, MIN_DISCOUNT_PCT, MIN_QUANTITY, VALID_DATE_RANGE
from etl.quality import combine_reasons, is_null, not_in_range, not_in_reference


def validate_sales(sales: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame, sales_reps: pd.DataFrame):
    checks = [
        (is_null(sales, "invoice_number"), "missing invoice_number"),
        (is_null(sales, "customer_code"), "missing customer_code"),
        (is_null(sales, "sku"), "missing sku"),
        (not_in_reference(sales["customer_code"], customers["customer_code"]), "unknown customer_code"),
        (not_in_reference(sales["sku"], products["sku"]), "unknown sku"),
        (not_in_reference(sales["rep_code"], sales_reps["rep_code"]), "unknown rep_code"),
        (not_in_range(sales["quantity"], MIN_QUANTITY, MAX_QUANTITY), "quantity out of range"),
        (not_in_range(sales["discount_pct"], MIN_DISCOUNT_PCT, MAX_DISCOUNT_PCT), "discount_pct out of range"),
        (
            not_in_range(sales["invoice_date"], pd.Timestamp(VALID_DATE_RANGE[0]), pd.Timestamp(VALID_DATE_RANGE[1])),
            "invoice_date out of range",
        ),
        (sales["list_price"] <= 0, "non-positive list_price"),
    ]
    reasons = combine_reasons(sales, checks)
    valid = sales[reasons == ""].copy()
    rejected = sales[reasons != ""].copy()
    rejected["reason"] = reasons[reasons != ""]
    return valid, rejected


def validate_dimension(df: pd.DataFrame, key_column: str):
    """Lightweight dimension check: key present and unique."""
    checks = [
        (is_null(df, key_column), f"missing {key_column}"),
        (df[key_column].duplicated(keep="first"), f"duplicate {key_column}"),
    ]
    reasons = combine_reasons(df, checks)
    valid = df[reasons == ""].copy()
    rejected = df[reasons != ""].copy()
    rejected["reason"] = reasons[reasons != ""]
    return valid, rejected
