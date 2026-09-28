"""
http_station_events_repository.py
==================================
Fetches station events from the dashboard backend
(GET /internal/station-events), see the contract in
docs/API_endpoints.md.

Same situation as http_repository.py - camelCase on the wire,
handled via the alias_generator on StationEvent in models.py.
"""

from __future__ import annotations

import logging

import requests

from models import StationEvent
from repositories.station_events_base import StationEventsRepository

logger = logging.getLogger(__name__)


class HttpStationEventsRepository(StationEventsRepository):
    def __init__(self, base_url: str, timeout_seconds: float = 3.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def get_station_events(self) -> list[StationEvent]:
        url = f"{self._base_url}/internal/station-events"
        try:
            response = requests.get(url, timeout=self._timeout_seconds)
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Dashboard backend unreachable (%s)", url)
            raise

        return [StationEvent(**entry) for entry in response.json()]
