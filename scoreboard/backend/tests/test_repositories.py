"""Tests for the two GamesRepository implementations."""

from unittest.mock import Mock, patch

import pytest
import requests

from models import Game
from repositories.fake_repository import FakeGamesRepository
from repositories.http_repository import HttpGamesRepository


def test_fake_repository_returns_game_objects():
    games = FakeGamesRepository().get_games()

    assert len(games) > 0
    assert all(isinstance(g, Game) for g in games)


@patch("repositories.http_repository.requests.get")
def test_http_repository_parses_response_into_games(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "team_name": "Alpha Team",
            "outcome": "defused",
            "started_at": "2026-09-21T10:00:00",
            "ended_at": "2026-09-21T10:38:12",
        }
    ]
    mock_get.return_value = mock_response

    games = HttpGamesRepository(base_url="http://dashboard.local:5000").get_games()

    assert games == [
        Game(
            team_name="Alpha Team",
            outcome="defused",
            started_at="2026-09-21T10:00:00",
            ended_at="2026-09-21T10:38:12",
        )
    ]


@patch("repositories.http_repository.requests.get")
def test_http_repository_calls_the_agreed_endpoint(mock_get):
    mock_get.return_value.json.return_value = []

    HttpGamesRepository(base_url="http://dashboard.local:5000/").get_games()

    called_url = mock_get.call_args[0][0]
    assert called_url == "http://dashboard.local:5000/internal/games"


@patch("repositories.http_repository.requests.get")
def test_http_repository_raises_when_dashboard_backend_unreachable(mock_get):
    mock_get.side_effect = requests.ConnectionError("connection refused")

    with pytest.raises(requests.RequestException):
        HttpGamesRepository(base_url="http://dashboard.local:5000").get_games()
