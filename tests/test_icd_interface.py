"""Tests for icd_interface.py.

Expected values come from the ICD (docs/ICD_Bomb_Defusal_Parkour.md),
not from the implementation - otherwise a test would only check that the
code agrees with itself.
"""

import pytest

from icd_interface import ICDInterface

# Values taken from the ICD example for the `status` payload (solved station)
ICD_SOLVED_EXAMPLE = {
    "station_id": 1,
    "state": "solved",
    "rating": "green",
    "timestamp_start": "2026-09-17T10:15:00",
    "timestamp_end": "2026-09-17T10:20:00",
}

# Exactly the fields the ICD defines for `status` (no duration, see ICD note)
ICD_STATUS_FIELDS = {"station_id", "state", "rating", "timestamp_start", "timestamp_end"}


# --- Topics ------------------------------------------------------------------

@pytest.mark.parametrize("station_id, expected", [
    (1, "parkour/station/1/start"),
    (3, "parkour/station/3/start"),
    (6, "parkour/station/6/start"),
])
def test_start_topic_matches_icd(station_id, expected):
    assert ICDInterface.start_topic(station_id) == expected


@pytest.mark.parametrize("station_id, expected", [
    (1, "parkour/station/1/status"),
    (5, "parkour/station/5/status"),
    (6, "parkour/station/6/status"),
])
def test_status_topic_matches_icd(station_id, expected):
    assert ICDInterface.status_topic(station_id) == expected


# --- start payload (Coordination Team -> Station) ---------------------------

@pytest.mark.parametrize("digit", [0, 5, 9])
def test_start_payload_matches_icd(digit):
    assert ICDInterface.start_payload(digit) == {"digit": digit}


@pytest.mark.parametrize("digit", [-1, 10])
def test_start_payload_rejects_digit_outside_0_to_9(digit):
    with pytest.raises(ValueError, match="digit"):
        ICDInterface.start_payload(digit)


# --- status payload (Station -> Coordination Team) --------------------------

def test_status_payload_solved_matches_icd():
    payload = ICDInterface.status_payload(**ICD_SOLVED_EXAMPLE)

    assert payload == ICD_SOLVED_EXAMPLE


def test_status_payload_idle_has_null_fields():
    payload = ICDInterface.status_payload(station_id=1, state="idle")

    assert payload == {
        "station_id": 1,
        "state": "idle",
        "rating": None,
        "timestamp_start": None,
        "timestamp_end": None,
    }


def test_status_payload_active_has_start_but_no_end():
    payload = ICDInterface.status_payload(
        station_id=2,
        state="active",
        timestamp_start="2026-09-17T10:15:00",
    )

    assert payload["timestamp_start"] == "2026-09-17T10:15:00"
    assert payload["timestamp_end"] is None


def test_status_payload_contains_exactly_the_icd_fields():
    payload = ICDInterface.status_payload(**ICD_SOLVED_EXAMPLE)

    assert set(payload) == ICD_STATUS_FIELDS
    assert "duration_seconds" not in payload


@pytest.mark.parametrize("state", ["idle", "active", "solved"])
def test_status_payload_accepts_every_icd_state(state):
    assert ICDInterface.status_payload(station_id=1, state=state)["state"] == state


@pytest.mark.parametrize("rating", ["green", "yellow", "red"])
def test_status_payload_accepts_every_icd_rating(rating):
    payload = ICDInterface.status_payload(station_id=1, state="solved", rating=rating)

    assert payload["rating"] == rating


# "unsolved" was an earlier state value that no longer exists; the values
# are case sensitive.
@pytest.mark.parametrize("state", ["broken", "unsolved", "Solved", ""])
def test_status_payload_rejects_invalid_state(state):
    with pytest.raises(ValueError, match="state"):
        ICDInterface.status_payload(station_id=1, state=state)


@pytest.mark.parametrize("rating", ["blue", "GREEN", ""])
def test_status_payload_rejects_invalid_rating(rating):
    # state is valid here, so only the rating can trigger the error
    with pytest.raises(ValueError, match="rating"):
        ICDInterface.status_payload(station_id=1, state="idle", rating=rating)
