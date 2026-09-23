"""Tests for station_ranking.py - one ranking per station."""

import itertools

from models import StationEvent
from station_ranking import build_station_comparison

_game_id_counter = itertools.count(1)


def event(team_name="A", station_id=1, state="solved", timestamp_start="2026-01-01T10:00:00", timestamp_end="2026-01-01T10:05:00", game_id=None):
    if game_id is None:
        game_id = next(_game_id_counter)
    return StationEvent(game_id=game_id, team_name=team_name, station_id=station_id, state=state, timestamp_start=timestamp_start, timestamp_end=timestamp_end)


def test_only_solved_events_count():
    events = [
        event(team_name="A", state="solved"),
        event(team_name="B", state="active", timestamp_end=None),
        event(team_name="C", state="idle", timestamp_start=None, timestamp_end=None),
    ]

    stations = build_station_comparison(events)

    assert len(stations) == 1
    assert [entry.team_name for entry in stations[0].ranking] == ["A"]


def test_events_are_grouped_by_station():
    events = [
        event(team_name="A", station_id=1),
        event(team_name="A", station_id=2),
        event(team_name="B", station_id=1),
    ]

    stations = build_station_comparison(events)

    assert [s.station_id for s in stations] == [1, 2]
    assert len(stations[0].ranking) == 2  # station 1: A and B
    assert len(stations[1].ranking) == 1  # station 2: only A


def test_fastest_team_is_rank_1_per_station():
    events = [
        event(team_name="Slow", station_id=1, timestamp_end="2026-01-01T10:10:00"),
        event(team_name="Fast", station_id=1, timestamp_end="2026-01-01T10:02:00"),
    ]

    stations = build_station_comparison(events)

    ranking = stations[0].ranking
    assert ranking[0].team_name == "Fast"
    assert ranking[0].rank == 1
    assert ranking[1].team_name == "Slow"
    assert ranking[1].rank == 2


def test_stations_are_sorted_by_station_id():
    events = [
        event(station_id=3),
        event(station_id=1),
        event(station_id=2),
    ]

    stations = build_station_comparison(events)

    assert [s.station_id for s in stations] == [1, 2, 3]


def test_solved_event_without_timestamps_is_skipped_not_crashed(caplog):
    events = [
        event(team_name="Broken", timestamp_start=None, timestamp_end=None, state="solved"),
        event(team_name="Ok"),
    ]

    stations = build_station_comparison(events)

    assert [entry.team_name for entry in stations[0].ranking] == ["Ok"]
    assert "Broken" in caplog.text


def test_no_events_returns_no_stations():
    assert build_station_comparison([]) == []
