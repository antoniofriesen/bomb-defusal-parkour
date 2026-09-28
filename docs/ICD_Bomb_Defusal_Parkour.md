# ICD "Bomb Defusal Parkour - LF07 ITECH BGH"

Version: v1 – Draft – 2026-09-17

## Identification of the Interface
Interface between the Coordination Team (broker + dashboard) and each Station, communicating via MQTT.

## Systems Involved
- **Station (Zelle)**: builds and operates one puzzle station. Receives its digit from the Coordination Team at game start, and sends state updates (idle / active / solved) back.
- **Coordination Team**: operates the central MQTT broker and the dashboard. Sends each station its digit at game start, and receives status updates from all stations to display live progress and the scoreboard.

## Topics & Protocol
Protocol: MQTT (Mosquitto broker), JSON payloads, transmitted event-based (not periodic).

- `parkour/station/{id}/start` → Coordination Team sends the station its digit at game start
- `parkour/station/{id}/status` → Station sends its current status to the Coordination Team

Note: since two teams can never play in parallel (only stations run in parallel, not teams), no team identifier is included in the payloads — there is only ever one active game run to disambiguate.

Note: upon receiving a new `digit` on `start` (i.e. at the beginning of a new game round), a station MUST reset its own state and publish a `status` update with `state: "idle"` — even if it was `solved` in a previous round. This both resets stale `solved` state from a previous round and confirms to the dashboard that the station is online and ready.

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
  "state": "solved",
  "rating": "green",
  "timestamp_start": "2026-09-17T10:15:00",
  "timestamp_end": "2026-09-17T10:20:00"
}
```
| # | Field | Type | Meaning |
|---|---|---|---|
| 1 | station_id | int | identifies which station sent the update |
| 2 | state | enum (string): `"idle"` \| `"active"` \| `"solved"` | `idle` = not yet started, `active` = a player is currently at the station, `solved` = puzzle solved |
| 3 | rating | enum (string): `"green"` \| `"yellow"` \| `"red"` or `null` | visitor feedback — `null` as long as the station has not been played yet (e.g. the `idle` message sent on reset) |
| 4 | timestamp_start | string (as shown in the example above) or `null` | when the player started interacting with the station — `null` as long as the station has not been played yet (e.g. the `idle` message sent on reset) |
| 5 | timestamp_end | string (as shown in the example above) or `null` | when the station was solved — `null` if not yet solved |

Example of the `idle` message a station sends after receiving a new `digit` (nothing played yet, so all optional fields are `null`):
```json
{
  "station_id": 1,
  "state": "idle",
  "rating": null,
  "timestamp_start": null,
  "timestamp_end": null
}
```

Note: duration is intentionally not sent as its own field — it is fully derivable as `timestamp_end - timestamp_start` (both recorded by the same station, same clock, so no precision is lost by computing it on the receiving side instead).

## Dependencies
- Every station implements its own MQTT connection (paho-mqtt: connect, subscribe, publish) - this is intentionally not shared, so every station learns the MQTT mechanics themselves.
- Every station is responsible for using `icd_interface.py` (`ICDInterface.start_payload()` / `ICDInterface.status_payload()`) to build its payloads, instead of hand-building the JSON - this is what keeps every station's payloads compatible with the broker and dashboard, regardless of how each station's own MQTT code is written.
- Stations never communicate with each other directly; all communication goes through the Coordination Team's broker.
- A station cannot start its puzzle before receiving its `digit` on the `start` topic — it depends on the Coordination Team publishing that message first.
- Every station is responsible for resetting its own state to `idle` and publishing that reset whenever it receives a new `digit` — otherwise the dashboard could keep showing a stale `solved` state from a previous round.
- The Coordination Team depends on every station correctly publishing `status` updates (especially `station_id` and `state`) — without them, the dashboard cannot show live progress or assemble the final code.
- The Coordination Team is responsible for operating the broker; if it is unreachable, no station can receive its digit or report its status.
