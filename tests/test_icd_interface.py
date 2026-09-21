import pytest
from icd_interface import ICDInterface


def test_status_payload_idle_has_null_fields():
    payload = ICDInterface.status_payload(station_id=1, state="idle")

    assert payload == {
        "station_id": 1,
        "state": "idle",
        "rating": None,
        "timestamp_start": None,
        "timestamp_end": None,
    }

def test_status_payload_rejects_invalid_state():
    with pytest.raises(ValueError):
        ICDInterface.status_payload(station_id=1, state="broken")

def test_status_payload_rejects_invalid_rating():
    with pytest.raises(ValueError):
        ICDInterface.status_payload(station_id=1, state="idle", rating="blue")

def test_start_topic_matches_icd():
    assert ICDInterface.start_topic(3) == "parkour/station/3/start"

def test_status_topic_matches_icd():
    assert ICDInterface.status_topic(5) == "parkour/station/5/status"

def test_start_payload_matches_icd():
    payload = ICDInterface.start_payload(digit=7)

    assert payload == {"digit": 7}

@pytest.mark.parametrize("digit", [-1, 10])
def test_start_payload_rejects_invalid_digit(digit):
    with pytest.raises(ValueError):
        ICDInterface.start_payload(digit)

@pytest.mark.parametrize("digit", [0, 9])
def test_start_payload_accepts_boundary_digits(digit):
    payload = ICDInterface.start_payload(digit)

    assert payload == { "digit": digit}

def test_status_payload_solved_matches_icd():
    payload = ICDInterface.status_payload(
        station_id=1,
        state="solved",
        rating="green",
        timestamp_start="2026-09-17T10:15:00",
        timestamp_end="2026-09-17T10:20:00",
    )

    assert payload == {
        "station_id": 1,
        "state": "solved",
        "rating": "green",
        "timestamp_start": "2026-09-17T10:15:00",
        "timestamp_end": "2026-09-17T10:20:00",
    }