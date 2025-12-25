"""Yearly aggregation and year-over-year comparisons."""

import pandas as pd
from typing import Tuple


def calculate_yearly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate activities by year.

    Args:
        df: Activities DataFrame.

    Returns:
        Yearly aggregated DataFrame.
    """
    if df.empty:
        return pd.DataFrame()

    yearly = df.groupby("year").agg({
        "distance_km": "sum",
        "elevation_m": "sum",
        "duration_min": "sum",
        "activity_id": "count"
    }).reset_index()

    yearly.columns = ["year", "total_distance_km", "total_elevation_m",
                      "total_duration_min", "activity_count"]

    # Sort by year
    yearly = yearly.sort_values("year").reset_index(drop=True)

    return yearly


def calculate_yoy_change(yearly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate year-over-year percentage changes.

    Args:
        yearly_df: Yearly stats DataFrame.

    Returns:
        DataFrame with YoY change columns.
    """
    result = yearly_df.copy()

    for col in ["total_distance_km", "total_elevation_m", "total_duration_min", "activity_count"]:
        result[f"{col}_yoy_change"] = result[col].pct_change() * 100

    return result


def calculate_monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate activities by month.

    Args:
        df: Activities DataFrame.

    Returns:
        Monthly aggregated DataFrame.
    """
    if df.empty:
        return pd.DataFrame()

    monthly = df.groupby("month").agg({
        "distance_km": "sum",
        "elevation_m": "sum",
        "duration_min": "sum",
        "activity_id": "count"
    }).reset_index()

    monthly.columns = ["month", "total_distance_km", "total_elevation_m",
                       "total_duration_min", "activity_count"]

    return monthly.sort_values("month").reset_index(drop=True)


def find_best_month(monthly_df: pd.DataFrame, metric: str = "total_distance_km") -> Tuple[str, float]:
    """
    Find the best month for a given metric.

    Args:
        monthly_df: Monthly stats DataFrame.
        metric: Column name to find maximum.

    Returns:
        Tuple of (month, value).
    """
    if monthly_df.empty:
        return ("N/A", 0.0)

    best_row = monthly_df.loc[monthly_df[metric].idxmax()]
    return (best_row["month"], best_row[metric])


def get_yearly_by_sport(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate yearly stats broken down by sport type.

    Args:
        df: Activities DataFrame.

    Returns:
        Yearly DataFrame with sport breakdown.
    """
    if df.empty:
        return pd.DataFrame()

    yearly_sport = df.groupby(["year", "sport"]).agg({
        "distance_km": "sum",
        "elevation_m": "sum",
        "duration_min": "sum",
        "activity_id": "count"
    }).reset_index()

    yearly_sport.columns = ["year", "sport", "distance_km",
                           "elevation_m", "duration_min", "activity_count"]

    return yearly_sport
