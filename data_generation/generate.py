"""Entry point: generates all raw source-system extracts into RAW_DATA_DIR.

Run: python -m data_generation.generate
"""
from pathlib import Path

import numpy as np
from faker import Faker

from data_generation.dimensions import (
    build_contract_pricing,
    build_customers,
    build_products,
    build_regions,
    build_sales_reps,
)
from data_generation.sales import generate_sales
from utils.config import GEN_SEED, RAW_DATA_DIR
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def main() -> None:
    rng = np.random.default_rng(GEN_SEED)
    Faker.seed(GEN_SEED)
    fake = Faker()

    out_dir = Path(RAW_DATA_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating dimensions...")
    regions = build_regions()
    sales_reps = build_sales_reps(rng, fake)
    customers = build_customers(rng, fake)
    products = build_products(rng)
    contract_pricing = build_contract_pricing(rng, customers, products)

    logger.info("Generating sales transactions...")
    sales = generate_sales(customers, products, sales_reps, contract_pricing, rng)

    files = {
        "regions.csv": regions,
        "sales_reps.csv": sales_reps,
        "customers.csv": customers,
        "products.csv": products,
        "contract_pricing.csv": contract_pricing,
        "sales.csv": sales,
    }
    for filename, df in files.items():
        path = out_dir / filename
        df.to_csv(path, index=False)
        logger.info("Wrote %s rows=%d", path, len(df))

    _self_check(sales, customers)


def _self_check(sales, customers) -> None:
    """Assert the generator actually produced the anomalies later modules need."""
    n = len(sales)
    assert n > 400_000, f"expected substantial sales volume, got {n}"

    negative_margin = (sales["net_price"] < sales["unit_cost"]).sum()
    excessive_discount = (sales["discount_pct"] > 50).sum()
    invoice_identity = sales.groupby("invoice_number")[["invoice_date", "customer_code"]].nunique()
    duplicate_invoices = (invoice_identity["invoice_date"] > 1).sum() + (invoice_identity["customer_code"] > 1).sum()

    assert negative_margin > 0, "expected some negative-margin rows"
    assert excessive_discount > 0, "expected some excessive-discount rows"
    assert duplicate_invoices > 0, "expected some invoice numbers shared across distinct invoices"
    assert sales["customer_code"].isin(customers["customer_code"]).all(), "orphan customer_code in sales"

    logger.info(
        "Self-check passed: rows=%d negative_margin=%d excessive_discount=%d duplicate_invoices=%d",
        n,
        negative_margin,
        excessive_discount,
        duplicate_invoices,
    )


if __name__ == "__main__":
    main()
