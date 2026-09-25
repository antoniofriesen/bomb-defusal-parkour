"""
http_repository.py
===================
Fetches the games from the dashboard backend (GET /internal/games),
see the contract in docs/API_endpoints.md.

Verified against the real endpoint on 2026-09-25 - response used
camelCase field names (ASP.NET Core's default), handled via the
alias_generator on Game in models.py.
"""

from __future__ import annotations

import logging

import requests

from models import Game
from repositories.base import GamesRepository

logger = logging.getLogger(__name__)


class HttpGamesRepository(GamesRepository):
    def __init__(self, base_url: str, timeout_seconds: float = 3.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def get_games(self) -> list[Game]:
        url = f"{self._base_url}/internal/games"
        try:
            response = requests.get(url, timeout=self._timeout_seconds)
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Dashboard backend unreachable (%s)", url)
            raise

        return [Game(**entry) for entry in response.json()]
