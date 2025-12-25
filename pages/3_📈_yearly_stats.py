"""Year-over-year comparison page."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from endurance_metrics.config import AppConfig
from endurance_metrics.data_loader import load_activities, filter_activities
from endurance_metrics.yearly_stats import calculate_yearly_stats, calculate_yoy_change, get_yearly_by_sport
from endurance_metrics.ui_components import display_sidebar

st.title("📈 Yearly Statistics")

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

# Yearly summary table
st.subheader("Yearly Summary")

yearly_df = calculate_yearly_stats(df_filtered)
yearly_with_change = calculate_yoy_change(yearly_df)

# Format for display
display_df = yearly_with_change[[
    "year", "total_distance_km", "total_distance_km_yoy_change",
    "total_elevation_m", "total_elevation_m_yoy_change",
    "activity_count", "activity_count_yoy_change"
]].copy()

display_df.columns = [
    "Year", "Distance (km)", "Distance YoY %",
    "Elevation (m)", "Elevation YoY %",
    "Activities", "Activities YoY %"
]

# Format numbers
display_df["Distance (km)"] = display_df["Distance (km)"].round(1)
display_df["Distance YoY %"] = display_df["Distance YoY %"].round(1)
display_df["Elevation (m)"] = display_df["Elevation (m)"].round(0)
display_df["Elevation YoY %"] = display_df["Elevation YoY %"].round(1)
display_df["Activities YoY %"] = display_df["Activities YoY %"].round(1)

st.dataframe(display_df, width='stretch', hide_index=True)

st.divider()

# Yearly distance chart
col1, col2 = st.columns(2)

with col1:
    st.subheader("Yearly Distance")
    fig_distance = go.Figure()
    fig_distance.add_trace(go.Bar(
        x=yearly_df["year"],
        y=yearly_df["total_distance_km"],
        marker_color="lightblue"
    ))
    fig_distance.update_layout(
        xaxis_title="Year",
        yaxis_title="Distance (km)",
        height=400
    )
    st.plotly_chart(fig_distance, width='stretch')

with col2:
    st.subheader("Yearly Elevation")
    fig_elevation = go.Figure()
    fig_elevation.add_trace(go.Bar(
        x=yearly_df["year"],
        y=yearly_df["total_elevation_m"],
        marker_color="lightgreen"
    ))
    fig_elevation.update_layout(
        xaxis_title="Year",
        yaxis_title="Elevation (m)",
        height=400
    )
    st.plotly_chart(fig_elevation, width='stretch')

# Sport breakdown
st.divider()
st.subheader("Breakdown by Sport")

yearly_sport = get_yearly_by_sport(df_filtered)

fig_sport = px.bar(
    yearly_sport,
    x="year",
    y="distance_km",
    color="sport",
    title="Distance by Sport and Year",
    labels={"distance_km": "Distance (km)", "year": "Year"}
)

fig_sport.update_layout(height=400)

st.plotly_chart(fig_sport, width='stretch')

# Year-over-year insights
st.divider()
st.subheader("Year-over-Year Insights")

if len(yearly_with_change) > 1:
    latest_year = yearly_with_change.iloc[-1]

    col1, col2, col3 = st.columns(3)

    with col1:
        yoy_distance = latest_year["total_distance_km_yoy_change"]
        st.metric(
            "Distance Change",
            f"{yoy_distance:+.1f}%",
            delta=f"vs {int(latest_year['year'])-1}"
        )

    with col2:
        yoy_elevation = latest_year["total_elevation_m_yoy_change"]
        st.metric(
            "Elevation Change",
            f"{yoy_elevation:+.1f}%",
            delta=f"vs {int(latest_year['year'])-1}"
        )

    with col3:
        yoy_activities = latest_year["activity_count_yoy_change"]
        st.metric(
            "Activity Count Change",
            f"{yoy_activities:+.1f}%",
            delta=f"vs {int(latest_year['year'])-1}"
        )
else:
    st.info("Year-over-year comparison requires data from multiple years.")
