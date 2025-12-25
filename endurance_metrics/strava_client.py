"""Strava API client with authentication and rate limit handling."""

from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
import time
import streamlit as st
from endurance_metrics.config import AppConfig


class StravaAPIError(Exception):
    """Custom exception for Strava API errors."""
    pass


class StravaRateLimitError(StravaAPIError):
    """Raised when rate limit is hit."""
    pass


class StravaClient:
    """Client for interacting with Strava API v3."""

    BASE_URL = "https://www.strava.com/api/v3"
    TOKEN_URL = "https://www.strava.com/oauth/token"

    def __init__(self, config: AppConfig):
        """
        Initialize Strava API client.

        Args:
            config: Application configuration with API credentials.
        """
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def _get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary.
        Token is kept only in memory.

        Returns:
            str: Valid access token.

        Raises:
            StravaAPIError: If token refresh fails.
        """
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at - timedelta(minutes=5):
                return self._access_token

        # Refresh token
        payload = {
            "client_id": self.config.strava_client_id,
            "client_secret": self.config.strava_client_secret,
            "refresh_token": self.config.strava_refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            self._access_token = data["access_token"]
            self._token_expires_at = datetime.fromtimestamp(data["expires_at"])

            return self._access_token
        except requests.exceptions.Timeout:
            raise StravaAPIError("Connection timeout. Please check your network and try again.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise StravaAPIError(
                    "Invalid Strava credentials. Please check your secrets in .streamlit/secrets.toml"
                )
            raise StravaAPIError(f"Failed to refresh access token: {e}")
        except requests.exceptions.RequestException as e:
            raise StravaAPIError(f"Failed to refresh access token: {e}")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to Strava API.

        Args:
            endpoint: API endpoint (e.g., '/athlete/activities').
            params: Query parameters.

        Returns:
            Response JSON data.

        Raises:
            StravaRateLimitError: When rate limit is exceeded.
            StravaAPIError: For other API errors.
        """
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            # Check for rate limit
            if response.status_code == 429:
                # Parse rate limit headers
                limit_header = response.headers.get("X-RateLimit-Limit", "?,?")
                usage_header = response.headers.get("X-RateLimit-Usage", "?,?")
                limit_15min = limit_header.split(",")[0] if "," in limit_header else "?"
                usage_15min = usage_header.split(",")[0] if "," in usage_header else "?"

                raise StravaRateLimitError(
                    f"Rate limit exceeded. Usage: {usage_15min}/{limit_15min} per 15 minutes. "
                    "Please try again later or use cached data."
                )

            response.raise_for_status()
            return response.json()
        except StravaRateLimitError:
            # Re-raise rate limit errors
            raise
        except requests.exceptions.Timeout:
            raise StravaAPIError("Request timeout. Please check your network and try again.")
        except requests.exceptions.HTTPError as e:
            raise StravaAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise StravaAPIError(f"API request failed: {e}")

    def get_athlete_info(self) -> Dict:
        """
        Fetch authenticated athlete information.

        Returns:
            Dict: Athlete information from Strava API.
        """
        return self._make_request("/athlete")

    def get_activities(self, page: int = 1, per_page: int = 200) -> List[Dict]:
        """
        Fetch activities for authenticated athlete.

        Args:
            page: Page number (1-indexed).
            per_page: Results per page (max 200).

        Returns:
            List of activity dictionaries.
        """
        params = {"page": page, "per_page": per_page}
        return self._make_request("/athlete/activities", params)

    def fetch_all_activities(self, progress_callback=None) -> List[Dict]:
        """
        Fetch all activities with pagination.

        Args:
            progress_callback: Optional callback function(page_num, total_activities).

        Returns:
            Complete list of all activities.

        Raises:
            StravaRateLimitError: When rate limit is exceeded.
            StravaAPIError: For other API errors.
        """
        all_activities = []
        page = 1

        while True:
            try:
                activities = self.get_activities(
                    page=page,
                    per_page=self.config.activities_per_page
                )

                if not activities:
                    break

                all_activities.extend(activities)

                if progress_callback:
                    progress_callback(page, len(all_activities))

                # Stop if we got fewer results than requested
                if len(activities) < self.config.activities_per_page:
                    break

                page += 1

                # Small delay to be nice to API
                time.sleep(0.5)

            except StravaRateLimitError:
                # Re-raise rate limit errors
                raise
            except StravaAPIError as e:
                st.warning(f"Error fetching page {page}: {e}")
                break

        return all_activities
