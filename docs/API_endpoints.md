# API Contract - Bomb Defusal Parkour

Version: v1 – Draft – 2026-09-23

## Overview

Two backend services, each documented in its own section below:

- **Scoreboard Backend** (Python/FastAPI, `scoreboard/backend/`) - implemented and tested. Reads game/station data, builds rankings, serves the scoreboard page.
- **Dashboard Backend** (C#/.NET, `dashboard/backend/`) - owns the database and the MQTT connection. The Scoreboard Backend depends on two endpoints from it (Section 2).

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
  "gap_seconds": 0,
  "stations": [
    { "station_id": 1, "rank": 2, "duration_seconds": 190, "gap_seconds": 30 }
  ]
}
```
Response `404`: `game_id` doesn't exist or isn't a `defused` game.

---

## 2. Internal API needed from the Dashboard Backend

**✅ Implemented by the Dashboard Team.** The Scoreboard Backend can run against fake data (`repositories/fake_repository.py`, `repositories/fake_station_events_repository.py`) or against these real endpoints, controlled by `SCOREBOARD_USE_FAKE_DATA`.

Both endpoints: return **everything**, unfiltered and unsorted - the Scoreboard Backend does all filtering/sorting/ranking itself.

**Field naming: camelCase**, not snake_case (differs from Section 1/3 below). This is ASP.NET Core's default JSON serialization for the Dashboard Backend's C# models - kept as-is rather than requiring extra configuration on that side. The Scoreboard Backend's Pydantic models accept both spellings (`alias_generator`), so this only affects what you see on the wire, not the Python field names used elsewhere in the codebase.

| Method | Path | Status |
|---|---|---|
| `GET` | `/internal/games` | ✅ Implemented |
| `GET` | `/internal/station-events` | ✅ Implemented |

### `GET /internal/games`
One entry per game (every attempt, by every team, regardless of outcome).

```json
[
  {
    "gameId": 3,
    "teamName": "Alpha Team",
    "outcome": "defused",
    "startedAt": "2026-09-22T09:00:00",
    "endedAt": "2026-09-22T09:22:05"
  },
  {
    "gameId": 4,
    "teamName": "Beta Team",
    "outcome": "exploded",
    "startedAt": "2026-09-22T09:00:00",
    "endedAt": "2026-09-22T09:22:05"
  }
]
```
| Field | Type | Meaning |
|---|---|---|
| `gameId` | int | unique per attempt - the same team can play more than once |
| `teamName` | string | as entered at game start |
| `outcome` | `"running"` \| `"defused"` \| `"exploded"` | |
| `startedAt` | string (ISO 8601) | |
| `endedAt` | string (ISO 8601) or `null` | `null` while `running` |

### `GET /internal/station-events`
One entry per station event ever recorded (mirrors the ICD `status` payload, plus `teamName` and `gameId`).

```json
[
  {
    "gameId": 3,
    "teamName": "Alpha Team",
    "stationId": 1,
    "state": "solved",
    "timestampStart": "2026-09-22T09:00:00",
    "timestampEnd": "2026-09-22T09:03:10"
  }
]
```
| Field | Type | Meaning |
|---|---|---|
| `gameId` | int | which attempt this event belongs to (same value as in `/internal/games`) |
| `teamName` | string | |
| `stationId` | int | |
| `state` | `"idle"` \| `"active"` \| `"solved"` | same values as the ICD |
| `timestampStart` | string (ISO 8601) or `null` | |
| `timestampEnd` | string (ISO 8601) or `null` | |

---

## 3. Dashboard Public API (browser ↔ Dashboard Backend)

| Method | Path | Status |
|---|---|---|
| `GET` | `/dashboard/backend/status` | ✅ Implemented |
| `POST` | `/dashboard/backend/start` | ✅ Implemented |
| `POST` | `/dashboard/backend/stop` | ✅ Implemented |

### `GET /dashboard/backend/status`
One entry per station, returns the last known status of every station; If the state of a station is unknown, it will be missing

Response Example:
```json
[
    {
        "stationDatenId": 1,
        "stationId": 1,
        "spielId": 9,
        "state": "solved",
        "rating": "yellow",
        "timestampStart": "2026-09-25T00:07:22",
        "timestampEnd": "2026-09-25T00:07:29"
    },
    {
        "stationDatenId": 2,
        "stationId": 2,
        "spielId": 9,
        "state": "idle",
        "rating": "unknown",
        "timestampStart": null,
        "timestampEnd": null
    },
    {
        "stationDatenId": 3,
        "stationId": 3,
        "spielId": 9,
        "state": "idle",
        "rating": "unknown",
        "timestampStart": null,
        "timestampEnd": null
    }
]
```
NOTE: Please look at ./ICD_Bomb_Defusal_Parkour.md for more details.

### `POST /dashboard/backend/start`
Creates a new team and game object in the database and makes all incoming status updates from stations be associated with the new game.

Post Example:
```json
{
    "team_name": "My Cool Team",
    "member_count": 6
}
```
| Field | Type | Meaning |
|---|---|---|
| `team_name` | string | The name of the team which is playing now |
| `member_count` | int | The amout of players in this team |


### `POST /dashboard/backend/stop`
Stops the current game and stores the outcome / reason why it was stopped in the database.

Post Example:
```json
{
    "outcome": "exploded"
}
```
| Field | Type | Meaning |
|---|---|---|
| `outcome` | string | `"defused"` \| `"exploded"` |