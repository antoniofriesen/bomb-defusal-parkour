"""End-to-end tests of GET /scoreboard, GET /station-comparison and
GET /games/{game_id}, using a test data source instead of the real fake
or HTTP repository (dependency_overrides)."""

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


def make_client(games: list[Game], events: list[StationEvent] | None = None) -> TestClient:
    app.dependency_overrides[get_repository] = lambda: StubRepository(games)
    app.dependency_overrides[get_station_events_repository] = lambda: StubStationEventsRepository(events or [])
    return TestClient(app)


def test_scoreboard_endpoint_returns_ranking_json():
    games = [
        Game(game_id=1, team_name="Alpha", outcome="defused", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
        Game(game_id=2, team_name="Bravo", outcome="exploded", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
    ]
    client = make_client(games)

    response = client.get("/scoreboard")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "ranking": [
            {
                "game_id": 1,
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
        StationEvent(game_id=1, team_name="Alpha", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:03:00"),
        StationEvent(game_id=2, team_name="Bravo", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:05:00"),
    ]
    client = make_client(games=[], events=events)

    response = client.get("/station-comparison")

    assert response.status_code == 200
    assert response.json() == {
        "stations": [
            {
                "station_id": 1,
                "ranking": [
                    {"game_id": 1, "rank": 1, "team_name": "Alpha", "duration_seconds": 180},
                    {"game_id": 2, "rank": 2, "team_name": "Bravo", "duration_seconds": 300},
                ],
            }
        ]
    }


def test_station_comparison_endpoint_with_no_events_returns_empty_list():
    client = make_client(games=[], events=[])

    response = client.get("/station-comparison")

    assert response.status_code == 200
    assert response.json() == {"stations": []}


def test_game_detail_endpoint_combines_overall_and_per_station_results():
    games = [
        Game(game_id=1, team_name="Alpha", outcome="defused", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
        Game(game_id=2, team_name="Bravo", outcome="defused", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:10:00"),
    ]
    events = [
        StationEvent(game_id=1, team_name="Alpha", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:02:00"),
        StationEvent(game_id=2, team_name="Bravo", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:04:00"),
    ]
    client = make_client(games, events)

    response = client.get("/games/1")

    assert response.status_code == 200
    assert response.json() == {
        "game_id": 1,
        "team_name": "Alpha",
        "duration_seconds": 300,
        "overall_rank": 1,
        "stations": [
            {"station_id": 1, "rank": 1, "duration_seconds": 120},
        ],
    }


def test_game_detail_endpoint_returns_404_for_unknown_game_id():
    client = make_client(games=[], events=[])

    response = client.get("/games/999")

    assert response.status_code == 404
