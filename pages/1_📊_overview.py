"""Overview dashboard page with KPIs and trends."""

import streamlit as st
import plotly.graph_objects as go
from endurance_metrics.config import AppConfig
from endurance_metrics.data_loader import load_activities, filter_activities
from endurance_metrics.weekly_stats import calculate_weekly_stats, add_rolling_averages, find_best_week
from endurance_metrics.yearly_stats import calculate_monthly_stats, find_best_month
from endurance_metrics.ui_components import (
    display_sidebar, display_kpi_card,
    format_distance, format_elevation, format_duration
)

st.title("📊 Overview")

# Load data
config = AppConfig()
filters = display_sidebar()

# Load and filter data
df = load_activities(config, force_refresh=filters["force_refresh"])

# Update available sports in session state
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

# KPI Cards
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_distance = df_filtered["distance_km"].sum()
    display_kpi_card("Total Distance", format_distance(total_distance))

with col2:
    total_elevation = df_filtered["elevation_m"].sum()
    display_kpi_card("Total Elevation", format_elevation(total_elevation))

with col3:
    total_duration = df_filtered["duration_min"].sum()
    display_kpi_card("Total Duration", format_duration(total_duration))

with col4:
    total_activities = len(df_filtered)
    display_kpi_card("Activities", f"{total_activities:,}")

st.divider()

# Weekly distance chart with rolling average
st.subheader("Weekly Distance Trend")

weekly_df = calculate_weekly_stats(df_filtered)
weekly_df = add_rolling_averages(weekly_df, windows=[4])

fig_distance = go.Figure()

# Bar chart for weekly distance
fig_distance.add_trace(go.Bar(
    x=weekly_df["year_week"],
    y=weekly_df["total_distance_km"],
    name="Weekly Distance",
    marker_color="lightblue"
))

# Line chart for 4-week rolling average
fig_distance.add_trace(go.Scatter(
    x=weekly_df["year_week"],
    y=weekly_df["distance_km_4w_avg"],
    name="4-Week Average",
    line=dict(color="red", width=2),
    mode="lines"
))

fig_distance.update_layout(
    xaxis_title="Week",
    yaxis_title="Distance (km)",
    hovermode="x unified",
    height=400,
    xaxis=dict(tickangle=-45)
)

st.plotly_chart(fig_distance, width='stretch')

# Weekly elevation chart
st.subheader("Weekly Elevation Gain")

fig_elevation = go.Figure()

fig_elevation.add_trace(go.Bar(
    x=weekly_df["year_week"],
    y=weekly_df["total_elevation_m"],
    name="Weekly Elevation",
    marker_color="lightgreen"
))

fig_elevation.update_layout(
    xaxis_title="Week",
    yaxis_title="Elevation (m)",
    hovermode="x unified",
    height=400,
    xaxis=dict(tickangle=-45)
)

st.plotly_chart(fig_elevation, width='stretch')

# Weekly duration chart
st.subheader("Weekly Duration")

fig_duration = go.Figure()

fig_duration.add_trace(go.Bar(
    x=weekly_df["year_week"],
    y=weekly_df["total_duration_min"] / 60,  # Convert to hours
    name="Weekly Duration",
    marker_color="orange",
    hovertemplate='%{y:.1f} hours<extra></extra>'
))

fig_duration.update_layout(
    xaxis_title="Week",
    yaxis_title="Duration (hours)",
    hovermode="x unified",
    height=400,
    xaxis=dict(tickangle=-45)
)

st.plotly_chart(fig_duration, width='stretch')

# Best week/month summaries
st.divider()
st.subheader("🏆 Personal Bests")

col1, col2 = st.columns(2)

with col1:
    st.write("**Best Week**")
    best_week, best_distance = find_best_week(weekly_df, "total_distance_km")
    st.metric("Distance", f"{best_distance:.1f} km", delta=best_week)

    best_week_elev, best_elev = find_best_week(weekly_df, "total_elevation_m")
    st.metric("Elevation", f"{best_elev:.0f} m", delta=best_week_elev)

    best_week_duration, best_duration = find_best_week(weekly_df, "total_duration_min")
    st.metric("Duration", format_duration(best_duration), delta=best_week_duration)

with col2:
    st.write("**Best Month**")
    monthly_df = calculate_monthly_stats(df_filtered)
    best_month, best_month_distance = find_best_month(monthly_df, "total_distance_km")
    st.metric("Distance", f"{best_month_distance:.1f} km", delta=best_month)

    best_month_elev, best_month_elev_val = find_best_month(monthly_df, "total_elevation_m")
    st.metric("Elevation", f"{best_month_elev_val:.0f} m", delta=best_month_elev)

    best_month_duration, best_month_duration_val = find_best_month(monthly_df, "total_duration_min")
    st.metric("Duration", format_duration(best_month_duration_val), delta=best_month_duration)
