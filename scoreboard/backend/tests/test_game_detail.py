"""Tests for game_detail.py."""

from game_detail import build_game_detail
from models import RankingEntry, StationRanking, StationRankingEntry


def test_build_game_detail_combines_overall_and_station_results():
    ranking = [
        RankingEntry(game_id=1, rank=1, team_name="Alpha", duration_seconds=300, gap_seconds=0, started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
        RankingEntry(game_id=2, rank=2, team_name="Bravo", duration_seconds=600, gap_seconds=300, started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:10:00"),
    ]
    station_rankings = [
        StationRanking(station_id=1, ranking=[
            StationRankingEntry(game_id=1, rank=1, team_name="Alpha", duration_seconds=120, gap_seconds=0),
            StationRankingEntry(game_id=2, rank=2, team_name="Bravo", duration_seconds=240, gap_seconds=120),
        ]),
        StationRanking(station_id=2, ranking=[
            StationRankingEntry(game_id=1, rank=2, team_name="Alpha", duration_seconds=180, gap_seconds=90),
            StationRankingEntry(game_id=2, rank=1, team_name="Bravo", duration_seconds=90, gap_seconds=0),
        ]),
    ]

    detail = build_game_detail(game_id=1, ranking=ranking, station_rankings=station_rankings)

    assert detail.game_id == 1
    assert detail.team_name == "Alpha"
    assert detail.duration_seconds == 300
    assert detail.overall_rank == 1
    assert [(s.station_id, s.rank, s.duration_seconds, s.gap_seconds) for s in detail.stations] == [
        (1, 1, 120, 0),
        (2, 2, 180, 90),
    ]


def test_build_game_detail_returns_none_for_unknown_game_id():
    detail = build_game_detail(game_id=999, ranking=[], station_rankings=[])

    assert detail is None


def test_build_game_detail_only_includes_stations_this_game_has_an_entry_for():
    ranking = [
        RankingEntry(game_id=1, rank=1, team_name="Alpha", duration_seconds=300, gap_seconds=0, started_at="2026-01-01T10:00:00", ended_at="2026-01-01T10:05:00"),
    ]
    # Station 2 has no entry for game_id=1 (e.g. that team never solved it)
    station_rankings = [
        StationRanking(station_id=1, ranking=[
            StationRankingEntry(game_id=1, rank=1, team_name="Alpha", duration_seconds=120, gap_seconds=0),
        ]),
        StationRanking(station_id=2, ranking=[
            StationRankingEntry(game_id=2, rank=1, team_name="Bravo", duration_seconds=90, gap_seconds=0),
        ]),
    ]

    detail = build_game_detail(game_id=1, ranking=ranking, station_rankings=station_rankings)

    assert [s.station_id for s in detail.stations] == [1]
