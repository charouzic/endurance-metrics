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

    # Aggregate existing activity data by week
    weekly = df.groupby("year_week", sort=False).agg({
        "distance_km": "sum",
        "elevation_m": "sum",
        "duration_min": "sum",
        "activity_id": "count",
        "week_start": "first"  # Get week start for sorting
    }).reset_index()

    weekly.columns = ["year_week", "total_distance_km", "total_elevation_m",
                      "total_duration_min", "activity_count", "week_start_date"]

    # Create complete date range for all weeks
    min_date = df["week_start"].min()
    max_date = df["week_start"].max()

    # Remove timezone for date range generation
    if hasattr(min_date, 'tz') and min_date.tz is not None:
        min_date = min_date.tz_localize(None)
    if hasattr(max_date, 'tz') and max_date.tz is not None:
        max_date = max_date.tz_localize(None)

    # Generate all Monday dates in the range
    all_mondays = pd.date_range(start=min_date, end=max_date, freq='W-MON')

    # Create complete week labels for all weeks
    complete_weeks = []
    for monday in all_mondays:
        # Convert back to timezone-aware to match original data
        if df["week_start"].dtype.tz is not None:
            monday_tz = pd.Timestamp(monday).tz_localize('UTC')
        else:
            monday_tz = monday

        sunday = monday + pd.Timedelta(days=6)
        week_label = (
            monday.strftime("%Y-W%V") + " (" +
            monday.strftime("%b %d") + " - " +
            sunday.strftime("%b %d") + ")"
        )
        complete_weeks.append({
            "year_week": week_label,
            "week_start_date": monday_tz
        })

    complete_weeks_df = pd.DataFrame(complete_weeks)

    # Merge with actual data, filling missing weeks with zeros
    # Only merge on year_week, then use the week_start_date from complete_weeks
    weekly_complete = complete_weeks_df.merge(
        weekly[["year_week", "total_distance_km", "total_elevation_m", "total_duration_min", "activity_count"]],
        on="year_week",
        how="left"
    )

    # Fill NaN values with 0 for weeks with no activities
    weekly_complete["total_distance_km"] = weekly_complete["total_distance_km"].fillna(0)
    weekly_complete["total_elevation_m"] = weekly_complete["total_elevation_m"].fillna(0)
    weekly_complete["total_duration_min"] = weekly_complete["total_duration_min"].fillna(0)
    weekly_complete["activity_count"] = weekly_complete["activity_count"].fillna(0).astype(int)

    # Sort chronologically by week start date
    weekly_complete = weekly_complete.sort_values("week_start_date").reset_index(drop=True)

    return weekly_complete


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
