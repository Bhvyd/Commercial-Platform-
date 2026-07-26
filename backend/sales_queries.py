"""Revenue forecasting for Sales Performance. Simple linear trend extrapolation
on monthly revenue — sufficient for a directional forecast without pulling in
Prophet/statsmodels as a dependency."""
from datetime import date

import numpy as np
from sqlalchemy.engine import Connection

from backend.queries import get_revenue_trend


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def get_revenue_forecast(conn: Connection, start_date: date, end_date: date, region, category, segment, periods_ahead: int = 3) -> list[dict]:
    history = get_revenue_trend(conn, start_date, end_date, region, category, segment)
    points = [{**row, "is_forecast": False} for row in history]
    if len(history) < 2:
        return points

    x = np.arange(len(history))
    y = np.array([float(row["revenue"]) for row in history])
    slope, intercept = np.polyfit(x, y, 1)

    last_month = history[-1]["label"]
    for i in range(1, periods_ahead + 1):
        forecast_month = _add_months(last_month, i)
        forecast_revenue = max(0.0, float(slope * (len(history) - 1 + i) + intercept))
        points.append({"label": forecast_month, "revenue": forecast_revenue, "gross_profit": None, "is_forecast": True})
    return points
