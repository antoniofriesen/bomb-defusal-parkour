"""
main.py
=======
FastAPI-App fuer das Scoreboard-Backend.

Start (im Ordner scoreboard/backend/):
    uvicorn main:app --reload --port 8001

Danach im Browser: http://localhost:8001/  (die Scoreboard-Seite)
API direkt:         http://localhost:8001/scoreboard
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from games_source import get_games
from ranking import build_ranking

app = FastAPI(title="Bomb Defusal Parkour - Scoreboard")

# Erlaubt dem Frontend (auch von einem anderen Port/Rechner) den Zugriff.
# Fuer die Messe koennt ihr das auf die echte Adresse des Dashboard-Pis einschraenken.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)


@app.get("/scoreboard")
def scoreboard() -> dict:
    games = get_games()
    return {"ranking": build_ranking(games)}


# Liefert scoreboard/frontend/ als Webseite aus (kein zweiter Server noetig)
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
