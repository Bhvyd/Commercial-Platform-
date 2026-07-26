"""Extract stage: read raw source-system extracts into DataFrames."""
import pandas as pd

from etl.config import RAW_DIR

DATE_COLUMNS = {
    "customers": ["since_date"],
    "sales_reps": ["hire_date"],
    "contract_pricing": ["effective_start", "effective_end"],
    "sales": ["invoice_date"],
}


def extract_all() -> dict[str, pd.DataFrame]:
    tables = {}
    for name in ["regions", "sales_reps", "customers", "products", "contract_pricing", "sales"]:
        path = RAW_DIR / f"{name}.csv"
        tables[name] = pd.read_csv(path, parse_dates=DATE_COLUMNS.get(name, []))
    return tables
