"""Configuration management using Streamlit secrets."""

from dataclasses import dataclass
from pathlib import Path
import streamlit as st


@dataclass
class AppConfig:
    """Application configuration from Streamlit secrets."""

    strava_client_id: str
    strava_client_secret: str
    strava_refresh_token: str
    cache_dir: Path = Path("data")
    cache_file: str = "strava_activities.parquet"

    # API rate limits
    rate_limit_overall: int = 200  # per 15 minutes
    rate_limit_read: int = 100     # per 15 minutes
    rate_limit_daily: int = 2000
    rate_limit_daily_read: int = 1000

    # Pagination
    activities_per_page: int = 200

    def __init__(self):
        """Initialize configuration from Streamlit secrets."""
        try:
            self.strava_client_id = st.secrets.get("STRAVA_CLIENT_ID", "")
            self.strava_client_secret = st.secrets.get("STRAVA_CLIENT_SECRET", "")
            self.strava_refresh_token = st.secrets.get("STRAVA_REFRESH_TOKEN", "")
        except FileNotFoundError:
            # secrets.toml doesn't exist
            self.strava_client_id = ""
            self.strava_client_secret = ""
            self.strava_refresh_token = ""

    def validate(self) -> bool:
        """
        Validate that all required configuration is present.

        Returns:
            bool: True if all required config exists, False otherwise.
        """
        return all([
            self.strava_client_id,
            self.strava_client_secret,
            self.strava_refresh_token
        ])

    @property
    def cache_path(self) -> Path:
        """
        Get full path to cache file.

        Returns:
            Path: Full path to parquet cache file.
        """
        return self.cache_dir / self.cache_file

    def ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
