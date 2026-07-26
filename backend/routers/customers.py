from datetime import date

from fastapi import APIRouter, Query

from backend import customer_queries as queries
from backend.schemas import RepeatPurchaseStats, RfmResponse
from database.connection import engine

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("/rfm", response_model=RfmResponse)
def rfm(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    limit: int = 20,
):
    with engine.connect() as conn:
        return queries.get_rfm(conn, start_date, end_date, region, category, segment, limit)


@router.get("/repeat-purchase", response_model=RepeatPurchaseStats)
def repeat_purchase(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_repeat_purchase_stats(conn, start_date, end_date, region, category, segment)
