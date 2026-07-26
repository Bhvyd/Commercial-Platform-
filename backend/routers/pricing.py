from datetime import date

from fastapi import APIRouter, Query

from backend import pricing_queries as queries
from backend.schemas import DiscountBand, ProductPricingDetail
from database.connection import engine

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.get("/discount-bands", response_model=list[DiscountBand])
def discount_bands(
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_discount_bands(conn, start_date, end_date, region, category, segment)


@router.get("/products", response_model=list[str])
def products():
    with engine.connect() as conn:
        return queries.get_product_list(conn)


@router.get("/product-detail", response_model=ProductPricingDetail)
def product_detail(
    product_name: str,
    start_date: date,
    end_date: date,
    region: str | None = Query(None),
    category: str | None = Query(None),
    segment: str | None = Query(None),
):
    with engine.connect() as conn:
        return queries.get_product_pricing_detail(conn, product_name, start_date, end_date, region, category, segment)
