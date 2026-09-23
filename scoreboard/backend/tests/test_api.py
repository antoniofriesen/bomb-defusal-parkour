"""End-to-end test of GET /scoreboard, using a test data source instead
of the real fake or HTTP repository (dependency_overrides)."""

from fastapi.testclient import TestClient

from main import app, get_repository
from models import Game
from repositories.base import GamesRepository


class StubRepository(GamesRepository):
    def __init__(self, games: list[Game]) -> None:
        self._games = games

    def get_games(self) -> list[Game]:
        return self._games


def make_client(games: list[Game]) -> TestClient:
    app.dependency_overrides[get_repository] = lambda: StubRepository(games)
    return TestClient(app)


def test_scoreboard_endpoint_returns_ranking_json():
    games = [
        Game(team_name="Alpha", outcome="defused", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
        Game(team_name="Bravo", outcome="exploded", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
    ]
    client = make_client(games)

    response = client.get("/scoreboard")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "ranking": [
            {
                "rank": 1,
                "team_name": "Alpha",
                "duration_seconds": 300,
                "started_at": "2026-01-01T10:00:00",
                "ended_at": "2026-01-01T10:05:00",
            }
        ]
    }


def test_scoreboard_endpoint_with_no_defused_games_returns_empty_list():
    client = make_client([])

    response = client.get("/scoreboard")

    assert response.status_code == 200
    assert response.json() == {"ranking": []}
