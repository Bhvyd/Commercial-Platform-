"""Orchestrates the ETL pipeline: extract -> validate -> clean -> transform -> load.

Run: python -m etl.run_pipeline
"""
from datetime import datetime, timezone

from database.connection import engine
from etl.audit import log_rejected, log_stage
from etl.clean import clean_sales
from etl.extract import extract_all
from etl.load import STAR_SCHEMA_TABLES_IN_LOAD_ORDER, load_table, reset_warehouse
from etl.transform import (
    build_dim_date,
    transform_contract_pricing,
    transform_customers,
    transform_fact_sales,
    transform_products,
    transform_regions,
    transform_sales_reps,
)
from etl.validate import validate_dimension, validate_sales
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def run() -> str:
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    logger.info("Starting ETL batch %s", batch_id)

    # --- extract ---
    t0 = datetime.now(timezone.utc)
    raw = extract_all()
    log_stage(batch_id, "extract", 0, sum(len(df) for df in raw.values()), 0, t0)

    # --- validate ---
    t0 = datetime.now(timezone.utc)
    valid_regions, _ = validate_dimension(raw["regions"], "region_code")
    valid_reps, rej_reps = validate_dimension(raw["sales_reps"], "rep_code")
    valid_customers, rej_customers = validate_dimension(raw["customers"], "customer_code")
    valid_products, rej_products = validate_dimension(raw["products"], "sku")
    valid_sales, rejected_sales = validate_sales(raw["sales"], valid_customers, valid_products, valid_reps)
    log_stage(
        batch_id, "validate", len(raw["sales"]), len(valid_sales), len(rejected_sales), t0,
        notes=f"dim rejects: reps={len(rej_reps)} customers={len(rej_customers)} products={len(rej_products)}",
    )
    log_rejected(batch_id, "validate", rejected_sales)

    # --- clean ---
    t0 = datetime.now(timezone.utc)
    cleaned_sales = clean_sales(valid_sales)
    log_stage(batch_id, "clean", len(valid_sales), len(cleaned_sales), 0, t0)

    # --- transform ---
    t0 = datetime.now(timezone.utc)
    dim_regions = transform_regions(valid_regions)
    region_map = dict(zip(dim_regions["region_code"], dim_regions["region_id"]))

    dim_reps = transform_sales_reps(valid_reps, region_map)
    rep_map = dict(zip(dim_reps["rep_code"], dim_reps["sales_rep_id"]))

    dim_customers = transform_customers(valid_customers, region_map)
    customer_map = dict(zip(dim_customers["customer_code"], dim_customers["customer_id"]))
    customer_region = dict(zip(valid_customers["customer_code"], valid_customers["region_code"]))

    dim_products = transform_products(valid_products)
    product_map = dict(zip(dim_products["sku"], dim_products["product_id"]))

    valid_contracts, _ = validate_dimension(raw["contract_pricing"], "contract_pricing_id")
    dim_contracts = transform_contract_pricing(valid_contracts, customer_map, product_map)

    dim_dates = build_dim_date(cleaned_sales["invoice_date"].min(), cleaned_sales["invoice_date"].max())

    fact_sales = transform_fact_sales(cleaned_sales, customer_map, product_map, rep_map, region_map, customer_region)
    log_stage(batch_id, "transform", len(cleaned_sales), len(fact_sales), 0, t0)

    # --- load ---
    t0 = datetime.now(timezone.utc)
    reset_warehouse(engine)
    load_table(dim_regions, "dim_region", engine)
    load_table(dim_reps, "dim_sales_rep", engine)
    load_table(dim_customers, "dim_customer", engine)
    load_table(dim_products, "dim_product", engine)
    load_table(dim_contracts, "dim_contract_pricing", engine)
    load_table(dim_dates, "dim_date", engine)
    load_table(fact_sales, "fact_sales_line", engine)
    log_stage(batch_id, "load", len(fact_sales), len(fact_sales), 0, t0, notes=",".join(STAR_SCHEMA_TABLES_IN_LOAD_ORDER))

    logger.info("ETL batch %s complete: %d fact rows loaded", batch_id, len(fact_sales))
    return batch_id


if __name__ == "__main__":
    run()
