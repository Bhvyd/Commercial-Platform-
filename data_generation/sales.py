"""Generates the sales transaction extract (invoice line items), including
deliberate anomalies that Revenue Leakage Detection (a later module) must find.

Vectorized with numpy/pandas rather than row-by-row Faker calls, since this
extract is the bulk of the data volume (~600K-900K rows).
"""
import numpy as np
import pandas as pd

from utils.config import GEN_END_DATE, GEN_START_DATE

TARGET_INVOICE_LINES = 700_000
AVG_LINES_PER_INVOICE = 2.7

# Anomaly injection rates — small but non-zero, applied on top of otherwise-clean data.
RATE_EXCESSIVE_DISCOUNT = 0.02
RATE_NEGATIVE_MARGIN = 0.015
RATE_DUPLICATE_INVOICE = 0.01
RATE_PRICE_INCONSISTENCY = 0.01
RATE_RETURN_BASE = 0.03
RATE_CANCEL_BASE = 0.02
PROBLEM_CUSTOMER_FRACTION = 0.05  # subset of customers with elevated return/cancel rates

TIER_BASE_DISCOUNT = {
    "Tier1": (12, 5),
    "Tier2": (8, 4),
    "Tier3": (4, 3),
    "Standard": (2, 2),
}


def _weighted_customer_ranks(n: int, rng: np.random.Generator) -> np.ndarray:
    """Pareto-ish weighting so a minority of customers place most orders."""
    ranks = np.arange(1, n + 1)
    weights = 1 / np.power(ranks, 0.6)
    return weights / weights.sum()


