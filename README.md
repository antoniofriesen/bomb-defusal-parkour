# Bomb Defusal Parkour

Cyber-physischer Rätselparkour (LF07, Klasse BGH): Mehrere Gruppen lösen Stationen, jede Station liefert eine Ziffer, aus den Ziffern entsteht der Code zum Entschärfen der Bombe. Die Stationen und das Dashboard der Koordinationszelle kommunizieren über MQTT.

## Dokumentation

- [`docs/ICD_Bomb_Defusal_Parkour.md`](./docs/ICD_Bomb_Defusal_Parkour.md): **Interface Control Document.** Verbindlich für alle Zellen (Topics, Payload-Format).
- [`docs/sequence_diagram_mqtt.md`](./docs/sequence_diagram_mqtt.md): Nachrichtenfluss zwischen Dashboard, Broker und Station.
- [`docs/network_diagram.md`](./docs/network_diagram.md): Netzwerk-Aufbau.
- [`docs/dashboard_mockup.html`](./docs/dashboard_mockup.html): Mockup des Dashboards.

## MQTT-Broker Verbindung

WLAN: `Group - Stadt` (Passwort: `Group-Stadt`)

| Parameter | Wert |
|---|---|
| `BROKER_HOST` | `172.17.0.1` |
| `BROKER_PORT` | `1883` |
| `USERNAME` | `pi_user` |
| `PASSWORD` | `group-1` |

## `icd_interface.py` benutzen

Die Datei baut Topic-Strings und Payloads exakt nach dem ICD und prüft die Werte. Sie hat **keine Abhängigkeiten** (nur Python-Standardbibliothek) und verbindet sich **nicht** selbst mit dem Broker. Die MQTT-Verbindung (`paho-mqtt`: connect, subscribe, publish) schreibt jede Zelle selbst.

Kopiere `icd_interface.py` in dein Stations-Projekt und importiere sie:

```python
import json

from icd_interface import ICDInterface

# Station: eigenen Status senden
payload = ICDInterface.status_payload(
    station_id=1,
    state="solved",
    rating="green",
    timestamp_start="2026-09-17T10:15:00",
    timestamp_end="2026-09-17T10:20:00",
)
client.publish(ICDInterface.status_topic(1), json.dumps(payload))

# Station: auf den eigenen Digit warten
client.subscribe(ICDInterface.start_topic(1))
```

Wer ruft was auf:

| Methode | Aufgerufen von |
|---|---|
| `status_payload()` | nur Stationen (sie senden den Status) |
| `start_payload()` | nur Koordinationszelle (sie sendet den Digit) |
| `start_topic()`, `status_topic()` | beide (Publish und Subscribe brauchen den Topic-String) |

Bei ungültigen Werten (z.B. `state="broken"`) wirft die Datei einen `ValueError`.

## Tests ausführen

Die Tests prüfen `icd_interface.py` gegen die Beispiele im ICD. Nach dem Klonen bzw. Pullen, in einer virtuellen Umgebung (`.venv`):

```bash
pip install -r requirements-dev.txt
pytest
```

Mit `pytest -v` siehst du jeden Test einzeln.
