"""
game_detail.py
===============
Builds the full detail for one specific game: its overall result plus
its own time at each station (with that station's rank there).

Reuses the already-built ranking (build_ranking) and per-station
ranking (build_station_comparison) - no separate data pass needed,
this just looks up one game_id inside them.
"""

from __future__ import annotations

from models import GameDetail, GameStationResult, RankingEntry, StationRanking


def build_game_detail(
    game_id: int,
    ranking: list[RankingEntry],
    station_rankings: list[StationRanking],
) -> GameDetail | None:
    """Returns None if game_id isn't in the overall ranking (not defused,
    or doesn't exist) - the caller turns that into a 404."""
    overall = next((entry for entry in ranking if entry.game_id == game_id), None)
    if overall is None:
        return None

    stations: list[GameStationResult] = []
    for station_ranking in station_rankings:
        entry = next((e for e in station_ranking.ranking if e.game_id == game_id), None)
        if entry is not None:
            stations.append(
                GameStationResult(
                    station_id=station_ranking.station_id,
                    rank=entry.rank,
                    duration_seconds=entry.duration_seconds,
                    gap_seconds=entry.gap_seconds,
                )
            )

    return GameDetail(
        game_id=overall.game_id,
        team_name=overall.team_name,
        duration_seconds=overall.duration_seconds,
        overall_rank=overall.rank,
        gap_seconds=overall.gap_seconds,
        stations=stations,
    )
