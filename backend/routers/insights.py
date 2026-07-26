from datetime import date

from fastapi import APIRouter, Query

from backend.insights import generate_insights
from backend.schemas import Insight
from database.connection import engine

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/generate", response_model=list[Insight])
def generate(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return generate_insights(conn, start_date, end_date, region, category, segment)
