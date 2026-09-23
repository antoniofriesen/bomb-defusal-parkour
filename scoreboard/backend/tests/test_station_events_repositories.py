"""Tests for the two StationEventsRepository implementations. Same pattern
as test_repositories.py, kept in a separate file to mirror the separate
repository pair (games vs. station events)."""

from unittest.mock import Mock, patch

import pytest
import requests

from models import StationEvent
from repositories.fake_station_events_repository import FakeStationEventsRepository
from repositories.http_station_events_repository import HttpStationEventsRepository


def test_fake_repository_returns_station_event_objects():
    events = FakeStationEventsRepository().get_station_events()

    assert len(events) > 0
    assert all(isinstance(e, StationEvent) for e in events)


@patch("repositories.http_station_events_repository.requests.get")
def test_http_repository_parses_response_into_station_events(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "game_id": 1,
            "team_name": "Alpha Team",
            "station_id": 1,
            "state": "solved",
            "timestamp_start": "2026-09-21T10:00:00",
            "timestamp_end": "2026-09-21T10:03:12",
        }
    ]
    mock_get.return_value = mock_response

    events = HttpStationEventsRepository(base_url="http://dashboard.local:5000").get_station_events()

    assert events == [
        StationEvent(
            game_id=1,
            team_name="Alpha Team",
            station_id=1,
            state="solved",
            timestamp_start="2026-09-21T10:00:00",
            timestamp_end="2026-09-21T10:03:12",
        )
    ]


@patch("repositories.http_station_events_repository.requests.get")
def test_http_repository_calls_the_agreed_endpoint(mock_get):
    mock_get.return_value.json.return_value = []

    HttpStationEventsRepository(base_url="http://dashboard.local:5000/").get_station_events()

    called_url = mock_get.call_args[0][0]
    assert called_url == "http://dashboard.local:5000/internal/station-events"


@patch("repositories.http_station_events_repository.requests.get")
def test_http_repository_raises_when_dashboard_backend_unreachable(mock_get):
    mock_get.side_effect = requests.ConnectionError("connection refused")

    with pytest.raises(requests.RequestException):
        HttpStationEventsRepository(base_url="http://dashboard.local:5000").get_station_events()
