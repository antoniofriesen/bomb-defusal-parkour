"""
ranking.py
==========
Builds the ranking from the raw list of all games.

Rules (agreed with the team):
- Only "defused" games get a rank (running/exploded are dropped)
- Sorted by total time (ended_at - started_at), fastest first
- Every game counts on its own - a team can appear multiple times
"""

from __future__ import annotations

import logging
from datetime import datetime

from models import Game, RankingEntry

logger = logging.getLogger(__name__)


def build_ranking(games: list[Game]) -> list[RankingEntry]:
    scored: list[tuple[Game, int]] = []

    for game in games:
        if game.outcome != "defused":
            continue
        if game.ended_at is None:
            # Shouldn't happen per the contract, but skip and log instead
            # of crashing the whole scoreboard over one bad entry from
            # the dashboard backend.
            logger.warning(
                "Game by %r has outcome=defused but no ended_at, skipping",
                game.team_name,
            )
            continue
        scored.append((game, _duration_seconds(game.started_at, game.ended_at)))

    scored.sort(key=lambda pair: pair[1])

    return [
        RankingEntry(
            game_id=game.game_id,
            rank=i + 1,
            team_name=game.team_name,
            duration_seconds=duration,
            started_at=game.started_at,
            ended_at=game.ended_at,
        )
        for i, (game, duration) in enumerate(scored)
    ]


def _duration_seconds(started_at: str, ended_at: str) -> int:
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(ended_at)
    return round((end - start).total_seconds())
