"""Load the repo's .env into os.environ, so the tools find FAL_KEY and OPENROUTER_API_KEY.

Variables already set in the environment win, so `FAL_KEY=... python tools/x.py` still overrides.
"""
import os
from pathlib import Path

ENV = Path(__file__).resolve().parent.parent / ".env"


def load_env(path=ENV):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():  # a BOM from Notepad is dropped
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
