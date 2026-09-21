"""
icd_interface.py
=================
Bomb Defusal Parkour - LF07 ITECH BGH

WHAT THIS IS NOT: this does not connect to the MQTT broker and does not
publish or subscribe to anything. Every station implements its own MQTT
connection (paho-mqtt: connect, subscribe, publish) - that is intentional,
so every station learns the MQTT mechanics themselves.

WHAT THIS IS: a stateless helper that builds MQTT message payloads exactly
as defined in the ICD (docs/ICD_Bomb_Defusal_Parkour.md), and validates
values against the ICD's allowed fields/enums - so every station sends the
same, correctly-shaped JSON, no matter how each station's own MQTT code
is written.

Usage:
    from icd_interface import ICDInterface
    import json

    payload = ICDInterface.status_payload(
        station_id=1,
        state="solved",
        rating="green",
        timestamp_start="2026-09-18T10:15:00",
        timestamp_end="2026-09-18T10:18:33",
    )

    # your own MQTT client/connection code:
    client.publish(ICDInterface.status_topic(1), json.dumps(payload))
"""

from __future__ import annotations

VALID_STATES = {"idle", "active", "solved"}
VALID_RATINGS = {"green", "yellow", "red"}

TOPIC_START = "parkour/station/{id}/start"
TOPIC_STATUS = "parkour/station/{id}/status"


class ICDInterface:
    """Builds ICD-compliant payload dicts and topic strings. Holds no state, makes no MQTT calls."""

    @staticmethod
    def start_topic(station_id: int) -> str:
        """Topic to subscribe to (as a station) or publish to (as the Coordination Team)."""
        return TOPIC_START.format(id=station_id)

    @staticmethod
    def status_topic(station_id: int) -> str:
        """Topic to publish to (as a station) or subscribe to (as the Coordination Team)."""
        return TOPIC_STATUS.format(id=station_id)

    @staticmethod
    def start_payload(digit: int) -> dict:
        """Payload for parkour/station/{id}/start (Coordination Team -> Station).

        Only called by the Coordination Team.
        A station never calls this.
        """
        if not (0 <= digit <= 9):
            raise ValueError(f"digit must be between 0 and 9, got {digit!r}")

        return {
            "digit": digit,
        }

    @staticmethod
    def status_payload(
        station_id: int,
        state: str,
        rating: str|None = None,
        timestamp_start: str|None = None,
        timestamp_end: str|None = None,
    ) -> dict:
        """Payload for parkour/station/{id}/status (Station -> Coordination Team).

        Only called by a Station. Only stations ever send a status update.
        The Coordination Team never calls this.

        No duration field - it's fully derivable as timestamp_end - timestamp_start
        (both from the same station's clock), so it's not duplicated here.
        """
        if state not in VALID_STATES:
            raise ValueError(f"state must be one of {VALID_STATES}, got {state!r}")
        if rating is not None and rating not in VALID_RATINGS:
            raise ValueError(f"rating must be one of {VALID_RATINGS}, got {rating!r}")

        return {
            "station_id": station_id,
            "state": state,
            "rating": rating,
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end,
        }
