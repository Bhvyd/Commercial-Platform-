"""Star schema for the Commercial Performance Intelligence Platform warehouse.

Grain of fact_sales_line: one product line item on one invoice.
Dimensions use SCD Type 1 (overwrite on change) — no history tracking needed.
"""
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DimDate(Base):
    __tablename__ = "dim_date"

    date_key: Mapped[date] = mapped_column(Date, primary_key=True)
    year: Mapped[int]
    quarter: Mapped[int]
    month: Mapped[int]
    month_name: Mapped[str] = mapped_column(String(20))
    week: Mapped[int]
    day_of_week: Mapped[int]
    day_name: Mapped[str] = mapped_column(String(20))
    is_weekend: Mapped[bool] = mapped_column(Boolean)
    fiscal_year: Mapped[int]
    fiscal_quarter: Mapped[int]


class DimRegion(Base):
    __tablename__ = "dim_region"

    region_id: Mapped[int] = mapped_column(primary_key=True)
    region_code: Mapped[str] = mapped_column(String(10), unique=True)
    region_name: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(50), default="USA")


class DimSalesRep(Base):
    __tablename__ = "dim_sales_rep"

    sales_rep_id: Mapped[int] = mapped_column(primary_key=True)
    rep_code: Mapped[str] = mapped_column(String(20), unique=True)
    rep_name: Mapped[str] = mapped_column(String(100))
    region_id: Mapped[int] = mapped_column(ForeignKey("dim_region.region_id"))
    team: Mapped[str] = mapped_column(String(50))
    hire_date: Mapped[date] = mapped_column(Date)


class DimCustomer(Base):
    __tablename__ = "dim_customer"

    customer_id: Mapped[int] = mapped_column(primary_key=True)
    customer_code: Mapped[str] = mapped_column(String(20), unique=True)
    customer_name: Mapped[str] = mapped_column(String(150))
    segment: Mapped[str] = mapped_column(String(30))
    region_id: Mapped[int] = mapped_column(ForeignKey("dim_region.region_id"))
    contract_tier: Mapped[str] = mapped_column(String(20))
    since_date: Mapped[date] = mapped_column(Date)


class DimProduct(Base):
    __tablename__ = "dim_product"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(30), unique=True)
    product_name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(50))
    subcategory: Mapped[str] = mapped_column(String(50))
    brand: Mapped[str] = mapped_column(String(50))
    standard_cost: Mapped[float] = mapped_column(Numeric(10, 2))
    list_price: Mapped[float] = mapped_column(Numeric(10, 2))


class DimContractPricing(Base):
    """Customer x Product negotiated pricing, effective-dated."""

    __tablename__ = "dim_contract_pricing"
    __table_args__ = (
        UniqueConstraint("customer_id", "product_id", "effective_start", name="uq_contract_key"),
    )

    contract_pricing_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("dim_customer.customer_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("dim_product.product_id"))
    negotiated_price: Mapped[float] = mapped_column(Numeric(10, 2))
    negotiated_discount_pct: Mapped[float] = mapped_column(Numeric(5, 2))
    effective_start: Mapped[date] = mapped_column(Date)
    effective_end: Mapped[date] = mapped_column(Date)


class FactSalesLine(Base):
    __tablename__ = "fact_sales_line"

    sales_line_id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(30), index=True)
    date_key: Mapped[date] = mapped_column(ForeignKey("dim_date.date_key"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("dim_customer.customer_id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("dim_product.product_id"), index=True)
    sales_rep_id: Mapped[int] = mapped_column(ForeignKey("dim_sales_rep.sales_rep_id"), index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("dim_region.region_id"), index=True)

    quantity: Mapped[int]
    list_price: Mapped[float] = mapped_column(Numeric(10, 2))
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2))
    discount_pct: Mapped[float] = mapped_column(Numeric(5, 2))
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    net_price: Mapped[float] = mapped_column(Numeric(10, 2))
    extended_revenue: Mapped[float] = mapped_column(Numeric(14, 2))
    extended_cost: Mapped[float] = mapped_column(Numeric(14, 2))
    gross_profit: Mapped[float] = mapped_column(Numeric(14, 2))

    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_return: Mapped[bool] = mapped_column(Boolean, default=False)
    source_row_id: Mapped[str] = mapped_column(String(50))


class EtlAuditLog(Base):
    __tablename__ = "etl_audit_log"

    audit_id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(50), index=True)
    stage: Mapped[str] = mapped_column(String(30))
    rows_in: Mapped[int]
    rows_out: Mapped[int]
    rows_rejected: Mapped[int]
    started_at: Mapped[datetime] = mapped_column(DateTime)
    finished_at: Mapped[datetime] = mapped_column(DateTime)
    notes: Mapped[str] = mapped_column(String(500), default="")


class RejectedRecord(Base):
    __tablename__ = "rejected_records"

    rejected_id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(50), index=True)
    stage: Mapped[str] = mapped_column(String(30))
    source_row_id: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(String(300))
    raw_payload: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
