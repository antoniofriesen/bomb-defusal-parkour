"""
models.py
=========
Typed data models. Replace raw dicts so a wrong field name or type
shows up when a Game is created, not only later when it's used.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Outcome = Literal["running", "defused", "exploded"]
StationState = Literal["idle", "active", "solved"]


class Game(BaseModel):
    """A game, exactly as delivered by the dashboard backend
    (contract: GET /internal/games, see docs/API_endpoints.md).

    The dashboard backend sends camelCase (its ASP.NET Core default) -
    alias_generator accepts that on the wire while the rest of this
    codebase keeps using snake_case field names.

    game_id identifies one specific attempt, since the same team can
    play multiple times - needed to link a game to its own station
    events (a team's second attempt must not mix with its first)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    game_id: int
    team_name: str
    outcome: Outcome
    started_at: str
    ended_at: str | None = None


class RankingEntry(BaseModel):
    """One entry in the ranking, exactly as returned by GET /scoreboard."""

    game_id: int
    rank: int
    team_name: str
    duration_seconds: int
    gap_seconds: int
    started_at: str
    ended_at: str | None


class StationEvent(BaseModel):
    """One station event, exactly as delivered by the dashboard backend
    (contract: GET /internal/station-events, see docs/API_endpoints.md).
    Mirrors the ICD status payload's fields, plus team_name and game_id
    (see Game.game_id above for why it's needed).

    The dashboard backend sends camelCase (its ASP.NET Core default) -
    alias_generator accepts that on the wire while the rest of this
    codebase keeps using snake_case field names."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    game_id: int
    team_name: str
    station_id: int
    state: StationState
    timestamp_start: str | None = None
    timestamp_end: str | None = None


class StationRankingEntry(BaseModel):
    """One team's ranked time at one station."""

    game_id: int
    rank: int
    team_name: str
    duration_seconds: int
    gap_seconds: int


class StationRanking(BaseModel):
    """Ranking for a single station, as returned by GET /station-comparison."""

    station_id: int
    ranking: list[StationRankingEntry]


class GameStationResult(BaseModel):
    """This game's own result at one station, with that station's rank."""

    station_id: int
    rank: int
    duration_seconds: int
    gap_seconds: int


class GameDetail(BaseModel):
    """Full detail for one specific game: its overall result plus its
    own per-station times, each with that station's rank - as returned
    by GET /games/{game_id}."""

    game_id: int
    team_name: str
    duration_seconds: int
    overall_rank: int
    gap_seconds: int
    stations: list[GameStationResult]
