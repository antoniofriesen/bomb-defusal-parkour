# ICD "Bomb Defusal Parkour - LF07 ITECH BGH"

Version: v1 – Draft – 2026-09-17

## Identification of the Interface
Interface between the Coordination Team (broker + dashboard) and each Station, communicating via MQTT.

## Systems Involved
- **Station (Zelle)**: builds and operates one puzzle station. Receives its digit from the Coordination Team at game start, and sends status updates (active / solved) back.
- **Coordination Team**: operates the central MQTT broker and the dashboard. Sends each station its digit at game start, and receives status updates from all stations to display live progress and the scoreboard.

## Topics & Protocol
Protocol: MQTT (Mosquitto broker), JSON payloads, transmitted event-based (not periodic).

- `parkour/station/{id}/start` → Coordination Team sends the station its digit at game start
- `parkour/station/{id}/status` → Station sends its current status to the Coordination Team

Note: since two teams can never play in parallel (only stations run in parallel, not teams), no team identifier is included in the payloads — there is only ever one active game run to disambiguate.

## Payload Format

`parkour/station/{id}/start`
```json
{
  "digit": 3
}
```
| # | Field | Type | Meaning |
|---|---|---|---|
| 1 | digit | int (0-9) | digit to be presented to the visitor once the station is solved |

`parkour/station/{id}/status`
```json
{
  "station_id": 1,
  "status": "solved",
  "active": false,
  "rating": "green",
  "duration_seconds": 300,
  "timestamp_start": "2026-09-17T10:15:00",
  "timestamp_end": "2026-09-17T10:20:00"
}
```
| # | Field | Type | Meaning |
|---|---|---|---|
| 1 | station_id | int | identifies which station sent the update |
| 2 | status | string | `"solved"` or `"unsolved"` |
| 3 | active | boolean | `true` if a player is currently at the station |
| 4 | rating | string | `"green"`, `"yellow"` or `"red"` — visitor feedback |
| 5 | duration_seconds | int | seconds taken to solve (`0` if unsolved) |
| 6 | timestamp_start | string (ISO 8601) | when the player started interacting with the station |
| 7 | timestamp_end | string (ISO 8601) or `null` | when the station was solved — `null` if not yet solved |

## Dependencies
- Every station is responsible for using `mqtt_interface.py` (or an equivalent implementing the same contract) instead of writing custom MQTT logic — this is what keeps every station compatible with the broker and dashboard.
- Stations never communicate with each other directly; all communication goes through the Coordination Team's broker.
- A station cannot start its puzzle before receiving its `digit` on the `start` topic — it depends on the Coordination Team publishing that message first.
- The Coordination Team depends on every station correctly publishing `status` updates (especially `station_id` and `status`) — without them, the dashboard cannot show live progress or assemble the final code.
- The Coordination Team is responsible for operating the broker; if it is unreachable, no station can receive its digit or report its status.
