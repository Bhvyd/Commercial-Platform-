"""ETL-specific settings: paths and validation thresholds.

DB connection lives in utils.config / database.connection — this module only
holds thresholds that are ETL business rules, not infrastructure.
"""
from pathlib import Path

from utils.config import GEN_END_DATE, GEN_START_DATE, RAW_DATA_DIR

RAW_DIR = Path(RAW_DATA_DIR)

# Business-rule bounds used by validate.py — a row outside these is quarantined,
# not silently fixed, because it indicates a genuinely broken record (as opposed
# to the deliberate discount/margin anomalies which are real business events).
VALID_DATE_RANGE = (GEN_START_DATE, GEN_END_DATE)
MIN_QUANTITY = 1
MAX_QUANTITY = 10_000
MIN_DISCOUNT_PCT = 0
MAX_DISCOUNT_PCT = 100
