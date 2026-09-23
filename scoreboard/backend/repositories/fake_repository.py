"""
fake_repository.py
===================
Fixed sample data, used as long as the real dashboard endpoint
(GET /internal/games) doesn't exist yet or isn't reachable.
Selected via config.py / main.py (dependency injection).
"""

from __future__ import annotations

from models import Game
from repositories.base import GamesRepository

FAKE_GAMES: list[Game] = [
    Game(
        team_name="Alpha Team",
        outcome="defused",
        started_at="2026-09-21T10:00:00",
        ended_at="2026-09-21T10:38:12",
    ),
    Game(
        team_name="Bravo Team",
        outcome="defused",
        started_at="2026-09-21T11:00:00",
        ended_at="2026-09-21T11:29:47",
    ),
    Game(
        team_name="Alpha Team",
        outcome="defused",
        started_at="2026-09-22T09:00:00",
        ended_at="2026-09-22T09:22:05",
    ),
    Game(
        team_name="Charlie Team",
        outcome="exploded",
        started_at="2026-09-21T12:00:00",
        ended_at="2026-09-21T12:45:00",
    ),
    Game(
        team_name="Delta Team",
        outcome="running",
        started_at="2026-09-22T10:00:00",
        ended_at=None,
    ),
]


class FakeGamesRepository(GamesRepository):
    def get_games(self) -> list[Game]:
        return FAKE_GAMES
