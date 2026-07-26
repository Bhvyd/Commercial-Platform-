"""FastAPI entry point.

Run: uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.customers import router as customers_router
from backend.routers.insights import router as insights_router
from backend.routers.kpis import router as kpis_router
from backend.routers.leakage import router as leakage_router
from backend.routers.pricing import router as pricing_router
from backend.routers.profitability import router as profitability_router
from backend.routers.report import router as report_router
from backend.routers.sales import router as sales_router

app = FastAPI(title="Commercial Performance Intelligence Platform API")

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
