"""
games_source.py
================
Liefert die Rohdaten aller Spiele, die das Ranking braucht.

WICHTIG - Übergabepunkt zum Dashboard-Backend (C#):
Aktuell liefert get_games() Fake-Daten, im vereinbarten Format des
geplanten Endpunkts GET /internal/games auf dem Dashboard-Backend.

Sobald dieser Endpunkt existiert, wird NUR diese Funktion ersetzt
(z.B. durch einen requests.get(...) Aufruf) - ranking.py und main.py
bleiben unverändert, weil sie nur mit dem Rückgabeformat arbeiten,
nicht mit der Datenquelle selbst.

Format pro Spiel (Vertrag mit dem Dashboard-Backend):
{
    "team_name": str,
    "outcome": "running" | "defused" | "exploded",
    "started_at": str (ISO 8601),
    "ended_at": str (ISO 8601) or None (solange das Spiel laeuft),
}
"""

from __future__ import annotations

FAKE_GAMES: list[dict] = [
    {
        "team_name": "Alpha Team",
        "outcome": "defused",
        "started_at": "2026-09-21T10:00:00",
        "ended_at": "2026-09-21T10:38:12",
    },
    {
        "team_name": "Bravo Team",
        "outcome": "defused",
        "started_at": "2026-09-21T11:00:00",
        "ended_at": "2026-09-21T11:29:47",
    },
    {
        "team_name": "Alpha Team",
        "outcome": "defused",
        "started_at": "2026-09-22T09:00:00",
        "ended_at": "2026-09-22T09:22:05",
    },
    {
        "team_name": "Charlie Team",
        "outcome": "exploded",
        "started_at": "2026-09-21T12:00:00",
        "ended_at": "2026-09-21T12:45:00",
    },
    {
        "team_name": "Delta Team",
        "outcome": "running",
        "started_at": "2026-09-22T10:00:00",
        "ended_at": None,
    },
]


def get_games() -> list[dict]:
    """Gibt alle Spiele zurueck. TODO: durch echten Aufruf an das
    Dashboard-Backend ersetzen, sobald GET /internal/games existiert."""
    return FAKE_GAMES
