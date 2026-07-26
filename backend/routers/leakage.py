from datetime import date

from fastapi import APIRouter, Query

from backend import leakage_queries as queries
from backend.schemas import FlaggedTransaction, LeakageSummaryItem
from database.connection import engine

router = APIRouter(prefix="/api/leakage", tags=["leakage"])


@router.get("/summary", response_model=list[LeakageSummaryItem])
def summary(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_leakage_summary(conn, start_date, end_date, region, category, segment)


@router.get("/transactions", response_model=list[FlaggedTransaction])
def transactions(
    leak_type: str,
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    limit: int = 50,
):
    with engine.connect() as conn:
        return queries.get_flagged_transactions(conn, leak_type, start_date, end_date, region, category, segment, limit)
