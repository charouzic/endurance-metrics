"""Data loading, transformation, and caching logic."""

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from pathlib import Path
import streamlit as st
from endurance_metrics.config import AppConfig
from endurance_metrics.strava_client import StravaClient, StravaRateLimitError


def normalize_activities(raw_activities: List[Dict]) -> pd.DataFrame:
    """
    Transform raw Strava activities to normalized DataFrame.

    Args:
        raw_activities: List of activity dicts from Strava API.

    Returns:
        Normalized DataFrame with computed columns.
    """
    if not raw_activities:
        return pd.DataFrame()

    # Extract relevant fields
    activities = []
    for activity in raw_activities:
        # Parse datetime
        dt = pd.to_datetime(activity.get("start_date_local", activity.get("start_date")))

        normalized = {
            "activity_id": activity.get("id"),
            "name": activity.get("name", "Untitled"),
            "datetime": dt,
            "date": dt.date(),
            "sport": activity.get("type", "Unknown"),
            "distance_km": activity.get("distance", 0) / 1000.0,  # meters to km
            "duration_min": activity.get("moving_time", 0) / 60.0,  # seconds to minutes
            "elevation_m": activity.get("total_elevation_gain", 0),
            # Optional fields
            "avg_hr": activity.get("average_heartrate"),
            "suffer_score": activity.get("suffer_score"),
            "power": activity.get("average_watts"),
        }
        activities.append(normalized)

    df = pd.DataFrame(activities)

    # Add computed time columns
    df["year"] = df["datetime"].dt.year
    df["iso_week"] = df["datetime"].dt.isocalendar().week
    df["year_week"] = df["datetime"].dt.strftime("%Y-W%W")
    df["month"] = df["datetime"].dt.strftime("%Y-%m")

    # Sort by datetime descending
    df = df.sort_values("datetime", ascending=False).reset_index(drop=True)

    return df


def save_to_cache(df: pd.DataFrame, config: AppConfig) -> None:
    """
    Save DataFrame to parquet cache file.

    Args:
        df: Activities DataFrame to cache.
        config: Application configuration.
    """
    config.ensure_cache_dir()
    df.to_parquet(config.cache_path, index=False)


def load_from_cache(config: AppConfig) -> Optional[pd.DataFrame]:
    """
    Load DataFrame from parquet cache if it exists.

    Args:
        config: Application configuration.

    Returns:
        Cached DataFrame if exists, None otherwise.
    """
    if config.cache_path.exists():
        df = pd.read_parquet(config.cache_path)
        # Ensure datetime column is properly typed
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    return None


@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def fetch_activities_from_api(_client: StravaClient) -> pd.DataFrame:
    """
    Fetch activities from Strava API with caching.

    Args:
        _client: StravaClient instance (underscore prefix prevents hashing).

    Returns:
        Normalized DataFrame of activities.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(page: int, total: int):
        status_text.text(f"Fetching activities: page {page}, total {total} activities...")
        # Can't update progress bar precisely without knowing total pages
        progress_bar.progress(min(page * 5, 100) / 100)

    try:
        raw_activities = _client.fetch_all_activities(progress_callback=update_progress)
        progress_bar.progress(100)
        status_text.text(f"Successfully fetched {len(raw_activities)} activities!")

        if not raw_activities:
            st.warning("No activities found in your Strava account.")
            return pd.DataFrame()

        df = normalize_activities(raw_activities)

        if df.empty:
            st.warning("Failed to normalize activities data.")
            return pd.DataFrame()

        # Save to cache
        save_to_cache(df, _client.config)

        return df
    finally:
        progress_bar.empty()
        status_text.empty()


def load_activities(config: AppConfig, force_refresh: bool = False) -> pd.DataFrame:
    """
    Load activities with smart caching strategy.

    Args:
        config: Application configuration.
        force_refresh: If True, bypass cache and fetch from API.

    Returns:
        DataFrame of activities.
    """
    client = StravaClient(config)

    if force_refresh:
        # Clear Streamlit cache
        st.cache_data.clear()
        try:
            return fetch_activities_from_api(client)
        except StravaRateLimitError as e:
            st.error(f"🚫 Rate limit exceeded: {e}")
            st.info("Loading from cached data instead...")
            cached_df = load_from_cache(config)
            if cached_df is not None:
                return cached_df
            else:
                st.error("No cached data available. Please try again later.")
                st.stop()
    else:
        # Try cache first, then API
        cached_df = load_from_cache(config)
        if cached_df is not None:
            st.info(f"📦 Loaded {len(cached_df)} activities from cache")
            return cached_df

        # No cache, fetch from API
        try:
            return fetch_activities_from_api(client)
        except StravaRateLimitError as e:
            st.error(f"🚫 Rate limit exceeded: {e}")
            st.stop()


def filter_activities(
    df: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    sport_types: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Filter activities by date range and sport type.

    Args:
        df: Activities DataFrame.
        start_date: Minimum date (inclusive).
        end_date: Maximum date (inclusive).
        sport_types: List of sport types to include (None = all).

    Returns:
        Filtered DataFrame.
    """
    # Return empty DataFrame if input is empty
    if df.empty:
        return df.copy()

    # Check if required columns exist
    if "datetime" not in df.columns:
        st.error(f"DataFrame missing 'datetime' column. Available columns: {df.columns.tolist()}")
        return pd.DataFrame()

    filtered = df.copy()

    if start_date is not None:
        filtered = filtered[filtered["datetime"] >= start_date]

    if end_date is not None:
        filtered = filtered[filtered["datetime"] <= end_date]

    if sport_types and "sport" in filtered.columns:
        filtered = filtered[filtered["sport"].isin(sport_types)]

    return filtered
