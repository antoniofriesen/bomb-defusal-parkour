"""
config.py
=========
Central settings via environment variables, instead of values
scattered through the code. Switchable at the event via an
environment variable, without touching code.
"""

from __future__ import annotations

import os

DASHBOARD_BACKEND_URL = os.environ.get("DASHBOARD_BACKEND_URL", "http://localhost:5000")

# "true" as long as the colleague's real endpoint isn't ready yet.
USE_FAKE_DATA = os.environ.get("SCOREBOARD_USE_FAKE_DATA", "true").lower() == "true"
