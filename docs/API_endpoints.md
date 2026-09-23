# API Contract - Bomb Defusal Parkour

Version: v1 – Draft – 2026-09-23

## Overview

Two backend services, each documented in its own section below:

- **Scoreboard Backend** (Python/FastAPI, `scoreboard/backend/`) - implemented and tested. Reads game/station data, builds rankings, serves the scoreboard page.
- **Dashboard Backend** (C#/.NET, `dashboard/backend/`) - owns the database and the MQTT connection. The Scoreboard Backend depends on two endpoints from it (Section 2) that don't exist yet.

```
Stations --MQTT (ICD)--> Dashboard Backend --owns--> Database
                                |
                                | GET /internal/games
                                | GET /internal/station-events
                                v
                         Scoreboard Backend --serves--> Scoreboard page (browser)
```

---

## 1. Scoreboard API (implemented)

Base: `scoreboard/backend/main.py`. All GET, no authentication (internal event network only).

| Method | Path | Status |
|---|---|---|
| `GET` | `/scoreboard` | ✅ Implemented |
| `GET` | `/station-comparison` | ✅ Implemented |
| `GET` | `/games/{game_id}` | ✅ Implemented |

### `GET /scoreboard`
Overall ranking. Only `defused` games get a rank, sorted by total time (fastest first). A team can appear multiple times (each attempt counts on its own).

Response `200`:
```json
{
  "ranking": [
    {
      "game_id": 3,
      "rank": 1,
      "team_name": "Alpha Team",
      "duration_seconds": 1325,
      "gap_seconds": 0,
      "started_at": "2026-09-22T09:00:00",
      "ended_at": "2026-09-22T09:22:05"
    }
  ]
}
```

### `GET /station-comparison`
One ranking per station (all 6), comparing every team's time at that specific station. Only `solved` events count.

Response `200`:
```json
{
  "stations": [
    {
      "station_id": 1,
      "ranking": [
        { "game_id": 3, "rank": 1, "team_name": "Alpha Team", "duration_seconds": 190, "gap_seconds": 0 }
      ]
    }
  ]
}
```

### `GET /games/{game_id}`
Full detail for one specific attempt: overall result plus its own time (and that station's rank) at each station it solved.

Response `200`:
```json
{
  "game_id": 3,
  "team_name": "Alpha Team",
  "duration_seconds": 1325,
  "overall_rank": 1,
  "stations": [
    { "station_id": 1, "rank": 2, "duration_seconds": 190, "gap_seconds": 30 }
  ]
}
```
Response `404`: `game_id` doesn't exist or isn't a `defused` game.

---

## 2. Internal API needed from the Dashboard Backend

**⚠️ NOT IMPLEMENTED YET - owned by the Dashboard Team.** The Scoreboard Backend currently runs against fake data (`repositories/fake_repository.py`, `repositories/fake_station_events_repository.py`) until these two endpoints exist. See `dashboard/backend/README.md` for the same contract with setup instructions.

Both endpoints: return **everything**, unfiltered and unsorted - the Scoreboard Backend does all filtering/sorting/ranking itself. Keep this as simple as possible on your side.

| Method | Path | Status |
|---|---|---|
| `GET` | `/internal/games` | ❌ TODO (Dashboard Team) |
| `GET` | `/internal/station-events` | ❌ TODO (Dashboard Team) |

### `GET /internal/games`
One entry per game (every attempt, by every team, regardless of outcome).

```json
[
  {
    "game_id": 3,
    "team_name": "Alpha Team",
    "outcome": "defused",
    "started_at": "2026-09-22T09:00:00",
    "ended_at": "2026-09-22T09:22:05"
  }
]
```
| Field | Type | Meaning |
|---|---|---|
| `game_id` | int | unique per attempt - the same team can play more than once |
| `team_name` | string | as entered at game start |
| `outcome` | `"running"` \| `"defused"` \| `"exploded"` | |
| `started_at` | string (ISO 8601) | |
| `ended_at` | string (ISO 8601) or `null` | `null` while `running` |

### `GET /internal/station-events`
One entry per station event ever recorded (mirrors the ICD `status` payload, plus `team_name` and `game_id`).

```json
[
  {
    "game_id": 3,
    "team_name": "Alpha Team",
    "station_id": 1,
    "state": "solved",
    "timestamp_start": "2026-09-22T09:00:00",
    "timestamp_end": "2026-09-22T09:03:10"
  }
]
```
| Field | Type | Meaning |
|---|---|---|
| `game_id` | int | which attempt this event belongs to (same value as in `/internal/games`) |
| `team_name` | string | |
| `station_id` | int | |
| `state` | `"idle"` \| `"active"` \| `"solved"` | same values as the ICD |
| `timestamp_start` | string (ISO 8601) or `null` | |
| `timestamp_end` | string (ISO 8601) or `null` | |

---

## 3. Dashboard Public API (browser ↔ Dashboard Backend)

**To be documented by the Dashboard Team.** This section covers the endpoints the Dashboard frontend calls directly (start a game, submit a code attempt, live updates, etc.) - not part of the Scoreboard's contract, but belongs in this document so the whole system's API surface is in one place.

_(Dashboard Team: add your endpoints here, same format as Section 1 - method, path, example request/response, status codes.)_
