"""Detailed weekly analysis page."""

import streamlit as st
import plotly.graph_objects as go
from endurance_metrics.config import AppConfig
from endurance_metrics.data_loader import load_activities, filter_activities
from endurance_metrics.weekly_stats import calculate_weekly_stats, get_weekly_by_sport
from endurance_metrics.ui_components import display_sidebar

st.title("📅 Weekly View")

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

# Chart options
st.subheader("Chart Options")
stack_by_sport = st.checkbox("Stack by sport type", value=False)

st.divider()

# Weekly distance chart
st.subheader("Weekly Distance")

weekly_df = calculate_weekly_stats(df_filtered)

if stack_by_sport:
    # Create stacked bar chart by sport
    weekly_sport = get_weekly_by_sport(df_filtered)

    fig_distance = go.Figure()

    for sport in weekly_sport["sport"].unique():
        sport_data = weekly_sport[weekly_sport["sport"] == sport]
        fig_distance.add_trace(go.Bar(
            x=sport_data["year_week"],
            y=sport_data["distance_km"],
            name=sport
        ))

    fig_distance.update_layout(
        barmode="stack",
        xaxis_title="Week",
        yaxis_title="Distance (km)",
        hovermode="x unified",
        height=400
    )
else:
    # Simple weekly totals
    fig_distance = go.Figure()

    fig_distance.add_trace(go.Bar(
        x=weekly_df["year_week"],
        y=weekly_df["total_distance_km"],
        marker_color="lightblue",
        name="Weekly Distance"
    ))

    fig_distance.update_layout(
        xaxis_title="Week",
        yaxis_title="Distance (km)",
        hovermode="x unified",
        height=400
    )

st.plotly_chart(fig_distance, width='stretch')

# Weekly duration chart
st.subheader("Weekly Duration")

fig_duration = go.Figure()

fig_duration.add_trace(go.Bar(
    x=weekly_df["year_week"],
    y=weekly_df["total_duration_min"],
    marker_color="orange",
    name="Weekly Duration"
))

fig_duration.update_layout(
    xaxis_title="Week",
    yaxis_title="Duration (minutes)",
    hovermode="x unified",
    height=400
)

st.plotly_chart(fig_duration, width='stretch')

# Weekly elevation chart
st.subheader("Weekly Elevation Gain")

fig_elevation = go.Figure()

fig_elevation.add_trace(go.Bar(
    x=weekly_df["year_week"],
    y=weekly_df["total_elevation_m"],
    marker_color="lightgreen",
    name="Weekly Elevation"
))

fig_elevation.update_layout(
    xaxis_title="Week",
    yaxis_title="Elevation (m)",
    hovermode="x unified",
    height=400
)

st.plotly_chart(fig_elevation, width='stretch')

# Weekly stats table
st.divider()
st.subheader("Weekly Statistics")

weekly_df = calculate_weekly_stats(df_filtered)

# Format for display
display_df = weekly_df[["year_week", "total_distance_km", "total_elevation_m",
                        "total_duration_min", "activity_count"]].copy()

display_df.columns = ["Week", "Distance (km)", "Elevation (m)", "Duration (min)", "Activities"]

# Format numbers
display_df["Distance (km)"] = display_df["Distance (km)"].round(1)
display_df["Elevation (m)"] = display_df["Elevation (m)"].round(0)
display_df["Duration (min)"] = display_df["Duration (min)"].round(0)

st.dataframe(display_df, width='stretch', hide_index=True)

# Summary statistics
st.divider()
st.subheader("Summary")

col1, col2, col3 = st.columns(3)

with col1:
    avg_weekly_distance = weekly_df["total_distance_km"].mean()
    st.metric("Avg Weekly Distance", f"{avg_weekly_distance:.1f} km")

with col2:
    avg_weekly_elevation = weekly_df["total_elevation_m"].mean()
    st.metric("Avg Weekly Elevation", f"{avg_weekly_elevation:.0f} m")

with col3:
    avg_weekly_activities = weekly_df["activity_count"].mean()
    st.metric("Avg Activities/Week", f"{avg_weekly_activities:.1f}")
