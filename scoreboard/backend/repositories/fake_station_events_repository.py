"""
fake_station_events_repository.py
==================================
Fixed sample data for the per-station comparison, used as long as the
real dashboard endpoint (GET /internal/station-events) isn't ready.

game_id values here match the ones used in fake_repository.py, so the
fake data behaves consistently end to end. Covers all 6 stations, to
preview the real layout before the dashboard backend delivers actual data.
"""

from __future__ import annotations

from models import StationEvent
from repositories.station_events_base import StationEventsRepository

FAKE_STATION_EVENTS: list[StationEvent] = [
    # Alpha Team's second run, game_id=3 (matches the Alpha Team game ended at 2026-09-22T09:22:05)
    StationEvent(game_id=3, team_name="Alpha Team", station_id=1, state="solved", timestamp_start="2026-09-22T09:00:00", timestamp_end="2026-09-22T09:03:10"),
    StationEvent(game_id=3, team_name="Alpha Team", station_id=2, state="solved", timestamp_start="2026-09-22T09:00:00", timestamp_end="2026-09-22T09:05:45"),
    StationEvent(game_id=3, team_name="Alpha Team", station_id=3, state="solved", timestamp_start="2026-09-22T09:00:00", timestamp_end="2026-09-22T09:04:20"),
    StationEvent(game_id=3, team_name="Alpha Team", station_id=4, state="solved", timestamp_start="2026-09-22T09:00:00", timestamp_end="2026-09-22T09:02:35"),
    StationEvent(game_id=3, team_name="Alpha Team", station_id=5, state="solved", timestamp_start="2026-09-22T09:00:00", timestamp_end="2026-09-22T09:03:50"),
    StationEvent(game_id=3, team_name="Alpha Team", station_id=6, state="solved", timestamp_start="2026-09-22T09:00:00", timestamp_end="2026-09-22T09:03:05"),
    # Bravo Team's run, game_id=2 (matches the Bravo Team game ended at 2026-09-21T11:29:47)
    StationEvent(game_id=2, team_name="Bravo Team", station_id=1, state="solved", timestamp_start="2026-09-21T11:00:00", timestamp_end="2026-09-21T11:02:50"),
    StationEvent(game_id=2, team_name="Bravo Team", station_id=2, state="solved", timestamp_start="2026-09-21T11:00:00", timestamp_end="2026-09-21T11:07:15"),
    StationEvent(game_id=2, team_name="Bravo Team", station_id=3, state="solved", timestamp_start="2026-09-21T11:00:00", timestamp_end="2026-09-21T11:03:55"),
    StationEvent(game_id=2, team_name="Bravo Team", station_id=4, state="solved", timestamp_start="2026-09-21T11:00:00", timestamp_end="2026-09-21T11:03:40"),
    StationEvent(game_id=2, team_name="Bravo Team", station_id=5, state="solved", timestamp_start="2026-09-21T11:00:00", timestamp_end="2026-09-21T11:04:20"),
    StationEvent(game_id=2, team_name="Bravo Team", station_id=6, state="solved", timestamp_start="2026-09-21T11:00:00", timestamp_end="2026-09-21T11:03:50"),
    # Delta Team is mid-game (game_id=5) - active, not solved yet, must be excluded from the comparison
    StationEvent(game_id=5, team_name="Delta Team", station_id=1, state="active", timestamp_start="2026-09-22T10:00:00"),
    StationEvent(game_id=5, team_name="Delta Team", station_id=2, state="idle"),
]


class FakeStationEventsRepository(StationEventsRepository):
    def get_station_events(self) -> list[StationEvent]:
        return FAKE_STATION_EVENTS
