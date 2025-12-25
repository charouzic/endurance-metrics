"""Raw data exploration and export page."""

import streamlit as st
import pandas as pd
from endurance_metrics.config import AppConfig
from endurance_metrics.data_loader import load_activities, filter_activities
from endurance_metrics.ui_components import display_sidebar

st.title("📋 Raw Data")

# Load data
config = AppConfig()
filters = display_sidebar()

df = load_activities(config, force_refresh=filters["force_refresh"])

if not df.empty:
    st.session_state["available_sports"] = sorted(df["sport"].unique().tolist())

df_filtered = filter_activities(
    df,
    start_date=filters["start_date"],
    end_date=filters["end_date"],
    sport_types=filters["sport_types"]
)

if df_filtered.empty:
    st.warning("No activities found for selected filters.")
    st.stop()

# Reset force_refresh flag
if st.session_state.get("force_refresh"):
    st.session_state["force_refresh"] = False

# Display metrics
st.subheader(f"Showing {len(df_filtered)} activities")

# Column selector
st.subheader("Select Columns to Display")

all_columns = df_filtered.columns.tolist()
default_columns = ["name", "datetime", "sport", "distance_km", "duration_min", "elevation_m"]

selected_columns = st.multiselect(
    "Columns",
    options=all_columns,
    default=[col for col in default_columns if col in all_columns]
)

if not selected_columns:
    st.warning("Please select at least one column to display.")
    st.stop()

# Display dataframe
st.divider()
st.subheader("Activity Data")

display_df = df_filtered[selected_columns].copy()

# Format datetime for better readability
if "datetime" in display_df.columns:
    display_df["datetime"] = display_df["datetime"].dt.strftime("%Y-%m-%d %H:%M")

st.dataframe(display_df, width='stretch', height=600)

# Download buttons
st.divider()
st.subheader("Export Data")

col1, col2 = st.columns(2)

with col1:
    csv_data = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name="strava_activities.csv",
        mime="text/csv",
        width='stretch'
    )

with col2:
    # Download filtered data
    filtered_csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered View",
        data=filtered_csv,
        file_name="strava_activities_filtered.csv",
        mime="text/csv",
        width='stretch'
    )

# Data summary
st.divider()
st.subheader("Data Summary")

st.write("**Numeric Columns Summary:**")
numeric_cols = df_filtered.select_dtypes(include=["float64", "int64"]).columns
if len(numeric_cols) > 0:
    st.dataframe(df_filtered[numeric_cols].describe(), width='stretch')

st.write("**Sport Type Distribution:**")
sport_counts = df_filtered["sport"].value_counts()
st.bar_chart(sport_counts)
