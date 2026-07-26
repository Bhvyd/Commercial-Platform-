"""Column contracts for the raw source-system extracts.

Documents what the generator produces and what etl/extract.py expects to read.
Kept as plain dicts (dtype names) rather than a validation library — validate.py
does the actual business-rule checking; this is just the shared contract.
"""

CUSTOMERS_COLUMNS = {
    "customer_code": "string",
    "customer_name": "string",
    "segment": "string",
    "region_code": "string",
    "contract_tier": "string",
    "since_date": "date",
}

PRODUCTS_COLUMNS = {
    "sku": "string",
    "product_name": "string",
    "category": "string",
    "subcategory": "string",
    "brand": "string",
    "standard_cost": "float",
    "list_price": "float",
}

SALES_REPS_COLUMNS = {
    "rep_code": "string",
    "rep_name": "string",
    "region_code": "string",
    "team": "string",
    "hire_date": "date",
}

CONTRACT_PRICING_COLUMNS = {
    "customer_code": "string",
    "sku": "string",
    "negotiated_price": "float",
    "negotiated_discount_pct": "float",
    "effective_start": "date",
    "effective_end": "date",
}

SALES_COLUMNS = {
    "source_row_id": "string",
    "invoice_number": "string",
    "invoice_date": "date",
    "customer_code": "string",
    "sku": "string",
    "rep_code": "string",
    "quantity": "int",
    "unit_price_charged": "float",
    "is_cancelled": "bool",
    "is_return": "bool",
}
