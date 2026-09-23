"""
main.py
=======
FastAPI app for the scoreboard backend.

Start (inside scoreboard/backend/):
    uvicorn main:app --reload --port 8001

Then in the browser: http://localhost:8001/  (the scoreboard page)
API directly:         http://localhost:8001/scoreboard

Which data source is used is decided by get_repository() below,
controlled via config.py (environment variable SCOREBOARD_USE_FAKE_DATA).
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from models import RankingEntry
from ranking import build_ranking
from repositories.base import GamesRepository
from repositories.fake_repository import FakeGamesRepository
from repositories.http_repository import HttpGamesRepository

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Bomb Defusal Parkour - Scoreboard")

# For the event, restrict this to the real address of the dashboard Pi.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)


def get_repository() -> GamesRepository:
    """The single place that decides which data source is used.
    Tests override this via app.dependency_overrides."""
    if config.USE_FAKE_DATA:
        return FakeGamesRepository()
    return HttpGamesRepository(base_url=config.DASHBOARD_BACKEND_URL)


class ScoreboardResponse(BaseModel):
    ranking: list[RankingEntry]


@app.get("/scoreboard", response_model=ScoreboardResponse)
def scoreboard(repository: GamesRepository = Depends(get_repository)) -> ScoreboardResponse:
    games = repository.get_games()
    return ScoreboardResponse(ranking=build_ranking(games))


# Serves scoreboard/frontend/ as a website (no second server needed)
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
