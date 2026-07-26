"""Reusable data-quality check functions shared by validate.py.

Each check returns a boolean Series that is True where the row is INVALID.
"""
import pandas as pd


def is_null(df: pd.DataFrame, column: str) -> pd.Series:
    return df[column].isna()


def not_in_range(series: pd.Series, low, high) -> pd.Series:
    return (series < low) | (series > high)


def not_in_reference(series: pd.Series, valid_values: pd.Series) -> pd.Series:
    return ~series.isin(set(valid_values))


def combine_reasons(df: pd.DataFrame, checks: list[tuple[pd.Series, str]]) -> pd.Series:
    """Given [(invalid_mask, reason), ...], return a 'reason' Series (empty string = valid)."""
    reasons = pd.Series([""] * len(df), index=df.index)
    for mask, reason in checks:
        addition = mask.map(lambda invalid, r=reason: r if invalid else "")
        reasons = reasons.where(reasons != "", addition)
    return reasons
