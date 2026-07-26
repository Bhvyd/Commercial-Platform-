import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from backend.routers.customers import router as customers_router
from backend.routers.insights import router as insights_router
from backend.routers.kpis import router as kpis_router
from backend.routers.leakage import router as leakage_router
from backend.routers.pricing import router as pricing_router
from backend.routers.profitability import router as profitability_router
from backend.routers.report import router as report_router
from backend.routers.sales import router as sales_router
from database.connection import engine
from database.init_db import init_db
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def _ensure_db_ready():
    max_retries = 30
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection verified.")
            break
        except Exception as e:
            if i == max_retries - 1:
                logger.error("Failed to connect to Postgres: %s", e)
                raise
            logger.info("Waiting for database connection... (attempt %d/%d)", i + 1, max_retries)
            time.sleep(2)

    init_db()

    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            if inspector.has_table("fact_sales_line"):
                count = conn.execute(text("SELECT COUNT(*) FROM fact_sales_line")).scalar()
                if count and count > 0:
                    logger.info("Database already populated with %d sales records.", count)
                    return
    except Exception as e:
        logger.warning("Error checking table contents: %s", e)

    logger.info("Database empty. Auto-generating synthetic data and running ETL pipeline...")
    from data_generation.generate import main as generate_main
    from etl.run_pipeline import run as run_etl

    generate_main()
    run_etl()
    logger.info("Automatic database seeding complete.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _ensure_db_ready()
    except Exception as err:
        logger.error("Failed to auto-initialize database on startup: %s", err)
    yield


app = FastAPI(title="Commercial Performance Intelligence Platform API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kpis_router)
app.include_router(profitability_router)
app.include_router(pricing_router)
app.include_router(leakage_router)
app.include_router(sales_router)
app.include_router(customers_router)
app.include_router(insights_router)
app.include_router(report_router)


@app.get("/health")
def health():
    return {"status": "ok"}

