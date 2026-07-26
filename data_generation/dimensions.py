"""Generates the dimension ("master data") source extracts: regions, sales reps,
customers, products, and negotiated contract pricing.
"""
import numpy as np
import pandas as pd
from faker import Faker

from utils.config import (
    GEN_END_DATE,
    GEN_NUM_CUSTOMERS,
    GEN_NUM_PRODUCTS,
    GEN_NUM_SALES_REPS,
    GEN_START_DATE,
)

REGIONS = [
    ("NE", "Northeast"),
    ("MW", "Midwest"),
    ("SO", "South"),
    ("WE", "West"),
]

SEGMENTS = ["MRO", "OEM", "Construction", "Government", "Industrial"]
CONTRACT_TIERS = ["Tier1", "Tier2", "Tier3", "Standard"]
TIER_WEIGHTS = [0.10, 0.20, 0.30, 0.40]

CATEGORIES = {
    "Fasteners": ["Bolts", "Screws", "Anchors", "Rivets"],
    "Power Tools": ["Drills", "Saws", "Grinders", "Sanders"],
    "Safety Equipment": ["Gloves", "Eyewear", "Respirators", "Hard Hats"],
    "Electrical": ["Wiring", "Conduit", "Switches", "Breakers"],
    "Plumbing": ["Pipes", "Valves", "Fittings", "Pumps"],
    "Material Handling": ["Pallets", "Hand Trucks", "Shelving", "Conveyors"],
    "Abrasives": ["Sanding Discs", "Grinding Wheels", "Wire Brushes"],
    "HVAC": ["Filters", "Thermostats", "Ductwork", "Fans"],
}
BRANDS = ["Milwaukee", "DeWalt", "3M", "Honeywell", "Bosch", "Generic-Pro", "Ironclad"]


def build_regions() -> pd.DataFrame:
    return pd.DataFrame(
        [{"region_code": c, "region_name": n} for c, n in REGIONS]
    )


def build_sales_reps(rng: np.random.Generator, fake: Faker) -> pd.DataFrame:
    region_codes = [c for c, _ in REGIONS]
    rows = []
    for i in range(GEN_NUM_SALES_REPS):
        region = rng.choice(region_codes)
        hire_date = fake.date_between(start_date=GEN_START_DATE - pd.Timedelta(days=1500), end_date=GEN_END_DATE)
        rows.append(
            {
                "rep_code": f"REP{i + 1:04d}",
                "rep_name": fake.name(),
                "region_code": region,
                "team": f"{region}-Team-{rng.integers(1, 4)}",
                "hire_date": hire_date,
            }
        )
    return pd.DataFrame(rows)


def build_customers(rng: np.random.Generator, fake: Faker) -> pd.DataFrame:
    region_codes = [c for c, _ in REGIONS]
    rows = []
    for i in range(GEN_NUM_CUSTOMERS):
        rows.append(
            {
                "customer_code": f"CUST{i + 1:05d}",
                "customer_name": fake.company(),
                "segment": rng.choice(SEGMENTS),
                "region_code": rng.choice(region_codes),
                "contract_tier": rng.choice(CONTRACT_TIERS, p=TIER_WEIGHTS),
                "since_date": fake.date_between(start_date=GEN_START_DATE - pd.Timedelta(days=2000), end_date=GEN_END_DATE),
            }
        )
    return pd.DataFrame(rows)


def build_products(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    cats = list(CATEGORIES.keys())
    for i in range(GEN_NUM_PRODUCTS):
        category = rng.choice(cats)
        subcategory = rng.choice(CATEGORIES[category])
        standard_cost = round(float(rng.uniform(2.0, 400.0)), 2)
        margin = float(rng.uniform(0.20, 0.45))
        list_price = round(standard_cost / (1 - margin), 2)
        rows.append(
            {
                "sku": f"SKU{i + 1:05d}",
                "product_name": f"{subcategory[:-1] if subcategory.endswith('s') else subcategory} {rng.choice(BRANDS)} #{i + 1}",
                "category": category,
                "subcategory": subcategory,
                "brand": rng.choice(BRANDS),
                "standard_cost": standard_cost,
                "list_price": list_price,
            }
        )
    return pd.DataFrame(rows)


def build_contract_pricing(rng: np.random.Generator, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Negotiated pricing for a subset of (customer, product) pairs.

    Only Tier1/Tier2 customers get negotiated contracts, and only for a
    sample of products they're likely to buy repeatedly.
    """
    eligible = customers[customers["contract_tier"].isin(["Tier1", "Tier2"])]
    rows = []
    contract_id = 1
    for _, cust in eligible.iterrows():
        n_products = rng.integers(3, 15)
        prod_sample = products.sample(n=n_products, random_state=int(rng.integers(0, 1_000_000)))
        for _, prod in prod_sample.iterrows():
            discount_pct = round(float(rng.uniform(5, 25)), 2)
            negotiated_price = round(float(prod["list_price"]) * (1 - discount_pct / 100), 2)
            start = GEN_START_DATE + pd.Timedelta(days=int(rng.integers(0, 300)))
            rows.append(
                {
                    "contract_pricing_id": contract_id,
                    "customer_code": cust["customer_code"],
                    "sku": prod["sku"],
                    "negotiated_price": negotiated_price,
                    "negotiated_discount_pct": discount_pct,
                    "effective_start": start,
                    "effective_end": GEN_END_DATE,
                }
            )
            contract_id += 1
    return pd.DataFrame(rows)
