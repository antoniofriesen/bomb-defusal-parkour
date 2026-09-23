"""
station_ranking.py
===================
Builds one ranking per station from the raw list of all station events.

Rules (same spirit as ranking.py):
- Only "solved" events count (idle/active are dropped)
- Sorted by duration (timestamp_end - timestamp_start), fastest first
- Grouped by station_id - each station gets its own ranking
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime

from models import StationEvent, StationRanking, StationRankingEntry

logger = logging.getLogger(__name__)


def build_station_comparison(events: list[StationEvent]) -> list[StationRanking]:
    by_station: dict[int, list[tuple[StationEvent, int]]] = defaultdict(list)

    for event in events:
        if event.state != "solved":
            continue
        if event.timestamp_start is None or event.timestamp_end is None:
            logger.warning(
                "Station %s event for %r has state=solved but missing timestamps, skipping",
                event.station_id,
                event.team_name,
            )
            continue
        duration = _duration_seconds(event.timestamp_start, event.timestamp_end)
        by_station[event.station_id].append((event, duration))

    stations = []
    for station_id in sorted(by_station):
        scored = sorted(by_station[station_id], key=lambda pair: pair[1])
        best_duration = scored[0][1]
        ranking = [
            StationRankingEntry(
                game_id=event.game_id,
                rank=i + 1,
                team_name=event.team_name,
                duration_seconds=duration,
                gap_seconds=duration - best_duration,
            )
            for i, (event, duration) in enumerate(scored)
        ]
        stations.append(StationRanking(station_id=station_id, ranking=ranking))

    return stations


def _duration_seconds(started_at: str, ended_at: str) -> int:
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(ended_at)
    return round((end - start).total_seconds())
