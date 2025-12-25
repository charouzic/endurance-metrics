"""Endurance Metrics - Strava training data analytics."""

__version__ = "0.1.0"
__author__ = "Viki"

from endurance_metrics.config import AppConfig
from endurance_metrics.data_loader import load_activities

__all__ = ["AppConfig", "load_activities"]
