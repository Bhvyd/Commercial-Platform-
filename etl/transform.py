"""Transform stage: surrogate keys, dim_date construction, derived fact metrics.

Produces DataFrames whose columns match database.models exactly, ready for load.py.
"""
import pandas as pd


def _with_surrogate_key(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    out = df.reset_index(drop=True).copy()
    out[id_col] = out.index + 1
    return out


def transform_regions(regions: pd.DataFrame) -> pd.DataFrame:
    return _with_surrogate_key(regions, "region_id")[["region_id", "region_code", "region_name"]].assign(country="USA")


def transform_sales_reps(sales_reps: pd.DataFrame, region_map: dict[str, int]) -> pd.DataFrame:
    df = _with_surrogate_key(sales_reps, "sales_rep_id")
    df["region_id"] = df["region_code"].map(region_map)
    return df[["sales_rep_id", "rep_code", "rep_name", "region_id", "team", "hire_date"]]


def transform_customers(customers: pd.DataFrame, region_map: dict[str, int]) -> pd.DataFrame:
    df = _with_surrogate_key(customers, "customer_id")
    df["region_id"] = df["region_code"].map(region_map)
    return df[["customer_id", "customer_code", "customer_name", "segment", "region_id", "contract_tier", "since_date"]]


def transform_products(products: pd.DataFrame) -> pd.DataFrame:
    df = _with_surrogate_key(products, "product_id")
    return df[["product_id", "sku", "product_name", "category", "subcategory", "brand", "standard_cost", "list_price"]]


def transform_contract_pricing(
    contract_pricing: pd.DataFrame, customer_map: dict[str, int], product_map: dict[str, int]
) -> pd.DataFrame:
    df = _with_surrogate_key(contract_pricing, "contract_pricing_id")
    df["customer_id"] = df["customer_code"].map(customer_map)
    df["product_id"] = df["sku"].map(product_map)
    return df[
        [
            "contract_pricing_id",
            "customer_id",
            "product_id",
            "negotiated_price",
            "negotiated_discount_pct",
            "effective_start",
            "effective_end",
        ]
    ]


def build_dim_date(min_date, max_date) -> pd.DataFrame:
    dates = pd.date_range(min_date, max_date, freq="D")
    df = pd.DataFrame({"date_key": dates})
    df["year"] = df["date_key"].dt.year
    df["quarter"] = df["date_key"].dt.quarter
    df["month"] = df["date_key"].dt.month
    df["month_name"] = df["date_key"].dt.month_name()
    df["week"] = df["date_key"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date_key"].dt.dayofweek
    df["day_name"] = df["date_key"].dt.day_name()
    df["is_weekend"] = df["day_of_week"] >= 5
    df["fiscal_year"] = df["year"]
    df["fiscal_quarter"] = df["quarter"]
    return df


def transform_fact_sales(
    sales_clean: pd.DataFrame,
    customer_map: dict[str, int],
    product_map: dict[str, int],
    rep_map: dict[str, int],
    region_map: dict[str, int],
    customer_region: dict[str, str],
) -> pd.DataFrame:
    df = sales_clean.copy()
    df["customer_id"] = df["customer_code"].map(customer_map)
    df["product_id"] = df["sku"].map(product_map)
    df["sales_rep_id"] = df["rep_code"].map(rep_map)
    df["region_id"] = df["customer_code"].map(customer_region).map(region_map)
    df["date_key"] = df["invoice_date"].dt.normalize()

    df["extended_revenue"] = (df["net_price"] * df["quantity"]).round(2)
    df["extended_cost"] = (df["unit_cost"] * df["quantity"]).round(2)
    df["gross_profit"] = (df["extended_revenue"] - df["extended_cost"]).round(2)

    df = df.reset_index(drop=True)
    df["sales_line_id"] = df.index + 1

    return df[
        [
            "sales_line_id",
            "invoice_number",
            "date_key",
            "customer_id",
            "product_id",
            "sales_rep_id",
            "region_id",
            "quantity",
            "list_price",
            "unit_cost",
            "discount_pct",
            "discount_amount",
            "net_price",
            "extended_revenue",
            "extended_cost",
            "gross_profit",
            "is_cancelled",
            "is_return",
            "source_row_id",
        ]
    ]
