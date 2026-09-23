"""Tests fuer ranking.py - Erwartungen kommen aus den Team-Regeln, nicht aus dem Code."""

from ranking import build_ranking


def test_only_defused_games_get_a_rank():
    games = [
        {"team_name": "A", "outcome": "defused", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:05:00"},
        {"team_name": "B", "outcome": "exploded", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:05:00"},
        {"team_name": "C", "outcome": "running", "started_at": "2026-01-01T10:00:00", "ended_at": None},
    ]

    ranking = build_ranking(games)

    assert [entry["team_name"] for entry in ranking] == ["A"]


def test_fastest_team_is_rank_1():
    games = [
        {"team_name": "Slow", "outcome": "defused", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:10:00"},
        {"team_name": "Fast", "outcome": "defused", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:03:00"},
    ]

    ranking = build_ranking(games)

    assert ranking[0]["team_name"] == "Fast"
    assert ranking[0]["rank"] == 1
    assert ranking[1]["team_name"] == "Slow"
    assert ranking[1]["rank"] == 2


def test_duration_seconds_is_computed_correctly():
    games = [
        {"team_name": "A", "outcome": "defused", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:05:13"},
    ]

    ranking = build_ranking(games)

    assert ranking[0]["duration_seconds"] == 313  # 5 min 13 s


def test_same_team_can_appear_multiple_times():
    games = [
        {"team_name": "Alpha", "outcome": "defused", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:10:00"},
        {"team_name": "Alpha", "outcome": "defused", "started_at": "2026-01-02T10:00:00", "ended_at": "2026-01-02T10:05:00"},
    ]

    ranking = build_ranking(games)

    assert len(ranking) == 2
    assert [entry["team_name"] for entry in ranking] == ["Alpha", "Alpha"]


def test_empty_game_list_returns_empty_ranking():
    assert build_ranking([]) == []


def test_tie_keeps_both_entries_with_different_ranks():
    games = [
        {"team_name": "A", "outcome": "defused", "started_at": "2026-01-01T10:00:00", "ended_at": "2026-01-01T10:05:00"},
        {"team_name": "B", "outcome": "defused", "started_at": "2026-01-01T11:00:00", "ended_at": "2026-01-01T11:05:00"},
    ]

    ranking = build_ranking(games)

    assert ranking[0]["duration_seconds"] == ranking[1]["duration_seconds"]
    assert {entry["rank"] for entry in ranking} == {1, 2}
