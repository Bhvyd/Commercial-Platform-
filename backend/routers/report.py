from datetime import date

from fastapi import APIRouter, Query, Response

from backend.report import build_report_pdf
from database.connection import engine

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/generate")
def generate(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        pdf_bytes = build_report_pdf(conn, start_date, end_date, region, category, segment)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=executive_report.pdf"})
