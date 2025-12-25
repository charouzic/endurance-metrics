"""Endurance Metrics - Main application entry point."""

import streamlit as st
from endurance_metrics.config import AppConfig
from endurance_metrics.ui_components import setup_page_config, display_sidebar


def main():
    """Main application entry point."""
    setup_page_config()
    config = AppConfig()

    # Validate configuration
    if not config.validate():
        st.error("❌ Missing required Strava API credentials")
        st.markdown("""
        Please configure your credentials in `.streamlit/secrets.toml`:

        ```toml
        STRAVA_CLIENT_ID = "your_client_id"
        STRAVA_CLIENT_SECRET = "your_client_secret"
        STRAVA_REFRESH_TOKEN = "your_refresh_token"
        ```

        See `.streamlit/secrets.toml.example` for a template.

        Get your credentials from: https://www.strava.com/settings/api
        """)
        st.stop()

    # Display sidebar with filters and refresh button
    display_sidebar()

    # Welcome message for home page
    st.title("🏃 Endurance Metrics")
    st.markdown("""
    Welcome to your Strava analytics dashboard!

    Use the sidebar to navigate between different views:
    - **📊 Overview**: High-level metrics and trends
    - **📅 Weekly View**: Detailed weekly analysis
    - **📈 Yearly Stats**: Year-over-year comparisons
    - **📋 Raw Data**: Export and explore your activities

    ### Getting Started

    1. The app loads cached data by default
    2. Click **"🔄 Refresh from Strava"** in the sidebar to fetch latest activities
    3. Use filters to narrow down your data by date range and sport type
    4. Navigate to different pages using the sidebar

    ### Features

    - **Automatic Caching**: Data is cached locally to minimize API calls
    - **Rate Limit Protection**: Graceful fallback to cached data if rate limited
    - **Interactive Charts**: Hover, zoom, and explore your training data
    - **Export Options**: Download filtered data as CSV

    **Strava API Rate Limits:**
    - 100 read requests per 15 minutes
    - 1,000 read requests per day

    Ready to explore your training data? Select a page from the sidebar!
    """)


if __name__ == "__main__":
    main()
