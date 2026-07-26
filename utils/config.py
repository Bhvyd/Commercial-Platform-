"""Central config loaded from environment variables (.env)."""
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes")


POSTGRES_USER = os.getenv("POSTGRES_USER", "cpip")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cpip")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cpip")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

GEN_SEED = int(os.getenv("GEN_SEED", "42"))
GEN_NUM_CUSTOMERS = int(os.getenv("GEN_NUM_CUSTOMERS", "3000"))
GEN_NUM_PRODUCTS = int(os.getenv("GEN_NUM_PRODUCTS", "750"))
GEN_NUM_SALES_REPS = int(os.getenv("GEN_NUM_SALES_REPS", "75"))
GEN_NUM_REGIONS = int(os.getenv("GEN_NUM_REGIONS", "4"))
GEN_START_DATE = date.fromisoformat(os.getenv("GEN_START_DATE", "2023-01-01"))
GEN_END_DATE = date.fromisoformat(os.getenv("GEN_END_DATE", "2025-12-31"))

RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data_generation/raw_output")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
