"""
mqtt_interface.py
=================
Bomb Defusal Parkour – LF07 BGH
Coordination Cell – MQTT Interface Library

Usage (every station imports this):
------------------------------------
    from mqtt_interface import MQTTInterface

    mqtt = MQTTInterface(station_id=1, broker_ip="192.168.1.100")
    mqtt.connect()

    # Listen for game start (receives digit)
    mqtt.on_start = lambda digit, team: print(f"Game started! My digit: {digit}, Team: {team}")

    # Send status update to dashboard
    mqtt.send_status(
        status="solved",
        active=False,
        rating="green",
        duration_seconds=213,
        timestamp_start="2026-09-16T09:15:00",
        timestamp_end="2026-09-16T09:18:33"
    )

    mqtt.loop_forever()
"""

import json
import paho.mqtt.client as mqtt
from datetime import datetime


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

BROKER_PORT = 1883
TOPIC_START  = "parkour/station/{id}/start"   # Dashboard → Station
TOPIC_STATUS = "parkour/station/{id}/status"  # Station   → Dashboard

STATUS_SOLVED   = "solved"
STATUS_UNSOLVED = "unsolved"

RATING_GREEN  = "green"
RATING_YELLOW = "yellow"
RATING_RED    = "red"


# ──────────────────────────────────────────────
# MQTTInterface Class
# ──────────────────────────────────────────────

class MQTTInterface:
    """
    Central MQTT interface for a single station.
    Each station creates one instance with its own station_id.
    """

    def __init__(self, station_id: int, broker_ip: str):
        """
        Args:
            station_id: Unique station number (1–6)
            broker_ip:  IP address of the central MQTT broker (Coordination Cell Pi)
        """
        self.station_id = station_id
        self.broker_ip  = broker_ip

        self._topic_start  = TOPIC_START.replace("{id}", str(station_id))
        self._topic_status = TOPIC_STATUS.replace("{id}", str(station_id))

        self._client = mqtt.Client(client_id=f"station_{station_id}")
        self._client.on_connect    = self._on_connect
        self._client.on_message    = self._on_message
        self._client.on_disconnect = self._on_disconnect

        # ── Callbacks (override these in your station code) ──
        self.on_start = None   # fn(digit: int, team: str) → called when game starts


    # ──────────────────────────────────────────
    # Connection
    # ──────────────────────────────────────────

    def connect(self):
        """Connect to the MQTT broker and start background loop."""
        print(f"[Station {self.station_id}] Connecting to broker at {self.broker_ip}...")
        self._client.connect(self.broker_ip, BROKER_PORT, keepalive=60)
        self._client.loop_start()

    def loop_forever(self):
        """Block and listen forever (use instead of loop_start if no other loop needed)."""
        self._client.loop_forever()

    def disconnect(self):
        """Disconnect from broker."""
        self._client.loop_stop()
        self._client.disconnect()
        print(f"[Station {self.station_id}] Disconnected.")


    # ──────────────────────────────────────────
    # Send: Station → Dashboard
    # ──────────────────────────────────────────

    def send_status(
        self,
        status: str,
        active: bool,
        rating: str,
        duration_seconds: int,
        timestamp_start: str,
        timestamp_end: str = None
    ):
        """
        Send a status update to the Dashboard.

        Args:
            status:           "solved" or "unsolved"
            active:           True if station is currently being played
            rating:           Visitor feedback – "green", "yellow", or "red"
            duration_seconds: Seconds taken to solve (0 if unsolved)
            timestamp_start:  ISO 8601 string, e.g. "2026-09-16T09:15:00"
            timestamp_end:    ISO 8601 string or None if not yet solved
        """
        payload = {
            "station_id":       self.station_id,
            "status":           status,
            "active":           active,
            "rating":           rating,
            "duration_seconds": duration_seconds,
            "timestamp_start":  timestamp_start,
            "timestamp_end":    timestamp_end,
        }
        self._publish(self._topic_status, payload)
        print(f"[Station {self.station_id}] Status sent: {status} | active={active} | rating={rating}")

    def send_active(self, timestamp_start: str):
        """
        Shortcut: mark station as active (player started interacting).

        Args:
            timestamp_start: ISO 8601 string of when interaction started
        """
        self.send_status(
            status=STATUS_UNSOLVED,
            active=True,
            rating=RATING_GREEN,
            duration_seconds=0,
            timestamp_start=timestamp_start,
            timestamp_end=None
        )

    def send_solved(self, rating: str, duration_seconds: int,
                    timestamp_start: str, timestamp_end: str):
        """
        Shortcut: mark station as solved.

        Args:
            rating:           Visitor feedback – "green", "yellow", or "red"
            duration_seconds: Total seconds to solve
            timestamp_start:  ISO 8601 start time
            timestamp_end:    ISO 8601 end time
        """
        self.send_status(
            status=STATUS_SOLVED,
            active=False,
            rating=rating,
            duration_seconds=duration_seconds,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end
        )


    # ──────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────

    @staticmethod
    def now_iso() -> str:
        """Returns current time as ISO 8601 string."""
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


    # ──────────────────────────────────────────
    # Internal MQTT callbacks
    # ──────────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[Station {self.station_id}] Connected to broker.")
            client.subscribe(self._topic_start)
            print(f"[Station {self.station_id}] Subscribed to: {self._topic_start}")
        else:
            print(f"[Station {self.station_id}] Connection failed. Code: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            print(f"[Station {self.station_id}] ERROR: Invalid JSON received.")
            return

        if msg.topic == self._topic_start:
            digit = payload.get("digit")
            team  = payload.get("team", "Unknown")
            print(f"[Station {self.station_id}] Game started! Digit: {digit} | Team: {team}")
            if self.on_start:
                self.on_start(digit, team)

    def _on_disconnect(self, client, userdata, rc):
        print(f"[Station {self.station_id}] Disconnected (code={rc}).")

    def _publish(self, topic: str, payload: dict):
        message = json.dumps(payload)
        self._client.publish(topic, message)


# ──────────────────────────────────────────────
# Example usage (run this file directly to test)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import time

    BROKER_IP  = "192.168.1.100"   # ← Change to your Coordination Cell Pi IP
    STATION_ID = 1                 # ← Change to your station number

    mqtt_iface = MQTTInterface(station_id=STATION_ID, broker_ip=BROKER_IP)

    # Define what happens when game starts
    def on_game_start(digit, team):
        print(f"\n>>> My digit this round: {digit} (Team: {team})")
        # TODO: Store digit, show it after puzzle is solved

    mqtt_iface.on_start = on_game_start
    mqtt_iface.connect()

    time.sleep(2)

    # Simulate: player starts interacting
    start_time = MQTTInterface.now_iso()
    mqtt_iface.send_active(timestamp_start=start_time)

    time.sleep(3)

    # Simulate: station solved
    end_time = MQTTInterface.now_iso()
    mqtt_iface.send_solved(
        rating=RATING_GREEN,
        duration_seconds=3,
        timestamp_start=start_time,
        timestamp_end=end_time
    )

    time.sleep(1)
    mqtt_iface.disconnect()