# MQTT Sequence Diagram - Bomb Defusal Parkour

Shows the message flow between the Coordination Team's dashboard, the MQTT broker, and a station, as defined in the [ICD](./ICD_Bomb_Defusal_Parkour.md). Only one station is shown as an example - the same flow repeats independently for all 6 stations, since they never communicate with each other directly (always via the broker).

```mermaid
sequenceDiagram
    participant D as Dashboard (Coordination Team)
    participant B as MQTT Broker
    participant S1 as Station 1

    Note over D,S1: Game start - Dashboard generates a 6-digit code, one digit per station

    D->>B: publish parkour/station/1/start {digit: 3}
    B->>S1: forward start message

    Note over S1: Station resets to idle upon receiving its digit (also resets a stale "solved" from a previous round)

    S1->>B: publish parkour/station/1/status {state: "idle"}
    B->>D: forward status update

    Note over S1: Player starts interacting with Station 1

    S1->>B: publish status {state: "active"}
    B->>D: forward status update

    Note over S1: Player solves the puzzle at Station 1

    S1->>B: publish status {state: "solved", rating: "green", duration_seconds: 213, timestamp_start, timestamp_end}
    B->>D: forward status update

    Note over D: Every other station goes through the same idle -> active -> solved flow independently, in parallel

    Note over D: Dashboard collects each station's digit as its status turns "solved"
    Note over D: Player enters the assembled 6-digit code directly in the Dashboard UI (not an MQTT message)
```