def generate_sales(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    sales_reps: pd.DataFrame,
    contract_pricing: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    n_invoices = int(TARGET_INVOICE_LINES / AVG_LINES_PER_INVOICE)

    # --- invoice-level attributes ---
    all_days = pd.date_range(GEN_START_DATE, GEN_END_DATE, freq="D")
    day_of_week = all_days.dayofweek.to_numpy()
    weekday_weight = np.where(day_of_week < 5, 1.0, 0.25)
    trend_weight = np.linspace(0.7, 1.3, len(all_days))  # mild growth over time
    day_weights = weekday_weight * trend_weight
    day_weights = day_weights / day_weights.sum()
    invoice_dates = rng.choice(all_days, size=n_invoices, p=day_weights)

    cust_shuffled = customers.sample(frac=1.0, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)
    cust_weights = _weighted_customer_ranks(len(cust_shuffled), rng)
    cust_idx = rng.choice(len(cust_shuffled), size=n_invoices, p=cust_weights)
    invoice_customers = cust_shuffled.iloc[cust_idx].reset_index(drop=True)

    lines_per_invoice = rng.choice([1, 2, 3, 4, 5], size=n_invoices, p=[0.30, 0.30, 0.20, 0.12, 0.08])

    invoice_seq = np.arange(1, n_invoices + 1)
    invoice_numbers = np.array([f"INV{n:08d}" for n in invoice_seq])

    invoices = pd.DataFrame(
        {
            "invoice_number": invoice_numbers,
            "invoice_date": invoice_dates,
            "customer_code": invoice_customers["customer_code"].to_numpy(),
            "region_code": invoice_customers["region_code"].to_numpy(),
            "contract_tier": invoice_customers["contract_tier"].to_numpy(),
            "n_lines": lines_per_invoice,
        }
    )

    # --- duplicate invoice numbers (anomaly) ---
    dup_mask = rng.random(n_invoices) < RATE_DUPLICATE_INVOICE
    if dup_mask.sum() > 0:
        donor_idx = rng.integers(0, n_invoices, size=dup_mask.sum())
        invoices.loc[dup_mask, "invoice_number"] = invoices["invoice_number"].to_numpy()[donor_idx]

    # --- expand to line level ---
    lines = invoices.loc[invoices.index.repeat(invoices["n_lines"])].reset_index(drop=True)
    n_lines = len(lines)

    prod_sample_idx = rng.integers(0, len(products), size=n_lines)
    prod_lines = products.iloc[prod_sample_idx].reset_index(drop=True)
    lines["sku"] = prod_lines["sku"].to_numpy()
    lines["list_price"] = prod_lines["list_price"].to_numpy().astype(float)
    lines["unit_cost"] = prod_lines["standard_cost"].to_numpy().astype(float)

    # rep assignment: random rep within the invoice's region
    reps_by_region = {
        region: group["rep_code"].to_numpy() for region, group in sales_reps.groupby("region_code")
    }
    rep_codes = np.empty(n_lines, dtype=object)
    for region, rep_pool in reps_by_region.items():
        mask = (lines["region_code"] == region).to_numpy()
        count = mask.sum()
        if count:
            rep_codes[mask] = rep_pool[rng.integers(0, len(rep_pool), size=count)]
    lines["rep_code"] = rep_codes

    lines["quantity"] = rng.poisson(lam=6, size=n_lines).clip(min=1) + 1

    # --- contract pricing lookup ---
    contracts = contract_pricing[["customer_code", "sku", "negotiated_discount_pct", "effective_start", "effective_end"]]
    lines = lines.merge(contracts, on=["customer_code", "sku"], how="left")
    has_contract = lines["negotiated_discount_pct"].notna() & (
        lines["invoice_date"] >= lines["effective_start"]
    ) & (lines["invoice_date"] <= lines["effective_end"])

    # --- baseline discount by tier (no contract) ---
    tier_mean = lines["contract_tier"].map(lambda t: TIER_BASE_DISCOUNT[t][0]).to_numpy(dtype=float)
    tier_std = lines["contract_tier"].map(lambda t: TIER_BASE_DISCOUNT[t][1]).to_numpy(dtype=float)
    baseline_discount = rng.normal(tier_mean, tier_std).clip(0, 40)

    discount_pct = np.where(has_contract, lines["negotiated_discount_pct"].to_numpy(dtype=float), baseline_discount)
    discount_pct = np.clip(discount_pct, 0, 95)

    # --- anomalies ---
    excessive_mask = rng.random(n_lines) < RATE_EXCESSIVE_DISCOUNT
    discount_pct = np.where(excessive_mask, rng.uniform(55, 85, size=n_lines), discount_pct)

    net_price = lines["list_price"].to_numpy() * (1 - discount_pct / 100)

    negative_margin_mask = rng.random(n_lines) < RATE_NEGATIVE_MARGIN
    net_price = np.where(
        negative_margin_mask,
        lines["unit_cost"].to_numpy() * rng.uniform(0.75, 0.98, size=n_lines),
        net_price,
    )

    # price inconsistency: perturb a random subset independent of contract/discount logic
    inconsistent_mask = rng.random(n_lines) < RATE_PRICE_INCONSISTENCY
    net_price = np.where(inconsistent_mask, net_price * rng.uniform(0.7, 1.3, size=n_lines), net_price)
    net_price = np.round(net_price, 2)

    lines["discount_pct"] = np.round(discount_pct, 2)
    lines["net_price"] = net_price
    lines["discount_amount"] = np.round((lines["list_price"] - lines["net_price"]) * lines["quantity"], 2)

    # --- returns / cancellations, elevated for a subset of "problem" customers ---
    unique_customers = lines["customer_code"].unique()
    n_problem = max(1, int(len(unique_customers) * PROBLEM_CUSTOMER_FRACTION))
    problem_customers = set(rng.choice(unique_customers, size=n_problem, replace=False))
    is_problem = lines["customer_code"].isin(problem_customers).to_numpy()

    return_rate = np.where(is_problem, RATE_RETURN_BASE * 5, RATE_RETURN_BASE)
    cancel_rate = np.where(is_problem, RATE_CANCEL_BASE * 5, RATE_CANCEL_BASE)
    lines["is_return"] = rng.random(n_lines) < return_rate
    lines["is_cancelled"] = rng.random(n_lines) < cancel_rate

    lines["source_row_id"] = [f"SRC{i:09d}" for i in range(1, n_lines + 1)]

    return lines[
        [
            "source_row_id",
            "invoice_number",
            "invoice_date",
            "customer_code",
            "sku",
            "rep_code",
            "quantity",
            "list_price",
            "unit_cost",
            "discount_pct",
            "net_price",
            "discount_amount",
            "is_cancelled",
            "is_return",
        ]
    ]
