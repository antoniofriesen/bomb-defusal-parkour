# Bomb Defusal Parkour – Frontend Dashboard

Modernes, reaktives Vue 3 Dashboard für den cyber-physischen Rätselparkour (LF07).

---

## 🚀 Schnelleinstieg

```bash
# Im Verzeichnis frontend/dashboard:
npm install

# Entwicklungsserver starten:
npm run dev

# Produktions-Build erstellen:
npm run build
```

Der Entwicklungsserver läuft standardmäßig unter: **`http://localhost:5173`**

---

## ✨ Umgesetzte Funktionen & Anforderungen

1. **Landing Page:**
   - Eingabe des **Teamnamens** und der **Teilnehmeranzahl** (Spieler).
   - Validierung der Eingaben.
   - Übermittlung an das Backend bzw. den Mock-Service.

2. **Nahtlose Weiterleitung ohne URL-Wechsel:**
   - Reine zustandsbasierte Navigation (`currentView = 'landing' | 'game' | 'result'`).
   - Die URL in der Browser-Adresszeile bleibt stets unverändert.

3. **Fetter roter 10-Minuten-Countdown (`MM:SS:MS`):**
   - Große, leuchtende digitale LED-Anzeige (`Orbitron`-Typografie) mit Millisekunden-Genauigkeit.
   - Dynamischer Fortschritts- und Spannungsbalken.
   - Visuelles und akustisches Warnpulsieren bei weniger als 60 bzw. 20 Sekunden.
   - Automatische Detonation / Game Over bei Ablauf der Zeit (`00:00:000`).

4. **6-stellige Code-Eingabe:**
   - Taktile Pin-Eingabefelder für die Ziffern der Stationen Z1 bis Z6.
   - Tastaturnavigation (automatischer Fokus auf das nächste Feld, Backspace-Sprung, Pfeiltasten, Enter).
   - Vollständige Paste-Unterstützung (z.B. Einfügen von `"739215"`).
   - Button **"Code prüfen & entschärfen"** mit Lade-Indikator.
   - Fehler-Shake-Animation bei falschem Code sowie Historie der bisherigen Versuche.
   - Konfetti-Animation und Sieges-Fanfare bei erfolgreicher Entschärfung.

5. **Single-Game-Garantie (Nur ein Spiel zeitgleich):**
   - Solange eine Mission aktiv läuft, kann kein zweites Spiel gestartet werden.
   - Sollte ein Nutzer auf die Landing Page navigieren, wird eine prominente Warnung mit Team-Details und dem Button **"Zurück zum Countdown"** angezeigt; das Startformular ist gesperrt.
   - Möglichkeit zum kontrollierten Missionsabbruch durch Spielleiter mit Bestätigungsdialog.

6. **Browser-Reload Persistenz:**
   - Der Spielstatus, die Startzeit und die Ziel-Endzeit (`targetEndTime`) werden in `localStorage` synchronisiert.
   - **Wird die Seite neu geladen oder der Browser geschlossen und wieder geöffnet**, erkennt das Dashboard das laufende Spiel und wechselt sofort wieder auf die Unterseite mit dem weiterlaufenden Countdown (in Echtzeit synchronisiert).

7. **Erweiterter Einstellungs- & Mocking-Modus (Mocking UI):**
   - Einstellungen können diskret über das Zahnrad-Icon oder die Schaltfläche **„LF07“** geöffnet werden.
   - **Dedizierte Mocking Steuerkonsole & Live-Stats:**
     - Über die Einstellungen kann mit einem Klick das **Mocking UI** aufgerufen werden.
     - Optional lässt sich ein **„🛠️ Mock-UI“** Schnellzugriffs-Button in der Navigationsleiste aktivieren.
     - **Funktionen der Mocking Steuerkonsole:**
       - **Spiel & Countdown:** Spielstatus (`not_started`, `running`, `defused`, `detonated`), Ansichtswechsel, Timer pausieren/fortsetzen, Restzeit manuell oder via Presets (10m, 5m, 1m Urgent, 20s Kritisch, Detonation) setzen, Team & Spieler live editieren.
       - **Stationen (1–6):** Status (`idle`, `active`, `solved`), Ampel-Ratings (`grün`, `gelb`, `rot`), Lösungsziffern und Zeiten für jede Station einzeln oder per Massenaktion setzen; automatischer Lösungsfortschritt per Schalter an-/abschaltbar.
       - **Code & Validierung:** 6-stelligen Mock-Code ändern, Zufallscode generieren, Validierungsmodus (`normal`, `immer korrekt / Force Win`, `immer falsch / Force Fail`) und eigene Fehlermeldungen konfigurieren, Code-Versuchs-Historie verwalten.
       - **Live Stats & Presets:** Schnellszenarien (Reset, Spielstart, Halbzeit, Finale, Sieg, Detonation) und JSON-Snapshot zum Kopieren.

8. **Stationen Live Monitor (REST-Synchronisation):**
   - Status-Karten für Station 1 bis 6:
     - State: `idle` (grau), `active` (blau), `solved` (grün)
     - Ampel-Feedback: `green`, `yellow`, `red`
     - Berechnete Dauer (`timestamp_end - timestamp_start`)
   - Im Live-Betrieb werden die Stationen automatisch über `GET /api/game/status` synchronisiert.

---

## 🔌 Backend REST-Schnittstelle

Die gesamte Kommunikation erfolgt über eine REST-API (`src/services/api.js`):

- **Endpunkte:**
  - `POST /api/game/start`: Übergibt `{ team_name, participant_count, duration_seconds }`
  - `POST /api/game/stop`: Stoppt / bricht das laufende Spiel ab
  - `GET  /api/game/status`: Liefert den aktuellen Spiel- und Stationsstatus
  - `POST /api/game/check-code`: Prüft den 6-stelligen Entschärfungscode (`{ code, team_name }`)
- **Konfiguration:**
  - Die Backend-URL (Standard: `http://localhost:8000/api`) lässt sich über den Klick auf **LF07** anpassen oder direkt in `src/services/api.js` konfigurieren.
