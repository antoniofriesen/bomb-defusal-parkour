"""
station_events_base.py
=======================
Abstraction for the data source of all station events, used for the
per-station comparison. Same pattern as GamesRepository in base.py.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models import StationEvent


class StationEventsRepository(ABC):
    @abstractmethod
    def get_station_events(self) -> list[StationEvent]:
        """Returns ALL station events (every state value), unfiltered,
        unsorted. Filtering/ranking happens in station_ranking.py."""
        raise NotImplementedError
