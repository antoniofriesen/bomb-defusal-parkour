"""
models.py
=========
Typed data models. Replace raw dicts so a wrong field name or type
shows up when a Game is created, not only later when it's used.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Outcome = Literal["running", "defused", "exploded"]
StationState = Literal["idle", "active", "solved"]


class Game(BaseModel):
    """A game, exactly as delivered by the dashboard backend
    (contract: GET /internal/games, see dashboard/backend/README.md)."""

    team_name: str
    outcome: Outcome
    started_at: str
    ended_at: str | None = None


class RankingEntry(BaseModel):
    """One entry in the ranking, exactly as returned by GET /scoreboard."""

    rank: int
    team_name: str
    duration_seconds: int
    started_at: str
    ended_at: str | None


class StationEvent(BaseModel):
    """One station event, exactly as delivered by the dashboard backend
    (contract: GET /internal/station-events, see dashboard/backend/README.md).
    Mirrors the ICD status payload's fields, plus team_name."""

    team_name: str
    station_id: int
    state: StationState
    timestamp_start: str | None = None
    timestamp_end: str | None = None


class StationRankingEntry(BaseModel):
    """One team's ranked time at one station."""

    rank: int
    team_name: str
    duration_seconds: int


class StationRanking(BaseModel):
    """Ranking for a single station, as returned by GET /station-comparison."""

    station_id: int
    ranking: list[StationRankingEntry]
