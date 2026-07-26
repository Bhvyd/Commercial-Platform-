from datetime import date

from fastapi import APIRouter, Query

from backend import sales_queries as queries
from backend.schemas import RevenueForecastPoint
from database.connection import engine

router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.get("/forecast", response_model=list[RevenueForecastPoint])
def forecast(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    periods_ahead: int = 3,
):
    with engine.connect() as conn:
        return queries.get_revenue_forecast(conn, start_date, end_date, region, category, segment, periods_ahead)
