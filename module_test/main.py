#!/usr/bin/env python3
"""
Bomb Defusal Parkour - Dashboard & Modul Test-Tool (All-in-One)
Komplett eigenständiges Skript – simuliert das Dashboard/Backend für Tests:
- Terminal 1: EMPFANGEN von Status-Meldungen (parkour/station/{id}/status)
- Terminal 2: SENDEN von Start-Signalen / Ziffern (parkour/station/{id}/start)
              sowie optionales Senden von Test-Statusmeldungen
"""

import sys
import time
import json
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import paho.mqtt.client as mqtt

# ==============================================================================
# BROKER-KONFIGURATION & GLOBALE EINSTELLUNGEN
# ==============================================================================
BROKER_HOST = "172.17.0.1"
BROKER_PORT = 1883
USERNAME = "pi_user"
PASSWORD = "group-1"
NUM_STATIONS = 6

# ANSI-Farbcodes für saubere Terminalausgabe
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[32m"
C_RED = "\033[31m"
C_YELLOW = "\033[33m"
C_CYAN = "\033[36m"
C_MAGENTA = "\033[35m"


def get_start_topic(station_id: int) -> str:
    return f"parkour/station/{station_id}/start"


def get_status_topic(station_id: int) -> str:
    return f"parkour/station/{station_id}/status"


def create_mqtt_client(client_id: str) -> mqtt.Client:
    """Erstellt Paho MQTT-Client (kompatibel mit Paho 1.x und 2.x)."""
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except (AttributeError, TypeError):
        client = mqtt.Client(client_id=client_id)

    if USERNAME:
        client.username_pw_set(USERNAME, PASSWORD)
    return client


# ==============================================================================
# ICD-VALIDIERUNG (LAUT SCHNITTSTELLENSPEZIFIKATION)
# ==============================================================================
VALID_STATES = {"idle", "active", "solved"}
VALID_RATINGS = {"green", "yellow", "red"}
TOPIC_REGEX = re.compile(r"^parkour/station/(\d+)/(start|status)$")


def is_iso8601(val: Any) -> bool:
    if not isinstance(val, str):
        return False
    try:
        datetime.fromisoformat(val.replace("Z", "+00:00"))
        return True
    except (ValueError, TypeError):
        return False


def validate_topic(topic: str) -> Tuple[bool, Optional[int], Optional[str], Optional[str]]:
    match = TOPIC_REGEX.match(topic)
    if not match:
        return False, None, None, f"Topic '{topic}' entspricht nicht 'parkour/station/{{id}}/(start|status)'"
    return True, int(match.group(1)), match.group(2), None


def validate_start_payload(raw_payload: str) -> Tuple[bool, Optional[dict], List[str]]:
    errors = []
    try:
        data = json.loads(raw_payload)
    except Exception as e:
        return False, None, [f"Ungültiges JSON: {e}"]

    if not isinstance(data, dict):
        return False, None, ["Payload muss ein JSON-Objekt sein."]

    if "digit" not in data:
        errors.append("Pflichtfeld 'digit' fehlt.")
    else:
        d = data["digit"]
        if not isinstance(d, int) or isinstance(d, bool):
            errors.append(f"'digit' muss int sein, erhalten: {type(d).__name__}")
        elif not (0 <= d <= 9):
            errors.append(f"'digit' muss 0-9 sein, erhalten: {d}")

    return len(errors) == 0, data, errors


def validate_status_payload(raw_payload: str, expected_station_id: Optional[int] = None) -> Tuple[bool, Optional[dict], List[str]]:
    errors = []
    try:
        data = json.loads(raw_payload)
    except Exception as e:
        return False, None, [f"Ungültiges JSON: {e}"]

    if not isinstance(data, dict):
        return False, None, ["Payload muss ein JSON-Objekt sein."]

    # station_id
    if "station_id" not in data:
        errors.append("Pflichtfeld 'station_id' fehlt.")
    else:
        sid = data["station_id"]
        if not isinstance(sid, int) or isinstance(sid, bool):
            errors.append(f"'station_id' muss int sein, erhalten: {type(sid).__name__}")
        elif expected_station_id is not None and sid != expected_station_id:
            errors.append(f"'station_id' ({sid}) stimmt nicht mit Topic-ID ({expected_station_id}) überein.")

    # state
    if "state" not in data:
        errors.append("Pflichtfeld 'state' fehlt.")
    elif data["state"] not in VALID_STATES:
        errors.append(f"'state' muss einer von {sorted(list(VALID_STATES))} sein, erhalten: '{data['state']}'")

    # rating (optional/null oder green/yellow/red)
    if data.get("rating") is not None and data["rating"] not in VALID_RATINGS:
        errors.append(f"'rating' muss null oder {sorted(list(VALID_RATINGS))} sein, erhalten: '{data['rating']}'")

    # duration_seconds
    dur = data.get("duration_seconds")
    if dur is not None and (not isinstance(dur, (int, float)) or isinstance(dur, bool) or dur < 0):
        errors.append(f"'duration_seconds' muss >= 0 sein, erhalten: {dur}")

    # timestamps
    for field in ("timestamp_start", "timestamp_end"):
        val = data.get(field)
        if val is not None and not is_iso8601(val):
            errors.append(f"'{field}' ist kein gültiger ISO-8601 Zeitstempel: '{val}'")

    return len(errors) == 0, data, errors


# ==============================================================================
# HILFSFUNKTIONEN & VERBINDUNGSAUFBAU
# ==============================================================================

def parse_stations_input(raw: str) -> List[int]:
    """Parst Eingaben wie 'all', '3', '3,4', '3, 4', '1-3'."""
    raw = raw.strip().lower()
    if not raw or raw in ("all", "alle", "*"):
        return list(range(1, NUM_STATIONS + 1))

    range_match = re.match(r"^(\d+)\s*-\s*(\d+)$", raw)
    if range_match:
        s, e = int(range_match.group(1)), int(range_match.group(2))
        return [i for i in range(s, e + 1) if 1 <= i <= NUM_STATIONS]

    parts = re.findall(r"\d+", raw)
    stations = []
    for p in parts:
        val = int(p)
        if 1 <= val <= NUM_STATIONS and val not in stations:
            stations.append(val)
    return sorted(stations) if stations else list(range(1, NUM_STATIONS + 1))


def connect_mqtt(client_id: str, timeout: float = 3.5) -> Optional[mqtt.Client]:
    """Stellt Verbindung zum MQTT-Broker her mit automatischer Fehlerbehandlung."""
    global BROKER_HOST, BROKER_PORT
    client = create_mqtt_client(client_id=client_id)
    connected = {"ok": False, "rc": None}

    def on_connect(c, userdata, flags, reason_code, properties=None):
        rc = getattr(reason_code, "value", reason_code)
        connected["rc"] = rc
        if rc == 0:
            connected["ok"] = True

    client.on_connect = on_connect

    try:
        client.connect_async(BROKER_HOST, BROKER_PORT)
        client.loop_start()

        start = time.time()
        while time.time() - start < timeout:
            if connected["ok"] or connected["rc"] is not None:
                break
            time.sleep(0.05)

        if connected["ok"]:
            return client

        client.loop_stop()
        client.disconnect()

        print(f"\n{C_RED}❌ Keine Verbindung zum Broker ({BROKER_HOST}:{BROKER_PORT}){C_RESET}")
        if connected["rc"] is not None:
            print(f"   Grund: Fehlercode {connected['rc']} (Benutzername/Passwort falsch?)")
        else:
            print("   Grund: Timeout. Bist du mit dem WLAN des Raspberry Pi verbunden?")

        change = input(f"\n   Möchtest du eine andere Broker-IP testen (z.B. localhost)? [j/N]: ").strip().lower()
        if change in ("j", "ja", "y", "yes"):
            new_ip = input("   Neue Broker-IP: ").strip()
            if new_ip:
                BROKER_HOST = new_ip
                return connect_mqtt(client_id, timeout=timeout)
        return None

    except Exception as e:
        print(f"\n{C_RED}❌ Netzwerkfehler beim Verbindungsaufbau:{C_RESET} {e}")
        return None


# ==============================================================================
# MODUS 1: EMPFANGEN (DASHBOARD STATUS-MONITOR)
# ==============================================================================

def run_receiver(stations: List[int]):
    print(f"\n{C_BOLD}{'=' * 65}{C_RESET}")
    print(f"📥 {C_BOLD}EMPFÄNGER AKTIV (Dashboard Monitor){C_RESET}")
    print(f"   Überwachte Station(en): {C_CYAN}{stations}{C_RESET}")
    print(f"   Broker: {BROKER_HOST}:{BROKER_PORT} (User: {USERNAME})")
    print(f"{C_BOLD}{'=' * 65}{C_RESET}\n")

    client = connect_mqtt(client_id=f"dash_rx_{int(time.time())}")
    if not client:
        return

    station_state: Dict[int, Dict[str, Any]] = {
        sid: {"state": "unbekannt", "digit": "-", "dur": "-", "rating": "-", "updated": "-"}
        for sid in stations
    }

    def print_summary_table():
        print(f"\n{C_BOLD}--- STATUS-ÜBERSICHT ---{C_RESET}")
        print(f"{'Station':<8} | {'Status':<10} | {'Ziffer':<6} | {'Dauer':<8} | {'Rating':<8} | {'Zeit':<8}")
        print("-" * 55)
        for sid in stations:
            info = station_state[sid]
            st = info["state"]
            if st == "solved":
                st_str = f"{C_GREEN}{st:<10}{C_RESET}"
            elif st == "active":
                st_str = f"{C_YELLOW}{st:<10}{C_RESET}"
            elif st == "idle":
                st_str = f"{C_CYAN}{st:<10}{C_RESET}"
            else:
                st_str = f"{st:<10}"

            dur_str = f"{info['dur']}s" if info["dur"] != "-" else "-"
            print(f"Station {sid:<2} | {st_str} | {str(info['digit']):<6} | {dur_str:<8} | {str(info['rating']):<8} | {str(info['updated']):<8}")
        print("-" * 55 + "\n")

    def on_message(c, userdata, msg):
        topic = msg.topic
        payload_raw = msg.payload.decode("utf-8", errors="replace")
        now_str = datetime.now().strftime("%H:%M:%S")

        is_valid_topic, sid, action, err = validate_topic(topic)
        if not is_valid_topic or sid not in stations:
            return

        print(f"\n[{now_str}] {C_MAGENTA}{topic}{C_RESET}")

        if action == "status":
            valid, data, errors = validate_status_payload(payload_raw, expected_station_id=sid)
            if valid and data:
                st = data.get("state")
                dur = data.get("duration_seconds")
                rat = data.get("rating")
                t_start = data.get("timestamp_start")
                t_end = data.get("timestamp_end")

                station_state[sid]["state"] = st
                station_state[sid]["dur"] = dur if dur is not None else "-"
                station_state[sid]["rating"] = rat if rat else "-"
                station_state[sid]["updated"] = now_str

                if st == "idle":
                    print(f"  Status:       {C_CYAN}idle ⚪ (Station bereit & zurückgesetzt){C_RESET}")
                elif st == "active":
                    print(f"  Status:       {C_YELLOW}active 🟡 (Spieler interagiert){C_RESET}")
                    if t_start:
                        print(f"  Startzeit:    {t_start}")
                elif st == "solved":
                    print(f"  Status:       {C_GREEN}solved 🟢 (RÄTSEL GELÖST!){C_RESET}")
                    if dur is not None:
                        print(f"  Lösungsdauer: {C_BOLD}{dur} Sekunden{C_RESET}")
                    if rat:
                        print(f"  Rating:       {rat}")
                    if t_start and t_end:
                        print(f"  Zeitfenster:  {t_start} -> {t_end}")

                print(f"  ICD-Check:    {C_GREEN}✅ Gültig{C_RESET}")
            else:
                print(f"  {C_RED}❌ ICD-VALIDIERUNGSFEHLER:{C_RESET}")
                for e in errors:
                    print(f"     - {e}")
                print(f"  Rohdaten:     {payload_raw}")

        elif action == "start":
            valid, data, errors = validate_start_payload(payload_raw)
            if valid and data:
                digit = data.get("digit")
                station_state[sid]["digit"] = digit
                station_state[sid]["updated"] = now_str
                print(f"  Signal:       {C_BOLD}Game Start{C_RESET} -> Zugewiesene Ziffer: {C_BOLD}{digit}{C_RESET}")
                print(f"  ICD-Check:    {C_GREEN}✅ Gültig{C_RESET}")
            else:
                print(f"  {C_RED}❌ ICD-START FEHLER: {errors}{C_RESET}")

    client.on_message = on_message

    for sid in stations:
        client.subscribe(get_status_topic(sid), qos=1)
        client.subscribe(get_start_topic(sid), qos=1)

    print(f"{C_GREEN}✅ Verbunden und abonnierbereit!{C_RESET}")
    print(f"{C_CYAN}Warte auf eingehende MQTT-Nachrichten... (Drücke Ctrl+C zum Beenden){C_RESET}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}Empfänger beendet.{C_RESET}")
        print_summary_table()
    finally:
        client.loop_stop()
        client.disconnect()


# ==============================================================================
# MODUS 2: SENDEN (DASHBOARD START-SENDER & TEST-INJEKTOR)
# ==============================================================================

def run_sender(stations: List[int]):
    print(f"\n{C_BOLD}{'=' * 65}{C_RESET}")
    print(f"📤 {C_BOLD}SENDER AKTIV (Dashboard / Backend Simulator){C_RESET}")
    print(f"   Ziel-Station(en): {C_CYAN}{stations}{C_RESET}")
    print(f"   Broker: {BROKER_HOST}:{BROKER_PORT} (User: {USERNAME})")
    print(f"{C_BOLD}{'=' * 65}{C_RESET}\n")

    client = connect_mqtt(client_id=f"dash_tx_{int(time.time())}")
    if not client:
        return

    acks_received: Dict[int, Optional[dict]] = {}

    def on_status_ack(c, userdata, msg):
        for sid in stations:
            if msg.topic == get_status_topic(sid):
                valid, data, _ = validate_status_payload(msg.payload.decode("utf-8", errors="replace"), expected_station_id=sid)
                if valid and data:
                    acks_received[sid] = data

    client.on_message = on_status_ack
    for sid in stations:
        client.subscribe(get_status_topic(sid), qos=1)

    def send_start_to_stations(digits_map: Dict[int, int]):
        acks_received.clear()
        t0 = time.time()

        for sid, d in digits_map.items():
            topic = get_start_topic(sid)
            payload = json.dumps({"digit": d})
            client.publish(topic, payload, qos=1)
            print(f"-> Gesendet an Station {sid} ({topic}): {C_BOLD}{payload}{C_RESET}")

        print("Warte auf 'idle'-Antwort der Station(en)...")
        while time.time() - t0 < 3.0:
            if all(sid in acks_received and acks_received[sid].get("state") == "idle" for sid in digits_map):
                break
            time.sleep(0.05)

        for sid in digits_map:
            if sid in acks_received and acks_received[sid].get("state") == "idle":
                print(f"  Station {sid}: {C_GREEN}✅ BEREIT (idle bestätigt){C_RESET}")
            else:
                print(f"  Station {sid}: {C_YELLOW}⚠️  Keine Antwort (Modul noch offline?){C_RESET}")

    try:
        while True:
            print(f"\n{C_BOLD}Was möchtest du an Station(en) {stations} senden?{C_RESET}")
            print(" [1] 🚀 Game Start senden (Start-Topic mit Ziffer/Code)")
            print(" [2] 📡 Test-Status als Station senden (idle / active / solved simulieren)")
            print(" [q] Beenden")

            choice = input("\nAktion [1/2/q] > ").strip().lower()
            if choice in ("q", "0", "exit"):
                break

            if choice == "1":
                if len(stations) == 1:
                    sid = stations[0]
                    digit_in = input(f"Ziffer für Station {sid} (0-9) [Enter für Zufall]: ").strip()
                    digit = int(digit_in) if digit_in.isdigit() and 0 <= int(digit_in) <= 9 else random.randint(0, 9)
                    print(f"\nSende Start an Station {sid} mit Ziffer {digit}...")
                    send_start_to_stations({sid: digit})
                else:
                    code_in = input(f"{len(stations)}-stelliger Code [Enter für Zufall]: ").strip()
                    if len(code_in) == len(stations) and code_in.isdigit():
                        digits_map = {sid: int(code_in[i]) for i, sid in enumerate(stations)}
                    else:
                        digits_map = {sid: random.randint(0, 9) for sid in stations}

                    code_str = "".join(str(digits_map[s]) for s in stations)
                    print(f"\nSende Start an Stationen {stations} (Code: {code_str})...")
                    send_start_to_stations(digits_map)

            elif choice == "2":
                print(f"\n{C_BOLD}Welchen Status möchtest du für Station(en) {stations} senden?{C_RESET}")
                print(" [1] 'idle'   (Bereit)")
                print(" [2] 'active' (Spieler interagiert)")
                print(" [3] 'solved' (Gelöst - grün)")
                print(" [4] 'solved' (Gelöst - gelb)")
                print(" [5] 'solved' (Gelöst - rot)")
                print(" [6] Auto-Zyklus (idle -> 2s -> active -> 4s -> solved)")

                st_choice = input("Status-Auswahl [1-6] > ").strip()

                for sid in stations:
                    topic = get_status_topic(sid)
                    now_iso = datetime.now().isoformat(timespec="seconds")

                    if st_choice == "1":
                        payload = {"station_id": sid, "state": "idle", "rating": None, "duration_seconds": None, "timestamp_start": None, "timestamp_end": None}
                        client.publish(topic, json.dumps(payload), qos=1)
                        print(f"-> Gesendet auf '{topic}': {json.dumps(payload)}")
                    elif st_choice == "2":
                        payload = {"station_id": sid, "state": "active", "rating": None, "duration_seconds": None, "timestamp_start": now_iso, "timestamp_end": None}
                        client.publish(topic, json.dumps(payload), qos=1)
                        print(f"-> Gesendet auf '{topic}': {json.dumps(payload)}")
                    elif st_choice in ("3", "4", "5"):
                        rat = "green" if st_choice == "3" else ("yellow" if st_choice == "4" else "red")
                        payload = {"station_id": sid, "state": "solved", "rating": rat, "duration_seconds": 45, "timestamp_start": now_iso, "timestamp_end": now_iso}
                        client.publish(topic, json.dumps(payload), qos=1)
                        print(f"-> Gesendet auf '{topic}': {json.dumps(payload)}")
                    elif st_choice == "6":
                        print(f"\nStarte Test-Zyklus für Station {sid}...")
                        p_idle = {"station_id": sid, "state": "idle", "rating": None, "duration_seconds": None, "timestamp_start": None, "timestamp_end": None}
                        client.publish(topic, json.dumps(p_idle), qos=1)
                        print("  1. 'idle' gesendet. Warte 2s...")
                        time.sleep(2)

                        t_start = datetime.now()
                        p_act = {"station_id": sid, "state": "active", "rating": None, "duration_seconds": None, "timestamp_start": t_start.isoformat(timespec="seconds"), "timestamp_end": None}
                        client.publish(topic, json.dumps(p_act), qos=1)
                        print("  2. 'active' gesendet. Warte 4s...")
                        time.sleep(4)

                        t_end = datetime.now()
                        dur = int((t_end - t_start).total_seconds())
                        p_solv = {"station_id": sid, "state": "solved", "rating": "green", "duration_seconds": dur, "timestamp_start": t_start.isoformat(timespec="seconds"), "timestamp_end": t_end.isoformat(timespec="seconds")}
                        client.publish(topic, json.dumps(p_solv), qos=1)
                        print(f"  3. 'solved' (grün, {dur}s) gesendet! Zyklus fertig.")

    finally:
        client.loop_stop()
        client.disconnect()
        print("\nSender beendet.")


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def main():
    cli_mode = None
    cli_stations = None

    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        if arg1 in ("rx", "empfangen", "receive", "sub", "monitor", "1"):
            cli_mode = "1"
        elif arg1 in ("tx", "senden", "send", "pub", "start", "2"):
            cli_mode = "2"

    if len(sys.argv) > 2:
        cli_stations = parse_stations_input(sys.argv[2])

    print("\n" + "=" * 65)
    print(f"   💣 {C_BOLD}BOMB DEFUSAL PARKOUR - BACKEND & MODUL TESTER{C_RESET} 💣")
    print(f"   Broker: {C_CYAN}{BROKER_HOST}:{BROKER_PORT}{C_RESET} | User: {C_CYAN}{USERNAME}{C_RESET}")
    print("=" * 65)

    if cli_stations:
        stations = cli_stations
        print(f"Station(en) per Parameter gewählt: {C_CYAN}{stations}{C_RESET}")
    else:
        print("\nSchritt 1: Welche Station(en) möchtest du testen?")
        print(f"  - Einzelne Station: z.B. {C_BOLD}3{C_RESET}")
        print(f"  - Mehrere Stationen: z.B. {C_BOLD}3, 4{C_RESET}")
        print(f"  - Alle 6 Stationen:  {C_BOLD}all{C_RESET} oder einfach [Enter] drücken")

        station_input = input("\nStation(en) wählen [Standard: all] > ").strip()
        stations = parse_stations_input(station_input)

    print(f"-> Ausgewählte Station(en): {C_BOLD}{C_GREEN}{stations}{C_RESET}")

    if cli_mode:
        mode = cli_mode
    else:
        print("\nSchritt 2: Was soll dieses Terminal tun?")
        print(f"  [1] 📥 {C_BOLD}EMPFANGEN{C_RESET} (Dashboard-Monitor: Status der Stationen empfangen & prüfen)")
        print(f"  [2] 📤 {C_BOLD}SENDEN{C_RESET}    (Dashboard-Sender: Game Start & Ziffern an Stationen senden)")

        mode = input("\nModus wählen [1/2] > ").strip()

    if mode == "1":
        run_receiver(stations)
    elif mode == "2":
        run_sender(stations)
    else:
        print(f"{C_RED}Ungültige Auswahl (1 oder 2). Programm beendet.{C_RESET}")


if __name__ == "__main__":
    main()
