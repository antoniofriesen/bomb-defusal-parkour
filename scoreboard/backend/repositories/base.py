"""
base.py
=======
Abstraction for the data source of all games. The ranking logic and
the API layer only know this interface, never a concrete source -
this is the single swap point towards the dashboard backend.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models import Game


class GamesRepository(ABC):
    @abstractmethod
    def get_games(self) -> list[Game]:
        """Returns ALL games (every outcome value), unfiltered,
        unsorted. Filtering/sorting happens in ranking.py."""
        raise NotImplementedError
