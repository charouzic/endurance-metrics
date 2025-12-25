"""Weekly aggregation and rolling average calculations."""

import pandas as pd
from typing import Tuple


def calculate_weekly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate activities by week.

    Args:
        df: Activities DataFrame.

    Returns:
        Weekly aggregated DataFrame with columns:
        - year_week, year, iso_week
        - total_distance_km, total_elevation_m, total_duration_min
        - activity_count
        - week_start_date (for plotting)
    """
    if df.empty:
        return pd.DataFrame()

    weekly = df.groupby("year_week").agg({
        "distance_km": "sum",
        "elevation_m": "sum",
        "duration_min": "sum",
        "activity_id": "count",
        "datetime": "min"  # Get earliest activity datetime in week
    }).reset_index()

    weekly.columns = ["year_week", "total_distance_km", "total_elevation_m",
                      "total_duration_min", "activity_count", "week_start_date"]

    # Extract year and week number for sorting
    weekly["year"] = weekly["year_week"].str[:4].astype(int)
    weekly["iso_week"] = weekly["year_week"].str[-2:].astype(int)

    # Sort chronologically
    weekly = weekly.sort_values(["year", "iso_week"]).reset_index(drop=True)

    return weekly


def add_rolling_averages(weekly_df: pd.DataFrame, windows: list = [4]) -> pd.DataFrame:
    """
    Add rolling average columns to weekly stats.

    Args:
        weekly_df: Weekly stats DataFrame.
        windows: List of window sizes (in weeks).

    Returns:
        DataFrame with additional rolling average columns.
    """
    result = weekly_df.copy()

    for window in windows:
        result[f"distance_km_{window}w_avg"] = (
            result["total_distance_km"].rolling(window=window, min_periods=1).mean()
        )
        result[f"elevation_m_{window}w_avg"] = (
            result["total_elevation_m"].rolling(window=window, min_periods=1).mean()
        )

    return result


def get_weekly_by_sport(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate weekly stats broken down by sport type.

    Args:
        df: Activities DataFrame.

    Returns:
        Weekly DataFrame with sport breakdown.
    """
    if df.empty:
        return pd.DataFrame()

    weekly_sport = df.groupby(["year_week", "sport"]).agg({
        "distance_km": "sum",
        "elevation_m": "sum",
        "duration_min": "sum",
        "activity_id": "count"
    }).reset_index()

    weekly_sport.columns = ["year_week", "sport", "distance_km",
                           "elevation_m", "duration_min", "activity_count"]

    return weekly_sport


def find_best_week(weekly_df: pd.DataFrame, metric: str = "total_distance_km") -> Tuple[str, float]:
    """
    Find the week with the highest value for a metric.

    Args:
        weekly_df: Weekly stats DataFrame.
        metric: Column name to find maximum.

    Returns:
        Tuple of (year_week, value).
    """
    if weekly_df.empty:
        return ("N/A", 0.0)

    best_row = weekly_df.loc[weekly_df[metric].idxmax()]
    return (best_row["year_week"], best_row[metric])
