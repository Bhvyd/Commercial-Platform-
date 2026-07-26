from datetime import date

from fastapi import APIRouter, Query

from backend import queries
from backend.schemas import BreakdownItem, FilterOptions, KpiSummary, TrendPoint
from database.connection import engine

router = APIRouter(prefix="/api", tags=["kpis"])


@router.get("/filters/options", response_model=FilterOptions)
def filter_options():
    with engine.connect() as conn:
        return queries.get_filter_options(conn)


@router.get("/kpis/summary", response_model=KpiSummary)
def kpi_summary(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_kpi_summary(conn, start_date, end_date, region, category, segment)


@router.get("/kpis/revenue-trend", response_model=list[TrendPoint])
def revenue_trend(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_revenue_trend(conn, start_date, end_date, region, category, segment)


@router.get("/kpis/revenue-by-region", response_model=list[BreakdownItem])
def revenue_by_region(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_revenue_by_region(conn, start_date, end_date, region, category, segment)


@router.get("/kpis/revenue-by-segment", response_model=list[BreakdownItem])
def revenue_by_segment(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_revenue_by_segment(conn, start_date, end_date, region, category, segment)


@router.get("/kpis/revenue-by-product", response_model=list[BreakdownItem])
def revenue_by_product(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
    limit: int = 10,
):
    with engine.connect() as conn:
        return queries.get_revenue_by_product(conn, start_date, end_date, region, category, segment, limit)
