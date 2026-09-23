# ICD "Internal Dashboard-Dashboard - LF07 ITECH BGH"

Version: v1 – Draft – 2026-09-23

## Identification of the Interface
Interface between the Dashboard-Frontend and the Dashboard-Backend, communicating via HTTP.

## Systems Involved
- **Dashboard-Frontend**: Creates teams, starts the game, shows real-time information about stations and controlls game logic.
- **Dashboard-Backend**: Manages the database and provides the HTTP-endpoints to interact with it

## Protocol & Endpoints
Protocol: HTTP, JSON payloads, Request-Response-Pattern.

- POST `/internal/dashboardbackend/start` → Registers a new group in the database and generates the code to end the game
Request:
```json
{
  "group_name": "Example Group",
  "player_count": 6
}
```
| # | Field | Type | Meaning |
|---|---|---|---|
| 1 | group_name | string | The name of the group |
| 2 | player_count | int | The amount of members of the group |

Response:
```json
{
  "code": "ABCDEF"
}
```
| # | Field | Type | Meaning |
|---|---|---|---|
| 1 | code | string | The 6-digit-code needed to win the game |

- POST `/internal/dashboardbackend/stop` → Stops the game if the provided code is correct, otherwise 400 gets returned
Request:
```json
{
  "code": "ABCDEF",
  "force": false
}
```
| # | Field | Type | Meaning |
|---|---|---|---|
| 1 | code | string | The 6-digit-code needed to win the game; Ends the game if it is correct |
| 2 | force | bool | If true, ends the game and assumes the group has lost the game |

Response:
```
200: Only if the rovided code is correct (The game has been won) or force has been true,
400: Only if the provided code is wrong
```

- GET `/internal/dashboardbackend/status` → Returns the last known state of the individual stations
Request:
```
[EMPTY]
```

Response:
```json
[
    {
        "station_id": 1,
        "state": "solved",
        "rating": "green",
        "timestamp_start": "2026-09-17T10:15:00",
        "timestamp_end": "2026-09-17T10:20:00"
    },
    {
        "station_id": 2,
        "state": "solved",
        "rating": "green",
        "timestamp_start": "2026-09-17T10:15:00",
        "timestamp_end": "2026-09-17T10:20:00"
    },
    {
        "station_id": 3,
        "state": "solved",
        "rating": "green",
        "timestamp_start": "2026-09-17T10:15:00",
        "timestamp_end": "2026-09-17T10:20:00"
    }
]
```
NOTE: Please view at ./ICD_Bomb_Defusal_Parkour.md for the proper definition of these objects!!!


## Dependencies
- The Dashboard-Frontend is responsible for sending requests in the correct order: You can not start the game if it is already running; You can not stop a game while no game is running.
- The definition of the objects returned by /internal/dashboardbackend/status comes from ./ICD_Bomb_Defusal_Parkour.md
