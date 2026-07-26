from datetime import date

from fastapi import APIRouter, Query

from backend import profitability_queries as queries
from backend.schemas import MarginTrendPoint, ProfitabilityItem
from database.connection import engine

router = APIRouter(prefix="/api/profitability", tags=["profitability"])

Dimension = str  # "product" | "customer" | "category" | "region" | "rep"


@router.get("/by-dimension", response_model=list[ProfitabilityItem])
def by_dimension(
    dimension: Dimension,
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    sort_by: str = "gross_profit",
    ascending: bool = False,
    limit: int = 15,
):
    with engine.connect() as conn:
        return queries.get_profitability_by_dimension(
            conn, dimension, start_date, end_date, region, category, segment, sort_by, ascending, limit
        )


@router.get("/margin-trend", response_model=list[MarginTrendPoint])
def margin_trend(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_margin_trend(conn, start_date, end_date, region, category, segment)


@router.get("/loss-making-customers", response_model=list[ProfitabilityItem])
def loss_making_customers(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    limit: int = 15,
):
    with engine.connect() as conn:
        results = queries.get_loss_making_customers(conn, start_date, end_date, region, category, segment, limit)
        for r in results:
            r["margin_pct"] = round(r["gross_profit"] / r["revenue"] * 100, 2) if r["revenue"] else 0.0
        return results
