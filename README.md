# Commercial Performance Intelligence Platform

A consulting-grade commercial analytics platform for a fictional B2B industrial
distributor (Grainger/Fastenal-style): executive KPIs, profitability,
pricing/discount analytics with a live pricing simulator, revenue leakage
detection, sales performance with forecasting, customer analytics (RFM), an
auto-generated business insights engine, and one-click executive PDF reporting.

## Architecture

```
Synthetic Data Generator (Python)  →  Raw CSV extracts  →  ETL pipeline  →  PostgreSQL (star schema)
                                                                                   ↑
                                                                              FastAPI backend
                                                                                   ↑
                                                                          Streamlit frontend (8 tabs)
```

See [DESIGN.md](DESIGN.md) for the visual system and `docs/` for module-level notes.

## Prerequisites

- Docker + Docker Compose
- Python 3.12+ (for the one-time data generation/ETL step, run from the host)

## Quick start

**1. Start Postgres**

```bash
docker compose up -d postgres
```

**2. Set up a Python environment (host-side, for data generation/ETL only)**

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

**3. Create the warehouse schema, generate synthetic data, and run the ETL pipeline**

```bash
python -m database.init_db
python -m data_generation.generate
python -m etl.run_pipeline
```

This produces ~750 products, ~3,000 customers, ~75 sales reps, and ~600K+
transaction lines across 2023–2025, with deliberate data-quality anomalies
(excessive discounts, negative-margin transactions, duplicate invoices, price
inconsistencies) seeded in for the Revenue Leakage Detection module to find.

**4. Start the backend and frontend**

```bash
docker compose up -d --build backend frontend
```

**5. Open the dashboard**

http://localhost:8501 — the FastAPI backend is at http://localhost:8000
(interactive API docs at http://localhost:8000/docs).

## Project structure

```
data_generation/   synthetic source-system generator
etl/               extract → validate → clean → transform → load pipeline
database/          SQLAlchemy models (star schema) + init script
backend/           FastAPI app: routers, SQL query modules, PDF report builder
frontend/          Streamlit app: app.py (entry) + sections/ (one module each)
utils/             shared config
docs/              module notes
```

## Modules

1. Foundation — ETL pipeline, star schema, synthetic warehouse
2. Executive Summary — KPIs, revenue trend, regional/segment/product breakdowns
3. Profitability Analysis — profit by product/customer/category/region/rep, loss-making customers
4. Pricing & Discount Analytics — discount-band margin erosion + live pricing simulator
5. Revenue Leakage Detection — excessive discounts, negative margin, duplicate invoices, price inconsistencies
6. Sales Performance — trends, regional/rep/product performance, 3-month forecast
7. Customer Analytics — RFM segmentation, repeat purchase rate, high-value customers
8. Business Insights Engine — rule-based recommendations generated from live data
9. Executive Reporting — one-click PDF export of the above, for the filters currently selected

## Development (without Docker for backend/frontend)

```bash
source .venv/Scripts/activate
uvicorn backend.main:app --reload --port 8000
streamlit run frontend/app.py --server.port 8501
```
