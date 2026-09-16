# 💣 Bomb Defusal Parkour – README

Diese README richtet sich an **alle Zellen**, die eine Station bauen. Sie erklärt, wie ihr `mqtt_interface.py` nutzt, um mit dem Dashboard der Koordinationszelle zu kommunizieren.

> Für Details zum Spielablauf, MQTT-Schema und ICD siehe [`CLAUDE.md`](./CLAUDE.md).

---

## Setup

1. `mqtt_interface.py` in euer Stations-Projekt kopieren (oder das ganze Repo klonen).
2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

3. IP-Adresse des Brokers (Koordinations-Pi) von der Koordinationszelle erfragen.

---

## Grundgerüst einer Station

```python
from mqtt_interface import MQTTInterface

mqtt = MQTTInterface(station_id=1, broker_ip="192.168.1.100")  # eure Stationsnummer + Broker-IP

# Wird aufgerufen, sobald das Spiel gestartet wird und ihr euren Digit bekommt
def on_game_start(digit, team):
    print(f"Mein Digit: {digit}, Team: {team}")
    # TODO: Digit merken, erst nach gelöstem Rätsel anzeigen

mqtt.on_start = on_game_start
mqtt.connect()

mqtt.loop_forever()  # blockiert – hält die Verbindung offen
```

- `station_id`: eure feste Stationsnummer (1–6), von der Koordinationszelle vergeben.
- `broker_ip`: IP-Adresse des Mosquitto-Brokers auf dem Koordinations-Pi.
- `mqtt.connect()` verbindet sich und lauscht im Hintergrund automatisch auf euer `start`-Topic.

---

## Status an das Dashboard melden

Sobald ein Spieler an eurer Station **aktiv wird**:

```python
start_time = MQTTInterface.now_iso()
mqtt.send_active(timestamp_start=start_time)
```

Sobald die Station **gelöst** ist:

```python
end_time = MQTTInterface.now_iso()
mqtt.send_solved(
    rating="green",              # "green" | "yellow" | "red" – Schwierigkeitsfeedback
    duration_seconds=213,
    timestamp_start=start_time,
    timestamp_end=end_time
)
```

`now_iso()` liefert euch die aktuelle Zeit im richtigen ISO-8601-Format – keine eigene Zeitformatierung nötig.

Für Sonderfälle könnt ihr auch direkt `send_status(...)` mit allen Feldern aufrufen (siehe Docstring in `mqtt_interface.py`).

---

## Pflicht-Methoden

`mqtt_interface.py` ist fertig implementiert – Zellen **rufen die Methoden nur auf**, sie schreiben keine eigene MQTT-Logik (siehe Regeln unten). Diese Methoden sind für jede Station Pflicht:

| # | Methode | Wann aufrufen |
|---|---|---|
| 1 | `MQTTInterface(station_id, broker_ip)` | Einmal beim Start des Stations-Scripts |
| 2 | `mqtt.on_start = callback` | Direkt danach, um den Digit zu empfangen |
| 3 | `mqtt.connect()` | Einmal, verbindet zum Broker |
| 4 | `MQTTInterface.now_iso()` | Für jeden Zeitstempel (in Kombination mit 5/6) |
| 5 | `mqtt.send_active(timestamp_start)` | Wenn ein Spieler an der Station anfängt |
| 6 | `mqtt.send_solved(...)` | Wenn das Rätsel gelöst ist |
| 7 | `mqtt.loop_forever()` | Am Ende des Scripts – **nur falls die Station keine eigene Dauerschleife hat** (z.B. für Sensor-Polling). Habt ihr selbst ein `while True:`, braucht ihr `loop_forever()` nicht zusätzlich. |

**Optional / selten nötig:**
- `send_status(...)` – der "rohe" Aufruf mit allen Feldern einzeln. Nur für Sonderfälle, die nicht durch `send_active`/`send_solved` abgedeckt sind.
- `disconnect()` – sauberes Aufräumen, v.a. beim Testen/Debuggen relevant.

**Nie direkt aufrufen** (interne Plumbing, `_`-Prefix): `_on_connect`, `_on_message`, `_on_disconnect`, `_publish`.

Was die Zelle **selbst schreibt**, ist nur die eigene Sensorik-/Rätsellogik – also was innerhalb von `on_game_start(digit, team)` passiert und wann genau `send_active`/`send_solved` getriggert wird. Die Kommunikation mit dem Broker läuft immer über die obigen Methoden.

---

## Wichtige Regeln

- **Nie** eigene MQTT-Logik schreiben – immer über `mqtt_interface.py` kommunizieren.
- Stationen sprechen **nie direkt miteinander**, nur über die Koordinationszelle (Broker/Dashboard).
- Nur die vorgesehenen `rating`-Werte verwenden: `"green"`, `"yellow"`, `"red"` (Groß-/Kleinschreibung beachten).
- `station_id` muss exakt der von der Koordinationszelle zugewiesenen Nummer entsprechen – sonst landen eure Digits/Status bei der falschen Station.

---

## Testen ohne echten Broker-Zugriff

`mqtt_interface.py` kann direkt ausgeführt werden und simuliert einen kompletten Durchlauf (verbinden → aktiv → gelöst):

```bash
python mqtt_interface.py
```

Vorher `BROKER_IP` und `STATION_ID` am Ende der Datei anpassen.

---

## Fragen / Probleme

Bei Problemen mit Broker-Verbindung, Topics oder dem ICD: Koordinationszelle ansprechen.
