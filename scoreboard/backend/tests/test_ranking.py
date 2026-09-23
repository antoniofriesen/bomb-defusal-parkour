"""Tests for ranking.py - expected values come from the team rules, not from the code."""

from models import Game
from ranking import build_ranking


def game(team_name="A", outcome="defused", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"):
    return Game(team_name=team_name, outcome=outcome, started_at=started_at, ended_at=ended_at)


def test_only_defused_games_get_a_rank():
    games = [
        game(team_name="A", outcome="defused"),
        game(team_name="B", outcome="exploded"),
        game(team_name="C", outcome="running", ended_at=None),
    ]

    ranking = build_ranking(games)

    assert [entry.team_name for entry in ranking] == ["A"]


def test_fastest_team_is_rank_1():
    games = [
        game(team_name="Slow", ended_at="2026-01-01T10:10:00"),
        game(team_name="Fast", ended_at="2026-01-01T10:03:00"),
    ]

    ranking = build_ranking(games)

    assert ranking[0].team_name == "Fast"
    assert ranking[0].rank == 1
    assert ranking[1].team_name == "Slow"
    assert ranking[1].rank == 2


def test_duration_seconds_is_computed_correctly():
    ranking = build_ranking([game(ended_at="2026-01-01T10:05:13")])

    assert ranking[0].duration_seconds == 313  # 5 min 13 s


def test_same_team_can_appear_multiple_times():
    games = [
        game(team_name="Alpha", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:10:00"),
        game(team_name="Alpha", started_at="2026-01-02T10:00:00", ended_at="2026-01-02T10:05:00"),
    ]

    ranking = build_ranking(games)

    assert len(ranking) == 2
    assert [entry.team_name for entry in ranking] == ["Alpha", "Alpha"]


def test_empty_game_list_returns_empty_ranking():
    assert build_ranking([]) == []


def test_tie_keeps_both_entries_with_different_ranks():
    games = [
        game(team_name="A", started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
        game(team_name="B", started_at="2026-01-01T11:00:00", ended_at="2026-01-01T11:05:00"),
    ]

    ranking = build_ranking(games)

    assert ranking[0].duration_seconds == ranking[1].duration_seconds
    assert {entry.rank for entry in ranking} == {1, 2}


def test_defused_without_ended_at_is_skipped_not_crashed(caplog):
    # Shouldn't happen per the contract, but a bug in the dashboard backend
    # must not take down the whole scoreboard with an exception.
    games = [game(team_name="Broken", ended_at=None), game(team_name="Ok")]

    ranking = build_ranking(games)

    assert [entry.team_name for entry in ranking] == ["Ok"]
    assert "Broken" in caplog.text
