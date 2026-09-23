"""End-to-end test of GET /scoreboard and GET /station-comparison, using a
test data source instead of the real fake or HTTP repository
(dependency_overrides)."""

from fastapi.testclient import TestClient

from main import app, get_repository, get_station_events_repository
from models import Game, StationEvent
from repositories.base import GamesRepository
from repositories.station_events_base import StationEventsRepository


class StubRepository(GamesRepository):
    def __init__(self, games: list[Game]) -> None:
        self._games = games

    def get_games(self) -> list[Game]:
        return self._games


class StubStationEventsRepository(StationEventsRepository):
    def __init__(self, events: list[StationEvent]) -> None:
        self._events = events

    def get_station_events(self) -> list[StationEvent]:
        return self._events


def make_client(games: list[Game]) -> TestClient:
    app.dependency_overrides[get_repository] = lambda: StubRepository(games)
    return TestClient(app)


def make_station_client(events: list[StationEvent]) -> TestClient:
    app.dependency_overrides[get_station_events_repository] = lambda: StubStationEventsRepository(events)
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


def test_station_comparison_endpoint_returns_ranking_per_station():
    events = [
        StationEvent(team_name="Alpha", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:03:00"),
        StationEvent(team_name="Bravo", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:05:00"),
    ]
    client = make_station_client(events)

    response = client.get("/station-comparison")

    assert response.status_code == 200
    assert response.json() == {
        "stations": [
            {
                "station_id": 1,
                "ranking": [
                    {"rank": 1, "team_name": "Alpha", "duration_seconds": 180},
                    {"rank": 2, "team_name": "Bravo", "duration_seconds": 300},
                ],
            }
        ]
    }


def test_station_comparison_endpoint_with_no_events_returns_empty_list():
    client = make_station_client([])

    response = client.get("/station-comparison")

    assert response.status_code == 200
    assert response.json() == {"stations": []}
