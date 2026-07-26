"""Pydantic response models for the KPI API."""
from datetime import date

from pydantic import BaseModel


class FilterOptions(BaseModel):
    regions: list[str]
    categories: list[str]
    segments: list[str]
    min_date: date
    max_date: date


class KpiSummary(BaseModel):
    revenue: float
    gross_profit: float
    gross_margin_pct: float
    average_order_value: float
    active_customers: int
    customer_growth_pct: float | None
    sales_growth_pct: float | None
    prior_period_start: date
    prior_period_end: date


class BreakdownItem(BaseModel):
    label: str
    revenue: float
    gross_profit: float


class TrendPoint(BaseModel):
    label: date
    revenue: float
    gross_profit: float


class ProfitabilityItem(BaseModel):
    label: str
    revenue: float
    gross_profit: float
    margin_pct: float


class MarginTrendPoint(BaseModel):
    label: date
    revenue: float
    gross_profit: float
    margin_pct: float


class DiscountBand(BaseModel):
    label: str
    transaction_count: int
    revenue: float
    gross_profit: float
    margin_pct: float


class ProductPricingDetail(BaseModel):
    list_price: float
    standard_cost: float
    quantity: int
    revenue: float
    gross_profit: float
    avg_discount_pct: float


class LeakageSummaryItem(BaseModel):
    category: str
    count: int
    impact: float


class RevenueForecastPoint(BaseModel):
    label: date
    revenue: float
    gross_profit: float | None
    is_forecast: bool


class FlaggedTransaction(BaseModel):
    invoice_number: str | None
    customer_name: str | None
    product_name: str | None
    discount_pct: float | None
    net_price: float | None
    gross_profit: float | None


class RfmSegmentCount(BaseModel):
    label: str
    customer_count: int


class RfmCustomer(BaseModel):
    label: str
    recency_days: int
    frequency: int
    monetary: float
    gross_profit: float
    segment: str


class RfmResponse(BaseModel):
    segments: list[RfmSegmentCount]
    top_customers: list[RfmCustomer]


class RepeatPurchaseStats(BaseModel):
    total_customers: int
    repeat_customers: int
    repeat_rate_pct: float
    avg_orders_per_customer: float


class Insight(BaseModel):
    title: str
    detail: str
