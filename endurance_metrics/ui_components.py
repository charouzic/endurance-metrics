"""Reusable UI components and sidebar."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
import pandas as pd


def setup_page_config():
    """Configure global Streamlit page settings."""
    st.set_page_config(
        page_title="Endurance Metrics",
        page_icon="🏃",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def display_kpi_card(label: str, value: str, delta: Optional[str] = None):
    """
    Display a KPI metric card.

    Args:
        label: Metric label.
        value: Primary value to display.
        delta: Optional delta/change value.
    """
    st.metric(label=label, value=value, delta=delta)


def display_sidebar() -> dict:
    """
    Display sidebar with filters and refresh button.

    Returns:
        Dictionary with filter values.
    """
    with st.sidebar:
        st.title("⚙️ Settings")

        # Refresh button
        st.subheader("Data Management")
        refresh = st.button("🔄 Refresh from Strava", width='stretch')

        if refresh:
            st.session_state["force_refresh"] = True
            st.rerun()
        else:
            st.session_state.setdefault("force_refresh", False)

        st.divider()

        # Date range filter
        st.subheader("Filters")

        # Default to last 5 years
        default_start = datetime.now() - timedelta(days=365*5)
        default_end = datetime.now()

        date_range = st.date_input(
            "Date Range",
            value=(default_start.date(), default_end.date()),
            max_value=datetime.now().date()
        )

        # Handle date range selection
        if isinstance(date_range, tuple):
            if len(date_range) == 2:
                start_date, end_date = date_range
            elif len(date_range) == 1:
                # User is in middle of selecting, use first date for both
                start_date = date_range[0]
                end_date = date_range[0]
            else:
                # Empty tuple, use defaults
                start_date = default_start.date()
                end_date = default_end.date()
        else:
            # Single date object
            start_date = date_range if date_range else default_start.date()
            end_date = datetime.now().date()

        # Sport type filter
        st.session_state.setdefault("available_sports", [])

        # Set default to "Run" if available and not yet selected
        available_sports = st.session_state.get("available_sports", [])
        default_sports = ["Run"] if "Run" in available_sports else None

        sport_types = st.multiselect(
            "Sport Types",
            options=available_sports,
            default=default_sports,
            help="Leave empty to include all sports"
        )

        st.divider()

        # Info section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Endurance Metrics** pulls your training data from Strava
            and provides analytics on your activities.

            - Data is cached locally
            - Use 'Refresh' to update from Strava
            - Rate limits: 100 reads/15min
            """)

        return {
            "start_date": pd.Timestamp(start_date, tz='UTC'),
            "end_date": pd.Timestamp(end_date, tz='UTC') + pd.Timedelta(days=1) - pd.Timedelta(seconds=1),
            "sport_types": sport_types if sport_types else None,
            "force_refresh": st.session_state.get("force_refresh", False)
        }


def create_date_range_selector(df: pd.DataFrame, key_prefix: str = "") -> Tuple[datetime, datetime]:
    """
    Create date range selector based on available data.

    Args:
        df: Activities DataFrame.
        key_prefix: Unique prefix for widget keys.

    Returns:
        Tuple of (start_date, end_date).
    """
    if df.empty:
        return (datetime.now() - timedelta(days=365), datetime.now())

    min_date = df["datetime"].min().to_pydatetime()
    max_date = df["datetime"].max().to_pydatetime()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=max(min_date, datetime.now() - timedelta(days=365)),
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_start"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_end"
        )

    return (start_date, end_date)


def format_duration(minutes: float) -> str:
    """
    Format duration in minutes to human-readable string.

    Args:
        minutes: Duration in minutes.

    Returns:
        Formatted string like "2h 30m".
    """
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m"


def format_distance(km: float) -> str:
    """
    Format distance in km.

    Args:
        km: Distance in kilometers.

    Returns:
        Formatted string like "42.2 km".
    """
    return f"{km:,.1f} km"


def format_elevation(meters: float) -> str:
    """
    Format elevation in meters.

    Args:
        meters: Elevation in meters.

    Returns:
        Formatted string like "1,234 m".
    """
    return f"{meters:,.0f} m"
