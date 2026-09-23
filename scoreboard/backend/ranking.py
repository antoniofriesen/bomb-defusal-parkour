"""
ranking.py
==========
Baut die Rangliste aus den Rohdaten von games_source.get_games().

Regeln (abgestimmt im Team):
- Nur "defused"-Spiele bekommen einen Platz (running/exploded fliegen raus)
- Sortiert nach Gesamtzeit (ended_at - started_at), schnellste zuerst
- Jedes Spiel zaehlt einzeln - ein Team kann mehrfach in der Liste stehen
"""

from __future__ import annotations

from datetime import datetime


def build_ranking(games: list[dict]) -> list[dict]:
    """Nimmt die Rohliste aller Spiele, gibt die sortierte Rangliste zurueck.

    Jeder Eintrag im Ergebnis: {"rank", "team_name", "duration_seconds",
    "started_at", "ended_at"}.
    """
    defused = [g for g in games if g["outcome"] == "defused"]

    with_duration = [
        {**g, "duration_seconds": _duration_seconds(g["started_at"], g["ended_at"])}
        for g in defused
    ]

    with_duration.sort(key=lambda g: g["duration_seconds"])

    return [
        {
            "rank": i + 1,
            "team_name": g["team_name"],
            "duration_seconds": g["duration_seconds"],
            "started_at": g["started_at"],
            "ended_at": g["ended_at"],
        }
        for i, g in enumerate(with_duration)
    ]


def _duration_seconds(started_at: str, ended_at: str) -> int:
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(ended_at)
    return round((end - start).total_seconds())
